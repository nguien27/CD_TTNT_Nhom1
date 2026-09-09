# INTEGRATION RULES — QUY TẮC TÍCH HỢP GIỮA CÁC MODULE

**Phiên bản:** 0.2  
**Ngày cập nhật:** 09/09/2026

## 1. Mục tiêu

Đảm bảo CK1-02, CK1-03, CK1-04 và CK1-05 có thể phát triển độc lập nhưng ghép được ở CK2.

Quy tắc cốt lõi:

> `ho_ten` là field bắt buộc. Mọi field khác phải được bảo toàn dưới dạng dữ liệu mở rộng, không hard-code 6 field cũ.

## 2. Contract 1 — File Reader Output

File Reader không được tự loại cột chưa biết.

Ví dụ structured file:

```python
{
    "trang_thai": "success",
    "ten_file": "employees.xlsx",
    "loai_file": "xlsx",
    "pdf_mode": None,
    "ocr_da_su_dung": False,
    "du_lieu": [
        {
            "Họ tên": "Nguyễn Văn A",
            "Đơn vị": "CNTT",
            "Dự án": "ERP",
            "Kỹ năng": "Python"
        }
    ],
    "loi": None
}
```

Ví dụ PDF scan:

```python
{
    "trang_thai": "success",
    "ten_file": "employees_scan.pdf",
    "loai_file": "pdf",
    "pdf_mode": "scan",
    "ocr_da_su_dung": True,
    "du_lieu": "...text OCR hoặc cấu trúc trích xuất được...",
    "loi": None
}
```

## 3. Contract 2 — Normalized Record

Sau khi phát hiện field họ tên:

```python
{
    "ho_ten": "Nguyễn Văn A",
    "ho_ten_chuan": "nguyen van a",
    "thong_tin_mo_rong": {
        "Đơn vị": "CNTT",
        "Dự án": "ERP",
        "Kỹ năng": "Python"
    },
    "nguon_file": "employees.xlsx",
    "nguon_sheet": "Sheet1"
}
```

### Rule

- `ho_ten` không được xuất hiện lặp lại trong `thong_tin_mo_rong`.
- Field khác phải được giữ nếu có giá trị.
- Có thể trim tên field đầu/cuối; không tự đổi nghĩa field.

## 4. Contract 3 — Missing Name Field

Nếu không tìm được field họ tên:

```python
{
    "trang_thai": "error",
    "ma_loi": "MISSING_NAME_FIELD",
    "thong_bao": "Không phát hiện trường họ tên trong dữ liệu đầu vào.",
    "chi_tiet": {
        "ten_file": "employees.xlsx",
        "cac_truong_da_doc": ["Mã NV", "Đơn vị", "Chức vụ"]
    }
}
```

Không được tạo record giả có `ho_ten=None` rồi cho vào search index.

## 5. Contract 4 — SQLite Storage

Backend/storage nhận normalized record và lưu:

```sql
INSERT INTO nhan_vien (
    ho_ten,
    ho_ten_chuan,
    thong_tin_mo_rong,
    nguon_file,
    nguon_sheet
) VALUES (?, ?, ?, ?, ?);
```

`thong_tin_mo_rong` được JSON serialize trước khi lưu.

## 6. Contract 5 — Search Function

Interface logic đề xuất:

```python
def tim_nhan_vien(query: str, danh_sach_record: list[dict]) -> list[dict]:
    ...
```

Hoặc khi tích hợp DB:

```python
def tim_nhan_vien(query: str) -> list[dict]:
    ...
```

Search result:

```python
[
    {
        "id": 1,
        "ho_ten": "Nguyễn Văn A",
        "do_khop": 96.5,
        "thong_tin_mo_rong": {
            "Mã NV": "NV001",
            "Đơn vị": "CNTT",
            "Dự án": "ERP",
            "Kỹ năng": "Python"
        }
    }
]
```

Search Engine không được chỉ trả `ma_nhan_vien/ho_ten/don_vi/chuc_vu`.

## 7. Contract 6 — Backend API

### GET /health

```json
{"status": "ok"}
```

### GET /search?q=Nguyen%20Van

```json
{
  "trang_thai": "success",
  "query": "Nguyen Van",
  "so_ket_qua": 2,
  "ket_qua": [
    {
      "id": 1,
      "ho_ten": "Nguyễn Văn A",
      "do_khop": 96.5,
      "thong_tin_mo_rong": {
        "Đơn vị": "CNTT",
        "Dự án": "ERP"
      }
    }
  ]
}
```

### POST /upload

Response gợi ý:

```json
{
  "trang_thai": "success",
  "ten_file": "employees.xlsx",
  "tong_record_doc": 50,
  "record_hop_le": 48,
  "record_loi": 2,
  "truong_ho_ten_da_nhan_dien": "Tên nhân viên"
}
```

## 8. Contract 7 — UI

UI nhận `ket_qua` và render động:

- `ho_ten` là tiêu đề chính;
- `do_khop` nếu có;
- duyệt toàn bộ key/value trong `thong_tin_mo_rong` để hiển thị.

Không viết UI kiểu cố định chỉ có:

```text
Mã NV | Họ tên | Đơn vị | Chức vụ
```

## 9. Error codes cơ bản

| Code | Ý nghĩa |
|---|---|
| `UNSUPPORTED_FILE_TYPE` | Định dạng chưa hỗ trợ |
| `EMPTY_FILE` | File rỗng |
| `FILE_READ_ERROR` | Không đọc được file |
| `OCR_ERROR` | OCR thất bại |
| `MISSING_NAME_FIELD` | Không nhận diện được trường họ tên |
| `EMPTY_NAME_VALUE` | Record có trường họ tên nhưng giá trị rỗng |
| `DATABASE_ERROR` | Lỗi SQLite |
| `SEARCH_ERROR` | Lỗi Search Engine |

## 10. Git/Branch

Gợi ý branch:

```text
feature/ck1-02-file-reader-ocr
feature/ck1-03-search-engine
feature/ck1-04-sqlite-backend
feature/ck1-05-ui-server
```

Commit nên có Jira ID hoặc CK task ID.

Ví dụ:

```text
CK1-02: add PDF scan OCR reader
CK1-04: store dynamic extra fields as JSON
```

## 11. Quy tắc thay đổi contract

Nếu thành viên muốn thay đổi:

- tên field bắt buộc;
- cấu trúc normalized record;
- response API;
- cách lưu JSON;

thì phải:

1. báo leader;
2. cập nhật `data_schema.md` / `integration_rules.md`;
3. thông báo các task bị ảnh hưởng;
4. chỉ merge khi contract mới được chấp nhận.
