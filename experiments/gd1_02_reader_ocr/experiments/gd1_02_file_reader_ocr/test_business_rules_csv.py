# -*- coding: utf-8 -*-
"""GĐ1-02: Kiểm tra File Reader có đọc được mock_business_rules.csv."""

from __future__ import annotations

import csv
import json
from pathlib import Path

THU_MUC_DU_AN = Path(__file__).resolve().parents[2]
TEST_FILE = THU_MUC_DU_AN / "data" / "mock_business_rules.csv"

CAC_COT_BAT_BUOC = {
    "ma_quy_tac",
    "pham_vi",
    "ket_qua",
    "can_cu",
    "dang_ap_dung",
}


def doc_csv_rule(duong_dan: Path):
    with open(duong_dan, "r", encoding="utf-8-sig", newline="") as tep:
        reader = csv.DictReader(tep)
        headers = reader.fieldnames or []
        rows = [dict(row) for row in reader]
    return headers, rows


def kiem_tra_cau_truc(headers, rows):
    loi = []
    thieu_cot = sorted(CAC_COT_BAT_BUOC - set(headers))
    if thieu_cot:
        loi.append(f"Thiếu cột bắt buộc: {thieu_cot}")

    for i, row in enumerate(rows, start=2):
        if row.get("ket_qua") not in {"YES", "NO"}:
            loi.append(f"Dòng {i}: ket_qua phải là YES hoặc NO")
        if row.get("dang_ap_dung") not in {"0", "1"}:
            loi.append(f"Dòng {i}: dang_ap_dung phải là 0 hoặc 1")
    return loi


def tao_output(headers, rows, duong_dan: Path):
    return {
        "trang_thai": "success",
        "ten_file": duong_dan.name,
        "loai_file": "csv",
        "pdf_mode": None,
        "ocr_da_su_dung": False,
        "du_lieu": {
            "headers": headers,
            "rows": rows,
            "so_dong": len(rows),
        },
        "loi": None,
    }


def main():
    if not TEST_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy {TEST_FILE}")

    headers, rows = doc_csv_rule(TEST_FILE)
    errors = kiem_tra_cau_truc(headers, rows)

    print(f"File      : {TEST_FILE}")
    print(f"Headers   : {headers}")
    print(f"Số record : {len(rows)}")
    print(f"Validation: {'OK' if not errors else 'CÓ LỖI'}")
    for error in errors:
        print(f"- {error}")

    print("\nFILE READER OUTPUT")
    print(json.dumps(tao_output(headers, rows, TEST_FILE), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
