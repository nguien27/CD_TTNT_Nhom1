# DATA SCHEMA – Cấu trúc dữ liệu chuẩn của hệ thống nhân viên

**Phiên bản:** 0.2 – CK1  
**Mục đích:** Là hợp đồng dữ liệu chung cho File Reader, OCR, Extraction, Normalization, SQLite/SQL, Search, Backend và UI.

---

## 1. Nguyên tắc chung

Mọi dữ liệu nhân viên sau khi đi qua bước trích xuất/chuẩn hóa phải được chuyển về cùng một schema.

Tên field trong code sử dụng `snake_case`, tiếng Việt không dấu:

```text
ma_nhan_vien
ho_ten
don_vi
chuc_vu
email
so_dien_thoai
```

Không module nào được tự đổi tên field chuẩn nếu chưa được leader duyệt và cập nhật tài liệu này.

---

## 2. Schema chuẩn v0.2

| Field chuẩn | Kiểu logic | Bắt buộc | Cho phép rỗng | Ý nghĩa |
|---|---|---:|---:|---|
| `ma_nhan_vien` | string | Có | Không | Mã định danh nhân viên |
| `ho_ten` | string | Có | Không | Họ và tên đầy đủ |
| `don_vi` | string | Có | Không | Đơn vị/phòng/ban công tác |
| `chuc_vu` | string | Không | Có | Chức vụ/vị trí công việc |
| `email` | string | Không | Có | Email nhân viên |
| `so_dien_thoai` | string | Không | Có | Số điện thoại/liên hệ |

Ba trường cốt lõi bắt buộc để một record được chấp nhận trong baseline:

```text
ma_nhan_vien
ho_ten
don_vi
```

---

## 3. Ví dụ record chuẩn

```json
{
  "ma_nhan_vien": "NV001",
  "ho_ten": "Nguyễn Văn A",
  "don_vi": "Phòng Công nghệ thông tin",
  "chuc_vu": "Chuyên viên",
  "email": "mock001@example.com",
  "so_dien_thoai": "SDT_MOCK_001"
}
```

Record có trường tùy chọn bị thiếu:

```json
{
  "ma_nhan_vien": "NV002",
  "ho_ten": "Nguyễn Văn B",
  "don_vi": "Phòng Nhân sự",
  "chuc_vu": null,
  "email": null,
  "so_dien_thoai": null
}
```

---

## 4. Danh sách record chuẩn

Các module trao đổi danh sách nhân viên dưới dạng `list[dict]` hoặc cấu trúc tương đương có thể serialize thành JSON.

```json
[
  {
    "ma_nhan_vien": "NV001",
    "ho_ten": "Nguyễn Văn A",
    "don_vi": "Phòng CNTT",
    "chuc_vu": "Chuyên viên",
    "email": "mock001@example.com",
    "so_dien_thoai": "SDT_MOCK_001"
  }
]
```

---

## 5. Bảng ánh xạ tên cột – Alias Mapping

### 5.1. Mã nhân viên → `ma_nhan_vien`

```text
Mã NV
Ma NV
Mã nhân viên
Ma nhan vien
Mã cán bộ
Ma can bo
Mã CB
Employee ID
EmployeeID
Staff ID
ID nhân viên
```

### 5.2. Họ tên → `ho_ten`

```text
Họ tên
Ho ten
Họ và tên
Tên nhân viên
Tên CBCNV
Full Name
Employee Name
Name
```

### 5.3. Đơn vị → `don_vi`

```text
Đơn vị
Don vi
Đơn vị công tác
Phòng ban
Phòng
Ban
Bộ phận
Department
Unit
Division
```

### 5.4. Chức vụ → `chuc_vu`

```text
Chức vụ
Chuc vu
Vị trí
Vị trí việc làm
Chức danh
Position
Job Title
Role
```

### 5.5. Email → `email`

```text
Email
E-mail
Mail
Thư điện tử
Email công ty
Company Email
```

### 5.6. Số điện thoại → `so_dien_thoai`

```text
Số điện thoại
So dien thoai
Điện thoại
SĐT
SDT
Phone
Phone Number
Mobile
```

---

## 6. Quy tắc chuẩn hóa tên cột

Trước khi so khớp alias:

1. chuyển về string;
2. trim khoảng trắng đầu/cuối;
3. gộp nhiều khoảng trắng liên tiếp;
4. chuyển về chữ thường để so sánh;
5. có thể tạo phiên bản không dấu;
6. bỏ ký tự phân cách không cần thiết khi so sánh như `_`, `-`, `.`, `:`;
7. giữ tên cột gốc trong metadata/log để debug.

Ví dụ:

```text
"  MÃ   NHÂN-VIÊN  "
        ↓
"mã nhân viên"
        ↓
ma_nhan_vien
```

---

## 7. Quy tắc chuẩn hóa giá trị

### 7.1. `ma_nhan_vien`

- lưu dưới dạng string;
- trim khoảng trắng;
- không được rỗng;
- không ép sang số;
- phải giữ zero đầu nếu có;
- kiểm tra duplicate.

```text
" NV001 " → "NV001"
"00123"   → "00123"
```

### 7.2. `ho_ten`

- trim khoảng trắng;
- gộp nhiều khoảng trắng thành một;
- giữ Unicode tiếng Việt;
- không bắt buộc đổi kiểu viết hoa/thường trong dữ liệu gốc;
- Search Engine tự tạo dạng chuẩn hóa phục vụ tìm kiếm.

### 7.3. `don_vi`

- trim/gộp khoảng trắng;
- giữ tên đơn vị ở dạng có dấu;
- có thể chuẩn hóa alias đơn vị sau nếu dữ liệu thật yêu cầu.

### 7.4. `chuc_vu`

- cho phép `null`;
- trim/gộp khoảng trắng nếu có.

### 7.5. `email`

- cho phép `null`;
- trim khoảng trắng;
- nên chuyển lowercase;
- có thể validate định dạng cơ bản;
- email sai định dạng không được làm toàn pipeline crash.

### 7.6. `so_dien_thoai`

- lưu dạng string;
- cho phép `null`;
- không ép số để tránh mất zero đầu;
- rule chuẩn hóa chi tiết chờ dữ liệu thật.

---

## 8. Giá trị rỗng

Các giá trị sau có thể được chuẩn hóa thành `null` khi phù hợp:

```text
""
"N/A"
"NA"
"null"
"None"
"Không có"
```

Không được tự biến dữ liệu hợp lệ thành null chỉ vì chuỗi khác lạ; cần có rule rõ ràng.

---

## 9. Record hợp lệ và record lỗi

### Record hợp lệ

Có đầy đủ tối thiểu:

```text
ma_nhan_vien
ho_ten
don_vi
```

### Record lỗi

Ví dụ:

- thiếu `ma_nhan_vien`;
- thiếu `ho_ten`;
- thiếu `don_vi`;
- trùng `ma_nhan_vien` theo policy import;
- OCR quá lỗi khiến không xác định được trường bắt buộc.

Record lỗi phải được ghi nhận để báo cáo, không âm thầm bỏ qua.

---

## 10. Schema SQL chính thức – SQLite

Database chính thức của bản demo là **SQLite**, truy vấn bằng SQL.

### 10.1. Bảng `nhan_vien`

DDL baseline:

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

Lý do dùng `TEXT` cho mã và số điện thoại:

- mã có thể chứa chữ;
- mã/số điện thoại có thể có zero đầu;
- không dùng chúng để tính toán số học.

### 10.2. Index phục vụ Search

Baseline có thể tạo index:

```sql
CREATE INDEX IF NOT EXISTS idx_nhan_vien_ho_ten
ON nhan_vien(ho_ten);

CREATE INDEX IF NOT EXISTS idx_nhan_vien_don_vi
ON nhan_vien(don_vi);
```

Fuzzy Search có thể cần xử lý thêm ở tầng Python/Search Engine thay vì chỉ SQL thuần.

### 10.3. Policy duplicate

Baseline đề xuất:

- `ma_nhan_vien` là khóa chính;
- record cùng mã không được chèn thành hai nhân viên riêng;
- CK2 chốt một trong hai policy:
  - `UPDATE/UPSERT` record cũ; hoặc
  - từ chối và trả cảnh báo duplicate.

Cho đến khi CK2 chốt, module phải phát hiện duplicate và báo rõ.

---

## 11. Metadata nguồn dữ liệu

Để phục vụ debug/test, pipeline có thể giữ metadata ngoài bảng nhân viên chính:

```json
{
  "ten_file": "employees_scan.pdf",
  "loai_file": "pdf",
  "pdf_mode": "scan",
  "ocr_da_su_dung": true,
  "ocr_engine": "tesseract",
  "canh_bao": []
}
```

Metadata này không bắt buộc phải nằm trong bảng `nhan_vien`.

---

## 12. Metadata OCR

Khi nguồn là PDF scan, output trung gian nên có tối thiểu:

- `pdf_mode`: `text` hoặc `scan`;
- `ocr_da_su_dung`: boolean;
- `ocr_engine`: tên engine nếu biết;
- `ocr_confidence`: điểm tin cậy nếu engine cung cấp;
- `ocr_text`: text sau OCR hoặc đường dẫn/field tương đương;
- `canh_bao`: các vấn đề nhận dạng.

Không bắt buộc mọi OCR engine đều có confidence score.

---

## 13. Search result schema

Kết quả Search Engine có thể mở rộng EmployeeRecord bằng:

```json
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
```

`do_khop` ưu tiên thang 0–100 để UI dễ hiển thị.

---

## 14. Quy tắc thay đổi schema

Nếu thành viên cần thêm field:

1. tạo đề xuất;
2. nêu lý do;
3. đánh giá ảnh hưởng tới SQL, Search, Backend và UI;
4. leader duyệt;
5. cập nhật `data_schema.md`;
6. cập nhật SQLite migration/schema;
7. thông báo toàn nhóm.

Không tự thay đổi schema trong branch cá nhân mà không báo.
