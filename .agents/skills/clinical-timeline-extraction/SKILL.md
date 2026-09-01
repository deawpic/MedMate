---
name: clinical-timeline-extraction
description: >-
  Extracts, reconstructs, and chronologically orders clinical events, symptom onsets,
  door-to-intervention times, and clinical progression into structured JSON timelines.
---

# Clinical Timeline Extraction (MedMate)

This skill reconstructs complex medical histories into a strict chronological sequence of clinical events, crucial for managing time-critical emergencies (e.g., Stroke rt-PA window, STEMI Door-to-Balloon, Sepsis Hour-1 bundle).

---

## 1. Timeline Detection Scope

Identify and extract:
- **Onset of Symptoms**: Time elapsed from symptom appearance to arrival (e.g., "เจ็บหน้าอก 2 ชม. ก่อนมา", "Last known normal at 06:00").
- **Triage & Arrival Events**: ER door time, vital signs at admission.
- **Diagnostic Interventions**: Time of initial EKG, CT Brain scan, ABG sampling, troponin results.
- **Therapeutic Actions**: Intubation, thrombolytic bolus, PCI wire crossing, IV fluid resuscitation, antibiotic administration.
- **Clinical Deterioration / Response**: Changes in Glasgow Coma Scale (GCS), drop in blood pressure, relief of symptoms.

---

## 2. Chronological Ordering Rules

1. **Relative & Absolute Anchors**: Map relative times (e.g., "1 hour after admission") relative to primary time anchors.
2. **Explicit Sequence**: If exact time is unknown, order by clinical sequence and mark `"time": "unknown / prior to admission"`.
3. **Preserve Medical Accuracy**: Do not alter event descriptions or invent timestamps.

---

## 3. Output JSON Schema

```json
{
  "case_id": "DIS-2026-0093",
  "last_known_normal": "07:30",
  "door_time": "09:00 (Onset-to-Door: 90 minutes)",
  "timeline": [
    {
      "time": "07:30",
      "event": "Last known normal. Patient suddenly developed right-sided hemiplegia and global aphasia.",
      "category": "symptom_onset"
    },
    {
      "time": "09:00 (Door)",
      "event": "Arrival at ER. BP 175/95 mmHg, NIHSS score 16. Stroke Code activated.",
      "category": "admission"
    },
    {
      "time": "09:25",
      "event": "Emergency Non-contrast CT Brain completed: ASPECT score 9, no intracranial hemorrhage.",
      "category": "diagnostic"
    },
    {
      "time": "09:45",
      "event": "IV rt-PA (Alteplase) administered within 4.5-hour therapeutic window (Door-to-Needle: 45 min).",
      "category": "treatment"
    }
  ]
}
```
