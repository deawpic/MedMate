---
name: clinical-qa
description: >-
  Strict grounded question-answering on clinical records and RAG documents. Enforces
  zero-hallucination policies and explicit "Not available in the provided text" fallbacks.
---

# Grounded Clinical Question Answering (Clinical QA)

This skill extracts precise medical facts from patient charts, case studies in `./RAG/`, and clinical guidelines without extrapolating beyond documented evidence.

---

## 1. Grounding Rules & Anti-Hallucination Policy

1. **Strict Context Limitation**: Answer questions using ONLY the explicitly stated data in the provided clinical text.
2. **No Extrapolation**: If the patient's allergy history, medication dosage, or lab value is not explicitly documented, NEVER guess.
3. **Standard Fallback Response**: When requested information is absent, respond with:
   **"Not available in the provided text."** (หรือ *"ไม่มีข้อมูลดังกล่าวระบุในเอกสารเวชระเบียนที่ให้มา"*)
4. **Cite Direct Text Evidence**: Whenever answering a factual query, provide exact quotation or clear reference to the source note.

---

## 2. Output Format

```text
Answer: 
ผู้ป่วยได้รับยา Amoxicillin/Clavulanate 1.2 g ทางหลอดเลือดดำ (IV) 15 นาทีก่อนเกิดอาการหายใจไม่ออกและผื่นลมพิษเฉียบพลัน

Evidence:
- "Case Study 08: 15 minutes post-infusion of IV Amoxicillin/Clavulanate 1.2 g, patient developed acute generalized urticaria, facial angioedema, and inspiratory stridor."
```

If the requested information is absent:
```text
Answer: 
Not available in the provided text. (ไม่มีข้อมูลประวัติการแพ้ยาในอดีตระบุไว้ในเอกสาร)
```
