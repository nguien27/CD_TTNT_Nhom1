# GĐ1-04 - Search Engine + Rule Engine

Thư mục này là bản thử nghiệm đã chỉnh lại để đưa vào `experiments/`.

## Phạm vi

Luồng của GĐ1-04:

```text
SQLite
  -> Search Engine
  -> xác định cá nhân / đơn vị
  -> Rule Engine
  -> YES / NO / CHUA_XAC_DINH + can_cu
```

Search Engine chỉ tìm kiếm và xếp hạng. Rule Engine mới được phép quyết định kết quả nghiệp vụ. AI Schema Mapping không tham gia quyết định YES/NO.

## Các lỗi của bản ban đầu đã sửa

1. Query có hình dạng MSNV (`NV001`, `CB00025`, `EMP102`) được nhận diện và exact-match trước. Không fuzzy `NV001` sang `NV002`, `NV003`...
2. Fuzzy Search chuyển sang RapidFuzz và khảo sát đủ Ratio, Partial Ratio, Token-based matching, Levenshtein normalized similarity.
3. Ngưỡng fuzzy tăng lên `0.75`; điểm fuzzy giữ nguyên nghĩa 0..1 và luôn thấp hơn Partial/Exact khi ranking.
4. Bỏ bảng `don_vi` và `ma_don_vi` khỏi core schema. Nhân viên chỉ lưu tên đơn vị trong trường `don_vi`.
5. Nhân viên không lưu YES/NO. Kết quả nghiệp vụ chỉ sinh ra từ Rule Engine.
6. `business_rule` có `muc_uu_tien`, `ngay_hieu_luc`, `ngay_het_hieu_luc`, `dang_ap_dung`, `la_mock`.
7. Rule hết hạn hoặc chưa hiệu lực bị bỏ qua.
8. Có test riêng cho Search Engine và Rule Engine.
9. Không đóng gói DB runtime, `__pycache__`, `venv`.

## Schema thử nghiệm

### `nhan_vien`

- `ma_nhan_vien`
- `ho_ten`
- `ho_ten_chuan`
- `don_vi`
- `chuc_vu`
- `email`

Không có trường YES/NO và không có `ma_don_vi`.

### `business_rule`

- `ma_quy_tac`
- `ten_quy_tac`
- `ten_don_vi`
- `loai_don_vi`
- `pham_vi`
- `ket_qua`
- `can_cu`
- `muc_uu_tien`
- `ngay_hieu_luc`
- `ngay_het_hieu_luc`
- `dang_ap_dung`
- `la_mock`
- `ghi_chu`

## Matching

Thứ tự ưu tiên:

```text
MSNV exact
    -> Exact Match tên
    -> Partial Match
    -> Fuzzy Match
    -> Ranking
```

Fuzzy dùng RapidFuzz để tính:

- Levenshtein normalized similarity
- Ratio
- Partial Ratio
- Token Set Ratio

`FUZZY_THRESHOLD = 0.85` chỉ là ngưỡng GĐ1 để demo. GĐ2 cần đánh giá bằng dữ liệu thực tế rồi mới chốt.

## Rule Engine

Thứ tự xét cá nhân:

```text
Ngoại lệ cá nhân đang hiệu lực
    -> đơn vị của nhân viên
    -> business rule đang hiệu lực
    -> chọn rule ưu tiên cao nhất
```

Không tìm thấy rule hợp lệ thì luôn trả:

```text
CHUA_XAC_DINH
```

Rule mock luôn được gắn `[MOCK]` vào `can_cu` khi trả kết quả.

## Cài thư viện

```powershell
python -m pip install -r requirements.txt
```

## Chạy test

```powershell
python test_search_engine.py
python test_rule_engine.py
```

Hoặc:

```powershell
python -m unittest -v
```

## Chạy demo

```powershell
python demo.py
```

`demo.py` sẽ sinh file `gd1_04_demo.db` tạm thời. File `.db` đã nằm trong `.gitignore` và không cần commit.

## Chuyển sang GĐ2

GĐ2 cần tiếp tục:

- benchmark ngưỡng fuzzy bằng dữ liệu thực tế;
- bổ sung nhiều biến thể tên và lỗi gõ;
- thay mock rule bằng rule khách hàng cung cấp;
- kiểm tra quy tắc chồng lấn và mức ưu tiên;
- tích hợp với SQLite/Backend chính thức của nhóm.


## Cập nhật ranking tên người (v2)

- Thứ tự ưu tiên: `EXACT -> TOKEN -> PARTIAL -> FUZZY`.
- Query một từ như `an` ưu tiên token `an`/`ân`, không xếp `anh` cùng tầng.
- Các nhân viên trùng hoàn toàn họ tên được xen kẽ theo nhóm trong top-N, tránh một tên lặp chiếm hết danh sách.
- Không xóa bản ghi trùng tên: mỗi MSNV vẫn là một nhân viên độc lập.
