# 📋 Medical Agent Use Cases & Examination Examples (Usage_exam.md)

คุณสามารถคัดลอกตัวอย่างข้อความไปใช้ในหน้าต่างแชตของ Antigravity Desktop หรือส่งผ่านคำสั่ง `agy prompt` เพื่อทดสอบลูปการประมวลผลและการปรับบทบาท (Adaptive Tier Routing) พร้อมทดสอบคลังเคสศึกษาทั้ง 5 รายการใน `RAG/`:

---

## 🗂️ สารบัญเคสศึกษาจำลองในคลังความรู้ (`RAG/`)

| Case ID | ไฟล์เอกสาร | หัวข้อทางการแพทย์ | ประเด็นทดสอบสำคัญ |
| :--- | :--- | :--- | :--- |
| **DIS-2026-0091** | [`RAG/case_study_01.txt`](RAG/case_study_01.txt) | DKA + Prerenal AKI | Anion Gap = 23, HAGMA, Fluid Resuscitation, Insulin Protocol |
| **DIS-2026-0092** | [`RAG/case_study_02.txt`](RAG/case_study_02.txt) | Inferior STEMI + RV Infarction | Killip IV Shock, ห้ามให้ Nitrate, Emergency Primary PCI < 90 min |
| **DIS-2026-0093** | [`RAG/case_study_03.txt`](RAG/case_study_03.txt) | Acute Ischemic Stroke | FAST Signs, Golden Period Thrombolysis (rt-PA), AF Cardioembolism |
| **DIS-2026-0094** | [`RAG/case_study_04.txt`](RAG/case_study_04.txt) | Severe CAP + Sepsis | CURB-65 = 4, Sepsis Hour-1 Bundle, Empirical Antibiotics |
| **DIS-2026-0095** | [`RAG/case_study_05.txt`](RAG/case_study_05.txt) | Decompensated Cirrhosis + Variceal Bleeding | EVL Hemostasis, Restrictive Transfusion (Hb 7-8), Hepatic Encephalopathy |

---

## 📝 1. ตัวอย่างสำหรับ "นักศึกษาแพทย์ (นศพ.)" [Tier 2 - Medical Student Mode]
*เน้นคำถามเชิงวิชาการเพื่อทบทวนข้อสอบ (เช่น NL2 หรือการฝึกบนวอร์ด) AI จะตอบด้วยภาษาเขียนสไตล์อาจารย์แพทย์ อธิบายกลไกพยาธิสรีรวิทยา (Pathophysiology) อย่างละเอียดเป็นขั้นตอน และเน้นการสอนคิดวิเคราะห์*

*   **ตัวอย่างเคส 01 (DKA / SOAP Note):**
    > `[นศพ.ปี 5] รบกวนอ่านผลแล็บและบันทึกประวัติผู้ป่วยจากไฟล์ RAG/case_study_01.txt แล้วช่วยเรียบเรียงสรุปประเด็นหลักออกมาในรูปแบบโครงสร้าง SOAP Note เพื่อใช้ประกอบการรายงานเคส (Bedside Rounds) ครับ`
*   **ตัวอย่างเคส 02 (Inferior STEMI / EKG Correlation):**
    > `[นศพ.ปี 4] รบกวนอ่านเคส RAG/case_study_02.txt แล้วช่วยอธิบายความสัมพันธ์ระหว่าง EKG ที่พบ ST elevation ใน lead II, III, aVF, V4R กับหลอดเลือดหัวใจ Right Coronary Artery (RCA) พร้อมเหตุผลว่าทำไมเคสนี้จึงห้ามให้ Nitroglycerin`
*   **ตัวอย่างเคส 03 (Acute Stroke / NIHSS Assessment):**
    > `[นศพ.ปี 5] จากเคส RAG/case_study_03.txt ช่วยวิเคราะห์คะแนน NIHSS = 16 และประเมินเกณฑ์ Inclusion/Exclusion criteria ในการพิจารณาให้ Intravenous rt-PA (Alteplase) ในคนไข้รายนี้`
*   **ตัวอย่างเคส 04 (Severe CAP / CURB-65):**
    > `[นศพ.ปี 4] ช่วยแสดงวิธีคำนวณและแจกแจงเกณฑ์ CURB-65 Score จากข้อมูลผู้ป่วยใน RAG/case_study_04.txt พร้อมสรุปแนวทางการให้ยาปฏิชีวนะตาม Sepsis Hour-1 Bundle`
*   **ตัวอย่างเคส 05 (Cirrhosis / Variceal Bleeding):**
    > `[นศพ.ปี 6] ช่วยสรุปหลักการ Restrictive Blood Transfusion Strategy และกลไกของยา Somatostatin/Octreotide ในการลด Portal Pressure จากเคส RAG/case_study_05.txt`

---

## 🩺 2. ตัวอย่างสำหรับ "แพทย์ / บุคลากรคลินิก" [Tier 1 - Doctor Mode]
*เน้นคำถามระดับผู้เชี่ยวชาญ คุยแบบวิชาชีพสากล (Peer-to-Peer) รวดเร็ว กระชับ มีการทับศัพท์แพทย์ (Jargon) ปนไทย และดึงข้อมูลหลักฐานเชิงประจักษ์ (Evidence-based Medicine) ล่าสุดจาก PubMed*

*   **ตัวอย่างเคส 02 (Cardiology / Primary PCI):**
    > `[Doctor Context] เคส DIS-2026-0092 ใน RAG/case_study_02.txt ขอ Comprehensive Management Protocol สำหรับ Inferior STEMI with RV Infarction & Cardiogenic Shock ระหว่างรอ Cath Lab (DAPT loading, Vasopressor choice, and Inotropic support)`
*   **ตัวอย่างเคส 03 (Neurology / Thrombolysis & EVT):**
    > `[Doctor Context] เคส Acute Ischemic Stroke ใน RAG/case_study_03.txt ขอ Clinical Consensus เรื่อง Post-thrombolysis BP management และข้อบ่งชี้ในการส่งทำ Emergency Mechanical Thrombectomy (EVT) ในกรณี suspected Large Vessel Occlusion`
*   **ตัวอย่างเคส 05 (GI / Variceal Bleeding Consensus):**
    > `[Doctor Context] คนไข้ Cirrhosis Child-Pugh Class C ที่มี Acute Variceal Bleeding s/p EVL ใน RAG/case_study_05.txt ขอ Clinical Guidelines ล่าสุดเรื่องการให้ Prophylactic Ceftriaxone ร่วมกับการเริ่มยา Non-selective Beta-blockers (Carvedilol vs Propranolol) สำหรับ Secondary Prophylaxis`

---

## 👥 3. ตัวอย่างสำหรับ "คนทั่วไป / คนไข้" [Tier 3 - Patient Mode]
*เน้นภาษาที่เข้าใจง่าย อ่อนโยน เข้าอกเข้าใจ หลีกเลี่ยงคำย่อหรือศัพท์เฉพาะทาง ให้คำแนะนำดูแลตนเองเบื้องต้น สัญญาณอันตราย (Red Flags) และมีข้อความแจ้งเตือนทางการแพทย์ท้ายคำตอบเสมอ*

*   **ตัวอย่างข้อความสอบถามอาการฉุกเฉิน (Red Flag Trigger):**
    > `คุณพ่อมีอาการแน่นหน้าอกเหมือนโดนเหงื่อแตกท่วมตัว หายใจไม่อิ่มมา 2 ชั่วโมงแล้ว แบบนี้ควรทำอย่างไรดีครับ`
*   **พฤติกรรมคำตอบที่คาดหวัง:** AI จะตรวจจับว่าเป็นสัญญาณวิกฤตของกล้ามเนื้อหัวใจขาดเลือดเฉียบพลัน และขึ้นคำเตือนตัวหนาสีแดงให้โทรแจ้งสายด่วน **1669** หรือนำส่งห้องฉุกเฉินทันที ห้ามขับรถไปเอง และห้ามรับประทานยาใดๆ โดยพลการ
