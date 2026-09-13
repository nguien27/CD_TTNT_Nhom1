# -*- coding: utf-8 -*-
"""Demo GĐ1-03: chỉ Schema Mapping, không có Rule Engine nghiệp vụ."""

from pathlib import Path

try:
    from .predict import ColumnMappingPredictor
except ImportError:
    from predict import ColumnMappingPredictor


THU_MUC_DU_AN = Path(__file__).resolve().parents[2]
MODEL_PATH = THU_MUC_DU_AN / "models" / "schema_mapping" / "column_mapping_model.pkl"


def main():
    model_path = MODEL_PATH if MODEL_PATH.exists() else None
    predictor = ColumnMappingPredictor(model_path=model_path)

    column_names = [
        "Mã NV",
        "Họ tên",
        "Phòng ban",
        "Loại đơn vị",
        "Ghi chú",
    ]

    print("=" * 72)
    print("DEMO AI SCHEMA MAPPING - GĐ1-03")
    print("=" * 72)
    print(f"AI model: {'Có' if model_path else 'Chưa train - dùng exact alias'}")

    for column_name in column_names:
        result = predictor.predict_single(column_name)
        print(f"{column_name:<20} -> {result}")


if __name__ == "__main__":
    main()
