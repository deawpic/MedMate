"""
Comprehensive Unit Tests for MedMate Clinical Lexicon Auto-Enrichment Engine
Tests:
1. FDA search-drugs markdown harvesting (medical-mcp)
2. FDA OpenFDA JSON / dict payload harvesting (medical-mcp)
3. RxNorm bracketed brand & formulation harvesting (medical-terminologies-mcp)
4. MeSH terminology and ATC drug class harvesting (medical-terminologies-mcp)
5. Clinical Safety & Invariant Guards (Blocks harmful/contradictory pairs)
6. End-to-End Cache-Set Interceptor Auto-Enrichment
"""

import os
import sys
import tempfile
import shutil
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from medical_skill.clinical_normalizer import ClinicalNormalizer
from medical_skill.clinical_enricher import ClinicalLexiconEnricher
from medical_skill.medical_mcp_cache import MedicalMcpCache


class TestClinicalEnricher(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.lex_path = Path(self.test_dir) / "test_lexicon.db"
        self.cache_path = Path(self.test_dir) / "test_cache.db"
        self.normalizer = ClinicalNormalizer(db_path=self.lex_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_fda_drug_search_markdown_enrichment(self):
        """Verify FDA search-drugs markdown output is harvested into brand->generic mapping."""
        fda_md = """
**Drug Search Results for "lipitor"**

Found 1 drug(s)

1. **Lipitor**
   Generic Name: ATORVASTATIN CALCIUM
   Manufacturer: Viatris Specialty LLC
   Route: ORAL
   Dosage Form: Not specified
"""
        added = self.normalizer.auto_enrich_from_mcp(
            provider="medical-mcp",
            tool_name="search-drugs",
            arguments={"query": "lipitor"},
            payload=fda_md
        )
        self.assertGreaterEqual(added, 1)

        # Verify normalizer now knows lipitor -> atorvastatin
        norm = self.normalizer.normalize("ผู้ป่วยรับประทาน lipitor 20 mg วันละครั้ง")
        self.assertIn("atorvastatin", norm)
        self.assertNotIn("lipitor", norm)

    def test_02_fda_drug_details_json_enrichment(self):
        """Verify OpenFDA structured JSON payload is cleanly harvested."""
        fda_json = {
            "status": "success",
            "results": [
                {
                    "brand_name": "Glucophage",
                    "generic_name": "METFORMIN HYDROCHLORIDE",
                    "route": "oral"
                },
                {
                    "brand_name": "Plavix",
                    "generic_name": "CLOPIDOGREL BISULFATE",
                    "route": "oral"
                }
            ]
        }
        added = self.normalizer.auto_enrich_from_mcp(
            provider="medical-mcp",
            tool_name="get-drug-details",
            arguments={"ndc": "0087-6060-05"},
            payload=fda_json
        )
        self.assertEqual(added, 2)

        norm_met = self.normalizer.normalize("คนไข้เบาหวานทาน glucophage 500 mg")
        self.assertIn("metformin", norm_met)

        norm_clop = self.normalizer.normalize("จ่าย plavix 75 mg หลังใส่ stent")
        self.assertIn("clopidogrel", norm_clop)

    def test_03_rxnorm_search_markdown_and_brackets(self):
        """Verify RxNorm bracketed brand names and formulations are harvested."""
        rx_md = """
1. **1043567** - 24 HR metformin hydrochloride 1000 MG / saxagliptin 2.5 MG Extended Release Oral Tablet [Kombiglyze]
   Type: SBD | Synonym: Kombiglyze 2.5/1000 24 HR Extended Release Oral Tablet

2. **1243026** - linagliptin 2.5 MG / metformin hydrochloride 1000 MG Oral Tablet [Jentadueto]
   Type: SBD | Synonym: Jentadueto 2.5/1000 Oral Tablet
"""
        added = self.normalizer.auto_enrich_from_mcp(
            provider="medical-terminologies-mcp",
            tool_name="rxnorm_search",
            arguments={"query": "metformin"},
            payload=rx_md
        )
        self.assertGreaterEqual(added, 2)

        norm_jent = self.normalizer.normalize("เคสนี้ให้ยา jentadueto ต่อได้")
        self.assertIn("metformin", norm_jent)

    def test_04_mesh_and_atc_enrichment(self):
        """Verify MeSH descriptor and ATC class harvesting."""
        mesh_md = """
| MeSH ID | Label |
|---------|-------|
| D000072658 | Non-ST Elevated Myocardial Infarction |
"""
        added_mesh = self.normalizer.auto_enrich_from_mcp(
            provider="medical-terminologies-mcp",
            tool_name="mesh_search",
            arguments={"query": "nstemi"},
            payload=mesh_md
        )
        self.assertGreaterEqual(added_mesh, 1)

        norm_mesh = self.normalizer.normalize("สงสัย nstemi ต้องส่ง troponin")
        for token in ["myocardial", "infarction", "non", "st"]:
            self.assertIn(token, norm_mesh)

        atc_md = """
| ATC code | Class name | Drug (RxNorm) | TTY |
|----------|------------|---------------|-----|
| A10BA | Biguanides | metformin | IN |
"""
        added_atc = self.normalizer.auto_enrich_from_mcp(
            provider="medical-terminologies-mcp",
            tool_name="atc_classify",
            arguments={"drug_name": "metformin"},
            payload=atc_md
        )
        self.assertGreaterEqual(added_atc, 1)

    def test_05_clinical_safety_guard_blocks_dangerous_mcp_pairs(self):
        """Verify safety invariants block contradictory or dangerous pairs from poisoning lexicon."""
        poisoned_json = {
            "results": [
                {"brand_name": "hypoglycemia", "generic_name": "hyperglycemia"},
                {"brand_name": "aspirin", "generic_name": "warfarin"},
                {"brand_name": "stemi", "generic_name": "nstemi"}
            ]
        }
        added = self.normalizer.auto_enrich_from_mcp(
            provider="medical-mcp",
            tool_name="search-drugs",
            arguments={"query": "aspirin"},
            payload=poisoned_json
        )
        # All dangerous pairs must be safely rejected (added == 0)
        self.assertEqual(added, 0)

        # Lexicon must not map hypoglycemia to hyperglycemia
        norm_hypo = self.normalizer.normalize("คนไข้มีภาวะ hypoglycemia")
        self.assertNotIn("hyperglycemia", norm_hypo)

    def test_06_end_to_end_cache_set_auto_enrichment(self):
        """Verify that cache.set automatically enriches the lexicon transparently."""
        cache = MedicalMcpCache(
            db_path=str(self.cache_path),
            lexicon_db_path=str(self.lex_path)
        )

        fda_response = """
**Drug Search Results for "crestor"**

Found 1 drug(s)

1. **Crestor**
   Generic Name: ROSUVASTATIN CALCIUM
   Manufacturer: AstraZeneca
"""
        # Cache.set simulates an external MCP call completing
        success = cache.set(
            provider="medical-mcp",
            tool_name="search-drugs",
            arguments={"query": "crestor"},
            raw_payload=fda_response
        )
        self.assertTrue(success)

        # Verify that cache normalizer immediately learned crestor -> rosuvastatin
        norm = cache.normalize_medical_query("crestor 10 mg")
        self.assertIn("rosuvastatin", norm)
        self.assertNotIn("crestor", norm)


if __name__ == "__main__":
    unittest.main()
