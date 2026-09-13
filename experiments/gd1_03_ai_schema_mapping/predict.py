# -*- coding: utf-8 -*-
"""Dự đoán nhãn Schema Mapping cho tên cột.

Không chứa Business Rule và không trả kết quả YES/NO trả lương.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import joblib
import numpy as np

try:
    from .alias_mapper import AliasMapper, DEFAULT_ALIAS_PATH
    from .preprocessing import TextPreprocessor
    from .settings import CONFIDENCE_THRESHOLD, LABELS
except ImportError:
    from alias_mapper import AliasMapper, DEFAULT_ALIAS_PATH
    from preprocessing import TextPreprocessor
    from settings import CONFIDENCE_THRESHOLD, LABELS


class ColumnMappingPredictor:
    def __init__(
        self,
        model_path: str | Path | None = None,
        alias_path: str | Path | None = None,
        confidence_threshold: float | None = None,
    ):
        self.preprocessor = TextPreprocessor()
        self.alias_mapper = AliasMapper(alias_path or DEFAULT_ALIAS_PATH)
        self.pipeline = None
        self.use_ai = False
        self.remove_accent = False
        self.confidence_threshold = (
            CONFIDENCE_THRESHOLD
            if confidence_threshold is None
            else float(confidence_threshold)
        )

        if model_path:
            path = Path(model_path)
            if path.exists():
                artifact = joblib.load(path)
                self.pipeline = artifact["pipeline"]
                artifact_labels = artifact.get("labels", LABELS)
                if list(artifact_labels) != list(LABELS):
                    raise ValueError(
                        "Model dùng class khác cấu hình hiện tại. Cần train lại model."
                    )
                self.remove_accent = artifact.get("preprocessor_config", {}).get(
                    "remove_accent", False
                )
                self.confidence_threshold = float(
                    artifact.get("confidence_threshold", self.confidence_threshold)
                )
                self.use_ai = True

    def predict_single(self, column_name: str) -> dict:
        original_text = "" if column_name is None else str(column_name)

        # Alias exact là rule xác định, ưu tiên trước AI để tránh model làm sai tên quen thuộc.
        alias_label = self.alias_mapper.lookup(original_text)
        if alias_label:
            return {
                "label": alias_label,
                "confidence": 1.0,
                "source": "alias_exact",
                "accepted": True,
                "original_text": original_text,
            }

        processed = self.preprocessor.preprocess(
            original_text,
            remove_accent=self.remove_accent,
        )

        if not processed or not self.use_ai:
            return self._other_result(original_text)

        X = np.asarray([processed])
        pred_label = str(self.pipeline.predict(X)[0])
        confidence = self._get_confidence(X, pred_label)

        if confidence >= self.confidence_threshold:
            return {
                "label": pred_label,
                "confidence": confidence,
                "source": "ai_model",
                "accepted": True,
                "original_text": original_text,
            }

        # AI confidence thấp và không có exact alias -> OTHER.
        result = self._other_result(original_text)
        result["suggested_label"] = pred_label
        result["suggested_confidence"] = confidence
        return result

    def predict_batch(self, column_names: list[str]) -> list[dict]:
        return [self.predict_single(name) for name in column_names]

    def _get_confidence(self, X: np.ndarray, pred_label: str) -> float:
        if self.pipeline is None or not hasattr(self.pipeline, "predict_proba"):
            return 0.0

        proba = self.pipeline.predict_proba(X)[0]
        clf = self.pipeline.named_steps["clf"]
        classes = list(clf.classes_)
        if pred_label not in classes:
            return 0.0
        return float(proba[classes.index(pred_label)])

    @staticmethod
    def _other_result(original_text: str) -> dict:
        return {
            "label": "OTHER",
            "confidence": 0.0,
            "source": "default",
            "accepted": False,
            "original_text": original_text,
        }
