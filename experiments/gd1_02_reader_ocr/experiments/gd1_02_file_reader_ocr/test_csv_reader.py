# -*- coding: utf-8 -*-
"""GĐ1-02: Thử nghiệm đọc CSV với encoding/delimiter linh hoạt."""

from __future__ import annotations

import csv
import json
from pathlib import Path

THU_MUC_DU_AN = Path(__file__).resolve().parents[2]
TEST_FILE = THU_MUC_DU_AN / "test_data" / "gd1_02" / "test_nhan_vien.csv"
CAC_ENCODING = ["utf-8-sig", "utf-8", "cp1252", "latin-1"]
CAC_DELIMITER = [",", ";", "\t", "|"]


def phat_hien_encoding(duong_dan: Path) -> str:
    for encoding in CAC_ENCODING:
        try:
            with open(duong_dan, "r", encoding=encoding) as tep:
                tep.read(4096)
            return encoding
        except UnicodeDecodeError:
            continue
    raise UnicodeError("Không xác định được encoding phù hợp")


def phat_hien_delimiter(duong_dan: Path, encoding: str) -> str:
    with open(duong_dan, "r", encoding=encoding, newline="") as tep:
        sample = tep.read(4096)

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters="".join(CAC_DELIMITER))
        return dialect.delimiter
    except csv.Error:
        return ","


def doc_csv(duong_dan: Path):
    if duong_dan.stat().st_size == 0:
        raise ValueError("EMPTY_FILE")

    encoding = phat_hien_encoding(duong_dan)
    delimiter = phat_hien_delimiter(duong_dan, encoding)

    with open(duong_dan, "r", encoding=encoding, newline="") as tep:
        reader = csv.DictReader(tep, delimiter=delimiter)
        headers = reader.fieldnames or []
        rows = [dict(row) for row in reader if any((v or "").strip() for v in row.values())]

    return headers, rows, encoding, delimiter


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
        raise FileNotFoundError(f"Không tìm thấy {TEST_FILE}. Hãy chạy generate_test_data.py trước.")

    headers, rows, encoding, delimiter = doc_csv(TEST_FILE)
    print(f"File      : {TEST_FILE}")
    print(f"Encoding  : {encoding}")
    print(f"Delimiter : {repr(delimiter)}")
    print(f"Headers   : {headers}")
    print(f"Số record : {len(rows)}")
    print("\nFILE READER OUTPUT")
    print(json.dumps(tao_output(headers, rows, TEST_FILE), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
