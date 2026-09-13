# -*- coding: utf-8 -*-
"""GĐ1-02: Thử nghiệm đọc PDF text và phát hiện PDF scan/mixed."""

from __future__ import annotations

import json
from pathlib import Path

import pymupdf

THU_MUC_DU_AN = Path(__file__).resolve().parents[2]
TEST_DIR = THU_MUC_DU_AN / "test_data" / "gd1_02"
PDF_TEXT = TEST_DIR / "test_nhan_vien_text.pdf"
PDF_SCAN = TEST_DIR / "test_nhan_vien_scan.pdf"

# Heuristic cho GĐ1. Không coi đây là ngưỡng cố định cho production.
NGUONG_TEXT_SCAN = 50


def phan_loai_trang(page):
    """Phân loại một trang PDF thành text, scan, empty hoặc mixed."""
    text = page.get_text("text").strip()
    so_anh = len(page.get_images(full=True))
    do_dai_text = len(text)

    if do_dai_text >= NGUONG_TEXT_SCAN and so_anh == 0:
        page_mode = "text"
    elif do_dai_text < NGUONG_TEXT_SCAN and so_anh > 0:
        page_mode = "scan"
    elif do_dai_text == 0 and so_anh == 0:
        page_mode = "empty"
    else:
        page_mode = "mixed"

    return {
        "page_mode": page_mode,
        "text": text,
        "text_length": do_dai_text,
        "image_count": so_anh,
    }


def doc_pdf(duong_dan: Path):
    """Đọc PDF và xác định mode tổng thể của file."""
    tai_lieu = pymupdf.open(duong_dan)
    pages = []

    try:
        for chi_so_trang, page in enumerate(tai_lieu):
            ket_qua = phan_loai_trang(page)
            ket_qua["page_number"] = chi_so_trang + 1
            pages.append(ket_qua)
    finally:
        tai_lieu.close()

    cac_mode = {p["page_mode"] for p in pages}

    if not pages or cac_mode == {"empty"}:
        pdf_mode = "empty"
    elif cac_mode == {"text"}:
        pdf_mode = "text"
    elif cac_mode == {"scan"}:
        pdf_mode = "scan"
    else:
        pdf_mode = "mixed"

    text_trich_xuat = "\n".join(
        p["text"] for p in pages if p["text"]
    )

    return pdf_mode, pages, text_trich_xuat


def tao_output(
    duong_dan: Path,
    pdf_mode: str,
    pages,
    text_trich_xuat: str,
    ocr_da_su_dung: bool = False,
):
    """
    Tạo output chuẩn cho File Reader.

    Lưu ý:
    - pdf_mode cho biết loại PDF đã phát hiện.
    - ocr_da_su_dung chỉ True khi OCR thực sự được gọi.
    """
    return {
        "trang_thai": "success",
        "ten_file": duong_dan.name,
        "loai_file": "pdf",
        "pdf_mode": pdf_mode,
        "ocr_da_su_dung": ocr_da_su_dung,
        "du_lieu": {
            "text": text_trich_xuat,
            "so_trang": len(pages),
            "pages": [
                {
                    "page_number": p["page_number"],
                    "page_mode": p["page_mode"],
                    "text_length": p["text_length"],
                    "image_count": p["image_count"],
                }
                for p in pages
            ],
        },
        "loi": None,
    }


def kiem_tra_file(duong_dan: Path):
    """Chạy thử reader với một file PDF."""
    if not duong_dan.exists():
        raise FileNotFoundError(
            f"Không tìm thấy {duong_dan}. "
            "Hãy chạy generate_test_data.py trước."
        )

    pdf_mode, pages, text = doc_pdf(duong_dan)

    # File này mới chỉ phát hiện PDF mode, chưa chạy OCR.
    output = tao_output(
        duong_dan=duong_dan,
        pdf_mode=pdf_mode,
        pages=pages,
        text_trich_xuat=text,
        ocr_da_su_dung=False,
    )

    print("=" * 72)
    print(f"File     : {duong_dan.name}")
    print(f"PDF mode : {pdf_mode}")
    print(f"OCR used : {output['ocr_da_su_dung']}")

    for p in pages:
        print(
            f"Trang {p['page_number']}: "
            f"mode={p['page_mode']}, "
            f"text_length={p['text_length']}, "
            f"image_count={p['image_count']}"
        )

    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    kiem_tra_file(PDF_TEXT)
    kiem_tra_file(PDF_SCAN)


if __name__ == "__main__":
    main()
