# -*- coding: utf-8 -*-
"""Upload adapter GĐ1-05.

GĐ1-05 không tự viết File Reader/OCR. CSV được dùng để kiểm tra đường tích hợp;
XLSX/DOCX/PDF sẽ được nối GĐ1-02 ở GĐ2. Mapping header CSV ưu tiên GĐ1-03.
"""

from __future__ import annotations

import csv
import io
import sqlite3
import unicodedata
from typing import Any

from .gd1_03_bridge import tao_predictor


def _chuan_hoa_ten(text: str) -> str:
    text = str(text or "").strip().lower().replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def _decode_csv(content: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return content.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("Không đọc được encoding CSV")


def _map_headers(headers: list[str]) -> tuple[dict[str, str], list[dict[str, Any]]]:
    predictor = tao_predictor()
    mapping: dict[str, str] = {}
    details: list[dict[str, Any]] = []

    for header in headers:
        if predictor is not None:
            result = predictor.predict_single(header)
            label = result["label"]
            details.append(result)
        else:
            # Chỉ fallback cho tên cột chuẩn của hệ thống, không thay AI Schema Mapping.
            norm = _chuan_hoa_ten(header).replace("_", " ")
            fallback = {
                "ma nhan vien": "MA_NHAN_VIEN",
                "ho ten": "HO_TEN",
                "don vi": "TEN_DON_VI",
                "ten don vi": "TEN_DON_VI",
                "loai don vi": "LOAI_DON_VI",
            }
            label = fallback.get(norm, "OTHER")
            details.append(
                {
                    "label": label,
                    "confidence": 1.0 if label != "OTHER" else 0.0,
                    "source": "standard_header_fallback",
                    "accepted": label != "OTHER",
                    "original_text": header,
                }
            )

        if label != "OTHER" and label not in mapping:
            mapping[label] = header

    return mapping, details


def import_employee_csv(conn: sqlite3.Connection, content: bytes) -> dict[str, Any]:
    text = _decode_csv(content)
    reader = csv.DictReader(io.StringIO(text))
    headers = reader.fieldnames or []
    if not headers:
        raise ValueError("CSV không có header")

    mapping, details = _map_headers(headers)
    if "MA_NHAN_VIEN" not in mapping or "HO_TEN" not in mapping:
        return {
            "ok": False,
            "message": "Không xác định được MA_NHAN_VIEN hoặc HO_TEN. Cần GĐ1-03/GĐ2 mapping thêm.",
            "mapping": details,
            "so_dong_import": 0,
        }

    count = 0
    for row in reader:
        ma = (row.get(mapping["MA_NHAN_VIEN"]) or "").strip()
        ho_ten = (row.get(mapping["HO_TEN"]) or "").strip()
        don_vi_col = mapping.get("TEN_DON_VI")
        don_vi = (row.get(don_vi_col) or "").strip() if don_vi_col else ""
        if not ma or not ho_ten:
            continue
        conn.execute(
            """
            INSERT INTO nhan_vien (ma_nhan_vien, ho_ten, ho_ten_chuan, don_vi)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(ma_nhan_vien) DO UPDATE SET
                ho_ten=excluded.ho_ten,
                ho_ten_chuan=excluded.ho_ten_chuan,
                don_vi=excluded.don_vi
            """,
            (ma, ho_ten, _chuan_hoa_ten(ho_ten), don_vi or None),
        )
        count += 1

    conn.commit()
    return {
        "ok": True,
        "message": f"Đã import {count} nhân viên từ CSV.",
        "mapping": details,
        "so_dong_import": count,
    }
