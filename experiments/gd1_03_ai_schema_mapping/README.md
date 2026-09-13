# GĐ1-03 – AI Schema Mapping

Thư mục này là bản đã sửa của phần thử nghiệm GĐ1-03.

## Phạm vi

AI chỉ nhận diện ý nghĩa của tên cột/trường đầu vào.

Class hiện tại:

- `MA_NHAN_VIEN`
- `HO_TEN`
- `TEN_DON_VI`
- `LOAI_DON_VI`
- `OTHER`

Không có `MA_DON_VI` theo kiến trúc hiện tại của nhóm.

Module này **không** chứa Business Rule và **không** quyết định:

- `YES`
- `NO`
- `CHUA_XAC_DINH`

## Các sửa đổi chính

1. Tách hoàn toàn Business Rule khỏi AI Schema Mapping.
2. Thay `rules.py` bằng `alias_mapper.py`; alias chỉ dùng để mapping tên cột.
3. Alias exact-match sau chuẩn hóa, không dùng substring để giảm match nhầm.
4. Bỏ class `MA_DON_VI`.
5. Evaluation nhận trực tiếp holdout test đã tách trước khi train, tránh data leakage.
6. Logistic Regression là baseline chính.
7. Nếu thử Linear SVM thì dùng `CalibratedClassifierCV` để có `predict_proba`.
8. Threshold `0.70` hiện là ngưỡng ban đầu; GĐ2 phải đánh giá lại trên dữ liệu thật.

## Chạy test GĐ1

Từ thư mục này:

```powershell
python test_column_mapping.py
```

Chạy demo chưa cần model:

```powershell
python run_demo.py
```

## GĐ2

Dataset dự kiến:

```text
data_ai/schema_mapping_dataset.csv
```

Cấu trúc:

```csv
text,label
Họ và tên,HO_TEN
Full Name,HO_TEN
Mã nhân viên,MA_NHAN_VIEN
Employee ID,MA_NHAN_VIEN
Department,TEN_DON_VI
Unit Type,LOAI_DON_VI
```

Train baseline:

```powershell
python train.py --dataset ../../data_ai/schema_mapping_dataset.csv --model ../../models/schema_mapping/column_mapping_model.pkl --model-type logistic
```

Lưu ý: đường dẫn trên giả định thư mục này nằm tại `experiments/gd1_03_ai_schema_mapping/`.
