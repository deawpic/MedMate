---
name: gdpr-data-handling
description: >-
  Healthcare Data Privacy, Patient De-identification & GDPR/PDPA/HIPAA Compliance.
  Use when handling patient medical records, lab reports in RAG, de-identifying Protected Health
  Information (PHI), and enforcing clinical data governance.
---

# Healthcare Data Privacy & De-Identification Guard

This skill ensures that patient records, clinical notes, and lab data processed by **MedMate** strictly comply with healthcare data privacy laws (PDPA, HIPAA, GDPR).

---

## 1. PHI / PII De-Identification Rules (The Safe Harbor Standard)

Before transmitting or storing medical case notes, the following identifiers must be masked or anonymized:

| Data Element | Action | Example Transformation |
| :--- | :--- | :--- |
| **Patient Full Name** | Mask with Pseudo-ID | "นายสมชาย ใจดี" -> "[Patient Case #0091]" |
| **Hospital Number (HN / AN)** | Mask | "HN 65001234" -> "[HN-MASKED]" |
| **National ID / SSN** | Strip entirely | "1-1004-99999-99-9" -> "[ID-REDACTED]" |
| **Contact Info (Phone, Email)** | Strip entirely | "081-234-5678" -> "[PHONE-REDACTED]" |
| **Exact Dates (DOB, Admission)** | Keep only relative intervals or year | "DOB: 14/05/1979" -> "Age: 45 years" |
| **Location / Addresses** | Generalize to province or department | "บ้านเลขที่ 12/3 กทม." -> "[Bangkok Area]" |

---

## 2. Clinical Data Sanitization Workflow

1. **Scan RAG Documents**: When reading raw clinical notes or case files from `./RAG/`, inspect for unmasked personal identifiers.
2. **On-the-Fly Redaction**: Strip direct identifiers from model context before generating external summaries.
3. **No External Egress of Raw PII**: Never send unanonymized patient details in API queries to external tools or web search.
4. **Consent & Storage**: Ensure cached logs in `~/.gemini` or telemetry traces do not contain raw patient identifiers.
