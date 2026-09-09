---
name: clinical-report-generation
description: >-
  Generates standardized clinical documentation, discharge summaries, emergency notes,
  and SOAP documentation saved into the `./output/` directory with UTF-8 encoding.
  Enforces multi-OS Thai typography standards (Bugs 1–6 prevention) for PDF, DOCX, ODT, and HTML exports.
---

# Clinical Report Generation (MedMate)

This skill produces professional, standardized clinical documentation and discharge summaries in Thai and English, following medical record guidelines, MedMate's `./output/` file export protocol (Rule 2.6), and cross-platform Thai document architecture standards (Rule 2.8 Bugs 1–6 prevention).

---

## 1. Standard Report Structure

1. **Patient Demographic & Admission Summary**: Masked ID/Age/Sex, Admission Date, Chief Complaint (using `gdpr-data-handling` de-identification).
2. **Clinical Summary & Course in Hospital**: HPI, initial physical findings, critical lab highlights.
3. **Principal Diagnosis & Secondary Conditions**: Stated with ICD-10 codification.
4. **Procedures & Significant Interventions**: Primary PCI, surgeries, mechanical ventilation.
5. **Discharge Medications & Instructions**: Exact drug names, doses, routes, and home care precautions.
6. **Follow-up & Red Flags Warning**: Clinic appointment date and immediate emergency warning signs.

---

## 2. File Export & Directory Protocol (Rule 2.6)

- **Target Directory**: Always save generated reports into `./output/<filename>.<ext>` (e.g., `./output/discharge_summary_case01.md`, `./output/discharge_summary_case01.pdf`).
- **Isolation Policy**: Never save export files in the workspace root or `RAG/` directory.
- **Encoding**: Strict UTF-8 without BOM (`encoding='utf-8'`) across all platforms (Linux, Windows, macOS).

---

## 3. Production-Grade Thai Typography & Document Architecture (Bugs 1–6)

All document exports (HTML, PDF, Word DOCX, OpenDocument ODT) must follow these 6 non-negotiable cross-platform standards:

### 3.1 Universal OS Font Stack Fallback (Bug 1 Prevention)
Never rely on a single Thai font face. Missing Thai glyphs in Western fonts cause "tofu" replacement boxes (`[ ]`). Always configure CSS font families in exact cascading priority:
```css
font-family: 'TH Sarabun New', 'Sarabun', 'Thonburi', 'Sukhumvit Set',
             'Loma', 'Garuda', 'Noto Sans Thai', 'Leelawadee UI', Tahoma, sans-serif;
```
- **Windows**: `Leelawadee UI`, `Tahoma`, or installed `TH Sarabun New`
- **macOS**: `Thonburi`, `Sukhumvit Set`
- **Linux / Docker**: `Loma`, `Garuda` (`fonts-thai-tlwg`), `Noto Sans Thai` (`fonts-noto-cjk`)

### 3.2 Tone Mark Preservation & Chromium Headless PDF (Bug 2 Prevention)
- **Flaw in Legacy Libraries**: Legacy engines (ReportLab, pyFPDF, WeasyPrint without HarfBuzz) fail at Thai vowel/tone mark stacking (ไม้เอก, ไม้โท, ไม้ตรี, ไม้จัตวา, สระอิ, สระอี, การันต์) and word wrapping.
- **Production Standard**: Always generate clean semantic HTML5 and convert to PDF via modern **Headless Chromium / Chrome / Edge**:
  ```bash
  google-chrome --headless=new --disable-gpu --no-sandbox \
    --disable-dev-shm-usage --user-data-dir=/tmp/profile \
    --no-pdf-header-footer --print-to-pdf=output.pdf input.html
  ```
  Chromium embeds HarfBuzz (OpenType complex text layout) and native ICU Thai dictionary word breaker, guaranteeing 100% correct glyph stacking and natural word breaks.

### 3.3 Subprocess & Multi-line Python Execution Safety (Bug 3 Prevention)
When executing document rendering or Python helper scripts:
1. **Never hardcode `"python"` or `"python3"`**: Always use `sys.executable` to preserve the active virtual environment.
2. **Never pass multi-line code via `-c "..."` inline strings**: Shell quoting and Windows batch shims (`python.bat`) fail on indentation and multiline text.
3. **Safe Subprocess Pattern**: Write the code to a `tempfile.NamedTemporaryFile(suffix='.py', encoding='utf-8')` and execute with `subprocess.run([sys.executable, temp_script.name], ...)`.

### 3.4 Thai Government Saraban Typography & Collision-Free Metrics (Bug 4 Prevention)
Thai characters have 4 vertical levels (subscript vowels, baseline consonants, upper vowels, and tone marks). Insufficient line-height causes vertical collisions:
- **Body Font Size**: `16pt` (`1.0rem` / `21.33px`).
- **Line Height**: Strict `1.45` to `1.5` (never default 1.1–1.2).
- **Page Setup (A4)**: Margins: Top 20mm, Bottom 20mm, Left 20mm, Right 15mm.
- **Headings**: H1: `20pt` Bold (line-height 1.3), H2: `18pt` Bold (line-height 1.35).

### 3.5 Microsoft Word (`.docx`) Justification Guardrail (Bug 5 Prevention)
- **Trap**: `w:jc w:val="thaiDistribute"` attempts character-level distribution instead of word-level distribution in Word without full Thai dictionary context, causing severe character stretching.
- **Production Standard**: Always set paragraph alignment to Left (`WD_ALIGN_PARAGRAPH.LEFT`) with line spacing `1.2`–`1.25` pt:
  ```python
  from docx.enum.text import WD_ALIGN_PARAGRAPH
  p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
  p.paragraph_format.line_spacing = 1.25
  ```

### 3.6 OpenDocument (`.odt`) Complex Text Layout (CTL) Font Binding (Bug 6 Prevention)
- **Trap**: Setting only `fontname="TH Sarabun New"` on LibreOffice/OpenOffice writes Western font properties (`style:font-name`), ignoring Complex Text Layout (`style:font-name-complex`). LibreOffice falls back to default Linux fonts.
- **Production Standard**: Always bind both Western and Complex Text Layout properties:
  ```python
  from odf.style import TextProperties
  text_props = TextProperties(
      fontname="TH Sarabun New",
      fontsize="16pt",
      fontnamecomplex="TH Sarabun New",
      fontsizecomplex="16pt"
  )
  ```

---

## 4. Python API Reference (`clinical_document_exporter.py`)

Helper functions are available under `medical_skill.clinical_document_exporter`:

```python
from medical_skill.clinical_document_exporter import (
    find_system_chromium_binary,
    generate_clinical_html,
    convert_html_to_thai_pdf,
    export_clinical_markdown,
    export_clinical_docx,
    export_clinical_odt,
    run_safe_python_script,
    check_document_system_health,
)

# Example: Generate HTML and PDF Discharge Summary
html = generate_clinical_html(
    title="เอกสารสรุปประวัติผู้ป่วยจำหน่าย (Discharge Summary)",
    patient_info={"hn": "[HN_1]", "age": "58", "gender": "ชาย", "adm_date": "2026-03-01"},
    content_html="<h2>การวินิจฉัยโรค</h2><p>ผู้ป่วยได้รับการวินิจฉัย Acute STEMI และทำ Primary PCI สำเร็จ</p>"
)

pdf_path = convert_html_to_thai_pdf(html, "./output/discharge_summary.pdf")
```
