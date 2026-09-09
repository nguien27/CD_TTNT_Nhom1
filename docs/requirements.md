# REQUIREMENTS – Hệ thống truy xuất thông tin nhân viên doanh nghiệp

**Phiên bản:** 0.2 – CK1  
**Cập nhật quyết định:** dùng cơ sở dữ liệu quan hệ SQL với **SQLite** làm database chính thức của bản demo; **OCR là bắt buộc đối với PDF scan/ảnh**.  
**Mục đích:** Làm tài liệu yêu cầu chung để các task CK1, CK2 và CK3 dùng cùng một ngữ cảnh.

---

## 1. Bối cảnh bài toán

Nhóm xây dựng một hệ thống có khả năng tiếp nhận dữ liệu nhân sự của doanh nghiệp từ nhiều loại tệp, trích xuất và chuẩn hóa thông tin nhân viên, lưu dữ liệu vào cơ sở dữ liệu SQL, sau đó cho phép người dùng tìm kiếm nhân viên và truy xuất các thông tin liên quan như mã nhân viên, họ tên, đơn vị, chức vụ và các trường mở rộng khác.

Ví dụ người dùng nhập:

```text
Nguyễn Văn
```

Hệ thống không chỉ tìm một tên khớp tuyệt đối mà cần trả về nhiều kết quả phù hợp, ví dụ:

```text
Nguyễn Văn A
Nguyễn Văn B
Nguyễn Văn An
```

Kết quả tìm kiếm cần hiển thị thông tin của từng nhân viên, tối thiểu gồm mã nhân viên, họ tên, đơn vị và chức vụ.

---

## 2. Mục tiêu tổng quát

Xây dựng một sản phẩm có luồng xử lý hoàn chỉnh:

```text
File đầu vào
    ↓
Nhận diện loại file
    ↓
Đọc file / OCR nếu cần
    ↓
Trích xuất dữ liệu
    ↓
Ánh xạ và chuẩn hóa trường dữ liệu
    ↓
Lưu vào SQLite bằng SQL
    ↓
Tìm kiếm / truy xuất
    ↓
Backend
    ↓
UI
    ↓
Người dùng
```

Sản phẩm cuối phải có thể chạy trên một máy đóng vai trò **server (máy chủ)** và máy khác có thể truy cập, xem và sử dụng hệ thống trong cùng môi trường mạng phù hợp.

---

## 3. Phạm vi dữ liệu đầu vào

### 3.1. Định dạng bắt buộc ưu tiên

Phiên bản đầu tiên phải hướng tới hỗ trợ:

- `.xlsx` – Excel.
- `.csv` – CSV.
- `.docx` – Word.
- `.pdf` – PDF có lớp text.
- `.pdf` – PDF scan hoặc PDF chứa ảnh, sử dụng OCR.

Các định dạng khác có thể mở rộng sau khi MVP ổn định.

### 3.2. Cấu trúc file

Không giả định các file có cùng cấu trúc. Hệ thống phải hướng tới xử lý các biến thể như:

```text
File A:
Mã NV | Họ tên | Đơn vị | Chức vụ

File B:
Mã nhân viên | Tên nhân viên | Phòng ban | Vị trí

File C:
Employee ID | Full Name | Department | Position
```

Các tên cột/nhãn khác nhau phải được ánh xạ về **Data Schema (cấu trúc dữ liệu chuẩn)** của hệ thống.

### 3.3. Yêu cầu bắt buộc đối với PDF scan

PDF phải được chia thành hai trường hợp:

#### PDF có text

```text
PDF
 ↓
Trích xuất text trực tiếp
 ↓
Information Extraction
```

#### PDF scan / PDF ảnh

```text
PDF scan
   ↓
Chuyển trang PDF thành ảnh nếu cần
   ↓
OCR – Optical Character Recognition
   ↓
Text nhận dạng
   ↓
Information Extraction
```

OCR là **chức năng bắt buộc của dự án**, không còn là phần mở rộng tùy chọn.

Yêu cầu tối thiểu:

- nhận biết trường hợp PDF không có text đủ dùng;
- thực hiện OCR trên PDF scan;
- hỗ trợ tiếng Việt ở mức có thể triển khai trong thời gian môn học;
- trả được text cho bước trích xuất dữ liệu;
- nếu OCR thất bại phải có lỗi/cảnh báo rõ ràng, không làm ứng dụng crash.

Engine OCR có thể được khảo sát trong CK1-02. Baseline ưu tiên giải pháp miễn phí/offline, ví dụ Tesseract OCR hoặc phương án tương đương. Việc thay OCR engine không được làm thay đổi contract giữa các module.

---

## 4. Thông tin nhân viên tối thiểu

Schema nền tảng gồm:

- `ma_nhan_vien`
- `ho_ten`
- `don_vi`
- `chuc_vu`
- `email`
- `so_dien_thoai`

Trong MVP, các trường quan trọng nhất để truy xuất là:

1. `ma_nhan_vien`
2. `ho_ten`
3. `don_vi`
4. `chuc_vu`

`email` và `so_dien_thoai` là trường mở rộng, có thể bị thiếu ở một số bản ghi.

Chi tiết kiểu dữ liệu, ràng buộc và quy tắc chuẩn hóa được định nghĩa trong `data_schema.md`.

---

## 5. Actor và cách sử dụng

### 5.1. Người dùng cuối

Người không cần kiến thức lập trình, sử dụng hệ thống thông qua giao diện web.

### 5.2. Leader / người vận hành

Có thể:

- khởi động server;
- nạp dữ liệu;
- kiểm tra log hoặc thông báo lỗi;
- kiểm thử hệ thống;
- quản lý phiên bản mã nguồn trên GitHub;
- kiểm tra trạng thái database SQLite.

---

## 6. Yêu cầu chức năng

### FR-01 – Upload file

Hệ thống cho phép người dùng chọn và tải file dữ liệu nhân viên lên.

**Định dạng tối thiểu:** `.xlsx`, `.csv`, `.docx`, `.pdf`.

Hệ thống phải xác định loại file và chuyển tới bộ xử lý phù hợp.

### FR-02 – Đọc nội dung file

Hệ thống có bộ đọc phù hợp cho từng loại file.

Kết quả đọc phải được chuyển thành dạng dữ liệu trung gian có cấu trúc để bước tiếp theo có thể xử lý.

### FR-03 – OCR PDF scan

Khi PDF không có lớp text hữu ích hoặc được nhận diện là PDF scan, hệ thống phải chạy OCR.

Luồng tối thiểu:

```text
PDF
 ↓
Thử đọc text trực tiếp
 ↓
Text đủ dùng? ── Có ──> tiếp tục Extraction
      │
      Không
      ↓
OCR
 ↓
Text OCR
 ↓
Extraction
```

Kết quả OCR phải kèm metadata cho biết OCR đã được sử dụng hay chưa.

### FR-04 – Kiểm tra file và xử lý lỗi

Hệ thống phải phản hồi hợp lý khi:

- file rỗng;
- file hỏng;
- định dạng chưa hỗ trợ;
- file không chứa dữ liệu có thể sử dụng;
- OCR không lấy được text;
- nội dung sau OCR quá kém để trích xuất trường bắt buộc.

Một file lỗi không được làm toàn bộ ứng dụng dừng đột ngột.

### FR-05 – Nhận diện và ánh xạ trường dữ liệu

Các tên cột/nhãn khác nhau phải được ánh xạ về trường chuẩn.

Ví dụ:

```text
Mã NV
Mã nhân viên
Mã cán bộ
Employee ID
      ↓
ma_nhan_vien
```

Quy tắc ánh xạ ban đầu được mô tả trong `data_schema.md`.

### FR-06 – Chuẩn hóa dữ liệu

Dữ liệu sau trích xuất phải được chuẩn hóa trước khi lưu, bao gồm tối thiểu:

- loại bỏ khoảng trắng thừa;
- chuẩn hóa tên trường;
- chuẩn hóa giá trị rỗng;
- kiểm tra trường bắt buộc;
- giữ Unicode tiếng Việt đúng;
- phát hiện mã nhân viên trùng;
- giữ mã nhân viên ở kiểu chuỗi.

### FR-07 – Lưu trữ bằng SQL

**Quyết định chính thức:** hệ thống sử dụng cơ sở dữ liệu quan hệ và SQL để lưu/truy vấn dữ liệu.

**Database chính thức của bản demo:** SQLite.

Lý do lựa chọn SQLite cho dự án hiện tại:

- sử dụng SQL thật;
- không cần dựng database server riêng;
- dễ đóng gói cùng ứng dụng;
- phù hợp nhóm 5 người và thời gian ngắn;
- đủ khả năng lưu, thêm, cập nhật và truy vấn dữ liệu nhân viên;
- phù hợp mô hình máy leader chạy ứng dụng/server.

Database tối thiểu có bảng `nhan_vien` theo schema trong `data_schema.md`.

Không được để UI đọc trực tiếp file Excel làm nguồn dữ liệu chính trong phiên bản tích hợp cuối.

### FR-08 – Import dữ liệu vào SQL

Sau khi file được đọc, OCR nếu cần, trích xuất và chuẩn hóa, các record hợp lệ phải được lưu vào SQLite.

Hệ thống phải có xử lý cơ bản đối với:

- mã nhân viên trùng;
- record thiếu trường bắt buộc;
- lỗi transaction/database;
- upload nhiều lần.

Policy cụ thể cho `INSERT/UPDATE/UPSERT` được khóa trong `integration_rules.md` và có thể điều chỉnh sau review CK1.

### FR-09 – Tìm kiếm chính xác

Người dùng có thể tìm bằng họ tên đầy đủ hoặc mã nhân viên.

Ví dụ:

```text
NV001
Nguyễn Văn A
```

### FR-10 – Tìm kiếm một phần tên

Người dùng không cần nhập toàn bộ tên.

Ví dụ:

```text
Query: Nguyễn Văn
```

Hệ thống trả về nhiều kết quả phù hợp.

### FR-11 – Tìm kiếm không phân biệt hoa/thường

Các query sau phải được xử lý tương đương về mặt logic:

```text
Nguyễn Văn
nguyễn văn
NGUYỄN VĂN
```

### FR-12 – Tìm kiếm có dấu/không dấu

Hệ thống hướng tới hỗ trợ:

```text
Nguyen Van
→ Nguyễn Văn ...
```

### FR-13 – Fuzzy Search

Hệ thống phải thử nghiệm tìm kiếm gần đúng để xử lý lỗi gõ nhỏ.

Ví dụ:

```text
Nguyne Van A
→ Nguyễn Văn A
```

Kết quả nên có cơ chế ranking hoặc điểm khớp để sắp xếp ứng viên.

### FR-14 – Hiển thị kết quả

UI phải hiển thị tối thiểu:

- mã nhân viên;
- họ tên;
- đơn vị;
- chức vụ;
- email nếu có;
- số điện thoại nếu có;
- độ khớp nếu Search Engine cung cấp.

UI phải hỗ trợ nhiều kết quả, không giả định chỉ có một nhân viên.

### FR-15 – Server

Máy leader chạy ứng dụng/server.

Máy khác trong môi trường mạng phù hợp phải có thể truy cập ứng dụng qua trình duyệt.

### FR-16 – Health check

Backend nên có endpoint hoặc cơ chế kiểm tra trạng thái hệ thống để phục vụ test/deploy.

Ví dụ:

```text
GET /health
```

### FR-17 – Logging lỗi xử lý

Các lỗi quan trọng của File Reader, OCR, Normalization, SQL và Backend phải có thông báo đủ để debug và lập báo cáo test.

---

## 7. Yêu cầu phi chức năng

### NFR-01 – Dễ sử dụng

Người dùng không chuyên phải có thể sử dụng thông qua UI và User Guide.

### NFR-02 – Ổn định

File hoặc query lỗi không được làm toàn hệ thống crash.

### NFR-03 – Khả năng tái lập

Một thành viên khác phải có thể clone repository, cài dependency và chạy hệ thống theo README.

### NFR-04 – Tách module

File Reader, OCR, Extraction, Normalization, Storage, Search, Backend và UI phải được tách trách nhiệm đủ rõ để có thể test và tích hợp.

### NFR-05 – Không hard-code máy cá nhân

Không dùng đường dẫn tuyệt đối như `C:\Users\...` trong business logic.

### NFR-06 – Database có thể khởi tạo lại

Repository phải có script hoặc cơ chế tạo SQLite database/schema từ đầu.

---

## 8. Quyết định kỹ thuật đã chốt

### 8.1. Database

```text
Đã chốt: SQLite + SQL
```

SQLite là database chính thức của bản demo hiện tại.

### 8.2. OCR

```text
Đã chốt: PDF scan phải được OCR
```

OCR là một phần của File Processing Pipeline.

### 8.3. AI

```text
Chưa chốt thành phần AI chính của đề tài
```

Các vị trí có thể khảo sát:

- semantic/AI-assisted schema mapping;
- semantic search;
- hiểu câu hỏi tự nhiên;
- mô hình hỗ trợ trích xuất thông tin.

Không được đưa một mô hình AI vào chỉ để “có AI”; thành phần được chọn phải có vai trò rõ ràng và đo/test được.

---

## 9. MVP – Sản phẩm tối thiểu phải demo được

MVP phải chạy được luồng:

```text
Upload XLSX/CSV/DOCX/PDF
        ↓
Đọc file
        ↓
Nếu PDF scan → OCR
        ↓
Trích xuất thông tin
        ↓
Chuẩn hóa theo Data Schema
        ↓
Lưu SQLite bằng SQL
        ↓
Nhập tên/mã nhân viên
        ↓
Search
        ↓
Hiển thị thông tin nhân viên trên UI
```

MVP phải được truy cập từ máy khác khi máy leader chạy server trong môi trường demo.

---

## 10. Phân kỳ

### CK1 – Phân tích và Prototype

- khóa requirements/schema/architecture;
- thử File Reader và OCR;
- thử Search;
- dựng SQLite/SQL + Backend prototype;
- dựng UI prototype;
- dùng mock data chung.

### CK2 – Xây dựng và tích hợp

- Reader + OCR + Extraction + Mapping + Normalization;
- lưu SQLite;
- Search Engine;
- Backend API;
- UI;
- chạy end-to-end.

### CK3 – Hoàn thiện và triển khai

- system test;
- sửa lỗi;
- server/deploy;
- đóng gói;
- báo cáo kỹ thuật;
- User Guide;
- GitHub;
- rehearsal demo.
