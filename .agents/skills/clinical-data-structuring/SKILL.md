---
name: clinical-data-structuring
description: >-
  Converts unstructured Thai and English clinical text, patient histories, and lab records
  into structured, machine-readable JSON format with explicit fields (symptoms, diagnoses,
  medications, procedures, lab_results, and timeline).
---

# Clinical Data Structuring (MedMate)

This skill converts raw clinical text, admission notes, doctor notes, and lab reports into structured JSON format for downstream processing in MedMate, MCP tool routing, and evaluation benchmarks.

---

## 1. Core Extraction Categories

Extract and categorize only explicitly stated clinical elements into the following keys:

- `symptoms`: Patient-reported complaints, signs, and symptoms (e.g., "เจ็บแน่นหน้าอกร้าวไปกราม", "Dyspnea on exertion").
- `diagnoses`: Explicitly documented diagnoses, conditions, or clinical impressions (e.g., "Inferior STEMI", "Type 2 Diabetes Mellitus").
- `medications`: All medications with dosage, frequency, and route when available (e.g., "Aspirin 300 mg po stat", "Regular Insulin IV infusion").
- `procedures`: Diagnostic procedures, surgeries, or clinical interventions (e.g., "Primary PCI", "Intubation", "Coronary Angiography").
- `lab_results`: Laboratory tests with quantitative values, units, and reference status (e.g., `{"test": "Serum Creatinine", "value": 2.4, "unit": "mg/dL", "status": "high"}`).
- `timeline`: Chronological sequence of clinical events with relative or explicit timestamps.

If a category has no data in the source text, return an empty array `[]`.

---

## 2. Extraction & Processing Rules

1. **Strict Text Fidelity**: Extract values exactly as they appear in the original source (Thai or English) without unauthorized paraphrasing or translation.
2. **No Hallucination or Extrapolation**: Do not infer unmentioned medications or diagnoses. If a lab value is missing, do not guess.
3. **De-duplication**: If an entity is mentioned multiple times, preserve only unique, distinct clinical elements unless status changes over time.
4. **Handling Uncertainty**: If an item is tentative or provisional, flag it explicitly (e.g., `"provisional": true`).

---

## 3. Output Formats (Table vs. JSON)

### 3.1 Presentation Mode (Default for User Responses): Markdown Table
เมื่อตอบหรือสรุปข้อมูลเวชระเบียนแก่ผู้ใช้ บุคลากรทางการแพทย์ หรือนักศึกษาแพทย์ ให้แสดงผลในรูปแบบ **ตาราง Markdown (Table)** เสมอ เพื่อความชัดเจน อ่านง่าย และเป็นระเบียบ:

| หมวดหมู่ (Category) | รายการ / รายละเอียด (Clinical Elements) | ข้อมูลสนับสนุน / ค่าสถานะ (Status / Details) |
| :--- | :--- | :--- |
| **อาการสำคัญและอาการแสดง (Symptoms)** | เจ็บแน่นหน้าอกร้าวไปกราม, เหงื่อแตกท่วมตัว, คลื่นไส้อาเจียน | เริ่มเป็น 2 ชั่วโมงก่อนมา รพ. |
| **การวินิจฉัย (Diagnoses)** | Acute Inferior STEMI, Right Ventricular Infarction | Killip Class IV / Cardiogenic Shock |
| **รายการยา (Medications)** | Aspirin 300 mg po stat, Ticagrelor 180 mg po stat | ได้รับการบริหารยาที่ห้องฉุกเฉิน |
| **หัตถการ (Procedures)** | Emergency EKG 12 leads + V4R, Urgent Primary PCI | ส่งห้องปฏิบัติการสวนหัวใจเร่งด่วน |
| **ผลแล็บ / สัญญาณชีพ (Labs & Vitals)** | Troponin T: 1450 ng/L (Elevated), BP: 78/48 mmHg | ความดันโลหิตต่ำรุนแรง (Hypotension) |
| **เส้นเวลาทางคลินิก (Timeline)** | 2 ชม. ก่อนมา: เจ็บแน่นหน้าอกรุนแรง<br>แรกรับ ER: BP 78/48, EKG ST-elevation | Door-to-Needle / Door-to-Balloon window |

> ⚠️ **Strict Ban on ASCII Text Tables & Diagrams:** ห้ามนำเสนอข้อมูลเวชระเบียนด้วยตัวอักษรตีกรอบ ASCII (`+---+`, `+===+`, `┌─┬─┐`) หรือเว้นวรรคช่องไฟแบบ plain text pseudo-table เด็ดขาด ทั้งในคำตอบสดและการบันทึกไฟล์ลงใน `./output/` (Rule 2.4, 2.6, 2.7)

### 3.2 Programmatic / JSON Schema Mode (สำหรับระบบ API หรือการประเมินผล Evaluator)
หากผู้ใช้ระบุเจาะจงว่าต้องการ raw JSON ให้จัดรูปแบบตามสคีมา:

```json
{
  "symptoms": [
    "เจ็บแน่นหน้าอกร้าวไปกราม 2 ชั่วโมงก่อนมา รพ.",
    "เหงื่อแตกท่วมตัว",
    "คลื่นไส้ อาเจียน"
  ],
  "diagnoses": [
    "Acute Inferior STEMI",
    "Right Ventricular Infarction",
    "Killip Class IV / Cardiogenic Shock"
  ],
  "medications": [
    {
      "name": "Aspirin",
      "dose": "300 mg",
      "route": "oral",
      "timing": "stat"
    },
    {
      "name": "Ticagrelor",
      "dose": "180 mg",
      "route": "oral",
      "timing": "stat"
    }
  ],
  "procedures": [
    "Emergency EKG 12 leads + Right-sided leads (V4R)",
    "Urgent Primary PCI"
  ],
  "lab_results": [
    {
      "test": "Troponin T",
      "value": "1450",
      "unit": "ng/L",
      "status": "elevated"
    },
    {
      "test": "Serum Potassium",
      "value": "4.2",
      "unit": "mEq/L",
      "status": "normal"
    }
  ],
  "timeline": [
    {
      "time": "2 hours prior to admission",
      "event": "Sudden onset of severe crushing retrosternal chest pain"
    },
    {
      "time": "At ER arrival",
      "event": "BP 78/48 mmHg, HR 52 bpm, EKG showed ST-elevation in II, III, aVF, V4R"
    }
  ]
}
```

---

## 4. Constraints & Safety Gates

- **Output Constraint**: Keep output strictly in valid JSON format without extraneous conversational filler unless requested.
- **Privacy First**: Ensure all personal identifiers (names, HN, phone numbers) are masked according to `gdpr-data-handling`.
