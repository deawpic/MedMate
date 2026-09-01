---
name: clinical-coding-icd
description: >-
  Maps clinical diagnoses and medical conditions to standardized ICD-10 and ICD-11 codes.
  Enforces strict evidence-based coding rules and structured JSON outputs to prevent code hallucinations.
---

# Clinical ICD Codification (MedMate)

This skill provides deterministic mapping of clinical diagnoses to international disease classification codes (ICD-10 / ICD-11), ensuring compliance with international medical documentation standards.

---

## 1. Codification Rules & Governance

1. **Explicit Diagnoses Only**: Code ONLY diagnoses, conditions, or clinical impressions explicitly documented by clinicians. **NEVER infer or code a definitive disease from symptoms alone** (e.g., do not code I21.9 Acute Myocardial Infarction if only "chest pain" is documented; instead code R07.9 Chest pain, unspecified).
2. **Maximum Specificity**: Assign the most specific valid ICD code supported by the clinical evidence (e.g., prefer `I21.19` STEMI of inferior wall over `I21.9` Acute MI unspecified).
3. **No Hallucinated Codes**: All assigned codes must be valid, standard ICD-10 / ICD-11 codes verified through `medical-terminologies-mcp` or authoritative WHO definitions.
4. **Primary vs. Secondary Mapping**: Clearly distinguish the Primary Diagnosis (Principal Condition) from Comorbidities / Secondary Conditions.

---

## 2. Common Clinical Benchmark Mappings (Ground Truth)

| Clinical Condition | ICD-10 Code | Description |
| :--- | :--- | :--- |
| Diabetic Ketoacidosis (Type 2 DM) | **E11.10** | Type 2 diabetes mellitus with ketoacidosis without coma |
| Acute Inferior STEMI | **I21.19** | ST elevation (STEMI) myocardial infarction involving other coronary artery of inferior wall |
| Acute Ischemic Stroke (Cerebral Infarction) | **I63.9** | Cerebral infarction, unspecified |
| Severe Community-Acquired Pneumonia | **J18.9** | Pneumonia, unspecified organism |
| Sepsis | **A41.9** | Sepsis, unspecified organism |
| Acute Kidney Injury | **N17.9** | Acute kidney failure, unspecified |
| Hepatic Encephalopathy in Cirrhosis | **K72.90 / K74.60** | Hepatic failure / Cirrhosis of liver |
| Severe Asthma with Status Asthmaticus | **J45.902** | Unspecified asthma with status asthmaticus |
| Acute Biliary Pancreatitis | **K85.10** | Biliary acute pancreatitis without necrosis or infection |
| Anaphylactic Shock due to Adverse Drug Reaction | **T88.6XXA** | Anaphylactic shock due to adverse effect of correct drug/medicament properly administered |

---

## 3. Output Format

Format result as a structured JSON object:

```json
{
  "primary_diagnosis": {
    "diagnosis": "Type 2 Diabetes Mellitus with Severe DKA",
    "icd10_code": "E11.10",
    "description": "Type 2 diabetes mellitus with ketoacidosis without coma",
    "justification": "Documented blood glucose 480 mg/dL, pH 7.15, positive urine ketones (4+), and serum anion gap 23."
  },
  "secondary_diagnoses": [
    {
      "diagnosis": "Acute Kidney Injury, Prerenal",
      "icd10_code": "N17.9",
      "description": "Acute kidney failure, unspecified",
      "justification": "BUN 56 mg/dL, Cr 2.8 mg/dL (BUN/Cr ratio = 20), severe dehydration."
    }
  ]
}
```
