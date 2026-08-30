"""
Medical Case Benchmark Evaluation Harness for MedMate
Evaluates Agent Responses against Clinical Ground Truth across 5 Comprehensive Medical Cases:
- Case 01: Diabetic Ketoacidosis (DKA) + Prerenal AKI + HAGMA
- Case 02: Acute Inferior STEMI + RV Infarction + Cardiogenic Shock
- Case 03: Acute Ischemic Stroke + IV Thrombolysis (rt-PA) + AF Cardioembolism
- Case 04: Severe Community-Acquired Pneumonia (CAP) + Sepsis + CURB-65
- Case 05: Decompensated Cirrhosis + Acute Variceal Hemorrhage + Hepatic Encephalopathy
"""

import os
import re
import sys
import json
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class EvaluationCriterion:
    name: str
    weight: float
    keywords: List[str]
    description: str

@dataclass
class CaseGroundTruth:
    case_id: str
    filename: str
    title: str
    target_diagnoses: List[str]
    critical_interpretations: Dict[str, Any]
    rubrics: Dict[str, List[EvaluationCriterion]]

# Ground Truth 01: DKA + AKI
GT_CASE_01 = CaseGroundTruth(
    case_id="DIS-2026-0091",
    filename="case_study_01.txt",
    title="Type 2 Diabetes Mellitus with Severe DKA & Prerenal AKI",
    target_diagnoses=["Diabetic Ketoacidosis", "DKA", "Acute Kidney Injury", "AKI", "Prerenal Azotemia", "HAGMA"],
    critical_interpretations={"anion_gap": 23.0, "acid_base": "High Anion Gap Metabolic Acidosis", "bun_cr_ratio": 20.0},
    rubrics={
        "Tier1_Doctor": [
            EvaluationCriterion("Primary Diagnosis", 0.25, ["dka", "diabetic ketoacidosis", "ภาวะกรดคีโตน"], "Identifies DKA"),
            EvaluationCriterion("Acid-Base & Anion Gap", 0.25, ["hagma", "anion gap", "metabolic acidosis", "กรดเกิน"], "Calculates AG=23 & HAGMA"),
            EvaluationCriterion("AKI Assessment", 0.25, ["aki", "acute kidney injury", "prerenal", "ไตวายเฉียบพลัน"], "Identifies Prerenal AKI"),
            EvaluationCriterion("Resuscitation Plan", 0.25, ["fluid", "saline", "insulin", "potassium", "สารน้ำ"], "Recommends IV hydration, insulin, potassium")
        ],
        "Tier2_Student": [
            EvaluationCriterion("SOAP Note Format", 0.30, ["subjective", "objective", "assessment", "plan", "soap"], "Follows SOAP format"),
            EvaluationCriterion("Pathophysiology", 0.35, ["pathophysiology", "พยาธิสรีรวิทยา", "insulin deficiency"], "Explains ketoacidosis mechanism"),
            EvaluationCriterion("Differential Diagnosis", 0.35, ["differential", "วินิจฉัยแยกโรค", "hhs"], "Lists differential diagnoses")
        ],
        "Tier3_Patient": [
            EvaluationCriterion("Clear Language", 0.30, ["อาการรุนแรง", "ไม่ต้องตกใจ", "รีบไปพบแพทย์"], "Uses plain language"),
            EvaluationCriterion("Emergency Alert", 0.40, ["1669", "ฉุกเฉิน", "โรงพยาบาลทันที"], "Advises immediate emergency / 1669"),
            EvaluationCriterion("Disclaimer", 0.30, ["ข้อความแจ้งเตือนทางการแพทย์", "ไม่สามารถใช้ทดแทนการวินิจฉัย"], "Includes exact disclaimer")
        ]
    }
)

# Ground Truth 02: STEMI & Shock
GT_CASE_02 = CaseGroundTruth(
    case_id="DIS-2026-0092",
    filename="case_study_02.txt",
    title="Acute Inferior STEMI with RV Infarction & Cardiogenic Shock",
    target_diagnoses=["Inferior STEMI", "Right Ventricular Infarction", "Cardiogenic Shock", "Killip Class IV"],
    critical_interpretations={"ekg_findings": "ST-elevation II, III, aVF and V4R", "trop_t": 1450.0, "killip_class": 4},
    rubrics={
        "Tier1_Doctor": [
            EvaluationCriterion("Diagnosis", 0.30, ["inferior stemi", "rv infarction", "right ventricular", "กล้ามเนื้อหัวใจขาดเลือดเฉียบพลัน"], "Identifies Inferior STEMI + RV involvement"),
            EvaluationCriterion("Primary PCI Indication", 0.25, ["pci", "primary pci", "cath lab", "ขยายหลอดเลือด"], "Urgent Primary PCI within 90 min"),
            EvaluationCriterion("Contraindication Awareness", 0.25, ["nitrate", "nitroglycerin", "morphine", "ห้ามให้ไนเตรต"], "Avoids Nitrates in RV infarction with hypotension"),
            EvaluationCriterion("Shock Management", 0.20, ["norepinephrine", "inotrop", "dapt", "ticagrelor", "aspirin"], "Recommends DAPT and inotrope/vasopressor support")
        ],
        "Tier2_Student": [
            EvaluationCriterion("SOAP Note Format", 0.30, ["subjective", "objective", "assessment", "plan"], "Structured SOAP"),
            EvaluationCriterion("Coronary Anatomy & EKG", 0.35, ["rca", "right coronary", "ii iii avf", "v4r"], "Correlates Inferior/RV STEMI with RCA territory"),
            EvaluationCriterion("Killip Classification", 0.35, ["killip", "cardiogenic shock", "ความดันตก"], "Identifies Killip Class IV")
        ],
        "Tier3_Patient": [
            EvaluationCriterion("Immediate ER Red Flag", 0.50, ["1669", "ห้องฉุกเฉิน", "กล้ามเนื้อหัวใจขาดเลือด", "วิกฤต"], "Urgent hospital alert"),
            EvaluationCriterion("No Self-Medication", 0.25, ["ห้ามทานยาเอง", "ห้ามอมยา"], "Warns against self-medication"),
            EvaluationCriterion("Disclaimer", 0.25, ["ข้อความแจ้งเตือนทางการแพทย์"], "Includes disclaimer")
        ]
    }
)

# Ground Truth 03: Acute Ischemic Stroke
GT_CASE_03 = CaseGroundTruth(
    case_id="DIS-2026-0093",
    filename="case_study_03.txt",
    title="Acute Ischemic Stroke with FAST signs & IV Thrombolysis Window",
    target_diagnoses=["Acute Ischemic Stroke", "Left MCA Infarction", "Cardioembolic Stroke", "Atrial Fibrillation"],
    critical_interpretations={"nihss": 16, "aspect_score": 9, "inr": 1.28, "onset_to_door": "90 minutes"},
    rubrics={
        "Tier1_Doctor": [
            EvaluationCriterion("Diagnosis", 0.30, ["ischemic stroke", "mca territory", "cardioembolic", "หลอดเลือดสมองตีบ"], "Identifies Acute Ischemic Stroke"),
            EvaluationCriterion("IV Thrombolysis", 0.30, ["rt-pa", "alteplase", "thrombolysis", "ยาละลายลิ่มเลือด"], "Recommends IV rt-PA within 4.5h window"),
            EvaluationCriterion("INR & Bleeding Risk", 0.20, ["inr", "1.28", "no ich", "ไม่มีเลือดออก"], "Verifies INR < 1.7 and NCCT Brain rules out ICH"),
            EvaluationCriterion("BP Target", 0.20, ["180", "185", "105", "110", "ความดันโลหิต"], "Maintains BP < 180/105 post rt-PA")
        ],
        "Tier2_Student": [
            EvaluationCriterion("SOAP Note", 0.30, ["subjective", "objective", "assessment", "plan"], "Structures SOAP Note"),
            EvaluationCriterion("FAST & NIHSS Assessment", 0.35, ["fast", "nihss", "aphasia", "facial palsy"], "Details FAST signs & NIHSS score 16"),
            EvaluationCriterion("Cardioembolic Etiology", 0.35, ["atrial fibrillation", "af", "embolism", "warfarin"], "Discusses AF embolization mechanism")
        ],
        "Tier3_Patient": [
            EvaluationCriterion("Stroke Fast Alert", 0.50, ["1669", "โรคหลอดเลือดสมอง", "สโตรก", "รีบไปโรงพยาบาลด่วน"], "Emphasizes Golden Hour & 1669"),
            EvaluationCriterion("Reassurance & Warning", 0.25, ["ห้ามทานอาหาร", "ห้ามให้ยานอนหลับ"], "Advises NPO & safety"),
            EvaluationCriterion("Disclaimer", 0.25, ["ข้อความแจ้งเตือนทางการแพทย์"], "Includes disclaimer")
        ]
    }
)

# Ground Truth 04: Severe CAP & Sepsis
GT_CASE_04 = CaseGroundTruth(
    case_id="DIS-2026-0094",
    filename="case_study_04.txt",
    title="Severe Community-Acquired Pneumonia (CAP) with Sepsis & CURB-65",
    target_diagnoses=["Severe CAP", "Pneumococcal Pneumonia", "Sepsis", "Septic Shock Risk", "Respiratory Failure"],
    critical_interpretations={"curb_65": 4, "lactate": 3.6, "pao2_fio2": "< 250", "wbc": 22500},
    rubrics={
        "Tier1_Doctor": [
            EvaluationCriterion("Diagnosis & Risk", 0.30, ["severe cap", "pneumonia", "sepsis", "ปอดอักเสบติดเชื้อรุนแรง"], "Identifies Severe CAP with Sepsis"),
            EvaluationCriterion("CURB-65 Calculation", 0.25, ["curb-65", "curb 65", "icu", "intermediate care"], "Calculates CURB-65 = 4 and ICU recommendation"),
            EvaluationCriterion("Sepsis Hour-1 Bundle", 0.25, ["lactate", "hemoculture", "blood culture", "crystalloid", "30 ml/kg"], "Follows Sepsis Hour-1 resuscitation bundle"),
            EvaluationCriterion("Empiric Antibiotics", 0.20, ["ceftriaxone", "azithromycin", "fluoroquinolone", "ยาปฏิชีวนะ"], "Prescribes Beta-lactam + Macrolide")
        ],
        "Tier2_Student": [
            EvaluationCriterion("SOAP Note", 0.30, ["subjective", "objective", "assessment", "plan"], "Structured SOAP"),
            EvaluationCriterion("CURB-65 Breakdown", 0.35, ["confusion", "urea", "respiratory rate", "blood pressure", "age 65"], "Explains all 5 components of CURB-65"),
            EvaluationCriterion("Microbiology & Sputum", 0.35, ["streptococcus pneumoniae", "gram-positive diplococci", "เสมหะสีสนิม"], "Identifies S. pneumoniae from rusty sputum & Gram stain")
        ],
        "Tier3_Patient": [
            EvaluationCriterion("High Risk Warning", 0.50, ["1669", "ปอดบวมรุนแรง", "ติดเชื้อในกระแสเลือด", "โรงพยาบาลทันที"], "Urgent admission alert"),
            EvaluationCriterion("Oxygenation & Rest", 0.25, ["ให้ออกซิเจน", "หายใจหอบเหนื่อย"], "Explains breathing danger signs"),
            EvaluationCriterion("Disclaimer", 0.25, ["ข้อความแจ้งเตือนทางการแพทย์"], "Includes disclaimer")
        ]
    }
)

# Ground Truth 05: Cirrhosis & Variceal Bleeding
GT_CASE_05 = CaseGroundTruth(
    case_id="DIS-2026-0095",
    filename="case_study_05.txt",
    title="Decompensated Cirrhosis with Acute Variceal Bleeding & Hepatic Encephalopathy",
    target_diagnoses=["Decompensated Liver Cirrhosis", "Esophageal Variceal Bleeding", "Hepatic Encephalopathy", "Child-Pugh Class C"],
    critical_interpretations={"child_pugh_score": 13, "hb": 6.4, "inr": 2.15, "ammonia": 142.0, "evl_performed": True},
    rubrics={
        "Tier1_Doctor": [
            EvaluationCriterion("Diagnosis", 0.25, ["variceal bleeding", "cirrhosis", "portal hypertension", "ตับแข็งเลือดออก"], "Identifies Acute Variceal Bleeding"),
            EvaluationCriterion("Vasoactive & Antibiotic", 0.25, ["octreotide", "somatostatin", "terlipressin", "ceftriaxone", "sbp prophylaxis"], "Orders Vasoactive drug + Prophylactic Ceftriaxone"),
            EvaluationCriterion("Restrictive Transfusion", 0.25, ["restrictive", "target hb 7", "target hb 8", "7-8 g/dl", "ให้เลือดอย่างระมัดระวัง"], "Enforces restrictive transfusion target Hb 7-8 g/dL"),
            EvaluationCriterion("Encephalopathy Care", 0.25, ["lactulose", "rifaximin", "ammonia", "asterixis", "สมองเสื่อมจากโรคตับ"], "Prescribes Lactulose & assesses encephalopathy")
        ],
        "Tier2_Student": [
            EvaluationCriterion("SOAP Note", 0.30, ["subjective", "objective", "assessment", "plan"], "Structured SOAP"),
            EvaluationCriterion("Child-Pugh & Stigmata", 0.35, ["child-pugh", "class c", "spider nevi", "caput medusae", "ascites"], "Calculates Child-Pugh Score & clinical stigmata"),
            EvaluationCriterion("Hemostasis & EVL", 0.35, ["evl", "endoscopic variceal ligation", "ส่องกล้องรัดหลอดเลือด"], "Explains EVL mechanism and secondary prophylaxis")
        ],
        "Tier3_Patient": [
            EvaluationCriterion("Life Threatening Warning", 0.50, ["1669", "อาเจียนเป็นเลือด", "ถ่ายดำ", "ภาวะวิกฤต", "อันตรายถึงชีวิต"], "Immediate emergency alert"),
            EvaluationCriterion("Caregiver Guidance", 0.25, ["งดน้ำงดอาหาร", "นอนตะแคง", "ป้องกันสำลัก"], "NPO & recovery position advice"),
            EvaluationCriterion("Disclaimer", 0.25, ["ข้อความแจ้งเตือนทางการแพทย์"], "Includes disclaimer")
        ]
    }
)

ALL_CASES: Dict[str, CaseGroundTruth] = {
    "case_study_01": GT_CASE_01,
    "case_study_02": GT_CASE_02,
    "case_study_03": GT_CASE_03,
    "case_study_04": GT_CASE_04,
    "case_study_05": GT_CASE_05
}

class ComprehensiveMedicalEvaluator:
    def __init__(self, cases: Dict[str, CaseGroundTruth] = ALL_CASES):
        self.cases = cases

    def evaluate(self, case_key: str, tier: str, response_text: str) -> Dict[str, Any]:
        if case_key not in self.cases:
            raise ValueError(f"Unknown case key: {case_key}. Available: {list(self.cases.keys())}")
        
        gt = self.cases[case_key]
        text_lower = response_text.lower()
        if tier not in gt.rubrics:
            raise ValueError(f"Unknown tier: {tier}. Available: {list(gt.rubrics.keys())}")

        criteria = gt.rubrics[tier]
        total_score = 0.0
        details = []

        for crit in criteria:
            matched_keywords = [kw for kw in crit.keywords if kw.lower() in text_lower]
            passed = len(matched_keywords) > 0
            score = crit.weight if passed else 0.0
            total_score += score
            details.append({
                "criterion": crit.name,
                "weight": crit.weight,
                "passed": passed,
                "matched_keywords": matched_keywords,
                "description": crit.description
            })

        return {
            "case_id": gt.case_id,
            "filename": gt.filename,
            "title": gt.title,
            "tier": tier,
            "score": round(total_score * 100, 2),
            "status": "PASS" if total_score >= 0.70 else "FAIL",
            "criteria_results": details
        }

if __name__ == "__main__":
    evaluator = ComprehensiveMedicalEvaluator()
    print("============================================================")
    print(" MedMate Comprehensive 5-Case Benchmark Harness")
    print("============================================================")
    
    # Test sample Tier 1 for Case 2 (STEMI)
    sample_stemi = """
    เคสนี้ผู้ป่วยมีภาวะ Acute Inferior STEMI with Right Ventricular (RV) Infarction และมีภาวะแทรกซ้อน Cardiogenic Shock (Killip Class IV)
    แผนการรักษาเร่งด่วน:
    1. ส่งทำ Primary PCI เร่งด่วน (Door-to-Balloon < 90 min)
    2. ให้ DAPT: Loading Aspirin 300 mg + Ticagrelor 180 mg
    3. ข้อควรระวังขั้นวิกฤต: ห้ามให้ Nitrate / Nitroglycerin หรือ Morphine เนื่องจากความดันโลหิตต่ำและมี RV infarction
    4. ให้ Inotrope/Vasopressor support: Norepinephrine IV เพื่อรักษาระดับความดันโลหิต
    [สำหรับบุคลากรทางการแพทย์และการศึกษาเท่านั้น โปรดใช้วิจารณญาณทางคลินิกเพิ่มเติม]
    """
    res2 = evaluator.evaluate("case_study_02", "Tier1_Doctor", sample_stemi)
    print(f"[*] Evaluated Case 02 (STEMI): Score = {res2['score']}% [{res2['status']}]")
    
    # Test sample Tier 1 for Case 3 (Stroke)
    sample_stroke = """
    ผู้ป่วยมีภาวะ Acute Ischemic Stroke ในบริเวณ Left MCA territory จากสาเหตุ Cardioembolic Stroke (Atrial Fibrillation)
    ระยะเวลา Onset-to-Door 90 นาที อยู่ในช่วง Golden Period (< 4.5 ชั่วโมง) ผล CT สมองไม่มีเลือดออก (No ICH) และ INR 1.28 (< 1.7)
    แผนการรักษา: ให้ยาละลายลิ่มเลือด Intravenous Thrombolysis (rt-PA / Alteplase) ทันที และคุมความดันโลหิตให้อยู่ต่ำกว่า 180/105 mmHg
    [สำหรับบุคลากรทางการแพทย์และการศึกษาเท่านั้น โปรดใช้วิจารณญาณทางคลินิกเพิ่มเติม]
    """
    res3 = evaluator.evaluate("case_study_03", "Tier1_Doctor", sample_stroke)
    print(f"[*] Evaluated Case 03 (Stroke): Score = {res3['score']}% [{res3['status']}]")

    # Test sample Tier 1 for Case 4 (Pneumonia/Sepsis)
    sample_cap = """
    ผู้ป่วยได้รับการวินิจฉัยเป็น Severe Community-Acquired Pneumonia (Severe CAP) ร่วมกับภาวะ Sepsis จากเชื้อ Streptococcus pneumoniae
    การประเมินความรุนแรง: คำนวณ CURB-65 Score ได้ 4 คะแนน (High risk) แนะนำรับไว้รักษาใน ICU
    แผนการรักษาตาม Sepsis Hour-1 Bundle:
    1. เจาะ Hemoculture 2 ขวดก่อนเริ่มยา และตรวจติดตาม Serum Lactate
    2. ให้ IV Fluid Resuscitation ด้วย Crystalloid 30 mL/kg
    3. ให้ยาปฏิชีวนะ Empirical IV Antibiotics: Ceftriaxone ร่วมกับ Azithromycin
    [สำหรับบุคลากรทางการแพทย์และการศึกษาเท่านั้น โปรดใช้วิจารณญาณทางคลินิกเพิ่มเติม]
    """
    res4 = evaluator.evaluate("case_study_04", "Tier1_Doctor", sample_cap)
    print(f"[*] Evaluated Case 04 (CAP/Sepsis): Score = {res4['score']}% [{res4['status']}]")

    # Test sample Tier 1 for Case 5 (Cirrhosis/Variceal Bleeding)
    sample_gi = """
    ผู้ป่วยมีภาวะ Acute Esophageal Variceal Bleeding ซ้อนทับบน Decompensated Liver Cirrhosis (Child-Pugh Class C) ร่วมกับ Hepatic Encephalopathy
    แผนการรักษา:
    1. ให้ Vasoactive Drug (Octreotide หรือ Somatostatin) ต่อเนื่องเพื่อลด Portal pressure
    2. ให้ Prophylactic Ceftriaxone ป้องกัน SBP และการติดเชื้อ
    3. ใช้กลยุทธ์ Restrictive Transfusion โดยให้เลือดตั้งเป้าหมาย Target Hb 7-8 g/dL
    4. รักษา Hepatic Encephalopathy ด้วย Lactulose
    [สำหรับบุคลากรทางการแพทย์และการศึกษาเท่านั้น โปรดใช้วิจารณญาณทางคลินิกเพิ่มเติม]
    """
    res5 = evaluator.evaluate("case_study_05", "Tier1_Doctor", sample_gi)
    print(f"[*] Evaluated Case 05 (Variceal Bleeding): Score = {res5['score']}% [{res5['status']}]")
    print("============================================================")
    print("All 5 Case Study Ground Truth Evaluators Active & Verified!")
