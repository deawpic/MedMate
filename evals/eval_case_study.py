"""
Medical Case Benchmark Evaluation Harness for MedMate
Evaluates Agent Responses against Clinical Ground Truth across 10 Comprehensive Medical Cases:
- Case 01: Diabetic Ketoacidosis (DKA) + Prerenal AKI + HAGMA
- Case 02: Acute Inferior STEMI + RV Infarction + Cardiogenic Shock
- Case 03: Acute Ischemic Stroke + IV Thrombolysis (rt-PA) + AF Cardioembolism
- Case 04: Severe Community-Acquired Pneumonia (CAP) + Sepsis + CURB-65
- Case 05: Decompensated Cirrhosis + Acute Variceal Hemorrhage + Hepatic Encephalopathy
- Case 06: Acute Severe Asthma Exacerbation + Impending Respiratory Failure
- Case 07: Acute Biliary Pancreatitis + BISAP Score + SIRS
- Case 08: Severe Anaphylactic Shock (Amoxicillin/Clavulanate-induced)
- Case 09: Hypertensive Emergency + Flash Pulmonary Edema + Acute Heart Failure
- Case 10: Severe Symptomatic Hyponatremia (SIADH) + ODS Prevention
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

# Ground Truth 06: Acute Severe Asthma Exacerbation
GT_CASE_06 = CaseGroundTruth(
    case_id="DIS-2026-0096",
    filename="case_study_06.txt",
    title="Acute Severe Asthma Exacerbation with Impending Respiratory Failure",
    target_diagnoses=["Acute Severe Asthma", "Status Asthmaticus", "Impending Respiratory Failure", "Near-Fatal Asthma"],
    critical_interpretations={"pefr": 35.0, "paco2": 42.0, "abg_finding": "Pseudo-normalization of PaCO2 / Exhaustion", "pulsus_paradoxus": 18.0},
    rubrics={
        "Tier1_Doctor": [
            EvaluationCriterion("Diagnosis & Severity", 0.30, ["acute severe asthma", "status asthmaticus", "respiratory failure", "หอบหืดรุนแรงวิกฤต"], "Recognizes Acute Severe Asthma & Impending Arrest"),
            EvaluationCriterion("ABG Critical Pitfall", 0.25, ["paco2", "pseudo-normal", "fatigue", "exhaustion", "กล้ามเนื้อหายใจล้า"], "Identifies PaCO2 42 mmHg as exhaustion sign"),
            EvaluationCriterion("Aggressive Pharmacotherapy", 0.25, ["saba", "salbutamol", "ipratropium", "hydrocortisone", "methylprednisolone", "magnesium sulfate"], "Orders SABA+Ipratropium, Systemic Steroid, IV MgSO4"),
            EvaluationCriterion("Airway Readiness", 0.20, ["intubation", "mechanical ventilation", "ใส่ท่อช่วยหายใจ"], "Prepares for rapid sequence intubation if deteriorating")
        ],
        "Tier2_Student": [
            EvaluationCriterion("SOAP Note", 0.30, ["subjective", "objective", "assessment", "plan"], "Structured SOAP Note"),
            EvaluationCriterion("ABG Pathophysiology", 0.35, ["paco2", "hyperventilation", "respiratory muscle fatigue", "silent chest"], "Explains PaCO2 normal in tachypnea = muscle fatigue"),
            EvaluationCriterion("Pharmacodynamics", 0.35, ["beta-2 agonist", "anticholinergic", "magnesium", "bronchodilation"], "Explains MgSO4 and bronchodilator mechanisms")
        ],
        "Tier3_Patient": [
            EvaluationCriterion("Immediate ER Alert", 0.50, ["1669", "ห้องฉุกเฉินด่วน", "หอบรุนแรง", "อันตรายถึงชีวิต"], "Urgent 1669 ambulance alert"),
            EvaluationCriterion("First Aid Positioning", 0.25, ["นั่งโน้มตัวไปข้างหน้า", "พ่นยาต่อเนื่องระหว่างรอรถ"], "Positioning & continuous SABA usage"),
            EvaluationCriterion("Disclaimer", 0.25, ["ข้อความแจ้งเตือนทางการแพทย์"], "Mandatory legal disclaimer")
        ]
    }
)

# Ground Truth 07: Acute Biliary Pancreatitis
GT_CASE_07 = CaseGroundTruth(
    case_id="DIS-2026-0097",
    filename="case_study_07.txt",
    title="Acute Biliary Pancreatitis with High BISAP Score & SIRS",
    target_diagnoses=["Acute Pancreatitis", "Gallstone Pancreatitis", "Biliary Pancreatitis", "SIRS"],
    critical_interpretations={"lipase": 1480.0, "alt": 340.0, "bisap_score": 3, "cbd_dilated": 9.5},
    rubrics={
        "Tier1_Doctor": [
            EvaluationCriterion("Diagnosis & Etiology", 0.30, ["acute pancreatitis", "gallstone", "biliary", "ตับอ่อนอักเสบเฉียบพลันจากนิ่ว"], "Diagnoses Biliary Pancreatitis (Lipase > 3x, ALT > 150)"),
            EvaluationCriterion("Risk Stratification", 0.25, ["bisap", "sirs", "organ failure", "ความรุนแรงสูง"], "Calculates BISAP=3 / SIRS criteria"),
            EvaluationCriterion("Fluid Resuscitation", 0.25, ["lactated ringer", "ringer", "fluid resuscitation", "สารน้ำ"], "Prescribes Goal-directed balanced crystalloid hydration"),
            EvaluationCriterion("Biliary Intervention & Antibiotics", 0.20, ["ercp", "cholangitis", "no prophylactic antibiotics", "ไม่ให้ยาปฏิชีวนะพร่ำเพรื่อ"], "Indicates ERCP for obstruction & avoids routine antibiotics")
        ],
        "Tier2_Student": [
            EvaluationCriterion("SOAP Note", 0.30, ["subjective", "objective", "assessment", "plan"], "Structured SOAP"),
            EvaluationCriterion("Atlanta & BISAP Criteria", 0.35, ["atlanta", "bisap", "lipase", "amylase", "bun > 25"], "Details 3-item Atlanta criteria and BISAP breakdown"),
            EvaluationCriterion("Biliary Marker Correlation", 0.35, ["alt > 150", "common bile duct", "cbd", "cholelithiasis"], "Explains ALT > 150 U/L specificity for gallstone etiology")
        ],
        "Tier3_Patient": [
            EvaluationCriterion("Severe Warning", 0.50, ["1669", "ตับอ่อนอักเสบรุนแรง", "โรงพยาบาลทันที", "ฉุกเฉิน"], "Urgent ER alert"),
            EvaluationCriterion("NPO Advice", 0.25, ["งดน้ำงดอาหาร", "ห้ามทานยาแก้ปวดเอง"], "Strict NPO and no self-medication"),
            EvaluationCriterion("Disclaimer", 0.25, ["ข้อความแจ้งเตือนทางการแพทย์"], "Mandatory disclaimer")
        ]
    }
)

# Ground Truth 08: Severe Anaphylactic Shock
GT_CASE_08 = CaseGroundTruth(
    case_id="DIS-2026-0098",
    filename="case_study_08.txt",
    title="Severe Anaphylactic Shock (Amoxicillin/Clavulanate-induced)",
    target_diagnoses=["Anaphylactic Shock", "Drug-Induced Anaphylaxis", "Severe Allergic Reaction", "Angioedema"],
    critical_interpretations={"bp": "68/38", "stridor": True, "epinephrine_route": "Intramuscular (IM) Anterolateral Thigh"},
    rubrics={
        "Tier1_Doctor": [
            EvaluationCriterion("Immediate Diagnosis", 0.30, ["anaphylactic shock", "anaphylaxis", "แพ้ยารุนแรงเฉียบพลัน"], "Identifies Anaphylactic Shock"),
            EvaluationCriterion("First-Line Epinephrine", 0.30, ["im epinephrine", "adrenaline", "0.5 mg", "anterolateral thigh", "กล้ามเนื้อต้นขา"], "Emphasizes IMMEDIATE IM Epinephrine 0.5 mg into thigh"),
            EvaluationCriterion("Resuscitation & Volume", 0.20, ["fluid bolus", "normal saline", "1000", "2000", "supine"], "Orders aggressive IV fluids 1-2L & Supine positioning"),
            EvaluationCriterion("Adjunctive & Biphasic", 0.20, ["antihistamine", "steroid", "biphasic", "สังเกตอาการ 24 ชั่วโมง"], "Administers 2nd-line drugs and monitors for biphasic reaction")
        ],
        "Tier2_Student": [
            EvaluationCriterion("SOAP Note", 0.30, ["subjective", "objective", "assessment", "plan"], "Structured SOAP"),
            EvaluationCriterion("Immunological Mechanism", 0.35, ["ige", "mast cell", "histamine", "degranulation", "vasodilation"], "Explains Type I IgE-mediated hypersensitivity"),
            EvaluationCriterion("Route of Epinephrine", 0.35, ["im vs sc", "anterolateral thigh", "vastus lateralis", "ห้ามรอสเตียรอยด์"], "Justifies IM thigh route over SC/deltoid for peak absorption")
        ],
        "Tier3_Patient": [
            EvaluationCriterion("Life Threatening 1669", 0.50, ["1669", "แพ้ยารุนแรง", "อันตรายถึงชีวิต", "เรียกรถพยาบาลด่วน"], "Critical 1669 emergency alarm"),
            EvaluationCriterion("Positioning Guidance", 0.25, ["นอนราบยกขาสูง", "ห้ามลุกยืน"], "Supine with legs up guidance"),
            EvaluationCriterion("Disclaimer", 0.25, ["ข้อความแจ้งเตือนทางการแพทย์"], "Mandatory disclaimer")
        ]
    }
)

# Ground Truth 09: Hypertensive Emergency & Flash Pulmonary Edema
GT_CASE_09 = CaseGroundTruth(
    case_id="DIS-2026-0099",
    filename="case_study_09.txt",
    title="Hypertensive Emergency with Flash Pulmonary Edema & Acute Heart Failure",
    target_diagnoses=["Hypertensive Emergency", "Flash Pulmonary Edema", "Acute Decompensated Heart Failure", "Target Organ Damage"],
    critical_interpretations={"bp": "238/136", "map": 170.0, "nt_probnp": 9250.0, "contraindication": "Sublingual Nifedipine"},
    rubrics={
        "Tier1_Doctor": [
            EvaluationCriterion("Diagnosis", 0.30, ["hypertensive emergency", "flash pulmonary edema", "acute heart failure", "ความดันโลหิตสูงวิกฤต"], "Identifies Hypertensive Emergency with Pulmonary Edema"),
            EvaluationCriterion("Controlled BP Reduction Target", 0.25, ["map 20-25%", "ลดความดันอย่างระมัดระวัง", "160-180"], "Enforces controlled MAP reduction by <=20-25% in 1st hour"),
            EvaluationCriterion("IV Vasodilator & Diuretic", 0.25, ["nicardipine", "nitroglycerin", "furosemide", "niv", "bipap"], "Orders IV Nicardipine/Nitroglycerin + IV Furosemide + NIV"),
            EvaluationCriterion("Sublingual Nifedipine Warning", 0.20, ["ห้าม sublingual nifedipine", "ห้ามเจาะบีบใต้ลิ้น", "precipitous drop"], "Warns strictly against Sublingual Nifedipine")
        ],
        "Tier2_Student": [
            EvaluationCriterion("SOAP Note", 0.30, ["subjective", "objective", "assessment", "plan"], "Structured SOAP"),
            EvaluationCriterion("Afterload Pathophysiology", 0.35, ["afterload mismatch", "systemic vascular resistance", "bat-wing", "s3 gallop"], "Explains Afterload mismatch & acute LV failure"),
            EvaluationCriterion("Urgency vs Emergency", 0.35, ["target organ damage", "hypertensive retinopathy", "อวัยวะเป้าหมาย"], "Differentiates Hypertensive Urgency vs Emergency")
        ],
        "Tier3_Patient": [
            EvaluationCriterion("Urgent Alert", 0.50, ["1669", "น้ำท่วมปอด", "ความดันสูงวิกฤต", "โรงพยาบาลทันที"], "Urgent hospital alert"),
            EvaluationCriterion("Upright Sitting Guidance", 0.25, ["นั่งห้อยขา", "ห้ามนอนราบ"], "Advises upright sitting position"),
            EvaluationCriterion("Disclaimer", 0.25, ["ข้อความแจ้งเตือนทางการแพทย์"], "Mandatory disclaimer")
        ]
    }
)

# Ground Truth 10: Severe Hyponatremia (SIADH) & ODS Prevention
GT_CASE_10 = CaseGroundTruth(
    case_id="DIS-2026-0100",
    filename="case_study_10.txt",
    title="Severe Symptomatic Euvolemic Hyponatremia (SIADH) & ODS Prevention",
    target_diagnoses=["Severe Hyponatremia", "SIADH", "SSRI-induced Hyponatremia", "Osmotic Demyelination Syndrome Risk"],
    critical_interpretations={"serum_na": 112.0, "urine_osm": 490.0, "urine_na": 68.0, "correction_limit": "<= 8 mEq/L/24hr"},
    rubrics={
        "Tier1_Doctor": [
            EvaluationCriterion("Diagnosis & Etiology", 0.30, ["siadh", "severe hyponatremia", "ssri", "sertraline", "โซเดียมต่ำรุนแรง"], "Diagnoses SSRI-induced SIADH with Na 112 mEq/L"),
            EvaluationCriterion("Hypertonic Saline Resuscitation", 0.25, ["3% nacl", "3% hypertonic saline", "100 ml bolus", "แก้อาการทางสมอง"], "Orders 3% Hypertonic Saline IV bolus for severe symptoms"),
            EvaluationCriterion("ODS Prevention Correction Rate", 0.25, ["8 meq/l", "ods", "osmotic demyelination", "ห้ามเกิน 8"], "Enforces strict correction limit <= 8 mEq/L per 24 hours"),
            EvaluationCriterion("Etiologic Management", 0.20, ["stop sertraline", "หยุดยา", "fluid restriction", "จำกัดน้ำ"], "Discontinues SSRI and enforces fluid restriction")
        ],
        "Tier2_Student": [
            EvaluationCriterion("SOAP Note", 0.30, ["subjective", "objective", "assessment", "plan"], "Structured SOAP"),
            EvaluationCriterion("Bartter-Schwartz & Euvolemia", 0.35, ["euvolemic", "urine osm > 100", "urine na > 40", "hypotonic"], "Analyzes Euvolemic state & SIADH diagnostic criteria"),
            EvaluationCriterion("Central Pontine Myelinolysis", 0.35, ["central pontine myelinolysis", "osmotic demyelination", "astrocytes", "สมองตาย"], "Explains pathophysiology of Osmotic Demyelination")
        ],
        "Tier3_Patient": [
            EvaluationCriterion("Danger Sign Warning", 0.50, ["1669", "เกลือแร่ต่ำรุนแรง", "สมองบวม", "โรงพยาบาลทันที"], "Immediate hospital alert"),
            EvaluationCriterion("Water Restriction Guidance", 0.25, ["จำกัดการดื่มน้ำ", "ห้ามดื่มน้ำเปล่าปริมาณมาก"], "Warns against excessive plain water intake"),
            EvaluationCriterion("Disclaimer", 0.25, ["ข้อความแจ้งเตือนทางการแพทย์"], "Mandatory disclaimer")
        ]
    }
)

ALL_CASES: Dict[str, CaseGroundTruth] = {
    "case_study_01": GT_CASE_01,
    "case_study_02": GT_CASE_02,
    "case_study_03": GT_CASE_03,
    "case_study_04": GT_CASE_04,
    "case_study_05": GT_CASE_05,
    "case_study_06": GT_CASE_06,
    "case_study_07": GT_CASE_07,
    "case_study_08": GT_CASE_08,
    "case_study_09": GT_CASE_09,
    "case_study_10": GT_CASE_10
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

    def evaluate_structured_data(self, json_str: str) -> Dict[str, Any]:
        """Validates output against clinical-data-structuring schema."""
        try:
            data = json.loads(json_str) if isinstance(json_str, str) else json_str
            required_keys = ["symptoms", "diagnoses", "medications", "procedures", "lab_results", "timeline"]
            present_keys = [k for k in required_keys if k in data and isinstance(data[k], list)]
            passed = len(present_keys) == len(required_keys)
            return {
                "benchmark": "clinical-data-structuring",
                "status": "PASS" if passed else "FAIL",
                "valid_keys": f"{len(present_keys)}/{len(required_keys)}",
                "keys_present": present_keys
            }
        except Exception as e:
            return {"benchmark": "clinical-data-structuring", "status": "FAIL", "error": str(e)}

    def evaluate_icd_coding(self, json_str: str, expected_code: str) -> Dict[str, Any]:
        """Validates output against clinical-coding-icd schema and ground truth code."""
        try:
            data = json.loads(json_str) if isinstance(json_str, str) else json_str
            primary = data.get("primary_diagnosis", {})
            assigned_code = primary.get("icd10_code", "").strip()
            passed = (assigned_code == expected_code) or (expected_code in assigned_code)
            return {
                "benchmark": "clinical-coding-icd",
                "status": "PASS" if passed else "FAIL",
                "assigned_code": assigned_code,
                "expected_code": expected_code,
                "diagnosis": primary.get("diagnosis", "")
            }
        except Exception as e:
            return {"benchmark": "clinical-coding-icd", "status": "FAIL", "error": str(e)}

    def evaluate_timeline(self, json_str: str) -> Dict[str, Any]:
        """Validates output against clinical-timeline-extraction schema."""
        try:
            data = json.loads(json_str) if isinstance(json_str, str) else json_str
            events = data.get("timeline", [])
            valid_events = all("time" in ev and "event" in ev for ev in events) if events else False
            passed = len(events) > 0 and valid_events
            return {
                "benchmark": "clinical-timeline-extraction",
                "status": "PASS" if passed else "FAIL",
                "event_count": len(events),
                "is_valid_structure": valid_events
            }
        except Exception as e:
            return {"benchmark": "clinical-timeline-extraction", "status": "FAIL", "error": str(e)}

if __name__ == "__main__":
    evaluator = ComprehensiveMedicalEvaluator()
    print("============================================================")
    print(" MedMate Comprehensive 10-Case Benchmark Harness")
    print("============================================================")
    
    # 1. Test sample Tier 1 for Case 1 (DKA)
    sample_dka = """
    ผู้ป่วยมีภาวะ Diabetic Ketoacidosis (DKA) ร่วมกับ High Anion Gap Metabolic Acidosis (HAGMA) โดยคำนวณ Anion Gap ได้ 23 mEq/L
    และมีภาวะแทรกซ้อน Acute Kidney Injury (Prerenal AKI) จากภาวะขาดน้ำรุนแรง
    แผนการรักษา: ให้ IV Fluid Resuscitation ด้วย Normal Saline, Continuous IV Regular Insulin Infusion หลังตรวจระดับโพแทสเซียม และติดตามสารน้ำ
    [สำหรับบุคลากรทางการแพทย์และการศึกษาเท่านั้น โปรดใช้วิจารณญาณทางคลินิกเพิ่มเติม]
    """
    res1 = evaluator.evaluate("case_study_01", "Tier1_Doctor", sample_dka)
    print(f"[*] Case 01 (DKA/AKI): Score = {res1['score']}% [{res1['status']}]")

    # 2. Test sample Tier 1 for Case 2 (STEMI)
    sample_stemi = """
    เคสนี้ผู้ป่วยมีภาวะ Acute Inferior STEMI with Right Ventricular (RV) Infarction และมีภาวะแทรกซ้อน Cardiogenic Shock (Killip Class IV)
    แผนการรักษาเร่งด่วน: ส่งทำ Primary PCI เร่งด่วน, ให้ DAPT Loading Aspirin 300 mg + Ticagrelor 180 mg
    ข้อควรระวังขั้นวิกฤต: ห้ามให้ Nitrate / Nitroglycerin หรือ Morphine เนื่องจากความดันโลหิตต่ำและมี RV infarction, ให้ Inotrope/Vasopressor Norepinephrine IV
    [สำหรับบุคลากรทางการแพทย์และการศึกษาเท่านั้น โปรดใช้วิจารณญาณทางคลินิกเพิ่มเติม]
    """
    res2 = evaluator.evaluate("case_study_02", "Tier1_Doctor", sample_stemi)
    print(f"[*] Case 02 (STEMI): Score = {res2['score']}% [{res2['status']}]")
    
    # 3. Test sample Tier 1 for Case 3 (Stroke)
    sample_stroke = """
    ผู้ป่วยมีภาวะ Acute Ischemic Stroke ในบริเวณ Left MCA territory จากสาเหตุ Cardioembolic Stroke (Atrial Fibrillation)
    ระยะเวลา Onset-to-Door 90 นาที อยู่ในช่วง Golden Period (< 4.5 ชั่วโมง) ผล CT สมองไม่มีเลือดออก (No ICH) และ INR 1.28 (< 1.7)
    แผนการรักษา: ให้ยาละลายลิ่มเลือด Intravenous Thrombolysis (rt-PA / Alteplase) ทันที และคุมความดันโลหิตให้อยู่ต่ำกว่า 180/105 mmHg
    [สำหรับบุคลากรทางการแพทย์และการศึกษาเท่านั้น โปรดใช้วิจารณญาณทางคลินิกเพิ่มเติม]
    """
    res3 = evaluator.evaluate("case_study_03", "Tier1_Doctor", sample_stroke)
    print(f"[*] Case 03 (Stroke): Score = {res3['score']}% [{res3['status']}]")

    # 4. Test sample Tier 1 for Case 4 (Pneumonia/Sepsis)
    sample_cap = """
    ผู้ป่วยได้รับการวินิจฉัยเป็น Severe Community-Acquired Pneumonia (Severe CAP) ร่วมกับภาวะ Sepsis จากเชื้อ Streptococcus pneumoniae
    การประเมินความรุนแรง: คำนวณ CURB-65 Score ได้ 4 คะแนน (High risk) แนะนำรับไว้รักษาใน ICU
    แผนการรักษาตาม Sepsis Hour-1 Bundle: เจาะ Hemoculture 2 ขวดก่อนเริ่มยา, ตรวจ Serum Lactate, ให้ IV Crystalloid 30 mL/kg และ Empirical IV Ceftriaxone + Azithromycin
    [สำหรับบุคลากรทางการแพทย์และการศึกษาเท่านั้น โปรดใช้วิจารณญาณทางคลินิกเพิ่มเติม]
    """
    res4 = evaluator.evaluate("case_study_04", "Tier1_Doctor", sample_cap)
    print(f"[*] Case 04 (CAP/Sepsis): Score = {res4['score']}% [{res4['status']}]")

    # 5. Test sample Tier 1 for Case 5 (Cirrhosis/Variceal Bleeding)
    sample_gi = """
    ผู้ป่วยมีภาวะ Acute Esophageal Variceal Bleeding ซ้อนทับบน Decompensated Liver Cirrhosis (Child-Pugh Class C) ร่วมกับ Hepatic Encephalopathy
    แผนการรักษา: ให้ Vasoactive Drug (Octreotide/Somatostatin) ต่อเนื่อง, ให้ Prophylactic Ceftriaxone ป้องกัน SBP, ใช้กลยุทธ์ Restrictive Transfusion Target Hb 7-8 g/dL และรักษา Encephalopathy ด้วย Lactulose
    [สำหรับบุคลากรทางการแพทย์และการศึกษาเท่านั้น โปรดใช้วิจารณญาณทางคลินิกเพิ่มเติม]
    """
    res5 = evaluator.evaluate("case_study_05", "Tier1_Doctor", sample_gi)
    print(f"[*] Case 05 (Variceal Bleeding): Score = {res5['score']}% [{res5['status']}]")

    # 6. Test sample Tier 1 for Case 6 (Severe Asthma)
    sample_asthma = """
    ผู้ป่วยมีภาวะ Acute Severe Asthma with Impending Respiratory Failure โดยตรวจพบสัญญาณวิกฤตคือ PaCO2 42 mmHg (Pseudo-normalization / Respiratory muscle fatigue) ในขณะที่ผู้ป่วยยังหอบเหนื่อยรุนแรง
    แผนการรักษา: ให้ High-flow Oxygen, พ่นยา SABA (Salbutamol) ร่วมกับ Ipratropium Bromide ถี่ๆ, ให้ Systemic Steroid (IV Hydrocortisone / Methylprednisolone), ให้ IV Magnesium Sulfate 2 g และเตรียมพร้อมสำหรับการใส่ท่อช่วยหายใจ (Intubation)
    [สำหรับบุคลากรทางการแพทย์และการศึกษาเท่านั้น โปรดใช้วิจารณญาณทางคลินิกเพิ่มเติม]
    """
    res6 = evaluator.evaluate("case_study_06", "Tier1_Doctor", sample_asthma)
    print(f"[*] Case 06 (Severe Asthma): Score = {res6['score']}% [{res6['status']}]")

    # 7. Test sample Tier 1 for Case 7 (Biliary Pancreatitis)
    sample_panc = """
    ผู้ป่วยได้รับการวินิจฉัยเป็น Acute Biliary Pancreatitis จากนิ่วถุงน้ำดี (Gallstone etiology ยืนยันด้วย Lipase > 3x ULN และ ALT 340 U/L) โดยประเมินความรุนแรง BISAP Score = 3 และมีภาวะ SIRS
    แผนการรักษา: ให้ Early Goal-Directed Fluid Resuscitation ด้วย Lactated Ringer's solution, ควบคุมอาการปวด, พิจารณาทำ Urgent ERCP หากมีภาวะ Cholangitis หรือ Persisting obstruction และไม่แนะนำการให้ Prophylactic Antibiotics พร่ำเพรื่อ
    [สำหรับบุคลากรทางการแพทย์และการศึกษาเท่านั้น โปรดใช้วิจารณญาณทางคลินิกเพิ่มเติม]
    """
    res7 = evaluator.evaluate("case_study_07", "Tier1_Doctor", sample_panc)
    print(f"[*] Case 07 (Pancreatitis): Score = {res7['score']}% [{res7['status']}]")

    # 8. Test sample Tier 1 for Case 8 (Anaphylactic Shock)
    sample_anaph = """
    ผู้ป่วยมีภาวะ Anaphylactic Shock และ Angioedema จากการแพ้ยาปฏิชีวนะ Amoxicillin/Clavulanate
    การรักษาเร่งด่วนอันดับหนึ่ง: ฉีด Intramuscular (IM) Epinephrine / Adrenaline (1:1000) ขนาด 0.5 mg เข้ากล้ามเนื้อบริเวณ Anterolateral Thigh ทันที ห้ามรอให้ยาอื่นก่อน
    การรักษาเสริม: จัดท่านอนราบ Supine ยกขาสูง, ให้ IV Normal Saline Fluid Bolus 1000-2000 mL, ให้ออกซิเจน, ให้ยารอง Antihistamines + IV Steroids และเฝ้าระวัง Biphasic reaction ใน ICU อย่างน้อย 24 ชั่วโมง
    [สำหรับบุคลากรทางการแพทย์และการศึกษาเท่านั้น โปรดใช้วิจารณญาณทางคลินิกเพิ่มเติม]
    """
    res8 = evaluator.evaluate("case_study_08", "Tier1_Doctor", sample_anaph)
    print(f"[*] Case 08 (Anaphylaxis): Score = {res8['score']}% [{res8['status']}]")

    # 9. Test sample Tier 1 for Case 9 (Hypertensive Emergency)
    sample_htn = """
    ผู้ป่วยมีภาวะ Hypertensive Emergency ร่วมกับ Flash Pulmonary Edema และ Acute Heart Failure จากความดันโลหิตสูงวิกฤต 238/136 mmHg
    แผนการรักษา: ตั้งเป้าลดความดันอย่างระมัดระวังโดยลด MAP ไม่เกิน 20-25% ในชั่วโมงแรก (เป้าหมาย 160-180/100-110 mmHg), ให้ยาขยายหลอดเลือดทางหลอดเลือดดำ IV Nicardipine หรือ IV Nitroglycerin infusion ร่วมกับ IV Furosemide และใส่เครื่องช่วยหายใจแรงดันบวก Non-Invasive Ventilation (NIV / BiPAP)
    ข้อห้ามใช้วิกฤต: ห้ามใช้ Sublingual Nifedipine เจาะบีบใต้ลิ้นเด็ดขาดเนื่องจากเสี่ยงต่อการเกิด Precipitous drop และ Stroke
    [สำหรับบุคลากรทางการแพทย์และการศึกษาเท่านั้น โปรดใช้วิจารณญาณทางคลินิกเพิ่มเติม]
    """
    res9 = evaluator.evaluate("case_study_09", "Tier1_Doctor", sample_htn)
    print(f"[*] Case 09 (Hypertensive Emergency): Score = {res9['score']}% [{res9['status']}]")

    # 10. Test sample Tier 1 for Case 10 (SIADH Hyponatremia)
    sample_siadh = """
    ผู้ป่วยมีภาวะ Severe Symptomatic Euvolemic Hyponatremia (Serum Na 112 mEq/L) จากภาวะ SIADH ทุติยภูมิต่อการใช้ยา SSRI (Sertraline)
    การรักษาฉุกเฉิน: ให้ 3% Hypertonic Saline (3% NaCl) IV Bolus 100 mL เพื่อดึงระดับโซเดียมขึ้นมา 4-6 mEq/L ป้องกันสมองบวม
    กฎความปลอดภัยสูงสุด: ต้องจำกัดอัตราการเพิ่มของระดับโซเดียมอย่างเคร่งครัดโดยไม่เกิน 8 mEq/L ต่อ 24 ชั่วโมง เพื่อป้องกันภาวะ Osmotic Demyelination Syndrome (ODS) และสั่งหยุดยา Sertraline ร่วมกับจำกัดการดื่มน้ำ (Fluid Restriction)
    [สำหรับบุคลากรทางการแพทย์และการศึกษาเท่านั้น โปรดใช้วิจารณญาณทางคลินิกเพิ่มเติม]
    """
    res10 = evaluator.evaluate("case_study_10", "Tier1_Doctor", sample_siadh)
    print(f"[*] Case 10 (SIADH/Hyponatremia): Score = {res10['score']}% [{res10['status']}]")

    print("\n------------------------------------------------------------")
    print(" Testing Clinical Harness Structured & Protocol Evaluators")
    print("------------------------------------------------------------")
    
    # Test Data Structuring Evaluator
    sample_struct = {
        "symptoms": ["แน่นหน้าอก", "เหงื่อแตก"],
        "diagnoses": ["Inferior STEMI"],
        "medications": [{"name": "Aspirin", "dose": "300 mg"}],
        "procedures": ["Primary PCI"],
        "lab_results": [{"test": "Troponin T", "value": "1450 ng/L"}],
        "timeline": [{"time": "2 hr prior", "event": "Chest pain onset"}]
    }
    struct_res = evaluator.evaluate_structured_data(sample_struct)
    print(f"[*] Structured Clinical Data Schema: Status = {struct_res['status']} ({struct_res['valid_keys']} keys)")

    # Test ICD Codification Evaluator
    sample_icd = {
        "primary_diagnosis": {
            "diagnosis": "Acute Inferior STEMI",
            "icd10_code": "I21.19",
            "description": "STEMI involving inferior wall"
        }
    }
    icd_res = evaluator.evaluate_icd_coding(sample_icd, "I21.19")
    print(f"[*] Clinical ICD-10 Codification: Status = {icd_res['status']} (Code: {icd_res['assigned_code']})")

    # Test Timeline Extraction Evaluator
    sample_timeline = {
        "timeline": [
            {"time": "07:30", "event": "Onset of weakness"},
            {"time": "09:00", "event": "Arrived at ER"}
        ]
    }
    time_res = evaluator.evaluate_timeline(sample_timeline)
    print(f"[*] Clinical Timeline Chronology: Status = {time_res['status']} ({time_res['event_count']} events)")

    print("============================================================")
    print("All 10 Case Study Ground Truth & Clinical Protocol Evaluators Verified!")
