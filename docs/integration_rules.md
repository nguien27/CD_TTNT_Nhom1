# Integration Rules

## 1. Naming
Dùng snake_case:
- `ma_nhan_vien`
- `ho_ten`
- `ma_don_vi`
- `ten_don_vi`
- `loai_don_vi`
- `thong_tin_mo_rong`

## 2. File Reader Output
```json
{
  "trang_thai": "success",
  "ten_file": "input.pdf",
  "loai_file": "pdf",
  "pdf_mode": "scan",
  "ocr_da_su_dung": true,
  "du_lieu": {},
  "loi": null
}
```

## 3. AI Mapping Output
```json
{"cot_goc":"Employee Name","truong_du_doan":"HO_TEN","do_tin_cay":0.94}
```

Confidence thấp → alias/rule fallback hoặc yêu cầu xác nhận.

## 4. Search Output
```json
{
  "query": "Nguyen Van A",
  "ket_qua": [
    {
      "loai_doi_tuong":"ca_nhan",
      "id":1,
      "ma_nhan_vien":"NV001",
      "ho_ten":"Nguyễn Văn A",
      "ma_don_vi":"DV01",
      "ten_don_vi":"Trung tâm X",
      "do_khop":98.5
    }
  ]
}
```

## 5. Rule Engine Input
```json
{"loai_doi_tuong":"ca_nhan","id":1,"ma_don_vi":"DV01","loai_don_vi":"LOAI_B"}
```

## 6. Rule Engine Output
```json
{"ket_qua":"NO","ma_quy_tac":"R002","can_cu":"Mock Business Rule 02","ghi_chu":"..."}
```

Không tìm được rule:
```json
{"ket_qua":"CHUA_XAC_DINH","ma_quy_tac":null,"can_cu":null,"ghi_chu":"Không tìm thấy quy tắc đang hiệu lực phù hợp"}
```

## 7. Rule Resolution
1. Rule đơn vị cụ thể
2. Rule loại đơn vị
3. CHUA_XAC_DINH

Nếu cùng mức: ưu tiên `muc_uu_tien` lớn hơn, sau đó rule có `ngay_hieu_luc` mới hơn.

## 8. Error Format
```json
{"trang_thai":"error","ma_loi":"ENTITY_NOT_FOUND","thong_bao":"Không tìm thấy đối tượng phù hợp"}
```

Mã lỗi chung:
- `UNSUPPORTED_FILE_TYPE`
- `EMPTY_FILE`
- `FILE_READ_ERROR`
- `OCR_ERROR`
- `SCHEMA_MAPPING_ERROR`
- `LOW_MAPPING_CONFIDENCE`
- `DATABASE_ERROR`
- `SEARCH_ERROR`
- `ENTITY_NOT_FOUND`
- `RULE_NOT_FOUND`
- `INVALID_QUERY`
- `INTERNAL_SERVER_ERROR`

## 9. Thay đổi business rule
Backend/UI được phép cập nhật rule trong SQLite.

Không sửa code Python chỉ để thay đổi một đơn vị từ YES sang NO hoặc ngược lại.
