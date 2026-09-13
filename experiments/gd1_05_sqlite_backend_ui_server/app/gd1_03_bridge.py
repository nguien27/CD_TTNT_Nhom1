# -*- coding: utf-8 -*-
"""Bridge tùy chọn tới GĐ1-03 để mapping tên cột khi upload CSV."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
EXPERIMENTS_DIR = THIS_DIR.parents[1]
GD1_03_DIR = EXPERIMENTS_DIR / "gd1_03_ai_schema_mapping"


def tao_predictor() -> Any | None:
    if not GD1_03_DIR.exists():
        return None
    if str(GD1_03_DIR) not in sys.path:
        sys.path.insert(0, str(GD1_03_DIR))
    from predict import ColumnMappingPredictor  # type: ignore

    return ColumnMappingPredictor(model_path=None)
