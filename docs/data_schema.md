# DATA SCHEMA – Cấu trúc dữ liệu chuẩn của hệ thống nhân viên

**Phiên bản:** 0.1 – CK1  
**Mục đích:** Là hợp đồng dữ liệu chung cho File Reader, Normalization, Storage, Search, Backend và UI.

---

## 1. Nguyên tắc chung

Mọi dữ liệu nhân viên sau khi đi qua bước trích xuất/chuẩn hóa phải được chuyển về cùng một schema. Các module phía sau không được tự đặt tên trường khác nếu chưa cập nhật tài liệu này.

Tên field trong code sử dụng `snake_case`, tiếng Việt không dấu.

Ví dụ:

```text
ma_nhan_vien
ho_ten
don_vi
chuc_vu
email
so_dien_thoai
```

---

## 2. Schema chuẩn v0.1

| Field chuẩn | Kiểu | Bắt buộc | Cho phép rỗng | Ý nghĩa |
|---|---|---:|---:|---|
| `ma_nhan_vien` | string | Có | Không | Mã định danh nhân viên trong doanh nghiệp |
| `ho_ten` | string | Có | Không | Họ và tên đầy đủ |
| `don_vi` | string | Có | Không | Đơn vị/phòng/ban công tác |
| `chuc_vu` | string | Không | Có | Chức vụ/vị trí công việc |
| `email` | string | Không | Có | Email nhân viên |
| `so_dien_thoai` | string | Không | Có | Số điện thoại hoặc chuỗi định danh liên hệ |

Trong dữ liệu thực tế, nếu giảng viên cung cấp thêm trường quan trọng, schema có thể mở rộng nhưng phải giữ tương thích với các trường cốt lõi.

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

Ví dụ trường tùy chọn bị thiếu:

```json
{
  "ma_nhan_vien": "NV002",
  "ho_ten": "Nguyễn Văn B",
  "don_vi": "Phòng Nhân sự",
  "chuc_vu": "Nhân viên",
  "email": null,
  "so_dien_thoai": null
}
```

---

## 4. Danh sách record chuẩn

Các module nên trao đổi danh sách nhân viên dưới dạng `list[dict]` hoặc cấu trúc tương đương có thể serialize thành JSON.

```json
[
  {
    "ma_nhan_vien": "NV001",
    "ho_ten": "Nguyễn Văn A",
    "don_vi": "Phòng CNTT",
    "chuc_vu": "Chuyên viên",
    "email": "mock001@example.com",
    "so_dien_thoai": "SDT_MOCK_001"
  },
  {
    "ma_nhan_vien": "NV002",
    "ho_ten": "Nguyễn Văn B",
    "don_vi": "Phòng Nhân sự",
    "chuc_vu": "Nhân viên",
    "email": null,
    "so_dien_thoai": null
  }
]
```

---

## 5. Bảng ánh xạ tên cột – Alias Mapping

### 5.1. Mã nhân viên

Các alias ban đầu:

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
ID
```

Ánh xạ về:

```text
ma_nhan_vien
```

### 5.2. Họ tên

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

Ánh xạ về:

```text
ho_ten
```

### 5.3. Đơn vị

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

Ánh xạ về:

```text
don_vi
```

### 5.4. Chức vụ

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

Ánh xạ về:

```text
chuc_vu
```

### 5.5. Email

```text
Email
E-mail
Mail
Thư điện tử
Email công ty
Company Email
```

Ánh xạ về:

```text
email
```

### 5.6. Số điện thoại

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

Ánh xạ về:

```text
so_dien_thoai
```

---

## 6. Quy tắc chuẩn hóa tên cột

Trước khi so khớp alias, tên cột nên được chuẩn hóa theo các bước:

1. chuyển về string;
2. trim khoảng trắng đầu/cuối;
3. gộp nhiều khoảng trắng liên tiếp thành một;
4. chuyển về chữ thường khi so sánh;
5. có thể tạo phiên bản không dấu để tăng khả năng ánh xạ;
6. bỏ một số ký tự phân cách không cần thiết như `_`, `-`, `.`, `:` khi so sánh alias;
7. giữ nguyên tên cột gốc để phục vụ log/debug.

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

- kiểu string;
- trim khoảng trắng;
- không được rỗng trong bản ghi hợp lệ;
- không tự ép thành số vì mã có thể chứa chữ và số;
- nên giữ nguyên zero ở đầu nếu có;
- kiểm tra trùng sau chuẩn hóa.

Ví dụ:

```text
" NV001 " → "NV001"
"00123"   → "00123"
```

### 7.2. `ho_ten`

- kiểu string;
- trim khoảng trắng;
- gộp nhiều khoảng trắng;
- giữ Unicode và dấu tiếng Việt;
- không được rỗng;
- không nên tự chuyển toàn bộ thành Title Case trong dữ liệu gốc nếu chưa kiểm chứng vì có thể làm sai tên đặc biệt;
- Search Engine có thể tạo phiên bản chuẩn hóa riêng cho tìm kiếm.

Ví dụ:

```text
"  Nguyễn   Văn A  " → "Nguyễn Văn A"
```

### 7.3. `don_vi`

- kiểu string;
- trim khoảng trắng;
- không được rỗng trong schema v0.1;
- không tự gộp các đơn vị gần giống nhau nếu chưa có quy tắc/đề xuất chính thức.

### 7.4. `chuc_vu`

- kiểu string hoặc null;
- trim khoảng trắng;
- cho phép thiếu.

### 7.5. `email`

- kiểu string hoặc null;
- trim khoảng trắng;
- có thể chuyển về chữ thường;
- validation email chỉ là kiểm tra định dạng cơ bản, không xác minh email có tồn tại.

### 7.6. `so_dien_thoai`

- kiểu string hoặc null;
- không ép sang integer;
- dữ liệu mock sử dụng chuỗi giả lập để tránh nhầm là số điện thoại thật.

---

## 8. Giá trị rỗng

Các dạng sau nên được quy về `null`/`None` khi thích hợp:

```text
""
"   "
"N/A"
"NA"
"null"
"None"
"Không có"
```

Không được quy về null nếu giá trị đó thực sự là dữ liệu hợp lệ của tổ chức.

---

## 9. Bản ghi hợp lệ và bản ghi lỗi

### 9.1. Bản ghi hợp lệ tối thiểu

Một bản ghi được xem là hợp lệ theo schema v0.1 nếu có:

```text
ma_nhan_vien
ho_ten
don_vi
```

`chuc_vu`, `email`, `so_dien_thoai` có thể thiếu.

### 9.2. Bản ghi lỗi

Các trường hợp cần cảnh báo hoặc loại khỏi import tùy chính sách CK2:

- thiếu `ma_nhan_vien`;
- thiếu `ho_ten`;
- thiếu `don_vi`;
- mã nhân viên bị trùng;
- một dòng hoàn toàn rỗng;
- dữ liệu không thể parse.

Không tự xóa dữ liệu lỗi mà không có log/summary.

---

## 10. Quy tắc xử lý mã trùng

Tại CK1 chưa khóa chính sách cuối cùng. CK2 phải chọn một trong các hướng:

1. từ chối bản ghi trùng;
2. cập nhật bản ghi cũ;
3. giữ bản ghi đầu tiên và log bản ghi sau;
4. hỏi người dùng khi upload nếu UI hỗ trợ.

Bất kể chọn hướng nào, hành vi phải ổn định và có log.

---

## 11. Schema dữ liệu trung gian từ File Reader

File Reader chưa bắt buộc phải trả ngay schema nhân viên chuẩn, vì Word/PDF có thể là text tự do. Tuy nhiên output chung nên có metadata:

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

Nếu lỗi:

```json
{
  "trang_thai": "error",
  "loai_file": "pdf",
  "ten_file": "employees.pdf",
  "du_lieu": null,
  "loi": "Không trích xuất được text",
  "canh_bao": ["Có thể là PDF scan"]
}
```

---

## 12. Schema kết quả chuẩn hóa

Normalization phải trả dữ liệu gần dạng sau:

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

`nhan_vien` chứa record theo schema chuẩn.

---

## 13. Schema kết quả Search

Search Engine nên trả danh sách có đủ dữ liệu cần hiển thị và metadata tìm kiếm:

```json
{
  "query": "Nguyễn Văn",
  "tong_ket_qua": 3,
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

`do_khop` và `kieu_khop` có thể null nếu phương pháp hiện tại chưa sử dụng scoring, nhưng interface nên dự trù để UI không phải thay đổi lớn sau này.

---

## 14. Kiểu khớp đề xuất

Giá trị `kieu_khop` có thể dùng:

```text
exact
partial
accent_insensitive
fuzzy
semantic
```

`semantic` chỉ dùng nếu sau này nhóm thực sự tích hợp tìm kiếm ngữ nghĩa.

---

## 15. Quy tắc version schema

Nếu schema thay đổi:

- cập nhật số phiên bản;
- ghi changelog;
- thông báo tất cả thành viên;
- cập nhật mock data;
- cập nhật API/interface nếu bị ảnh hưởng.

Ví dụ:

```text
v0.1 → thêm schema ban đầu
v0.2 → thêm truong dia_diem_lam_viec
```

---

## 16. Các quyết định chưa khóa

- Có bắt buộc `chuc_vu` hay không khi có dữ liệu thật.
- Có thêm phòng ban cấp cha/con hay không.
- Có lưu raw source để truy vết không.
- Có thêm `nguon_file`, `dong_nguon`, `thoi_gian_import` vào database không.
- Cách xử lý duplicate chính thức.

Các nội dung này phải được quyết định sau khi có dữ liệu thực tế hoặc sau review CK1.
