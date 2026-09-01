---
name: clinical-entity-extraction
description: >-
  Extracts structured clinical named entities (Clinical NER) including diseases, symptoms,
  medications, procedures, and laboratory tests from Thai and English healthcare notes.
---

# Clinical Entity Extraction (Clinical NER)

This skill performs Named Entity Recognition (NER) on Thai and English clinical narratives, identifying and classifying medical concepts with high precision to support terminology mapping (LOINC, RxNorm, MeSH, ICD-11).

---

## 1. Entity Classification Types

Every extracted entity must strictly belong to one of these 5 classes:

1. **`DISEASE`**: Pathologies, clinical diagnoses, syndromes, or medical conditions (e.g., *Diabetic Ketoacidosis*, *Sepsis*, *ความดันโลหิตสูง*).
2. **`SYMPTOM`**: Signs, patient-reported symptoms, or physical exam findings (e.g., *Kussmaul breathing*, *Dyspnea*, *เจ็บหน้าอก*, *Crackles*).
3. **`MEDICATION`**: Drugs, intravenous fluids, vaccines, or pharmacological agents including dosage/route (e.g., *Norepinephrine*, *Ceftriaxone 2g IV*, *0.9% NSS*).
4. **`PROCEDURE`**: Interventions, imaging, surgical operations, or specialized clinical maneuvers (e.g., *Endotracheal Intubation*, *CT Brain Non-contrast*, *Primary PCI*).
5. **`LAB_RESULT`**: Lab tests, biomarkers, blood gas parameters, or diagnostic scores with values (e.g., *HbA1c 11.4%*, *Serum Creatinine 2.8 mg/dL*, *pH 7.15*).

---

## 2. Extraction Principles

- **Exact Text Spans**: Extract text as originally written (preserve Thai and English terms exactly).
- **No Hallucination / Inference**: Extract only explicitly mentioned entities; do not assume unmentioned conditions.
- **Deduplication**: Retain distinct concepts while avoiding unnecessary exact duplicates within the same context.

---

## 3. Output Format

Format as a structured JSON object:

```json
{
  "entities": [
    {
      "text": "Diabetic Ketoacidosis",
      "type": "DISEASE"
    },
    {
      "text": "Kussmaul breathing",
      "type": "SYMPTOM"
    },
    {
      "text": "Regular Insulin IV infusion",
      "type": "MEDICATION"
    },
    {
      "text": "Serum Anion Gap 23 mEq/L",
      "type": "LAB_RESULT"
    },
    {
      "text": "Urgent Endotracheal Intubation",
      "type": "PROCEDURE"
    }
  ]
}
```

---

## 4. Integration with MedMate

Extracted entities feed directly into:
- `medical-terminologies-mcp`: For automated LOINC, RxNorm, and MeSH lookup.
- `clinical-coding-icd`: For ICD-10/11 diagnostic codification.
- `medical_skill`: For clinical calculations (e.g., Anion Gap, KDIGO AKI).
