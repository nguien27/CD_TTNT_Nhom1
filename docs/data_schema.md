# Data Schema

## 1. Cá nhân
```json
{
  "id": 1,
  "ma_nhan_vien": "NV001",
  "ho_ten": "Nguyễn Văn A",
  "ho_ten_chuan": "nguyen van a",
  "ma_don_vi": "DV01",
  "ten_don_vi": "Trung tâm X",
  "thong_tin_mo_rong": {}
}
```

## 2. Đơn vị
```json
{
  "id": 10,
  "ma_don_vi": "DV01",
  "ten_don_vi": "Trung tâm X",
  "ten_don_vi_chuan": "trung tam x",
  "loai_don_vi": "LOAI_B",
  "thong_tin_mo_rong": {}
}
```

## 3. Quy tắc chi trả
```json
{
  "id": 1,
  "ma_quy_tac": "R001",
  "pham_vi": "DON_VI",
  "ma_don_vi": "DV01",
  "loai_don_vi": null,
  "ket_qua": "YES",
  "can_cu": "Mock Business Rule 01",
  "muc_uu_tien": 100,
  "ngay_hieu_luc": "2026-09-01",
  "ngay_het_hieu_luc": null,
  "dang_ap_dung": true,
  "ghi_chu": "Quy tắc demo"
}
```

`pham_vi`:
- `DON_VI`
- `LOAI_DON_VI`

## 4. Thứ tự ưu tiên Rule Engine
1. Quy tắc dành riêng cho đơn vị
2. Quy tắc theo loại đơn vị
3. Không có quy tắc phù hợp → `CHUA_XAC_DINH`

## 5. Schema Mapping AI
Input:
```json
{"cot_goc":"Employee Name"}
```

Output:
```json
{"cot_goc":"Employee Name","truong_du_doan":"HO_TEN","do_tin_cay":0.94}
```

## 6. Search Result
Cá nhân:
```json
{
  "loai_doi_tuong": "ca_nhan",
  "id": 1,
  "ma_nhan_vien": "NV001",
  "ho_ten": "Nguyễn Văn A",
  "ma_don_vi": "DV01",
  "ten_don_vi": "Trung tâm X",
  "do_khop": 98.5
}
```

Đơn vị:
```json
{
  "loai_doi_tuong": "don_vi",
  "id": 10,
  "ma_don_vi": "DV01",
  "ten_don_vi": "Trung tâm X",
  "loai_don_vi": "LOAI_B",
  "do_khop": 97.2
}
```

## 7. Rule Result
```json
{"ket_qua":"YES","ma_quy_tac":"R001","can_cu":"Mock Business Rule 01","ghi_chu":"..."}
```
