# -*- coding: utf-8 -*-
"""Đánh giá model trên holdout test đã tách trước khi train.

Module này KHÔNG tự chia lại dataset để tránh nguy cơ data leakage.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


class ModelEvaluator:
    def __init__(self, labels: list[str]):
        self.labels = labels

    def evaluate(self, pipeline, X_test, y_test) -> dict:
        """Đánh giá đúng trên X_test/y_test chưa từng dùng để fit model."""
        y_pred = pipeline.predict(X_test)
        cm = confusion_matrix(y_test, y_pred, labels=self.labels)

        return {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision_macro": float(
                precision_score(y_test, y_pred, average="macro", zero_division=0)
            ),
            "recall_macro": float(
                recall_score(y_test, y_pred, average="macro", zero_division=0)
            ),
            "f1_macro": float(
                f1_score(y_test, y_pred, average="macro", zero_division=0)
            ),
            "f1_weighted": float(
                f1_score(y_test, y_pred, average="weighted", zero_division=0)
            ),
            "confusion_matrix": cm,
            "classification_report": classification_report(
                y_test,
                y_pred,
                labels=self.labels,
                zero_division=0,
                output_dict=True,
            ),
            "y_test": np.asarray(y_test),
            "y_pred": np.asarray(y_pred),
        }

    def print_metrics(self, metrics: dict) -> None:
        print("=" * 60)
        print("ĐÁNH GIÁ AI SCHEMA MAPPING")
        print("=" * 60)
        print(f"Accuracy          : {metrics['accuracy']:.4f}")
        print(f"Precision macro   : {metrics['precision_macro']:.4f}")
        print(f"Recall macro      : {metrics['recall_macro']:.4f}")
        print(f"F1 macro          : {metrics['f1_macro']:.4f}")
        print(f"F1 weighted       : {metrics['f1_weighted']:.4f}")

        print("\nConfusion Matrix:")
        cm_df = pd.DataFrame(
            metrics["confusion_matrix"],
            index=[f"Thực: {label}" for label in self.labels],
            columns=[f"Dự đoán: {label}" for label in self.labels],
        )
        print(cm_df)

        print("\nClassification Report:")
        report_df = pd.DataFrame(metrics["classification_report"]).transpose()
        print(report_df.to_string())

    def save_confusion_matrix(self, metrics: dict, save_path: str | Path) -> None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        display = ConfusionMatrixDisplay(
            confusion_matrix=metrics["confusion_matrix"],
            display_labels=self.labels,
        )
        fig, ax = plt.subplots(figsize=(9, 7))
        display.plot(ax=ax, xticks_rotation=45, colorbar=False)
        ax.set_title("Confusion Matrix - AI Schema Mapping")
        fig.tight_layout()
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
