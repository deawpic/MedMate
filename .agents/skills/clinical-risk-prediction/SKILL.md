---
name: clinical-risk-prediction
description: >-
  Assesses patient clinical severity, deterioration risk, and scores clinical risk stratifications
  (CURB-65, BISAP, Killip Classification, NIHSS, KDIGO) with grounded clinical justifications.
---

# Clinical Risk Prediction & Triage Scoring

This skill evaluates clinical stability, organ dysfunction, and stratifies patient risk into standardized categories (Low, Moderate, High/Critical) while validating evidence-based clinical scores.

---

## 1. Risk Stratification Levels

- **LOW RISK (Stable / Ambulatory)**: Normal vital signs, no red flags, isolated minor symptoms suitable for outpatient management.
- **MODERATE RISK (Subacute / Close Monitoring)**: Stable vitals with abnormal lab trends or comorbidities requiring hospital admission / telemetry.
- **HIGH / CRITICAL RISK (Emergency / ICU Level)**: Hemodynamic instability, impending respiratory failure, severe acidosis, acute organ failure, or positive red flags requiring immediate resuscitation.

---

## 2. Integrated Clinical Scoring Engines

| Clinical Domain | Scoring System | Interpretation |
| :--- | :--- | :--- |
| **Pneumonia** | **CURB-65** | 0-1: Outpatient, 2: Inpatient, 3-5: Severe (ICU consideration) |
| **STEMI / ACS** | **Killip Class** | I: No HF, II: S3/Crackles, III: Frank Pulmonary Edema, IV: Cardiogenic Shock |
| **Pancreatitis** | **BISAP Score** | $\ge 3$: High risk of severe acute pancreatitis & mortality |
| **Acute Stroke** | **NIHSS** | 1-4: Minor, 5-15: Moderate, 16-20: Moderate-Severe, 21-42: Severe |
| **Sepsis** | **qSOFA / SIRS** | qSOFA $\ge 2$: High risk of poor outcome, immediate sepsis bundle |
| **Renal Failure** | **KDIGO AKI Staging** | Stage 1 (mild) to Stage 3 (RRT / anuria) |

---

## 3. Output Format

```text
Risk Level: HIGH / CRITICAL

Primary Risk Scores:
- Killip Classification: Class IV (Cardiogenic Shock, SBP 78 mmHg)
- Immediate Mortality Risk: High

Key Deterioration Signals:
1. Profound hypotension (BP 78/48 mmHg) unresponsive to fluid challenge in RV infarction.
2. High-grade AV block / Bradycardia (HR 52 bpm).
3. Marked troponin elevation (>1450 ng/L).

Actionable Recommendations:
- Immediate Cath Lab activation for Primary PCI.
- Avoid all vasodilators (Nitrates, Morphine, ACEi).
- Initiate inotropic/vasopressor support (Norepinephrine) for cardiogenic shock.
```
