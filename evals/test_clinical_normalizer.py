"""
Unit & Benchmark Test Suite for MedMate Clinical Lexicon & Normalizer
=====================================================================
Tests:
1. Thai and English Synonym Normalization
2. Brand-to-Generic Drug Name Mapping
3. Laboratory Tests & Specimen Token Permutation Invariance
4. Word Boundary Clinical Safety (preventing unintended substring replacements)
5. Strict Clinical Safety prevent_merge Guards (ClinicalSafetyViolationError)
6. Database CRUD, Persistence and In-Memory Matcher Refresh
7. Cross-Lingual Zero-Shot Cache Hit (Thai Colloquial -> English Stored Cache)
8. High-Performance Latency Benchmark (<0.2ms)
"""

import os
import sys
import time
import shutil
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from medical_skill.clinical_normalizer import (
    ClinicalNormalizer,
    ClinicalSafetyViolationError
)
from medical_skill.medical_mcp_cache import MedicalMcpCache


class TestClinicalNormalizer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Uses master lexicon database created by seeder
        cls.normalizer = ClinicalNormalizer()

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.temp_db = Path(self.test_dir) / "test_isolated_lexicon.db"

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_thai_and_english_synonym_normalization(self):
        """Verify Thai clinical expressions map to standard canonical medical tokens."""
        cases = [
            ("ผู้ป่วยโรคเบาหวานชนิดที่ 2", "t2dm"),
            ("ภาวะกรดคีโตนจากเบาหวาน", "dka"),
            ("ไตวายเฉียบพลัน", "aki"),
            ("ไตวายเรื้อรัง", "ckd"),
            ("หลอดเลือดสมองอุดตัน", "stroke"),
            ("ความดันโลหิตสูง", "hypertension"),
            ("ปอดอักเสบชุมชน", "cap"),
            ("หัวใจเต้นสั่นพริ้ว", "af"),
        ]
        for query_in, expected_token in cases:
            normalized = self.normalizer.normalize(query_in)
            self.assertIn(expected_token, normalized.split(),
                          f"Expected token '{expected_token}' in normalized output '{normalized}' for input '{query_in}'")

    def test_02_brand_to_generic_drug_normalization(self):
        """Verify brand names accurately normalize to generic pharmaceutical entities."""
        cases = [
            ("glucophage 500mg", ["500mg", "metformin"]),
            ("plavix 75mg", ["75mg", "clopidogrel"]),
            ("lipitor 40mg", ["40mg", "atorvastatin"]),
            ("norvasc 10mg", ["10mg", "amlodipine"]),
            ("พาราเซตามอล 500mg", ["500mg", "paracetamol"]),
            ("tylenol 500mg", ["500mg", "paracetamol"]),
            ("แอสไพริน 81mg", ["81mg", "aspirin"]),
            ("aspent 81mg", ["81mg", "aspirin"]),
            ("activase rt-pa", ["alteplase"]),
        ]
        for query_in, expected_tokens in cases:
            normalized = self.normalizer.normalize(query_in)
            tokens = normalized.split()
            for exp in expected_tokens:
                self.assertIn(exp, tokens, f"Expected '{exp}' in '{normalized}' for query '{query_in}'")

    def test_03_lab_tests_and_specimens_invariance(self):
        """Verify permutations, abbreviations and Thai forms produce identical canonical tokens."""
        q1 = "serum creatinine normal range mg/dl"
        q2 = "normal range creatinine serum mg/dL"
        q3 = "creatinine mg/dl normal range serum"
        q4 = "scr normal range mg/dl"

        out1 = self.normalizer.normalize(q1)
        out2 = self.normalizer.normalize(q2)
        out3 = self.normalizer.normalize(q3)
        out4 = self.normalizer.normalize(q4)

        expected = "creatinine dl mg normal range serum"
        self.assertEqual(out1, expected)
        self.assertEqual(out2, expected)
        self.assertEqual(out3, expected)
        self.assertEqual(out4, expected)

    def test_04_word_boundary_safety(self):
        """Verify word boundaries prevent dangerous substring replacements."""
        # 'cr' should NOT match inside 'screen' or 'increase'
        query = "screen creatinine cr increase"
        normalized = self.normalizer.normalize(query)
        tokens = normalized.split()

        self.assertIn("screen", tokens)
        self.assertIn("increase", tokens)
        self.assertIn("creatinine", tokens)

        # 'asa' should NOT match inside 'passage'
        query_asa = "passage asa 81mg"
        normalized_asa = self.normalizer.normalize(query_asa)
        tokens_asa = normalized_asa.split()
        self.assertIn("passage", tokens_asa)
        self.assertIn("aspirin", tokens_asa)

    def test_05_clinical_safety_prevent_merge_guards(self):
        """Verify strict clinical safety constraints block contradictory or dangerous synonym merges."""
        iso_normalizer = ClinicalNormalizer(db_path=self.temp_db)

        # 1. Block STEMI vs NSTEMI
        with self.assertRaises(ClinicalSafetyViolationError):
            iso_normalizer.add_term("stemi", "nstemi", "disease", "en")

        with self.assertRaises(ClinicalSafetyViolationError):
            iso_normalizer.add_term("nstemi", "stemi", "disease", "en")

        # 2. Block Hypoglycemia vs Hyperglycemia
        with self.assertRaises(ClinicalSafetyViolationError):
            iso_normalizer.add_term("hypoglycemia", "hyperglycemia", "disease", "en")

        # 3. Block T1DM vs T2DM
        with self.assertRaises(ClinicalSafetyViolationError):
            iso_normalizer.add_term("t1dm", "t2dm", "disease", "en")

        # 4. Block Hypokalemia vs Hyperkalemia
        with self.assertRaises(ClinicalSafetyViolationError):
            iso_normalizer.add_term("hypokalemia", "hyperkalemia", "disease", "en")

        # 5. Block Acidosis vs Alkalosis
        with self.assertRaises(ClinicalSafetyViolationError):
            iso_normalizer.add_term("metabolic acidosis", "metabolic alkalosis", "disease", "en")

        # 6. Block UGIB vs LGIB
        with self.assertRaises(ClinicalSafetyViolationError):
            iso_normalizer.add_term("ugib", "lgib", "disease", "en")

        # 7. Block contradictory prefix on prevent_merge terms
        iso_normalizer.add_term("severe_hypotension", "hypotension", "disease", "en", prevent_merge=True)
        with self.assertRaises(ClinicalSafetyViolationError):
            iso_normalizer.add_term("severe_hypertension", "severe_hypotension", "disease", "en")

    def test_06_database_crud_and_isolation(self):
        """Verify SQLite CRUD, lookup, search, and dynamic in-memory matcher refresh."""
        iso_normalizer = ClinicalNormalizer(db_path=self.temp_db)

        # Initially empty
        self.assertIsNone(iso_normalizer.lookup("test_term"))

        # Add term
        added = iso_normalizer.add_term("test_term", "canonical_test", "general", "en")
        self.assertTrue(added)

        entry = iso_normalizer.lookup("test_term")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["canonical_term"], "canonical_test")

        # Normalize uses newly added term
        out = iso_normalizer.normalize("query with test_term here")
        self.assertIn("canonical_test", out.split())

        # Search term
        results = iso_normalizer.search("test")
        self.assertEqual(len(results), 1)

        # Delete term
        deleted = iso_normalizer.delete_term("test_term")
        self.assertTrue(deleted)
        self.assertIsNone(iso_normalizer.lookup("test_term"))

        # Normalize no longer replaces it
        out2 = iso_normalizer.normalize("query with test_term here")
        self.assertNotIn("canonical_test", out2.split())
        self.assertIn("test_term", out2.split())

    def test_07_cross_lingual_zero_shot_cache_hit(self):
        """Verify cross-lingual equivalence: Thai clinical query hits cache seeded in English."""
        cache_db = Path(self.test_dir) / "test_cache.db"
        cache = MedicalMcpCache(db_path=str(cache_db))

        # Doctor 1 queries using standard English medical terms
        english_args = {"query": "metformin 500mg t2dm"}
        payload = {"guideline": "First-line oral antidiabetic therapy for T2DM with eGFR > 30"}
        cache.set("medical-mcp", "search-clinical-guidelines", english_args, payload)

        # Doctor 2 or patient queries using Thai vernacular & brand name
        thai_args = {"query": "ยา glucophage 500mg โรคเบาหวานชนิดที่ 2"}
        cached_result = cache.get("medical-mcp", "search-clinical-guidelines", thai_args)

        self.assertIsNotNone(cached_result, "Cross-lingual cache miss: Thai query failed to hit English-seeded cache!")
        self.assertEqual(cached_result["guideline"], payload["guideline"])

    def test_08_sub_millisecond_latency(self):
        """Verify ClinicalNormalizer.normalize() executes under 0.2ms per query."""
        test_queries = [
            "ผู้ป่วยโรคเบาหวานชนิดที่ 2 มีภาวะกรดเกินในเลือดจากเบาหวาน Scr 2.1 mg/dL",
            "serum creatinine normal range mg/dl",
            "st-elevation myocardial infarction vs non-st-elevation myocardial infarction",
            "acetaminophen 500mg glucophage plavix",
            "acute kidney injury with hyperkalemia k+ 6.2 meq/l",
            "acute ischemic stroke t-pa alteplase within 4.5 hours"
        ]

        N = 1000
        t0 = time.perf_counter()
        for i in range(N):
            self.normalizer.normalize(test_queries[i % len(test_queries)])
        elapsed = time.perf_counter() - t0
        avg_ms = (elapsed / N) * 1000

        self.assertLess(avg_ms, 0.2, f"Normalization latency {avg_ms:.4f}ms exceeded 0.2ms limit")


if __name__ == "__main__":
    unittest.main(verbosity=2)
