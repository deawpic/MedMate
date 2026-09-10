---
name: clinical-report-generation
description: >-
  Generates standardized clinical documentation, discharge summaries, emergency notes,
  and SOAP documentation saved into `./output/` in UTF-8 Markdown format with Math (LaTeX)
  and chemistry equation preservation, along with PDF/printing advisory guidance.
---

# Clinical Report Generation (MedMate)

This skill produces professional, standardized clinical documentation, SOAP notes, and discharge summaries in Thai and English, following medical record guidelines, MedMate's `./output/` file export protocol (Rule 2.6), and Markdown-Native clinical math/chemistry standards (Rule 2.8).

---

## 1. Standard Report Structure

1. **Patient Demographic & Admission Summary**: Masked ID/Age/Sex, Admission Date, Chief Complaint (using `gdpr-data-handling` de-identification).
2. **Clinical Summary & Course in Hospital**: HPI, initial physical findings, critical lab highlights.
3. **Principal Diagnosis & Secondary Conditions**: Stated with ICD-10 codification.
4. **Procedures & Significant Interventions**: Primary PCI, surgeries, mechanical ventilation.
5. **Clinical Calculations & Dynamics**: Preserved in native $\LaTeX$ / KaTeX format (e.g., Anion Gap, Winter's formula, Corrected Electrolytes).
6. **Discharge Medications & Instructions**: Exact drug names, doses, routes, and home care precautions.
7. **Follow-up & Red Flags Warning**: Clinic appointment date and immediate emergency warning signs.

---

## 2. File Export & Directory Protocol (Rule 2.6)

- **Target Directory**: Always save generated reports into `./output/<filename>.md` (e.g., `./output/discharge_summary_case01.md`).
- **Isolation Policy**: Never save export files in the workspace root or `RAG/` directory.
- **Encoding**: Strict UTF-8 without BOM (`encoding='utf-8'`) across all platforms (Linux, Windows, macOS).

---

## 3. Markdown-Native Architecture & Math/Chemistry Preservation (Rule 2.8)

MedMate operates on a **Markdown-Native Architecture**:
1. **Mermaid Diagrams & Markdown Tables Mandatory (Zero ASCII Art/Tables):**
   - **Diagrams & Flowcharts:** All clinical pathways, patient admission workflows, diagnostic algorithms, and care timelines MUST be represented using **Mermaid diagrams (````mermaid ... ````)** compliant with Unicode safety rules (ASCII node IDs, quoted labels, `<br/>` line breaks).
   - **Tables & Structured Data:** All clinical entity summaries, lab panels, medications, and comparative lists MUST be formatted as **GFM Markdown tables (`| ... |`)**.
   - **Strict ASCII Ban:** Never generate or save ASCII text diagrams (e.g., `+---+`, `--->`, `├──`, `└──`) or ASCII border tables (`+===+`, `+---+`, `┌─┬─┐`) in reports or chat responses.
2. **Preservation of Clinical Formulas**:
   - Math and chemical formulas (e.g., $[H^+] = 24 \times \frac{PCO_2}{[HCO_3^-]}$, $Na^+, K^+, \beta\text{-OHB}$) are kept in native $\LaTeX$ / KaTeX syntax to guarantee zero distortion.
3. **Zero Conversion Fragility**:
   - Eliminates unstable conversions to HTML/PDF/DOCX/ODT that suffer from multi-OS font bugs, Thai tone mark clipping, and broken nested list indentation.
4. **Built-in PDF & Printing Advisory in Chat Only (แสดงในแชทเท่านั้น ไม่บันทึกลงไฟล์):**
   - Whenever clinicians or users request a PDF or ask to print the document, provide the standardized guidance callout box in the **chat response ONLY**.
   - **Never append this guidance into the saved `.md` file in `./output/`**, keeping exported clinical documentation strictly focused on patient data without external software usage notes.

---

## 4. Subprocess Execution Safety (sys.executable + tempfile)

When executing any helper script or external process:
1. **Never hardcode `"python"` or `"python3"`**: Always use `sys.executable`.
2. **Never pass multi-line code via `-c "..."` inline strings**: Shell quoting and Windows batch shims (`python.bat`) fail on indentation and multiline text.
3. **Safe Subprocess Pattern**: Write the code to a `tempfile.NamedTemporaryFile(suffix='.py', encoding='utf-8')` and execute with `subprocess.run([sys.executable, temp_script.name], ...)`.

---

## 5. Python API Reference (`clinical_document_exporter.py`)

Helper functions are available under `medical_skill.clinical_document_exporter`:

```python
from medical_skill.clinical_document_exporter import (
    export_clinical_markdown,
    get_pdf_export_guidance,
    run_safe_python_script,
)

# Example: Generate Clinical Discharge Summary Markdown
saved_path = export_clinical_markdown(
    title="เอกสารสรุปประวัติผู้ป่วยจำหน่าย (Discharge Summary)",
    markdown_content="""
## 1. ข้อมูลผู้ป่วย
- ผู้ป่วย: [PATIENT_1] ชายไทย 52 ปี
- วินิจฉัย: Type 2 Diabetes Mellitus with DKA (ICD-10: E11.1)

## 2. ผลการตรวจทางคลินิก
- Arterial Blood Gas: pH 7.15, $HCO_3^- = 10\\text{ mEq/L}$
- Anion Gap: $132 - (98 + 10) = 24\\text{ mEq/L}$ (High AG Metabolic Acidosis)
""",
    filename="discharge_summary_patient_01.md",
    include_pdf_guidance=True
)
print(f"Report saved to: {saved_path}")
```
