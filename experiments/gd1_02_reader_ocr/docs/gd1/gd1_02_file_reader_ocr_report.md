# GĐ1-02 – Khảo sát File Reader và OCR cho dữ liệu đa định dạng

> **Trạng thái:** Hoàn tất Giai đoạn 1  
> **Phạm vi:** XLSX, CSV, DOCX, PDF text, PDF scan/OCR  
> **Ghi chú:** Code trong `experiments/` chỉ dùng cho khảo sát và thử nghiệm. Code sản phẩm sẽ được xây dựng lại trong `src/` ở Giai đoạn 2.

---

## 1. Mục tiêu

GĐ1-02 thực hiện khảo sát phương án đọc dữ liệu từ nhiều định dạng file và xử lý PDF scan.

File Reader chỉ chịu trách nhiệm:

- Nhận file đầu vào.
- Xác định loại file.
- Đọc và bảo toàn dữ liệu có trong file.
- Phân biệt PDF text và PDF scan.
- Chuyển PDF scan thành ảnh để phục vụ OCR.
- Trả dữ liệu theo output contract chung cho module tiếp theo.

File Reader không thực hiện:

- Search.
- AI Schema Mapping.
- Rule Engine.
- Quyết định trạng thái trả lương.

### Schema dữ liệu nhân viên thử nghiệm

Bộ dữ liệu test nhân viên dùng chung gồm:

- `Mã NV`
- `Họ và tên`
- `Đơn vị`
- `Chức vụ`
- `Email`

Tương ứng với các trường chuẩn:

```text
ma_nhan_vien
ho_ten
don_vi
chuc_vu
email