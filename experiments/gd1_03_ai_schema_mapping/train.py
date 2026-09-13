# -*- coding: utf-8 -*-
"""Train AI Schema Mapping.

Baseline chính: TF-IDF Character N-gram + Logistic Regression.
Có thể so sánh Linear SVM nhưng dùng calibration để confidence có ý nghĩa hơn.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

try:
    from .evaluate import ModelEvaluator
    from .preprocessing import TextPreprocessor
    from .settings import CONFIDENCE_THRESHOLD, LABELS, RANDOM_STATE
except ImportError:
    from evaluate import ModelEvaluator
    from preprocessing import TextPreprocessor
    from settings import CONFIDENCE_THRESHOLD, LABELS, RANDOM_STATE


class ColumnMappingTrainer:
    def __init__(self, model_type: str = "logistic"):
        self.model_type = model_type
        self.preprocessor = TextPreprocessor()
        self.pipeline: Pipeline | None = None
        self.metrics: dict | None = None

    def load_data(self, csv_path: str | Path):
        df = pd.read_csv(csv_path)
        required = {"text", "label"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Dataset thiếu cột bắt buộc: {sorted(missing)}")

        df = df.dropna(subset=["text", "label"]).copy()
        df["text"] = df["text"].astype(str).str.strip()
        df["label"] = df["label"].astype(str).str.strip()
        df = df[df["text"] != ""]

        invalid_labels = sorted(set(df["label"]) - set(LABELS))
        if invalid_labels:
            raise ValueError(f"Dataset có label không hợp lệ: {invalid_labels}")

        counts = df["label"].value_counts()
        missing_labels = [label for label in LABELS if label not in counts]
        if missing_labels:
            raise ValueError(f"Dataset chưa có dữ liệu cho class: {missing_labels}")
        if counts.min() < 2:
            raise ValueError("Mỗi class cần ít nhất 2 mẫu để chia train/test stratify")

        texts = self.preprocessor.preprocess_batch(df["text"].tolist())
        return np.asarray(texts), df["label"].to_numpy()

    def _build_pipeline(self, calibration_cv: int = 3) -> Pipeline:
        if self.model_type == "logistic":
            classifier = LogisticRegression(
                max_iter=2000,
                C=1.0,
                class_weight="balanced",
                random_state=RANDOM_STATE,
            )
        elif self.model_type == "svm":
            base_svm = LinearSVC(
                C=1.0,
                class_weight="balanced",
                random_state=RANDOM_STATE,
                max_iter=5000,
            )
            classifier = CalibratedClassifierCV(
                estimator=base_svm,
                method="sigmoid",
                cv=calibration_cv,
            )
        else:
            raise ValueError("model_type chỉ nhận 'logistic' hoặc 'svm'")

        return Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(
                        analyzer="char",
                        ngram_range=(2, 5),
                        sublinear_tf=True,
                        strip_accents="unicode",
                    ),
                ),
                ("clf", classifier),
            ]
        )

    def train(
        self,
        csv_path: str | Path,
        test_size: float = 0.2,
        random_state: int = RANDOM_STATE,
    ) -> dict:
        X, y = self.load_data(csv_path)

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
            stratify=y,
        )

        # SVM calibration cần đủ mẫu/class trong train.
        train_counts = pd.Series(y_train).value_counts()
        calibration_cv = min(3, int(train_counts.min()))
        if self.model_type == "svm" and calibration_cv < 2:
            raise ValueError("SVM calibration cần ít nhất 2 mẫu/class trong tập train")

        self.pipeline = self._build_pipeline(calibration_cv=max(2, calibration_cv))
        self.pipeline.fit(X_train, y_train)

        # Cross-validation chỉ dùng tập train, không đụng vào holdout test.
        min_train_count = int(train_counts.min())
        cv = min(5, min_train_count)
        cv_f1_macro = None
        cv_f1_std = None
        if cv >= 2:
            scores = cross_val_score(
                self.pipeline,
                X_train,
                y_train,
                cv=cv,
                scoring="f1_macro",
            )
            cv_f1_macro = float(scores.mean())
            cv_f1_std = float(scores.std())

        evaluator = ModelEvaluator(LABELS)
        metrics = evaluator.evaluate(self.pipeline, X_test, y_test)
        metrics["cv_f1_macro"] = cv_f1_macro
        metrics["cv_f1_std"] = cv_f1_std
        metrics["train_size"] = len(X_train)
        metrics["test_size"] = len(X_test)
        self.metrics = metrics

        evaluator.print_metrics(metrics)
        if cv_f1_macro is not None:
            print(
                f"\nCross-validation trên TRAIN - F1 macro: "
                f"{cv_f1_macro:.4f} ± {cv_f1_std:.4f}"
            )

        return metrics

    def save_model(self, model_path: str | Path) -> None:
        if self.pipeline is None:
            raise RuntimeError("Chưa train model nên không thể lưu")

        model_path = Path(model_path)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        artifact = {
            "pipeline": self.pipeline,
            "model_type": self.model_type,
            "labels": LABELS,
            "confidence_threshold": CONFIDENCE_THRESHOLD,
            "preprocessor_config": {"remove_accent": False},
        }
        joblib.dump(artifact, model_path)
        print(f"Đã lưu model: {model_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train AI Schema Mapping")
    parser.add_argument(
        "--dataset",
        default="data_ai/schema_mapping_dataset.csv",
        help="CSV có 2 cột text,label",
    )
    parser.add_argument(
        "--model",
        default="models/schema_mapping/column_mapping_model.pkl",
        help="Nơi lưu model",
    )
    parser.add_argument(
        "--model-type",
        choices=["logistic", "svm"],
        default="logistic",
    )
    args = parser.parse_args()

    trainer = ColumnMappingTrainer(args.model_type)
    trainer.train(args.dataset)
    trainer.save_model(args.model)


if __name__ == "__main__":
    main()
