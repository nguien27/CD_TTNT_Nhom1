# INTEGRATION RULES – Quy tắc tích hợp giữa các module

**Phiên bản:** 0.2 – CK1  
**Quyết định đã chốt:** SQLite/SQL là Storage chính thức; OCR bắt buộc cho PDF scan.  
**Mục đích:** Đảm bảo các thành viên phát triển module độc lập nhưng ghép được trong CK2.

---

## 1. Nguyên tắc bắt buộc

1. Mọi module dùng Data Schema trong `data_schema.md`.
2. Không tự đổi tên field chuẩn nếu chưa được leader duyệt.
3. Module phải có input/output rõ ràng.
4. Lỗi phải có cấu trúc hoặc exception có ý nghĩa; không dùng `print` làm cơ chế giao tiếp chính giữa module.
5. Không hard-code đường dẫn máy cá nhân.
6. Không hard-code dữ liệu nhân viên vào business logic ngoài mock/test.
7. Mọi module phải có test nhỏ trước khi tích hợp.
8. Storage chính thức là SQLite; không thay bằng CSV/DataFrame trong phiên bản tích hợp cuối.
9. PDF scan phải đi qua OCR trước Extraction.
10. CK2 tích hợp sớm, không chờ mọi module hoàn hảo mới ghép.

---

## 2. Kiểu dữ liệu chung

### EmployeeRecord

```python
{
    "ma_nhan_vien": str,
    "ho_ten": str,
    "don_vi": str,
    "chuc_vu": str | None,
    "email": str | None,
    "so_dien_thoai": str | None
}
```

### EmployeeList

```python
list[EmployeeRecord]
```

Nếu dùng `dataclass`, Pydantic model hoặc class riêng, khi qua ranh giới API/module phải convert được về JSON-compatible dict.

---

## 3. Contract CK1-01 → tất cả module

CK1-01 cung cấp:

- `requirements.md`;
- `data_schema.md`;
- `architecture.md`;
- `integration_rules.md`;
- `mock_data.xlsx`.

CK1-02 đến CK1-05 phải dùng bộ tài liệu này làm chuẩn.

---

## 4. Contract File Reader

### Hàm logic đề xuất

```python
def doc_file(duong_dan_hoac_file) -> dict:
    ...
```

### Success response chung

```json
{
  "trang_thai": "success",
  "loai_file": "xlsx",
  "ten_file": "employees.xlsx",
  "du_lieu": [],
  "metadata": {},
  "loi": null,
  "canh_bao": []
}
```

`du_lieu` có thể là:

- list of dict cho dữ liệu bảng;
- text/tables cho DOCX/PDF;
- nhưng phải được mô tả rõ.

### Error response

```json
{
  "trang_thai": "error",
  "loai_file": "pdf",
  "ten_file": "employees.pdf",
  "du_lieu": null,
  "metadata": {},
  "loi": "Không đọc được file",
  "canh_bao": []
}
```

File Reader không tự ghi SQLite và không tự Search.

---

## 5. Contract PDF Reader + OCR

### Quy tắc xử lý

```text
PDF
 ↓
Thử lấy text trực tiếp
 ↓
Text đủ dùng?
  ├─ Có → trả text
  └─ Không → OCR → trả text OCR
```

### Success response PDF text

```json
{
  "trang_thai": "success",
  "loai_file": "pdf",
  "ten_file": "employees.pdf",
  "du_lieu": {
    "text": "...",
    "tables": []
  },
  "metadata": {
    "pdf_mode": "text",
    "ocr_da_su_dung": false,
    "ocr_engine": null,
    "ocr_confidence": null
  },
  "loi": null,
  "canh_bao": []
}
```

### Success response PDF scan

```json
{
  "trang_thai": "success",
  "loai_file": "pdf",
  "ten_file": "employees_scan.pdf",
  "du_lieu": {
    "text": "Mã NV: NV001\nHọ tên: Nguyễn Văn A\n...",
    "tables": []
  },
  "metadata": {
    "pdf_mode": "scan",
    "ocr_da_su_dung": true,
    "ocr_engine": "tesseract",
    "ocr_confidence": null
  },
  "loi": null,
  "canh_bao": []
}
```

Không bắt buộc engine phải là Tesseract; nếu thay engine thì giữ contract này.

### OCR error

```json
{
  "trang_thai": "error",
  "loai_file": "pdf",
  "ten_file": "scan_bad.pdf",
  "du_lieu": null,
  "metadata": {
    "pdf_mode": "scan",
    "ocr_da_su_dung": true
  },
  "loi": "OCR không trích xuất được nội dung sử dụng được",
  "canh_bao": []
}
```

---

## 6. Contract Extraction / Mapping / Normalization

### Input

Output từ File Reader/OCR.

### Hàm logic đề xuất

```python
def chuan_hoa_du_lieu(ket_qua_doc_file: dict) -> dict:
    ...
```

### Output

```json
{
  "trang_thai": "success",
  "nguon": {
    "ten_file": "employees_scan.pdf",
    "loai_file": "pdf",
    "ocr_da_su_dung": true
  },
  "tong_so_ban_ghi": 50,
  "so_hop_le": 48,
  "so_loi": 2,
  "nhan_vien": [],
  "loi_ban_ghi": [],
  "canh_bao": []
}
```

`nhan_vien` bắt buộc theo EmployeeRecord.

`loi_ban_ghi` tối thiểu:

```json
{
  "dong": 12,
  "ly_do": "Thiếu ma_nhan_vien",
  "du_lieu_goc": {}
}
```

---

## 7. Contract SQLite / SQL Storage

### 7.1. Database

Database baseline:

```text
data/employee.db
```

Schema SQL nằm trong:

```text
src/storage/schema.sql
```

hoặc một module migration tương đương.

### 7.2. Bảng chính

```sql
CREATE TABLE IF NOT EXISTS nhan_vien (
    ma_nhan_vien TEXT PRIMARY KEY,
    ho_ten TEXT NOT NULL,
    don_vi TEXT NOT NULL,
    chuc_vu TEXT,
    email TEXT,
    so_dien_thoai TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 7.3. Interface logic tối thiểu

```python
def khoi_tao_database() -> None:
    ...

def them_nhan_vien(nhan_vien: dict) -> dict:
    ...

def them_nhieu_nhan_vien(ds_nhan_vien: list[dict]) -> dict:
    ...

def lay_nhan_vien_theo_ma(ma_nhan_vien: str) -> dict | None:
    ...

def lay_tat_ca_nhan_vien() -> list[dict]:
    ...

def tim_ung_vien_theo_ten(query: str, gioi_han: int = 100) -> list[dict]:
    ...
```

### 7.4. Quy tắc SQL

- dùng parameterized query, không nối chuỗi query từ input người dùng;
- transaction khi insert nhiều record;
- rollback nếu transaction thất bại;
- trả EmployeeRecord theo schema chuẩn;
- không trả row tuple tùy ý qua ranh giới module nếu chưa convert;
- `ma_nhan_vien` là khóa chính;
- duplicate phải được báo hoặc xử lý theo policy đã chốt.

Ví dụ đúng:

```python
cursor.execute(
    "SELECT * FROM nhan_vien WHERE ma_nhan_vien = ?",
    (ma_nhan_vien,)
)
```

Không làm:

```python
sql = "SELECT * FROM nhan_vien WHERE ma_nhan_vien = '" + ma_nhan_vien + "'"
```

### 7.5. Import response đề xuất

```json
{
  "trang_thai": "success",
  "tong_nhan": 50,
  "so_insert": 48,
  "so_duplicate": 1,
  "so_loi": 1,
  "loi": []
}
```

---

## 8. Contract Search Engine

### Input

```text
query: string
```

Search Engine lấy ứng viên từ SQLite/Storage.

### Hàm logic đề xuất

```python
def tim_nhan_vien(query: str, gioi_han: int = 20) -> dict:
    ...
```

### Output

```json
{
  "query": "Nguyễn Văn",
  "tong_ket_qua": 2,
  "ket_qua": [
    {
      "ma_nhan_vien": "NV001",
      "ho_ten": "Nguyễn Văn A",
      "don_vi": "Phòng CNTT",
      "chuc_vu": "Chuyên viên",
      "email": "mock001@example.com",
      "so_dien_thoai": "SDT_MOCK_001",
      "do_khop": 100.0,
      "kieu_khop": "partial"
    }
  ]
}
```

### Quy tắc

- query phải trim;
- query rỗng không crash;
- kết quả có thể rỗng;
- exact/partial dùng trước khi fuzzy nếu phù hợp;
- có dấu/không dấu phải được xử lý;
- kết quả xếp theo ranking;
- `do_khop` ưu tiên thang 0–100;
- Search không render UI.

---

## 9. Contract Backend

Baseline API:

### `GET /health`

```json
{
  "status": "ok",
  "database": "ok",
  "ocr": "ok"
}
```

### `POST /upload`

Luồng:

```text
Backend
→ Reader
→ OCR nếu cần
→ Extraction
→ Mapping
→ Normalization
→ SQLite
```

Response đề xuất:

```json
{
  "trang_thai": "success",
  "ten_file": "employees_scan.pdf",
  "loai_file": "pdf",
  "ocr_da_su_dung": true,
  "tong_so_ban_ghi": 50,
  "so_hop_le": 48,
  "so_loi": 2,
  "canh_bao": []
}
```

### `GET /employees/{ma_nhan_vien}`

Trả một EmployeeRecord hoặc not-found response.

### `GET /search?q=...`

Trả Search Result schema.

---

## 10. Contract UI

UI chỉ gọi Backend trong bản tích hợp.

### Upload

Hiển thị:

- tên file;
- loại file;
- trạng thái;
- OCR có được sử dụng hay không;
- tổng record;
- số hợp lệ;
- số lỗi;
- cảnh báo.

### Search

Hiển thị tối thiểu:

```text
Mã NV
Họ tên
Đơn vị
Chức vụ
Độ khớp
```

Không giả định chỉ có một kết quả.

---

## 11. Quy tắc lỗi chung

Error object:

```json
{
  "trang_thai": "error",
  "ma_loi": "OCR_FAILED",
  "thong_bao": "Không thể OCR PDF scan",
  "chi_tiet": null
}
```

Các mã lỗi baseline:

```text
FILE_NOT_FOUND
FILE_EMPTY
FILE_UNSUPPORTED
FILE_READ_ERROR
PDF_NO_TEXT
OCR_REQUIRED
OCR_FAILED
OCR_NO_USABLE_TEXT
SCHEMA_MISSING_REQUIRED_FIELD
DUPLICATE_EMPLOYEE_ID
INVALID_QUERY
EMPLOYEE_NOT_FOUND
DATABASE_ERROR
DATABASE_TRANSACTION_ERROR
INTERNAL_ERROR
```

---

## 12. Quy tắc Git/GitHub

### Branch đề xuất

```text
main
feature/CK1-02-file-reader-ocr
feature/CK1-03-search
feature/CK1-04-sql-backend
feature/CK1-05-ui-server
```

### Commit

Commit nên gắn task Jira, ví dụ:

```text
CK1-02: thêm OCR cho PDF scan
CK1-04: tạo schema SQLite và import mock data
```

### Pull Request

PR phải có:

- task liên quan;
- thay đổi chính;
- cách chạy;
- test đã thực hiện;
- vấn đề còn lại.

Leader review trước khi merge vào nhánh tích hợp/main theo workflow nhóm.

---

## 13. Thứ tự tích hợp CK2

Ưu tiên:

```text
1. SQLite schema + Storage interface
2. Reader + OCR
3. Extraction + Mapping + Normalization
4. Import normalized records vào SQLite
5. Search Engine đọc từ SQLite
6. Backend gọi Upload/Search
7. UI gọi Backend
8. End-to-end test
```

Không chờ đến cuối CK2 mới ghép.

---

## 14. Quy trình thay đổi interface

Nếu một thành viên muốn đổi output/input:

1. ghi rõ thay đổi đề xuất;
2. nêu module bị ảnh hưởng;
3. báo leader;
4. leader duyệt;
5. cập nhật tài liệu contract;
6. thông báo thành viên liên quan;
7. mới merge code thay đổi.

Không tự đổi contract trong branch cá nhân.
