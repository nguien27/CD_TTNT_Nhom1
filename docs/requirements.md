# REQUIREMENTS — HỆ THỐNG TRUY XUẤT THÔNG TIN NHÂN VIÊN

**Phiên bản:** 0.2  
**Ngày cập nhật:** 09/09/2026  
**Trạng thái:** Baseline dùng chung cho CK1–CK3

## 1. Bài toán

Xây dựng hệ thống cho phép doanh nghiệp nạp dữ liệu nhân viên từ nhiều loại file và nhiều cấu trúc khác nhau, sau đó truy xuất thông tin nhân viên theo họ tên hoặc một phần họ tên.

Ví dụ người dùng nhập `Nguyễn Văn`, hệ thống có thể trả nhiều kết quả như `Nguyễn Văn A`, `Nguyễn Văn B`, `Nguyễn Văn An` cùng toàn bộ thông tin tương ứng có trong dữ liệu nguồn.

## 2. Quyết định nghiệp vụ đã chốt

1. **`ho_ten` là trường nghiệp vụ bắt buộc duy nhất** để một bản ghi tham gia chức năng tìm kiếm theo tên.
2. **Mọi trường còn lại là trường mở rộng động**. Hệ thống không được giới hạn ở 6 trường cố định.
3. Nếu file có 3, 8, 15, 20 hoặc nhiều trường hơn, hệ thống phải cố gắng **giữ lại toàn bộ các trường còn lại** sau khi xác định được trường họ tên.
4. Nếu file không có trường có thể ánh xạ về `ho_ten`, hệ thống phải cảnh báo rõ và không nhập file đó vào kho dữ liệu phục vụ tìm kiếm theo tên.
5. Nếu file có cột `ho_ten` nhưng một số dòng không có giá trị họ tên, chỉ các dòng đó bị đánh dấu lỗi/bỏ qua; các dòng hợp lệ khác vẫn được xử lý.
6. Database chính thức của phiên bản hiện tại: **SQLite**, sử dụng **SQL**.
7. PDF scan phải được xử lý bằng **OCR** để lấy text trước khi trích xuất dữ liệu.
8. Máy leader đóng vai trò server; máy khác có thể truy cập hệ thống bằng trình duyệt trong môi trường mạng phù hợp.

## 3. Input hệ thống

Hệ thống ưu tiên hỗ trợ:

- Excel `.xlsx`
- CSV `.csv`
- Word `.docx`
- PDF có text `.pdf`
- PDF scan `.pdf` thông qua OCR

Các file **không bắt buộc có cùng số cột, cùng tên cột hoặc cùng thứ tự cột**.

Ví dụ các tên cột có thể khác nhau:

- `Họ tên`, `Tên nhân viên`, `Tên CBCNV`, `Full Name`, `Employee Name` → đều có thể là trường `ho_ten`.
- Những cột khác như `Mã NV`, `Đơn vị`, `Dự án`, `Kỹ năng`, `Ngày vào làm`, `Trình độ`, `Địa điểm`... được bảo toàn như thông tin mở rộng.

## 4. Yêu cầu chức năng

### FR-01 — Upload nhiều định dạng

Người dùng có thể chọn và tải lên một file thuộc các định dạng hỗ trợ.

### FR-02 — Đọc dữ liệu

Hệ thống xác định loại file và gọi bộ đọc phù hợp.

### FR-03 — PDF scan + OCR

Nếu PDF không có lớp text hoặc text trích xuất không đủ dùng, hệ thống chuyển sang OCR. Kết quả OCR được chuyển thành text/dữ liệu trung gian để tiếp tục xử lý.

### FR-04 — Nhận diện trường họ tên

Hệ thống phải cố gắng xác định trường tương ứng với `ho_ten` từ các alias phổ biến.

Ví dụ:

- Họ tên
- Họ và tên
- Tên nhân viên
- Tên CBCNV
- Full Name
- Employee Name

### FR-05 — Bảo toàn trường mở rộng

Ngoài `ho_ten`, tất cả trường đọc được từ bản ghi phải được giữ lại dưới dạng thông tin mở rộng, trừ trường hoàn toàn rỗng hoặc dữ liệu bị loại theo rule validation.

### FR-06 — Validation

- Không tìm được cột/trường họ tên ở cấp file → cảnh báo file không đủ điều kiện tìm kiếm theo tên.
- Có cột họ tên nhưng một dòng bị rỗng → đánh dấu/bỏ qua dòng đó, không làm hỏng toàn file.
- File rỗng, file hỏng, định dạng không hỗ trợ → trả lỗi rõ ràng, không crash toàn hệ thống.

### FR-07 — Lưu trữ SQLite

Mỗi bản ghi hợp lệ được lưu với:

- `id` nội bộ tự sinh;
- `ho_ten`;
- `ho_ten_chuan` dùng cho tìm kiếm;
- `thong_tin_mo_rong` dạng JSON chứa toàn bộ trường còn lại;
- thông tin nguồn file nếu có.

### FR-08 — Tìm kiếm theo tên

Hỗ trợ tối thiểu:

- Exact Match — khớp chính xác;
- Partial Match — khớp một phần;
- không phân biệt hoa/thường;
- tìm không dấu;
- Fuzzy Search — tìm gần đúng khi gõ sai nhẹ;
- ranking — xếp kết quả phù hợp hơn lên trước.

### FR-09 — Trả toàn bộ thông tin

Khi tìm thấy nhân viên, kết quả phải trả:

- `ho_ten`;
- độ khớp nếu có;
- toàn bộ `thong_tin_mo_rong` của bản ghi.

Ví dụ file có 15 trường thì kết quả có thể hiển thị đủ 15 trường, không chỉ 4–6 trường cố định.

### FR-10 — UI động

UI phải có:

- khu vực Upload;
- ô tìm kiếm;
- danh sách kết quả;
- khả năng hiển thị số lượng trường thay đổi theo dữ liệu nguồn;
- thông báo lỗi/trạng thái rõ ràng.

### FR-11 — Server-client

Ứng dụng chạy trên máy leader và có thể được truy cập từ máy khác bằng trình duyệt khi cấu hình mạng/firewall phù hợp.

## 5. Luồng nghiệp vụ chính

### 5.1 Upload

```text
File
  ↓
File Reader
  ↓
PDF scan? → OCR
  ↓
Trích xuất cấu trúc/text
  ↓
Nhận diện trường ho_ten
  ↓
Có ho_ten?
 ├─ Không → Cảnh báo / không nhập vào kho tìm kiếm
 └─ Có
      ↓
Chuẩn hóa ho_ten
      ↓
Giữ toàn bộ trường còn lại
      ↓
SQLite
```

### 5.2 Search

```text
Query tên
   ↓
Chuẩn hóa query
   ↓
Exact / Partial / Accent-insensitive / Fuzzy
   ↓
Ranking
   ↓
Lấy record SQLite
   ↓
ho_ten + toàn bộ trường mở rộng
   ↓
UI
```

## 6. MVP bắt buộc để báo cáo

Sản phẩm tối thiểu phải demo được:

1. Upload ít nhất một định dạng có cấu trúc và một PDF scan.
2. OCR PDF scan thành công ở trường hợp mẫu.
3. Nhận diện được trường họ tên.
4. Lưu bản ghi vào SQLite.
5. Tìm theo tên đầy đủ hoặc một phần tên.
6. Trả nhiều kết quả khi phù hợp.
7. Hiển thị toàn bộ thông tin của nhân viên, kể cả các trường ngoài schema ban đầu.
8. Máy khác có thể truy cập UI từ máy leader trong môi trường demo.

## 7. Những phần chưa chốt hoàn toàn

- Vị trí AI chính thức ngoài OCR và fuzzy matching.
- Công cụ OCR chính thức nếu CK1-02 thử nhiều engine.
- Backend framework cuối cùng nếu CK1-04 chưa khóa FastAPI/Flask.
- UI framework cuối cùng nếu CK1-05 chưa khóa Streamlit/Gradio.

Các quyết định này phải được chốt sau review CK1 và cập nhật lại tài liệu trước CK2.

## 8. Nguyên tắc thay đổi yêu cầu

- Thành viên không tự thay đổi `ho_ten` khỏi vai trò trường bắt buộc.
- Không tự giới hạn hệ thống về 6 trường cố định.
- Mọi thay đổi contract dữ liệu phải báo leader và cập nhật `data_schema.md` + `integration_rules.md` trước khi merge.
