---
name: clinical-diagnostic-support
description: >-
  Generates ranked differential diagnoses with evidence justifications, pathophysiology links,
  and uncertainty safeguards for clinician and medical student consultation.
---

# Clinical Diagnostic Support (MedMate)

This skill assists doctors (Tier 1) and medical students (Tier 2) in generating structured differential diagnoses, ranking clinical hypotheses by likelihood, and identifying key discriminators.

---

## 1. Diagnostic Formulation Workflow

1. **Synthesize Clinical Problem List**: Summarize age, gender, cardinal symptoms, onset time, and key objective findings.
2. **Generate Broad Differential Diagnoses**: Formulate a comprehensive list of plausible etiologies covering:
   - Most common/probable conditions
   - Life-threatening "Must Not Miss" conditions (e.g., Aortic Dissection, PE, STEMI, Tension Pneumothorax)
3. **Rank by Clinical Likelihood**:
   - Primary Suspected Diagnosis (Most Likely)
   - Secondary / Alternative Differential Diagnoses
4. **Provide Grounded Justification**: Correlate each diagnosis with positive and negative findings present in the patient record.
5. **Express Clinical Uncertainty**: Maintain assistive tone; state remaining diagnostic ambiguity and suggest definitive confirmatory tests.

---

## 2. Output Format

```text
Problem Representation:
A 58-year-old male with poorly controlled diabetes presenting with acute altered mental status, Kussmaul respiration, severe dehydration, hyperglycemia (480 mg/dL), and High Anion Gap Metabolic Acidosis (AG 23).

Differential Diagnoses:

1. Diabetic Ketoacidosis (DKA) with Prerenal AKI [Most Likely]
   - Supporting Evidence: Marked hyperglycemia (480 mg/dL), metabolic acidosis (pH 7.15, HCO3 9), positive urine ketones (4+), AG 23, Kussmaul breathing.
   - Discriminator: Differentiated from HHS by significant acidosis and strong ketonemia.

2. Hyperosmolar Hyperglycemic State (HHS) [Possible / Overlap]
   - Supporting Evidence: Marked hyperglycemia, severe dehydration, altered sensorium.
   - Counter-Evidence: Severe metabolic acidosis and high anion gap favor DKA/mixed picture.

3. Lactic Acidosis secondary to Sepsis / Dehydration [Secondary Factor]
   - Supporting Evidence: Leukocytosis, dehydration.
   - Confirmatory Test: Serum Lactate level, Blood cultures.

Recommended Next Diagnostic Steps:
- Serial Electrolytes, venous blood gas, and beta-hydroxybutyrate.
- Urine analysis and chest X-ray to identify precipitating infectious source.
```
