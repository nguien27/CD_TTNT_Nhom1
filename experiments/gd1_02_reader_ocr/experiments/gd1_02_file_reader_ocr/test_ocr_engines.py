# -*- coding: utf-8 -*-
"""GĐ1-02: Thử nghiệm OCR thật trên PDF scan bằng PaddleOCR.

Mục đích:
- Render trang PDF scan thành ảnh.
- Chạy PaddleOCR thật trên CPU.
- Tắt oneDNN/MKLDNN để tránh lỗi runtime PIR trên một số bản PaddlePaddle 3.3.x.
- Ghi kết quả vào ocr_results.json.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image

THU_MUC_DU_AN = Path(__file__).resolve().parents[2]
TEST_DIR = THU_MUC_DU_AN / "test_data" / "gd1_02"
PDF_SCAN = TEST_DIR / "test_nhan_vien_scan.pdf"
KET_QUA_JSON = Path(__file__).with_name("ocr_results.json")

DPI_OCR = 200


def pdf_trang_dau_sang_anh(pdf_path: Path) -> Image.Image:
    """Render trang đầu PDF thành ảnh RGB phục vụ OCR."""
    if not pdf_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy {pdf_path}. "
            "Hãy chạy generate_test_data.py trước."
        )

    tai_lieu = pymupdf.open(pdf_path)
    try:
        if tai_lieu.page_count == 0:
            raise ValueError("PDF không có trang.")

        trang = tai_lieu[0]
        zoom = DPI_OCR / 72
        ma_tran = pymupdf.Matrix(zoom, zoom)
        pix = trang.get_pixmap(matrix=ma_tran, alpha=False)

        return Image.frombytes(
            "RGB",
            [pix.width, pix.height],
            pix.samples,
        )
    finally:
        tai_lieu.close()


def lay_text_tu_ket_qua_predict(ket_qua) -> list[str]:
    """Trích text từ kết quả PaddleOCR theo cách tương thích nhiều phiên bản."""
    cac_text = []

    def duyet(obj):
        if obj is None:
            return

        if isinstance(obj, dict):
            rec_texts = obj.get("rec_texts")
            if isinstance(rec_texts, list):
                for text in rec_texts:
                    if isinstance(text, str) and text.strip():
                        cac_text.append(text.strip())

            for value in obj.values():
                duyet(value)
            return

        if isinstance(obj, (list, tuple)):
            if (
                len(obj) >= 2
                and isinstance(obj[1], (list, tuple))
                and len(obj[1]) >= 1
                and isinstance(obj[1][0], str)
            ):
                text = obj[1][0].strip()
                if text:
                    cac_text.append(text)

            for item in obj:
                duyet(item)
            return

        for thuoc_tinh in ("json", "res"):
            if hasattr(obj, thuoc_tinh):
                try:
                    duyet(getattr(obj, thuoc_tinh))
                except Exception:
                    pass

    duyet(ket_qua)

    da_gap = set()
    ket_qua_sach = []
    for text in cac_text:
        if text not in da_gap:
            da_gap.add(text)
            ket_qua_sach.append(text)

    return ket_qua_sach


def chay_paddleocr(anh: Image.Image) -> dict:
    """Chạy PaddleOCR trên CPU, tắt MKLDNN/oneDNN."""
    try:
        from paddleocr import PaddleOCR
    except ImportError as exc:
        return {
            "engine": "paddleocr",
            "status": "not_installed",
            "error": str(exc),
            "time_s": None,
            "so_doan_text": 0,
            "text": [],
            "text_ghep": "",
        }

    bat_dau = time.perf_counter()

    try:
        try:
            ocr = PaddleOCR(
                lang="vi",
                device="cpu",
                enable_mkldnn=False,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
            )
        except TypeError:
            # Fallback cho API cũ.
            ocr = PaddleOCR(
                lang="vi",
                use_angle_cls=True,
                use_gpu=False,
                enable_mkldnn=False,
            )

        anh_numpy = np.array(anh)

        if hasattr(ocr, "predict"):
            raw_result = ocr.predict(anh_numpy)
        else:
            raw_result = ocr.ocr(anh_numpy, cls=True)

        cac_text = lay_text_tu_ket_qua_predict(raw_result)
        thoi_gian = round(time.perf_counter() - bat_dau, 3)

        return {
            "engine": "paddleocr",
            "status": "success",
            "time_s": thoi_gian,
            "so_doan_text": len(cac_text),
            "text": cac_text,
            "text_ghep": "\n".join(cac_text),
            "error": None,
        }

    except Exception as exc:
        thoi_gian = round(time.perf_counter() - bat_dau, 3)
        return {
            "engine": "paddleocr",
            "status": "error",
            "time_s": thoi_gian,
            "so_doan_text": 0,
            "text": [],
            "text_ghep": "",
            "error": f"{type(exc).__name__}: {exc}",
        }


def main():
    print("=" * 72)
    print("THỬ NGHIỆM OCR GĐ1-02")
    print("=" * 72)
    print(f"PDF scan : {PDF_SCAN.name}")
    print(f"DPI      : {DPI_OCR}")
    print("Device   : CPU")
    print("MKLDNN   : OFF")

    anh = pdf_trang_dau_sang_anh(PDF_SCAN)
    print(f"Kích thước ảnh OCR: {anh.width}x{anh.height}")

    ket_qua_paddle = chay_paddleocr(anh)

    ket_qua = {
        "nguon": PDF_SCAN.name,
        "dpi": DPI_OCR,
        "device": "cpu",
        "enable_mkldnn": False,
        "paddleocr": ket_qua_paddle,
        "ket_luan": (
            "PaddleOCR đã chạy thử thành công."
            if ket_qua_paddle["status"] == "success"
            else "Chưa thể kết luận chất lượng OCR; cần xử lý lỗi/cài đặt trước."
        ),
    }

    KET_QUA_JSON.write_text(
        json.dumps(ket_qua, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print()
    print(json.dumps(ket_qua, ensure_ascii=False, indent=2))
    print()
    print(f"Đã lưu kết quả: {KET_QUA_JSON}")


if __name__ == "__main__":
    main()
