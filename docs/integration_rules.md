# INTEGRATION RULES – Quy tắc tích hợp giữa các module

**Phiên bản:** 0.1 – CK1  
**Mục đích:** Đảm bảo 5 thành viên phát triển các module độc lập nhưng có thể ghép lại trong CK2.

---

## 1. Nguyên tắc bắt buộc

1. Mọi module dùng Data Schema trong `data_schema.md`.
2. Không tự đổi tên field chuẩn nếu chưa cập nhật tài liệu chung.
3. Module phải có input/output rõ ràng.
4. Lỗi phải được trả về có cấu trúc hoặc raise exception có ý nghĩa; không dùng `print` làm cơ chế giao tiếp chính giữa module.
5. Không hard-code đường dẫn máy cá nhân.
6. Không hard-code dữ liệu nhân viên vào business logic ngoài mock/test.
7. Mọi module phải chạy được độc lập bằng test nhỏ trước khi tích hợp.
8. CK2 ưu tiên tích hợp sớm; không chờ toàn bộ module hoàn hảo mới ghép.

---

## 2. Kiểu dữ liệu chung

### EmployeeRecord

Biểu diễn logic:

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

Nếu thành viên sử dụng `dataclass`, Pydantic model hoặc class riêng thì khi qua ranh giới API/module phải có khả năng convert về JSON-compatible dict.

---

## 3. Contract CK1-01 → tất cả module

CK1-01 cung cấp:

- `requirements.md`;
- `data_schema.md`;
- `architecture.md`;
- `integration_rules.md`;
- `mock_data.xlsx`.

Các task CK1-02 đến CK1-05 phải sử dụng bộ ngữ cảnh này làm chuẩn.

Nếu cần thay đổi schema, thành viên phải báo leader thay vì tự sửa local.

---

## 4. Contract File Reader

### Hàm logic đề xuất

```python
def doc_file(duong_dan_hoac_file) -> dict:
    ...
```

### Success response

```json
{
  "trang_thai": "success",
  "loai_file": "xlsx",
  "ten_file": "employees.xlsx",
  "du_lieu": [],
  "loi": null,
  "canh_bao": []
}
```

`du_lieu` có thể là:

- list of dict cho dữ liệu bảng;
- cấu trúc gồm `text` và `tables` cho Word/PDF;
- nhưng phải được mô tả rõ trong module.

### Error response

```json
{
  "trang_thai": "error",
  "loai_file": "pdf",
  "ten_file": "employees.pdf",
  "du_lieu": null,
  "loi": "Không đọc được file",
  "canh_bao": []
}
```

### Điều không được làm

File Reader không tự lưu database và không tự thực hiện Search.

---

## 5. Contract Extraction / Mapping / Normalization

### Input

Output từ File Reader.

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
    "ten_file": "employees.xlsx",
    "loai_file": "xlsx"
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

`loi_ban_ghi` nên ghi tối thiểu:

```json
{
  "dong": 12,
  "ly_do": "Thiếu ma_nhan_vien",
  "du_lieu_goc": {}
}
```

---

## 6. Contract Storage

Để tránh phụ thuộc database cụ thể, Storage nên cung cấp interface logic tối thiểu:

```python
def khoi_tao_luu_tru() -> None:
    ...

def them_nhan_vien(nhan_vien: dict) -> dict:
    ...

def them_nhieu_nhan_vien(ds_nhan_vien: list[dict]) -> dict:
    ...

def lay_nhan_vien_theo_ma(ma_nhan_vien: str) -> dict | None:
    ...

def lay_tat_ca_nhan_vien() -> list[dict]:
    ...

def tim_ung_vien_theo_ten(query: str) -> list[dict]:
    ...
```

Tên hàm thực tế có thể thay đổi nhưng chức năng phải tương đương và được thống nhất trước tích hợp.

Storage trả EmployeeRecord theo schema chuẩn.

---

## 7. Contract Search Engine

### Input

```text
query: string
```

và dữ liệu ứng viên từ Storage.

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

- query phải được trim;
- query rỗng không crash;
- kết quả có thể rỗng;
- nhiều kết quả phải được sắp xếp theo logic ranking;
- `do_khop` nằm trong thang được module định nghĩa rõ, ưu tiên 0–100 cho UI dễ hiển thị;
- Search không tự render HTML/UI.

---

## 8. Contract Backend

API cụ thể được khóa ở CK2. Baseline đề xuất:

### `GET /health`

Mục đích: kiểm tra server.

Response:

```json
{
  "status": "ok"
}
```

### `POST /upload`

Input: file.

Luồng:

```text
Backend
→ File Reader
→ Normalization
→ Storage
```

Response đề xuất:

```json
{
  "trang_thai": "success",
  "ten_file": "employees.xlsx",
  "tong_so_ban_ghi": 50,
  "so_hop_le": 48,
  "so_loi": 2,
  "canh_bao": []
}
```

### `GET /employees/{ma_nhan_vien}`

Trả một EmployeeRecord hoặc response not-found.

### `GET /search?q=...`

Trả schema Search Result ở mục 7.

---

## 9. Contract UI

UI chỉ dựa trên response của Backend trong bản tích hợp CK2/CK3.

### Upload screen

UI gửi file và hiển thị:

- tên file;
- trạng thái;
- tổng số bản ghi;
- số hợp lệ;
- số lỗi;
- cảnh báo.

### Search screen

UI gửi query và hiển thị tối thiểu:

```text
Mã NV
Họ tên
Đơn vị
Chức vụ
Độ khớp (nếu có)
```

Không giả định chỉ có một kết quả.

---

## 10. Quy tắc lỗi chung

Error object đề xuất:

```json
{
  "trang_thai": "error",
  "ma_loi": "FILE_UNSUPPORTED",
  "thong_bao": "Định dạng file chưa được hỗ trợ",
  "chi_tiet": null
}
```

Một số mã lỗi có thể dùng:

```text
FILE_NOT_FOUND
FILE_EMPTY
FILE_UNSUPPORTED
FILE_READ_ERROR
PDF_NO_TEXT
SCHEMA_MISSING_REQUIRED_FIELD
DUPLICATE_EMPLOYEE_ID
INVALID_QUERY
EMPLOYEE_NOT_FOUND
DATABASE_ERROR
INTERNAL_ERROR
```

Mục tiêu của mã lỗi là giúp UI và test xác định hành vi ổn định.

---

## 11. Quy tắc Git/GitHub

### Branch

Đề xuất:

```text
main
feature/CK1-02-file-reader
feature/CK1-03-search
feature/CK1-04-storage-backend
feature/CK1-05-ui
```

CK2 có thể dùng branch mới hoặc tiếp tục theo module.

### Commit

Commit message nên chứa task ID:

```text
CK1-02: thêm reader cho xlsx và csv
CK1-03: thêm partial search không phân biệt hoa thường
```

### Pull Request

Trước merge:

- code chạy;
- không commit file môi trường/secret;
- cập nhật README nếu cách chạy thay đổi;
- leader hoặc người review kiểm tra interface.

---

## 12. Quy tắc thư mục

Module không được tự tạo nhiều bản dữ liệu rải rác trong source.

Dữ liệu test đặt dưới:

```text
tests/sample_files/
```

Mock data chung đặt:

```text
data/mock_data.xlsx
```

Docs chung đặt:

```text
docs/
```

---

## 13. Quy tắc dependency Python

- thư viện mới phải thêm vào `requirements.txt` hoặc cơ chế quản lý dependency chung;
- tránh cài library mà không ghi lại;
- ưu tiên thư viện ổn định và có lý do sử dụng;
- không để mỗi module yêu cầu Python version khác nhau.

Python version sẽ được leader chốt sau khi khảo sát môi trường các thành viên; đề xuất ban đầu là Python 3.10 hoặc 3.11.

---

## 14. Quy tắc test trước tích hợp

Mỗi module phải có test tối thiểu cho đường chạy chính và lỗi phổ biến.

Trước CK2 integration:

```text
Reader → có output mẫu
Normalization → tạo được EmployeeList
Storage → lưu/đọc EmployeeRecord
Search → chạy trên mock data
UI → hiển thị mock result
```

Sau đó mới thay mock bằng kết nối thật từng bước.

---

## 15. Thứ tự tích hợp CK2

Không ghép tất cả trong một lần. Thứ tự đề xuất:

```text
1. Reader → Normalization
2. Normalization → Storage
3. Storage → Search
4. Search → Backend
5. Backend → UI
6. Upload end-to-end
7. Search end-to-end
```

Mỗi bước chạy được mới chuyển bước tiếp theo.

---

## 16. Nguyên tắc thay đổi interface

Nếu một thành viên muốn thay đổi input/output:

1. tạo đề xuất ngắn;
2. chỉ rõ task/module bị ảnh hưởng;
3. leader xác nhận;
4. cập nhật `integration_rules.md` và nếu cần `data_schema.md`;
5. thông báo nhóm;
6. sau đó mới merge code sử dụng interface mới.

Không tự thay interface trong branch cá nhân rồi yêu cầu các thành viên khác sửa theo.

---

## 17. Điểm chưa khóa

Các phần sau là placeholder, không phải quyết định cuối:

- framework Backend;
- database;
- framework UI;
- package structure chính xác;
- kiểu model/class dùng trong Python;
- AI/semantic search;
- OCR.

Sau review CK1, leader cập nhật phiên bản 0.2 và ghi rõ quyết định chính thức.
