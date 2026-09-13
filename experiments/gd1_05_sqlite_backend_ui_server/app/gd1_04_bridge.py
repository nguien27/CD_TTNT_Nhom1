# -*- coding: utf-8 -*-
"""Bridge dùng trực tiếp Search Engine + Rule Engine của GĐ1-04.

Không viết lại logic tìm kiếm hoặc logic YES/NO trong GĐ1-05.
Hai folder phải nằm cạnh nhau trong experiments/.
"""

from __future__ import annotations

import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
EXPERIMENTS_DIR = THIS_DIR.parents[1]
GD1_04_DIR = EXPERIMENTS_DIR / "gd1_04_search_rule_engine"

if not GD1_04_DIR.exists():
    raise RuntimeError(
        "Không tìm thấy experiments/gd1_04_search_rule_engine. "
        "Hãy đặt GĐ1-04 và GĐ1-05 cùng trong thư mục experiments/."
    )

if str(GD1_04_DIR) not in sys.path:
    sys.path.insert(0, str(GD1_04_DIR))

from api import PayrollLookupAPI  # type: ignore  # noqa: E402
from rule_engine import RuleEngine  # type: ignore  # noqa: E402
from search_engine import SearchEngine, chuan_hoa  # type: ignore  # noqa: E402

__all__ = ["PayrollLookupAPI", "RuleEngine", "SearchEngine", "chuan_hoa"]
