# -*- coding: utf-8 -*-
"""Alias fallback cho AI Schema Mapping.

File này CHỈ ánh xạ tên cột -> nhãn chuẩn.
Không đọc Business Rule và không quyết định YES/NO.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

try:
    from .preprocessing import TextPreprocessor
    from .settings import LABELS
except ImportError:
    from preprocessing import TextPreprocessor
    from settings import LABELS


DEFAULT_ALIAS_PATH = Path(__file__).resolve().parent / "config" / "field_aliases.json"


class AliasMapper:
    """Đọc alias từ một nguồn JSON duy nhất và match chính xác sau chuẩn hóa."""

    def __init__(self, alias_path: str | Path | None = None):
        self.preprocessor = TextPreprocessor()
        self.alias_path = Path(alias_path) if alias_path else DEFAULT_ALIAS_PATH
        self.alias_to_label: dict[str, str] = {}
        self._load_aliases()

    def _normalize_alias(self, text: str) -> str:
        return self.preprocessor.preprocess(text, remove_accent=True)

    def _load_aliases(self) -> None:
        if not self.alias_path.exists():
            raise FileNotFoundError(f"Không tìm thấy alias config: {self.alias_path}")

        with open(self.alias_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        allowed_labels = set(LABELS) - {"OTHER"}
        invalid_labels = sorted(set(data.keys()) - allowed_labels)
        if invalid_labels:
            raise ValueError(
                "Alias config có label không hợp lệ: " + ", ".join(invalid_labels)
            )

        for label, aliases in data.items():
            if not isinstance(aliases, list):
                raise ValueError(f"Alias của {label} phải là list")

            for alias in aliases:
                normalized = self._normalize_alias(str(alias))
                if not normalized:
                    continue

                old_label = self.alias_to_label.get(normalized)
                if old_label and old_label != label:
                    raise ValueError(
                        f"Alias '{alias}' bị trùng giữa {old_label} và {label}"
                    )
                self.alias_to_label[normalized] = label

    def lookup(self, column_name: str) -> Optional[str]:
        """Exact match sau chuẩn hóa; không dùng substring để tránh match nhầm."""
        if not column_name:
            return None
        normalized = self._normalize_alias(str(column_name))
        return self.alias_to_label.get(normalized)
