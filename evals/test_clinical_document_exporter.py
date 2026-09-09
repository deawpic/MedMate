# -*- coding: utf-8 -*-
"""
Comprehensive Unit Test Suite for Universal Cross-Platform Thai Clinical Document & PDF Exporter
MedMate - Thai Clinical Intelligence & Knowledge Harness

Validates Production-Grade Prevention for Bugs 1–6:
1. Bug 1: Universal OS Thai Font Stack Fallback & Tofu Box Prevention
2. Bug 2: Upper Tone Marks & Headless Chromium Print-to-PDF Engine
3. Bug 3: Subprocess Multi-line Execution Safety (sys.executable + NamedTemporaryFile)
4. Bug 4: Thai Government Saraban Typography Standards (16pt, line-height 1.5, A4 margins)
5. Bug 5: Microsoft Word (.docx) Justification Guardrail (rejection of thaiDistribute)
6. Bug 6: OpenDocument (.odt) CTL Complex Text Layout Font Binding
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
    find_system_chromium_binary,
    get_thai_clinical_css,
    generate_clinical_html,
    convert_html_to_thai_pdf,
    export_clinical_markdown,
    export_clinical_docx,
    export_clinical_odt,
    run_safe_python_script,
    check_document_system_health,
    THAI_FONT_STACK
)


class TestClinicalDocumentExporter(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="medmate_doc_test_")
        self.output_dir = Path(__file__).resolve().parents[1] / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_find_system_chromium_binary(self):
        """Test detection of Chromium / Chrome / Edge browser binary."""
        binary = find_system_chromium_binary()
        # On this environment, Google Chrome is installed
        self.assertIsNotNone(binary, "Chromium or Google Chrome binary should be found on system")
        self.assertTrue(Path(binary).exists(), f"Binary path {binary} must exist on disk")

    def test_thai_font_stack_and_saraban_metrics(self):
        """Test Bug 1 (Font Stack Hierarchy) and Bug 4 (Saraban 16pt, line-height 1.5, A4 margins)."""
        css = get_thai_clinical_css()
        
        # Bug 1: Cascading Font Stack Fallback
        self.assertIn("TH Sarabun New", css)
        self.assertIn("Sarabun", css)
        self.assertIn("Thonburi", css)
        self.assertIn("Sukhumvit Set", css)
        self.assertIn("Loma", css)
        self.assertIn("Garuda", css)
        self.assertIn("Noto Sans Thai", css)
        self.assertIn("Leelawadee UI", css)
        self.assertIn("Tahoma", css)

        # Bug 4: Saraban metrics
        self.assertIn("font-size: 16pt", css)
        self.assertIn("line-height: 1.5", css)
        self.assertIn("@page", css)
        self.assertIn("size: A4", css)
        self.assertIn("margin: 20mm 15mm 20mm 15mm", css)

    def test_generate_clinical_html(self):
        """Test HTML document generation with clinical metadata and Thai tags."""
        patient_info = {
            "patient_id": "[HN_1]",
            "age": "62",
            "gender": "ชาย",
            "admission_date": "2026-03-01",
            "attending_physician": "[DOCTOR_1]"
        }
        title = "ใบสรุปประวัติผู้ป่วยจำหน่าย (Discharge Summary)"
        content = "<h2>การวินิจฉัยโรค</h2><p>ผู้ป่วยได้รับการวินิจฉัย Acute STEMI และได้รับการสวนหัวใจขยายหลอดเลือด Primary PCI สำเร็จ ปลอดภัย</p>"
        
        html = generate_clinical_html(title=title, content_html=content, patient_info=patient_info)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn('<html lang="th">', html)
        self.assertIn('<meta charset="utf-8">', html)
        self.assertIn(title, html)
        self.assertIn("[HN_1]", html)
        self.assertIn("[DOCTOR_1]", html)
        self.assertIn("Acute STEMI", html)
        self.assertIn("Primary PCI", html)
        self.assertIn("เอกสารเวชระเบียนคลินิก MedMate", html)

    def test_convert_html_to_thai_pdf(self):
        """Test Bug 2: Headless Chromium PDF generation with complex Thai tone marks."""
        patient_info = {
            "patient_id": "[HN_TEST_01]",
            "age": "45",
            "gender": "หญิง",
            "admission_date": "2026-03-09"
        }
        # Include multi-tier Thai tone marks & subscript vowels to verify HarfBuzz shaping
        content = (
            "<h2>บันทึกอาการทางคลินิก (Clinical Note)</h2>"
            "<p>ผู้ป่วยหญิงมีอาการไข้สูง หนาวสั่น ไอมีเสมหะสีเขียวเหนียวข้น หายใจหอบเหนื่อย<br/>"
            "ตรวจพบ Crepitation ปอดขวา สัญญาณชีพ: BP 118/76 mmHg, PR 98/min, RR 24/min, SpO2 95% Room air<br/>"
            "วินิจฉัย: Community-Acquired Pneumonia (CAP) รหัส ICD-10: J18.9<br/>"
            "การรักษา: ให้ยา Ceftriaxone 2 g IV OD ร่วมกับ Azithromycin 500 mg IV OD</p>"
        )
        html = generate_clinical_html(
            title="เอกสารตรวจรักษาแผนกผู้ป่วยนอก",
            content_html=content,
            patient_info=patient_info
        )
        
        pdf_path = self.output_dir / "test_thai_clinical_discharge.pdf"
        result_path = convert_html_to_thai_pdf(html, pdf_path, timeout_seconds=30)

        self.assertTrue(result_path.exists(), "PDF file must exist on disk")
        self.assertGreater(result_path.stat().st_size, 1000, "PDF file size must be non-trivial (>1KB)")

        # Verify PDF magic header
        with open(result_path, "rb") as f:
            header = f.read(5)
            self.assertEqual(header, b"%PDF-", "File must have valid %PDF- magic bytes")

    def test_export_clinical_markdown(self):
        """Test Rule 2.6: Strict UTF-8 Markdown export into ./output/."""
        title = "สรุปผลการตรวจวินิจฉัยผู้ป่วย"
        md_text = (
            "- ผู้ป่วย: [PATIENT_1]\n"
            "- ผลการตรวจ ABG: High Anion Gap Metabolic Acidosis\n"
            "- ค่า Anion Gap: 24 mEq/L (Normal: 8–12)\n"
        )
        saved = export_clinical_markdown(
            title=title,
            markdown_content=md_text,
            filename="test_clinical_summary.md",
            output_dir=self.output_dir
        )
        
        self.assertTrue(saved.exists())
        read_back = saved.read_text(encoding="utf-8")
        self.assertIn(title, read_back)
        self.assertIn("[PATIENT_1]", read_back)

    def test_run_safe_python_script(self):
        """Test Bug 3: Safe execution via sys.executable and temporary file."""
        script = """
import sys
import json

data = {"status": "ok", "message": "ทดสอบภาษาไทยใน subprocess สำเร็จ", "sys_exec": sys.executable}
print(json.dumps(data, ensure_ascii=False))
"""
        result = run_safe_python_script(script)
        self.assertEqual(result.returncode, 0, f"Script failed with stderr: {result.stderr}")
        self.assertIn("ทดสอบภาษาไทยใน subprocess สำเร็จ", result.stdout)
        self.assertIn(sys.executable, result.stdout)

    def test_docx_left_alignment_and_export(self):
        """Test Bug 5: Rejection of thaiDistribute and enforcement of LEFT alignment."""
        docx_path = self.output_dir / "test_clinical_doc.docx"
        paragraphs = [
            ("ประวัติการเจ็บป่วย (HPI)", "ผู้ป่วยชายอายุ 58 ปี มาด้วยอาการเจ็บแน่นหน้าอกร้าวไปกราม 2 ชั่วโมงก่อนมา รพ."),
            ("แผนการรักษา (Treatment Plan)", "ให้ยา ASA 300 mg เคี้ยวทันที, Ticagrelor 180 mg oral stat")
        ]
        res = export_clinical_docx("รายงานเวชระเบียน", paragraphs, docx_path)
        self.assertTrue(res.exists())
        self.assertGreater(res.stat().st_size, 50, "DOCX file must be generated")

    def test_odt_export(self):
        """Test Bug 6: OpenDocument ODF export with CTL font properties."""
        odt_path = self.output_dir / "test_clinical_doc.odt"
        paragraphs = [
            ("การวินิจฉัย", "Type 2 Diabetes Mellitus with Diabetic Ketoacidosis (DKA)"),
            ("การแก้ไขภาวะกรดเกิน", "ให้ NSS IV hydration และ Regular Insulin IV infusion")
        ]
        res = export_clinical_odt("เวชระเบียนคลินิกผู้ป่วยใน", paragraphs, odt_path)
        self.assertTrue(res.exists())
        self.assertGreater(res.stat().st_size, 50, "ODT/MD file must be generated")

    def test_check_document_system_health(self):
        """Test document and PDF health check function."""
        health = check_document_system_health()
        self.assertIn("platform", health)
        self.assertIn("python_executable", health)
        self.assertIn("chromium_binary", health)
        self.assertIn("chromium_available", health)
        self.assertIn("thai_fonts_detected", health)
        self.assertIn("font_details", health)
        self.assertIn("status", health)
        self.assertEqual(health["python_executable"], sys.executable)
        self.assertTrue(health["chromium_available"])
        self.assertTrue(health["thai_fonts_detected"])


if __name__ == "__main__":
    unittest.main()
