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
    run_safe_python_script,
    detect_ascii_tables_or_diagrams,
    audit_document_formatting
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

    def test_export_clinical_markdown_with_mermaid_and_tables(self):
        """Test exporting clinical markdown containing valid Mermaid diagram and Markdown table."""
        title = "Stroke Clinical Pathway & Assessment"
        md_content = (
            "## 1. การประเมินเส้นเวลา (Clinical Timeline)\n\n"
            "| เวลา | เหตุการณ์ | หมวดหมู่ |\n"
            "| :--- | :--- | :--- |\n"
            "| 07:30 | อาการแขนขาอ่อนแรง | Onset |\n"
            "| 09:00 | ถึงห้องฉุกเฉิน NIHSS 16 | Door |\n\n"
            "## 2. ผังการตัดสินใจการรักษา (Clinical Pathway)\n\n"
            "```mermaid\n"
            "flowchart TD\n"
            "    NodeA[\"ผู้ป่วยสโตรก Onset < 4.5 ชม.\"] --> NodeB{\"NCCT Brain มีเลือดออกหรือไม่?\"}\n"
            "    NodeB -- \"ไม่พบ ICH\" --> NodeC[\"พิจารณาให้ยา IV rt-PA\"]\n"
            "    NodeB -- \"พบ ICH\" --> NodeD[\"ปรึกษาประสาทศัลยแพทย์\"]\n"
            "```\n"
        )
        saved_file = export_clinical_markdown(
            title=title,
            markdown_content=md_content,
            filename="test_stroke_pathway.md",
            output_dir=Path(self.test_dir)
        )

        self.assertTrue(saved_file.exists())
        text = saved_file.read_text(encoding="utf-8")
        self.assertIn("```mermaid", text)
        self.assertIn("| เวลา | เหตุการณ์ | หมวดหมู่ |", text)
        # Verify PDF guidance is excluded from saved file
        self.assertNotIn("คำแนะนำสำหรับการพิมพ์หรือแปลงเป็น PDF", text)
        
        # Verify Audit Passes
        audit = audit_document_formatting(text)
        self.assertTrue(audit["passed"])
        self.assertTrue(audit["has_mermaid"])
        self.assertTrue(audit["has_markdown_table"])
        self.assertEqual(audit["violation_count"], 0)

    def test_export_clinical_markdown_default_excludes_pdf_guidance(self):
        """Test that default export excludes PDF guidance callout from the saved file (chat only)."""
        title = "Clean Medical Record"
        md_content = "- Patient: [PATIENT_1]\n- Diagnosis: Acute Coronary Syndrome\n"
        saved_file = export_clinical_markdown(
            title=title,
            markdown_content=md_content,
            filename="test_clean_export.md",
            output_dir=Path(self.test_dir)
        )
        self.assertTrue(saved_file.exists())
        text = saved_file.read_text(encoding="utf-8")
        self.assertIn("Clean Medical Record", text)
        self.assertNotIn("คำแนะนำสำหรับการพิมพ์หรือแปลงเป็น PDF", text)
        self.assertNotIn("Obsidian", text)

    def test_detect_ascii_tables_or_diagrams_flags_violations(self):
        """Test detection of forbidden ASCII tables, box drawing characters, trees, and flowchart arrows."""
        # 1. ASCII border table
        ascii_table = (
            "+----------------+---------------+\n"
            "| Parameter      | Value         |\n"
            "+================+===============+\n"
            "| Blood Glucose  | 240 mg/dL     |\n"
            "+----------------+---------------+\n"
        )
        violations_table = detect_ascii_tables_or_diagrams(ascii_table)
        self.assertGreater(len(violations_table), 0)
        self.assertTrue(any(v["type"] == "ascii_table_border" for v in violations_table))

        # 2. Unicode box drawing table
        box_table = (
            "┌───────────────┬───────────────┐\n"
            "│ Parameter     │ Value         │\n"
            "├───────────────┼───────────────┤\n"
            "│ Potassium     │ 4.2 mEq/L     │\n"
            "└───────────────┴───────────────┘\n"
        )
        violations_box = detect_ascii_tables_or_diagrams(box_table)
        self.assertGreater(len(violations_box), 0)
        self.assertTrue(any(v["type"] == "box_drawing_characters" for v in violations_box))

        # 3. ASCII tree diagram
        ascii_tree = (
            "Assessment:\n"
            "├─ Vital signs: Stable\n"
            "└─ Response: Good\n"
        )
        violations_tree = detect_ascii_tables_or_diagrams(ascii_tree)
        self.assertGreater(len(violations_tree), 0)
        self.assertTrue(any(v["type"] == "ascii_tree_diagram" for v in violations_tree))

        # 4. ASCII flowchart arrow in prose
        ascii_arrow = "Workflow: [Triage] ---> [Doctor Exam] ===> [Discharge]"
        violations_arrow = detect_ascii_tables_or_diagrams(ascii_arrow)
        self.assertGreater(len(violations_arrow), 0)
        self.assertTrue(any(v["type"] == "ascii_flowchart_arrow" for v in violations_arrow))

    def test_audit_document_formatting(self):
        """Test audit_document_formatting detects compliant vs non-compliant documents."""
        compliant_doc = """
# Summary
| Test | Result |
| :--- | :--- |
| HbA1c | 8.5% |

```mermaid
flowchart LR
    Node1["Start"] --> Node2["Finish"]
```
"""
        audit_pass = audit_document_formatting(compliant_doc)
        self.assertTrue(audit_pass["passed"])
        self.assertTrue(audit_pass["has_mermaid"])
        self.assertTrue(audit_pass["has_markdown_table"])

        non_compliant_doc = """
# Summary
+-------+--------+
| Test  | Result |
+-------+--------+
| HbA1c | 8.5%   |
+-------+--------+
"""
        audit_fail = audit_document_formatting(non_compliant_doc)
        self.assertFalse(audit_fail["passed"])
        self.assertGreater(audit_fail["violation_count"], 0)


if __name__ == "__main__":
    unittest.main()
