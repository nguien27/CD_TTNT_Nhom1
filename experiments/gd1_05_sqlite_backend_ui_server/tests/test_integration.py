# -*- coding: utf-8 -*-
from __future__ import annotations

import unittest

from app.gd1_03_bridge import tao_predictor
from app.gd1_04_bridge import PayrollLookupAPI, RuleEngine, SearchEngine


class TestIntegration(unittest.TestCase):
    def test_gd1_04_modules_are_reused(self):
        self.assertEqual(SearchEngine.__module__, "search_engine")
        self.assertEqual(RuleEngine.__module__, "rule_engine")
        self.assertEqual(PayrollLookupAPI.__module__, "api")

    def test_gd1_03_alias_mapping_available(self):
        predictor = tao_predictor()
        self.assertIsNotNone(predictor)
        self.assertEqual(predictor.predict_single("Mã NV")["label"], "MA_NHAN_VIEN")
        self.assertEqual(predictor.predict_single("Họ tên")["label"], "HO_TEN")
        self.assertEqual(predictor.predict_single("Đơn vị")["label"], "TEN_DON_VI")


if __name__ == "__main__":
    unittest.main(verbosity=2)
