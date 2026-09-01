---
name: gdpr-data-handling
description: >-
  Healthcare Data Privacy, Patient De-identification & GDPR/PDPA/HIPAA Compliance.
  Use when handling patient medical records, lab reports in RAG, de-identifying Protected Health
  Information (PHI), and enforcing clinical data governance with consistent indexed placeholders.
---

# Healthcare Data Privacy & De-Identification Guard

This skill ensures that patient records, clinical notes, and lab data processed by **MedMate** strictly comply with healthcare data privacy laws (PDPA, HIPAA Safe Harbor, GDPR) while preserving clinical utility.

---

## 1. PHI / PII Identification & De-Identification Rules

Before transmitting, analyzing, or storing medical case notes, detect and transform sensitive identifiers using **consistent indexed placeholders**:

| Sensitive Data Element | Action | Standard Placeholder Format | Example Transformation |
| :--- | :--- | :--- | :--- |
| **Patient Names** | Mask with Indexed Tag | `[PATIENT_1]`, `[PATIENT_2]` | "นายสมชาย ใจดี" -> `[PATIENT_1]` |
| **Healthcare Providers** | Mask with Role Tag | `[DOCTOR_1]`, `[NURSE_1]` | "พญ.วิภา สุขสม" -> `[DOCTOR_1]` |
| **Hospital / Medical Record Numbers (HN/AN)** | Mask with ID Tag | `[ID_1]`, `[HN_1]` | "HN 65001234" -> `[HN_1]` |
| **National ID / SSN / Passport** | Redact completely | `[ID_REDACTED]` | "1-1004-99999-99-9" -> `[ID_REDACTED]` |
| **Contact Details (Phone, Email)** | Redact completely | `[CONTACT_1]` | "081-234-5678" -> `[CONTACT_1]` |
| **Exact Dates (DOB, Admission)** | Convert to relative interval | `[DATE_1]` or Age | "14/05/1979" -> "Age 45" / `[DATE_1]` |
| **Specific Addresses / Clinics** | Generalize | `[LOCATION_1]` / `[ORG_1]` | "รพ.จุฬาฯ" -> `[ORG_1]` |

---

## 2. Generalization Principles (Preserving Clinical Utility)

1. **Age Generalization**:
   - Exact Birthdate -> Relative Age in years (e.g., "14/05/1940" -> "84 years old").
   - Extreme age -> General bracket (e.g., "94 years old" -> "90+ years old").
2. **Date Generalization**:
   - Specific calendar dates -> Relative intervals (e.g., "12/03/2026 at 08:00" -> "Day 1 of Admission" or `[DATE_1]`).
3. **Location Generalization**:
   - Precise house address -> Province / Region level (e.g., "123/45 ซ.สุขุมวิท 21 กทม." -> "Bangkok Metropolitan Area").
4. **Preserve Medical Facts 100%**:
   - Never alter or redact symptoms, diagnoses, vital signs, lab values, dosages, or clinical timelines.

---

## 3. Clinical Data Sanitization Workflow

1. **Scan RAG Documents**: When reading raw clinical notes or case files from `./RAG/`, inspect for unmasked personal identifiers.
2. **On-the-Fly Redaction**: Strip direct identifiers from model context before generating external summaries or calling external APIs.
3. **No External Egress of Raw PII**: Never send unanonymized patient details in API queries to external tools or web search.
4. **Consistency**: Ensure the same entity maps to the same placeholder throughout a single conversation context.
