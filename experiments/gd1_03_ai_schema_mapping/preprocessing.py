# -*- coding: utf-8 -*-
"""Tiền xử lý tên cột trước khi đưa vào AI Schema Mapping."""

from __future__ import annotations

import re
import unicodedata


class TextPreprocessor:
    """Chuẩn hóa tên cột nhưng không gắn logic nghiệp vụ YES/NO."""

    @staticmethod
    def normalize_unicode(text: str) -> str:
        return unicodedata.normalize("NFC", text)

    @staticmethod
    def lowercase(text: str) -> str:
        return text.lower().strip()

    @staticmethod
    def remove_special_chars(text: str) -> str:
        # Đổi các ký tự phân cách thường gặp thành khoảng trắng trước.
        text = text.replace("_", " ").replace("-", " ")
        # \w trong Python hỗ trợ chữ Unicode; loại bỏ dấu câu/ký tự đặc biệt.
        text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def remove_accents(text: str) -> str:
        text = unicodedata.normalize("NFD", text)
        text = "".join(c for c in text if unicodedata.category(c) != "Mn")
        return text.replace("đ", "d").replace("Đ", "D")

    def preprocess(self, text: str, remove_accent: bool = False) -> str:
        if not isinstance(text, str):
            return ""

        text = self.normalize_unicode(text)
        text = self.lowercase(text)
        text = self.remove_special_chars(text)

        if remove_accent:
            text = self.remove_accents(text)

        return text

    def preprocess_batch(
        self,
        texts: list[str],
        remove_accent: bool = False,
    ) -> list[str]:
        return [self.preprocess(text, remove_accent) for text in texts]
