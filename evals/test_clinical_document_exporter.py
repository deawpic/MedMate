# -*- coding: utf-8 -*-
"""
Unit Test Suite for Markdown-Native Clinical Document Exporter
MedMate - Thai Clinical Intelligence & Knowledge Harness

Validates:
1. Native Markdown (.md) clinical report export with UTF-8 encoding (Rule 2.6)
2. 100% Preservation of Clinical Math (LaTeX / KaTeX) & Chemical Equations (Rule 2.8)
3. Standardized PDF/Printing Advisory for Clinicians (Obsidian, VS Code, Typora, Browsers)
4. Subprocess Multi-line Execution Safety (sys.executable + NamedTemporaryFile)
"""

import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from medical_skill.clinical_document_exporter import (
    export_clinical_markdown,
    get_pdf_export_guidance,
    run_safe_python_script
)


class TestClinicalDocumentExporter(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="medmate_doc_test_")
        self.output_dir = Path(__file__).resolve().parents[1] / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_get_pdf_export_guidance(self):
        """Test that PDF/Print guidance includes recommended external tools."""
        guidance = get_pdf_export_guidance()
        self.assertIn("คำแนะนำสำหรับการพิมพ์หรือแปลงเป็น PDF", guidance)
        self.assertIn("Obsidian", guidance)
        self.assertIn("VS Code", guidance)
        self.assertIn("Typora", guidance)
        self.assertIn("Markdown Viewer", guidance)
        self.assertIn("\\LaTeX", guidance)

    def test_export_clinical_markdown_with_math_and_guidance(self):
        """Test Markdown export preserving LaTeX math, chemistry formulas, and advisory callout."""
        title = "แนวทางการรักษาภาวะวิกฤต Diabetic Ketoacidosis (DKA)"
        md_content = (
            "## 1. ข้อมูลผู้ป่วยและผลแล็บ\n"
            "- ผู้ป่วย: [PATIENT_1] ชายไทย 52 ปี\n"
            "- Blood Gas: pH 7.15, $HCO_3^- = 10\\text{ mEq/L}$\n\n"
            "## 2. การคำนวณทางการแพทย์\n"
            "- **Serum Anion Gap:**\n"
            "  $$\\text{Anion Gap} = Na^+ - (Cl^- + HCO_3^-) = 132 - (98 + 10) = 24\\text{ mEq/L}$$\n"
            "- **Corrected Sodium:**\n"
            "  $$\\text{Corrected } Na^+ = Measured\\; Na^+ + 0.016 \\times (Glucose - 100)$$\n"
        )
        saved_file = export_clinical_markdown(
            title=title,
            markdown_content=md_content,
            filename="test_dka_export.md",
            output_dir=Path(self.test_dir),
            include_pdf_guidance=True
        )

        self.assertTrue(saved_file.exists())
        text = saved_file.read_text(encoding="utf-8")

        # Verify Title & Headers
        self.assertIn(f"# {title}", text)
        self.assertIn("## 1. ข้อมูลผู้ป่วยและผลแล็บ", text)

        # Verify Math & Chemical Formulas preservation
        self.assertIn("$HCO_3^- = 10\\text{ mEq/L}$", text)
        self.assertIn("\\text{Anion Gap} = Na^+ - (Cl^- + HCO_3^-)", text)
        self.assertIn("\\text{Corrected } Na^+", text)

        # Verify PDF guidance is appended
        self.assertIn("คำแนะนำสำหรับการพิมพ์หรือแปลงเป็น PDF", text)
        self.assertIn("Obsidian", text)

    def test_export_clinical_markdown_without_guidance(self):
        """Test Markdown export when include_pdf_guidance is disabled."""
        title = "สรุปข้อมูลแล็บคลินิก"
        md_content = "- DTX: 420 mg/dL\n- Urine Ketone: 3+\n"

        saved_file = export_clinical_markdown(
            title=title,
            markdown_content=md_content,
            filename="test_no_guidance.md",
            output_dir=Path(self.test_dir),
            include_pdf_guidance=False
        )

        self.assertTrue(saved_file.exists())
        text = saved_file.read_text(encoding="utf-8")
        self.assertIn(title, text)
        self.assertNotIn("คำแนะนำสำหรับการพิมพ์หรือแปลงเป็น PDF", text)

    def test_run_safe_python_script(self):
        """Test safe subprocess execution via sys.executable and temporary script file."""
        script = """
import sys
import json

data = {"status": "success", "engine": "markdown_native", "sys_exec": sys.executable}
print(json.dumps(data, ensure_ascii=False))
"""
        result = run_safe_python_script(script)
        self.assertEqual(result.returncode, 0, f"Script failed: {result.stderr}")
        self.assertIn("markdown_native", result.stdout)
        self.assertIn(sys.executable, result.stdout)


if __name__ == "__main__":
    unittest.main()
