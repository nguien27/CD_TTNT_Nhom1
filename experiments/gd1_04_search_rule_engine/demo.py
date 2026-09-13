# -*- coding: utf-8 -*-
"""Demo GĐ1-04: Search Engine -> Rule Engine."""

import json

from api import PayrollLookupAPI
from db import tao_db_demo


def hien_thi(api: PayrollLookupAPI, query: str, loai=None):
    print("\n" + "=" * 72)
    print(f"TRA CỨU: {query!r}")
    print("=" * 72)
    result = api.tra_cuu(query, loai_doi_tuong=loai, limit=5, ngay_xet="2026-09-12")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    conn = tao_db_demo(reset=True)
    api = PayrollLookupAPI(conn)

    hien_thi(api, "NV001")                         # MSNV exact, không fuzzy mã khác
    hien_thi(api, "nguyen van an")                 # exact sau chuẩn hóa
    hien_thi(api, "nguyen van")                    # partial
    hien_thi(api, "nguyen van anh")                # fuzzy typo nhẹ
    hien_thi(api, "Trung tam Cong nghe thong tin") # đơn vị exact sau bỏ dấu
    hien_thi(api, "cong nghe")                     # đơn vị partial
    hien_thi(api, "NV003")                         # ngoại lệ cá nhân
    hien_thi(api, "Do Thi Phuong")                 # thiếu đơn vị -> CHUA_XAC_DINH
    hien_thi(api, "Hoi Chu thap do")               # đơn vị chưa có rule -> CHUA_XAC_DINH

    conn.close()


if __name__ == "__main__":
    main()
