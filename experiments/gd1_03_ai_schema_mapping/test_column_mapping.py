# -*- coding: utf-8 -*-
"""Unit test cho GĐ1-03. Chạy: python test_column_mapping.py"""

from __future__ import annotations

import unittest

try:
    from .alias_mapper import AliasMapper
    from .predict import ColumnMappingPredictor
    from .preprocessing import TextPreprocessor
    from .settings import LABELS
except ImportError:
    from alias_mapper import AliasMapper
    from predict import ColumnMappingPredictor
    from preprocessing import TextPreprocessor
    from settings import LABELS


class TestTextPreprocessor(unittest.TestCase):
    def setUp(self):
        self.preprocessor = TextPreprocessor()

    def test_lowercase(self):
        self.assertEqual(self.preprocessor.preprocess("Họ Tên"), "họ tên")

    def test_remove_special_chars(self):
        self.assertEqual(self.preprocessor.preprocess("Mã@NV#2026!"), "mã nv 2026")

    def test_remove_accents(self):
        self.assertEqual(
            self.preprocessor.preprocess("Họ tên", remove_accent=True),
            "ho ten",
        )

    def test_none_input(self):
        self.assertEqual(self.preprocessor.preprocess(None), "")


class TestAliasMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = AliasMapper()

    def test_employee_id(self):
        self.assertEqual(self.mapper.lookup("Mã NV"), "MA_NHAN_VIEN")
        self.assertEqual(self.mapper.lookup("Employee ID"), "MA_NHAN_VIEN")

    def test_full_name(self):
        self.assertEqual(self.mapper.lookup("Họ và tên"), "HO_TEN")
        self.assertEqual(self.mapper.lookup("Full Name"), "HO_TEN")

    def test_department(self):
        self.assertEqual(self.mapper.lookup("Phòng ban"), "TEN_DON_VI")
        self.assertEqual(self.mapper.lookup("Department"), "TEN_DON_VI")

    def test_unit_type(self):
        self.assertEqual(self.mapper.lookup("Loại tổ chức"), "LOAI_DON_VI")

    def test_no_ma_don_vi_class(self):
        self.assertNotIn("MA_DON_VI", LABELS)
        self.assertIsNone(self.mapper.lookup("Mã đơn vị"))

    def test_no_substring_match(self):
        self.assertIsNone(self.mapper.lookup("Department note"))


class TestPredictorWithoutModel(unittest.TestCase):
    def setUp(self):
        self.predictor = ColumnMappingPredictor(model_path=None)

    def test_alias_fallback(self):
        result = self.predictor.predict_single("MSNV")
        self.assertEqual(result["label"], "MA_NHAN_VIEN")
        self.assertEqual(result["source"], "alias_exact")
        self.assertTrue(result["accepted"])

    def test_unknown(self):
        result = self.predictor.predict_single("Ghi chú tự do")
        self.assertEqual(result["label"], "OTHER")
        self.assertFalse(result["accepted"])

    def test_no_business_result(self):
        result = self.predictor.predict_single("Họ tên")
        self.assertNotIn(result["label"], {"YES", "NO", "CHUA_XAC_DINH"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
