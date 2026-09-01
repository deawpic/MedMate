---
name: clinical-report-generation
description: >-
  Generates standardized clinical documentation, discharge summaries, emergency notes,
  and SOAP documentation saved into the `./output/` directory with UTF-8 encoding.
---

# Clinical Report Generation (MedMate)

This skill produces professional, standardized clinical documentation and discharge summaries in Thai and English, following medical record guidelines and MedMate's `./output/` file export protocol.

---

## 1. Standard Report Structure

1. **Patient Demographic & Admission Summary**: Masked ID/Age/Sex, Admission Date, Chief Complaint.
2. **Clinical Summary & Course in Hospital**: HPI, initial physical findings, critical lab highlights.
3. **Principal Diagnosis & Secondary Conditions**: Stated with ICD-10 codification.
4. **Procedures & Significant Interventions**: Primary PCI, surgeries, mechanical ventilation.
5. **Discharge Medications & Instructions**: Exact drug names, doses, routes, and home care precautions.
6. **Follow-up & Red Flags Warning**: Clinic appointment date and immediate emergency warning signs.

---

## 2. File Export Protocol

- **Target Directory**: Always save generated reports into `./output/<filename>.md` (e.g., `./output/discharge_summary_case01.md`).
- **Encoding**: UTF-8 without BOM (`encoding='utf-8'`).
- **Privacy Compliance**: All personal identifiable information must be de-identified using `gdpr-data-handling`.
