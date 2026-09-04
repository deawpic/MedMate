"""
MedMate Clinical Lexicon Master Seeder & Harvester
===================================================
Seeds the master clinical lexicon database (`medical_skill/data/clinical_lexicon.db`)
with over 300 curated clinical conditions, lab markers, brand-generic drug synonyms,
units, and auto-harvested clinical abbreviations from MedMate's case studies.

Usage:
    python3 medical_skill/scripts/seed_clinical_lexicon.py [--rebuild]
"""

import os
import re
import sys
import glob
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from medical_skill.clinical_normalizer import ClinicalNormalizer, ClinicalSafetyViolationError


# Curated Bootstrap Knowledge Dictionary (300+ entries)
CURATED_BOOTSTRAP_TERMS: List[Dict[str, Any]] = [
    # ==========================================
    # 1. CARDIOLOGY & VASCULAR
    # ==========================================
    {"raw_term": "stemi", "canonical_term": "stemi", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "st-elevation myocardial infarction", "canonical_term": "stemi", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "กล้ามเนื้อหัวใจขาดเลือดเฉียบพลันชนิด stemi", "canonical_term": "stemi", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "กล้ามเนื้อหัวใจขาดเลือดเฉียบพลัน", "canonical_term": "stemi", "category": "disease", "language": "th"},
    {"raw_term": "nstemi", "canonical_term": "nstemi", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "non-st-elevation myocardial infarction", "canonical_term": "nstemi", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "กล้ามเนื้อหัวใจขาดเลือดเฉียบพลันชนิด nstemi", "canonical_term": "nstemi", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "acs", "canonical_term": "acs", "category": "disease", "language": "en"},
    {"raw_term": "acute coronary syndrome", "canonical_term": "acs", "category": "disease", "language": "en"},
    {"raw_term": "กลุ่มอาการหลอดเลือดหัวใจตีบเฉียบพลัน", "canonical_term": "acs", "category": "disease", "language": "th"},
    {"raw_term": "mi", "canonical_term": "mi", "category": "disease", "language": "en"},
    {"raw_term": "myocardial infarction", "canonical_term": "mi", "category": "disease", "language": "en"},
    {"raw_term": "กล้ามเนื้อหัวใจตาย", "canonical_term": "mi", "category": "disease", "language": "th"},
    {"raw_term": "af", "canonical_term": "af", "category": "disease", "language": "en"},
    {"raw_term": "atrial fibrillation", "canonical_term": "af", "category": "disease", "language": "en"},
    {"raw_term": "หัวใจเต้นสั่นพริ้ว", "canonical_term": "af", "category": "disease", "language": "th"},
    {"raw_term": "หัวใจห้องบนสั่นพลิ้ว", "canonical_term": "af", "category": "disease", "language": "th"},
    {"raw_term": "hf", "canonical_term": "heart_failure", "category": "disease", "language": "en"},
    {"raw_term": "chf", "canonical_term": "heart_failure", "category": "disease", "language": "en"},
    {"raw_term": "heart failure", "canonical_term": "heart_failure", "category": "disease", "language": "en"},
    {"raw_term": "congestive heart failure", "canonical_term": "heart_failure", "category": "disease", "language": "en"},
    {"raw_term": "hfref", "canonical_term": "hfref", "category": "disease", "language": "en"},
    {"raw_term": "adhf", "canonical_term": "adhf", "category": "disease", "language": "en"},
    {"raw_term": "หัวใจล้มเหลว", "canonical_term": "heart_failure", "category": "disease", "language": "th"},
    {"raw_term": "ภาวะหัวใจวาย", "canonical_term": "heart_failure", "category": "disease", "language": "th"},
    {"raw_term": "ht", "canonical_term": "hypertension", "category": "disease", "language": "en"},
    {"raw_term": "htn", "canonical_term": "hypertension", "category": "disease", "language": "en"},
    {"raw_term": "hypertension", "canonical_term": "hypertension", "category": "disease", "language": "en"},
    {"raw_term": "essential hypertension", "canonical_term": "hypertension", "category": "disease", "language": "en"},
    {"raw_term": "ความดันโลหิตสูง", "canonical_term": "hypertension", "category": "disease", "language": "th"},
    {"raw_term": "ความดันสูง", "canonical_term": "hypertension", "category": "disease", "language": "th"},
    {"raw_term": "hypotension", "canonical_term": "hypotension", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "ความดันโลหิตต่ำ", "canonical_term": "hypotension", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "ความดันต่ำ", "canonical_term": "hypotension", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "cad", "canonical_term": "cad", "category": "disease", "language": "en"},
    {"raw_term": "coronary artery disease", "canonical_term": "cad", "category": "disease", "language": "en"},
    {"raw_term": "โรคหลอดเลือดหัวใจ", "canonical_term": "cad", "category": "disease", "language": "th"},
    {"raw_term": "vt", "canonical_term": "vt", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "ventricular tachycardia", "canonical_term": "vt", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "vf", "canonical_term": "vf", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "ventricular fibrillation", "canonical_term": "vf", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "tachycardia", "canonical_term": "tachycardia", "category": "symptom", "language": "en", "prevent_merge": True},
    {"raw_term": "หัวใจเต้นเร็ว", "canonical_term": "tachycardia", "category": "symptom", "language": "th", "prevent_merge": True},
    {"raw_term": "bradycardia", "canonical_term": "bradycardia", "category": "symptom", "language": "en", "prevent_merge": True},
    {"raw_term": "หัวใจเต้นช้า", "canonical_term": "bradycardia", "category": "symptom", "language": "th", "prevent_merge": True},

    # ==========================================
    # 2. ENDOCRINOLOGY & METABOLISM
    # ==========================================
    {"raw_term": "t1dm", "canonical_term": "t1dm", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "type 1 diabetes mellitus", "canonical_term": "t1dm", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "type 1 diabetes", "canonical_term": "t1dm", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "เบาหวานชนิดที่ 1", "canonical_term": "t1dm", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "t2dm", "canonical_term": "t2dm", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "type 2 diabetes mellitus", "canonical_term": "t2dm", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "type 2 diabetes", "canonical_term": "t2dm", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "เบาหวานชนิดที่ 2", "canonical_term": "t2dm", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "โรคเบาหวานชนิดที่ 2", "canonical_term": "t2dm", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "dm", "canonical_term": "diabetes", "category": "disease", "language": "en"},
    {"raw_term": "diabetes mellitus", "canonical_term": "diabetes", "category": "disease", "language": "en"},
    {"raw_term": "diabetes", "canonical_term": "diabetes", "category": "disease", "language": "en"},
    {"raw_term": "เบาหวาน", "canonical_term": "diabetes", "category": "disease", "language": "th"},
    {"raw_term": "โรคเบาหวาน", "canonical_term": "diabetes", "category": "disease", "language": "th"},
    {"raw_term": "dka", "canonical_term": "dka", "category": "disease", "language": "en"},
    {"raw_term": "diabetic ketoacidosis", "canonical_term": "dka", "category": "disease", "language": "en"},
    {"raw_term": "ภาวะกรดคีโตนจากเบาหวาน", "canonical_term": "dka", "category": "disease", "language": "th"},
    {"raw_term": "ภาวะกรดเกินในเลือดจากเบาหวาน", "canonical_term": "dka", "category": "disease", "language": "th"},
    {"raw_term": "hhs", "canonical_term": "hhs", "category": "disease", "language": "en"},
    {"raw_term": "hyperosmolar hyperglycemic state", "canonical_term": "hhs", "category": "disease", "language": "en"},
    {"raw_term": "hypoglycemia", "canonical_term": "hypoglycemia", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "น้ำตาลในเลือดต่ำ", "canonical_term": "hypoglycemia", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "น้ำตาลต่ำ", "canonical_term": "hypoglycemia", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "hyperglycemia", "canonical_term": "hyperglycemia", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "น้ำตาลในเลือดสูง", "canonical_term": "hyperglycemia", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "น้ำตาลสูง", "canonical_term": "hyperglycemia", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "dyslipidemia", "canonical_term": "dyslipidemia", "category": "disease", "language": "en"},
    {"raw_term": "dlp", "canonical_term": "dyslipidemia", "category": "disease", "language": "en"},
    {"raw_term": "ไขมันในเลือดสูง", "canonical_term": "dyslipidemia", "category": "disease", "language": "th"},
    {"raw_term": "ไขมันสูง", "canonical_term": "dyslipidemia", "category": "disease", "language": "th"},
    {"raw_term": "gout", "canonical_term": "gout", "category": "disease", "language": "en"},
    {"raw_term": "โรคเกาต์", "canonical_term": "gout", "category": "disease", "language": "th"},
    {"raw_term": "hyperuricemia", "canonical_term": "hyperuricemia", "category": "disease", "language": "en"},
    {"raw_term": "กรดยูริกสูง", "canonical_term": "hyperuricemia", "category": "disease", "language": "th"},
    {"raw_term": "hypothyroidism", "canonical_term": "hypothyroidism", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "hyperthyroidism", "canonical_term": "hyperthyroidism", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "ไทรอยด์เป็นพิษ", "canonical_term": "hyperthyroidism", "category": "disease", "language": "th", "prevent_merge": True},

    # ==========================================
    # 3. NEPHROLOGY, ELECTROLYTES & ACID-BASE
    # ==========================================
    {"raw_term": "aki", "canonical_term": "aki", "category": "disease", "language": "en"},
    {"raw_term": "acute kidney injury", "canonical_term": "aki", "category": "disease", "language": "en"},
    {"raw_term": "acute renal failure", "canonical_term": "aki", "category": "disease", "language": "en"},
    {"raw_term": "ไตวายเฉียบพลัน", "canonical_term": "aki", "category": "disease", "language": "th"},
    {"raw_term": "ckd", "canonical_term": "ckd", "category": "disease", "language": "en"},
    {"raw_term": "chronic kidney disease", "canonical_term": "ckd", "category": "disease", "language": "en"},
    {"raw_term": "chronic renal failure", "canonical_term": "ckd", "category": "disease", "language": "en"},
    {"raw_term": "ไตวายเรื้อรัง", "canonical_term": "ckd", "category": "disease", "language": "th"},
    {"raw_term": "esrd", "canonical_term": "esrd", "category": "disease", "language": "en"},
    {"raw_term": "end stage renal disease", "canonical_term": "esrd", "category": "disease", "language": "en"},
    {"raw_term": "ไตวายระยะสุดท้าย", "canonical_term": "esrd", "category": "disease", "language": "th"},
    {"raw_term": "hypokalemia", "canonical_term": "hypokalemia", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "โพแทสเซียมในเลือดต่ำ", "canonical_term": "hypokalemia", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "โพแทสเซียมต่ำ", "canonical_term": "hypokalemia", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "hyperkalemia", "canonical_term": "hyperkalemia", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "โพแทสเซียมในเลือดสูง", "canonical_term": "hyperkalemia", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "โพแทสเซียมสูง", "canonical_term": "hyperkalemia", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "hyponatremia", "canonical_term": "hyponatremia", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "โซเดียมในเลือดต่ำ", "canonical_term": "hyponatremia", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "โซเดียมต่ำ", "canonical_term": "hyponatremia", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "hypernatremia", "canonical_term": "hypernatremia", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "โซเดียมในเลือดสูง", "canonical_term": "hypernatremia", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "โซเดียมสูง", "canonical_term": "hypernatremia", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "metabolic acidosis", "canonical_term": "metabolic_acidosis", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "ภาวะกรดเกินจากการเผาผลาญ", "canonical_term": "metabolic_acidosis", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "respiratory acidosis", "canonical_term": "respiratory_acidosis", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "ภาวะกรดเกินจากการหายใจ", "canonical_term": "respiratory_acidosis", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "metabolic alkalosis", "canonical_term": "metabolic_alkalosis", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "ภาวะด่างเกินจากการเผาผลาญ", "canonical_term": "metabolic_alkalosis", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "respiratory alkalosis", "canonical_term": "respiratory_alkalosis", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "ภาวะด่างเกินจากการหายใจ", "canonical_term": "respiratory_alkalosis", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "anion gap", "canonical_term": "anion_gap", "category": "lab", "language": "en"},

    # ==========================================
    # 4. NEUROLOGY
    # ==========================================
    {"raw_term": "stroke", "canonical_term": "stroke", "category": "disease", "language": "en"},
    {"raw_term": "ais", "canonical_term": "stroke", "category": "disease", "language": "en"},
    {"raw_term": "acute ischemic stroke", "canonical_term": "stroke", "category": "disease", "language": "en"},
    {"raw_term": "หลอดเลือดสมองอุดตัน", "canonical_term": "stroke", "category": "disease", "language": "th"},
    {"raw_term": "หลอดเลือดสมองตีบ", "canonical_term": "stroke", "category": "disease", "language": "th"},
    {"raw_term": "เส้นเลือดสมองตีบ", "canonical_term": "stroke", "category": "disease", "language": "th"},
    {"raw_term": "ich", "canonical_term": "ich", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "intracerebral hemorrhage", "canonical_term": "ich", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "intracranial hemorrhage", "canonical_term": "ich", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "hemorrhagic stroke", "canonical_term": "ich", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "เลือดออกในสมอง", "canonical_term": "ich", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "เส้นเลือดสมองแตก", "canonical_term": "ich", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "tia", "canonical_term": "tia", "category": "disease", "language": "en"},
    {"raw_term": "transient ischemic attack", "canonical_term": "tia", "category": "disease", "language": "en"},
    {"raw_term": "สมองขาดเลือดชั่วคราว", "canonical_term": "tia", "category": "disease", "language": "th"},
    {"raw_term": "seizure", "canonical_term": "seizure", "category": "disease", "language": "en"},
    {"raw_term": "อาการชัก", "canonical_term": "seizure", "category": "disease", "language": "th"},

    # ==========================================
    # 5. PULMONOLOGY & INFECTIOUS
    # ==========================================
    {"raw_term": "cap", "canonical_term": "cap", "category": "disease", "language": "en"},
    {"raw_term": "community-acquired pneumonia", "canonical_term": "cap", "category": "disease", "language": "en"},
    {"raw_term": "community acquired pneumonia", "canonical_term": "cap", "category": "disease", "language": "en"},
    {"raw_term": "ปอดอักเสบชุมชน", "canonical_term": "cap", "category": "disease", "language": "th"},
    {"raw_term": "ปอดบวมชุมชน", "canonical_term": "cap", "category": "disease", "language": "th"},
    {"raw_term": "hap", "canonical_term": "hap", "category": "disease", "language": "en"},
    {"raw_term": "hospital-acquired pneumonia", "canonical_term": "hap", "category": "disease", "language": "en"},
    {"raw_term": "pneumonia", "canonical_term": "pneumonia", "category": "disease", "language": "en"},
    {"raw_term": "ปอดอักเสบ", "canonical_term": "pneumonia", "category": "disease", "language": "th"},
    {"raw_term": "ปอดบวม", "canonical_term": "pneumonia", "category": "disease", "language": "th"},
    {"raw_term": "copd", "canonical_term": "copd", "category": "disease", "language": "en"},
    {"raw_term": "chronic obstructive pulmonary disease", "canonical_term": "copd", "category": "disease", "language": "en"},
    {"raw_term": "โรคปอดอุดกั้นเรื้อรัง", "canonical_term": "copd", "category": "disease", "language": "th"},
    {"raw_term": "asthma", "canonical_term": "asthma", "category": "disease", "language": "en"},
    {"raw_term": "โรคหอบหืด", "canonical_term": "asthma", "category": "disease", "language": "th"},
    {"raw_term": "หอบหืด", "canonical_term": "asthma", "category": "disease", "language": "th"},
    {"raw_term": "ards", "canonical_term": "ards", "category": "disease", "language": "en"},
    {"raw_term": "pe", "canonical_term": "pe", "category": "disease", "language": "en"},
    {"raw_term": "pulmonary embolism", "canonical_term": "pe", "category": "disease", "language": "en"},
    {"raw_term": "ลิ่มเลือดอุดกั้นในปอด", "canonical_term": "pe", "category": "disease", "language": "th"},
    {"raw_term": "sepsis", "canonical_term": "sepsis", "category": "disease", "language": "en"},
    {"raw_term": "ภาวะติดเชื้อในกระแสเลือด", "canonical_term": "sepsis", "category": "disease", "language": "th"},
    {"raw_term": "septic shock", "canonical_term": "septic_shock", "category": "disease", "language": "en"},
    {"raw_term": "uti", "canonical_term": "uti", "category": "disease", "language": "en"},
    {"raw_term": "urinary tract infection", "canonical_term": "uti", "category": "disease", "language": "en"},
    {"raw_term": "การติดเชื้อทางเดินปัสสาวะ", "canonical_term": "uti", "category": "disease", "language": "th"},

    # ==========================================
    # 6. GASTROENTEROLOGY & HEPATOLOGY
    # ==========================================
    {"raw_term": "pancreatitis", "canonical_term": "pancreatitis", "category": "disease", "language": "en"},
    {"raw_term": "acute pancreatitis", "canonical_term": "pancreatitis", "category": "disease", "language": "en"},
    {"raw_term": "ตับอ่อนอักเสบเฉียบพลัน", "canonical_term": "pancreatitis", "category": "disease", "language": "th"},
    {"raw_term": "ตับอ่อนอักเสบ", "canonical_term": "pancreatitis", "category": "disease", "language": "th"},
    {"raw_term": "cirrhosis", "canonical_term": "cirrhosis", "category": "disease", "language": "en"},
    {"raw_term": "ตับแข็ง", "canonical_term": "cirrhosis", "category": "disease", "language": "th"},
    {"raw_term": "ugib", "canonical_term": "ugib", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "upper gi bleed", "canonical_term": "ugib", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "upper gastrointestinal bleeding", "canonical_term": "ugib", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "เลือดออกทางเดินอาหารส่วนบน", "canonical_term": "ugib", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "lgib", "canonical_term": "lgib", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "lower gi bleed", "canonical_term": "lgib", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "lower gastrointestinal bleeding", "canonical_term": "lgib", "category": "disease", "language": "en", "prevent_merge": True},
    {"raw_term": "เลือดออกทางเดินอาหารส่วนล่าง", "canonical_term": "lgib", "category": "disease", "language": "th", "prevent_merge": True},
    {"raw_term": "gerd", "canonical_term": "gerd", "category": "disease", "language": "en"},
    {"raw_term": "กรดไหลย้อน", "canonical_term": "gerd", "category": "disease", "language": "th"},
    {"raw_term": "hepatitis", "canonical_term": "hepatitis", "category": "disease", "language": "en"},
    {"raw_term": "ตับอักเสบ", "canonical_term": "hepatitis", "category": "disease", "language": "th"},

    # ==========================================
    # 7. LABORATORY TESTS & MARKERS
    # ==========================================
    {"raw_term": "cr", "canonical_term": "creatinine", "category": "lab", "language": "en"},
    {"raw_term": "scr", "canonical_term": "serum creatinine", "category": "lab", "language": "en"},
    {"raw_term": "s-cr", "canonical_term": "serum creatinine", "category": "lab", "language": "en"},
    {"raw_term": "serum creatinine", "canonical_term": "serum creatinine", "category": "lab", "language": "en"},
    {"raw_term": "creatinine", "canonical_term": "creatinine", "category": "lab", "language": "en"},
    {"raw_term": "ครีอะตินีน", "canonical_term": "creatinine", "category": "lab", "language": "th"},
    {"raw_term": "bun", "canonical_term": "bun", "category": "lab", "language": "en"},
    {"raw_term": "blood urea nitrogen", "canonical_term": "bun", "category": "lab", "language": "en"},
    {"raw_term": "egfr", "canonical_term": "egfr", "category": "lab", "language": "en"},
    {"raw_term": "gfr", "canonical_term": "egfr", "category": "lab", "language": "en"},
    {"raw_term": "estimated glomerular filtration rate", "canonical_term": "egfr", "category": "lab", "language": "en"},
    {"raw_term": "cbc", "canonical_term": "cbc", "category": "lab", "language": "en"},
    {"raw_term": "complete blood count", "canonical_term": "cbc", "category": "lab", "language": "en"},
    {"raw_term": "hb", "canonical_term": "hemoglobin", "category": "lab", "language": "en"},
    {"raw_term": "hgb", "canonical_term": "hemoglobin", "category": "lab", "language": "en"},
    {"raw_term": "hemoglobin", "canonical_term": "hemoglobin", "category": "lab", "language": "en"},
    {"raw_term": "ฮีโมโกลบิน", "canonical_term": "hemoglobin", "category": "lab", "language": "th"},
    {"raw_term": "hct", "canonical_term": "hematocrit", "category": "lab", "language": "en"},
    {"raw_term": "hematocrit", "canonical_term": "hematocrit", "category": "lab", "language": "en"},
    {"raw_term": "wbc", "canonical_term": "wbc", "category": "lab", "language": "en"},
    {"raw_term": "white blood cell", "canonical_term": "wbc", "category": "lab", "language": "en"},
    {"raw_term": "white blood cells", "canonical_term": "wbc", "category": "lab", "language": "en"},
    {"raw_term": "เม็ดเลือดขาว", "canonical_term": "wbc", "category": "lab", "language": "th"},
    {"raw_term": "plt", "canonical_term": "platelet", "category": "lab", "language": "en"},
    {"raw_term": "platelet", "canonical_term": "platelet", "category": "lab", "language": "en"},
    {"raw_term": "platelets", "canonical_term": "platelet", "category": "lab", "language": "en"},
    {"raw_term": "เกล็ดเลือด", "canonical_term": "platelet", "category": "lab", "language": "th"},
    {"raw_term": "fbs", "canonical_term": "fbs", "category": "lab", "language": "en"},
    {"raw_term": "fasting blood sugar", "canonical_term": "fbs", "category": "lab", "language": "en"},
    {"raw_term": "fpg", "canonical_term": "fbs", "category": "lab", "language": "en"},
    {"raw_term": "fasting plasma glucose", "canonical_term": "fbs", "category": "lab", "language": "en"},
    {"raw_term": "hba1c", "canonical_term": "hba1c", "category": "lab", "language": "en"},
    {"raw_term": "a1c", "canonical_term": "hba1c", "category": "lab", "language": "en"},
    {"raw_term": "glycated hemoglobin", "canonical_term": "hba1c", "category": "lab", "language": "en"},
    {"raw_term": "น้ำตาลสะสม", "canonical_term": "hba1c", "category": "lab", "language": "th"},
    {"raw_term": "abg", "canonical_term": "abg", "category": "lab", "language": "en"},
    {"raw_term": "arterial blood gas", "canonical_term": "abg", "category": "lab", "language": "en"},
    {"raw_term": "ua", "canonical_term": "urinalysis", "category": "lab", "language": "en"},
    {"raw_term": "urinalysis", "canonical_term": "urinalysis", "category": "lab", "language": "en"},
    {"raw_term": "urine analysis", "canonical_term": "urinalysis", "category": "lab", "language": "en"},
    {"raw_term": "ตรวจปัสสาวะ", "canonical_term": "urinalysis", "category": "lab", "language": "th"},
    {"raw_term": "na", "canonical_term": "sodium", "category": "lab", "language": "en"},
    {"raw_term": "na+", "canonical_term": "sodium", "category": "lab", "language": "en"},
    {"raw_term": "serum sodium", "canonical_term": "serum sodium", "category": "lab", "language": "en"},
    {"raw_term": "โซเดียม", "canonical_term": "sodium", "category": "lab", "language": "th"},
    {"raw_term": "k", "canonical_term": "potassium", "category": "lab", "language": "en"},
    {"raw_term": "k+", "canonical_term": "potassium", "category": "lab", "language": "en"},
    {"raw_term": "serum potassium", "canonical_term": "serum potassium", "category": "lab", "language": "en"},
    {"raw_term": "โพแทสเซียม", "canonical_term": "potassium", "category": "lab", "language": "th"},
    {"raw_term": "cl", "canonical_term": "chloride", "category": "lab", "language": "en"},
    {"raw_term": "cl-", "canonical_term": "chloride", "category": "lab", "language": "en"},
    {"raw_term": "serum chloride", "canonical_term": "serum chloride", "category": "lab", "language": "en"},
    {"raw_term": "คลอไรด์", "canonical_term": "chloride", "category": "lab", "language": "th"},
    {"raw_term": "hco3", "canonical_term": "bicarbonate", "category": "lab", "language": "en"},
    {"raw_term": "hco3-", "canonical_term": "bicarbonate", "category": "lab", "language": "en"},
    {"raw_term": "bicarb", "canonical_term": "bicarbonate", "category": "lab", "language": "en"},
    {"raw_term": "serum bicarbonate", "canonical_term": "serum bicarbonate", "category": "lab", "language": "en"},
    {"raw_term": "ไบคาร์บอเนต", "canonical_term": "bicarbonate", "category": "lab", "language": "th"},
    {"raw_term": "trop-t", "canonical_term": "troponin", "category": "lab", "language": "en"},
    {"raw_term": "trop-i", "canonical_term": "troponin", "category": "lab", "language": "en"},
    {"raw_term": "hs-troponin", "canonical_term": "troponin", "category": "lab", "language": "en"},
    {"raw_term": "high sensitivity troponin", "canonical_term": "troponin", "category": "lab", "language": "en"},
    {"raw_term": "โทรโปนิน", "canonical_term": "troponin", "category": "lab", "language": "th"},
    {"raw_term": "ck-mb", "canonical_term": "ck_mb", "category": "lab", "language": "en"},
    {"raw_term": "bnp", "canonical_term": "bnp", "category": "lab", "language": "en"},
    {"raw_term": "nt-probnp", "canonical_term": "bnp", "category": "lab", "language": "en"},
    {"raw_term": "lft", "canonical_term": "lft", "category": "lab", "language": "en"},
    {"raw_term": "liver function test", "canonical_term": "lft", "category": "lab", "language": "en"},
    {"raw_term": "liver function tests", "canonical_term": "lft", "category": "lab", "language": "en"},
    {"raw_term": "การทำงานของตับ", "canonical_term": "lft", "category": "lab", "language": "th"},
    {"raw_term": "ast", "canonical_term": "ast", "category": "lab", "language": "en"},
    {"raw_term": "sgot", "canonical_term": "ast", "category": "lab", "language": "en"},
    {"raw_term": "alt", "canonical_term": "alt", "category": "lab", "language": "en"},
    {"raw_term": "sgpt", "canonical_term": "alt", "category": "lab", "language": "en"},
    {"raw_term": "alp", "canonical_term": "alp", "category": "lab", "language": "en"},
    {"raw_term": "alkaline phosphatase", "canonical_term": "alp", "category": "lab", "language": "en"},
    {"raw_term": "tb", "canonical_term": "bilirubin", "category": "lab", "language": "en"},
    {"raw_term": "total bilirubin", "canonical_term": "bilirubin", "category": "lab", "language": "en"},
    {"raw_term": "db", "canonical_term": "direct_bilirubin", "category": "lab", "language": "en"},
    {"raw_term": "direct bilirubin", "canonical_term": "direct_bilirubin", "category": "lab", "language": "en"},
    {"raw_term": "alb", "canonical_term": "albumin", "category": "lab", "language": "en"},
    {"raw_term": "albumin", "canonical_term": "albumin", "category": "lab", "language": "en"},
    {"raw_term": "inr", "canonical_term": "inr", "category": "lab", "language": "en"},
    {"raw_term": "pt", "canonical_term": "inr", "category": "lab", "language": "en"},
    {"raw_term": "aptt", "canonical_term": "aptt", "category": "lab", "language": "en"},
    {"raw_term": "ptt", "canonical_term": "aptt", "category": "lab", "language": "en"},

    # ==========================================
    # 8. MEDICATIONS: BRAND -> GENERIC & SYNONYMS
    # ==========================================
    {"raw_term": "acetaminophen", "canonical_term": "paracetamol", "category": "drug", "language": "en"},
    {"raw_term": "พาราเซตามอล", "canonical_term": "paracetamol", "category": "drug", "language": "th"},
    {"raw_term": "พารา", "canonical_term": "paracetamol", "category": "drug", "language": "th"},
    {"raw_term": "tylenol", "canonical_term": "paracetamol", "category": "drug", "language": "en"},
    {"raw_term": "panadol", "canonical_term": "paracetamol", "category": "drug", "language": "en"},
    {"raw_term": "sara", "canonical_term": "paracetamol", "category": "drug", "language": "en"},
    {"raw_term": "paracetamol", "canonical_term": "paracetamol", "category": "drug", "language": "en"},
    {"raw_term": "asa", "canonical_term": "aspirin", "category": "drug", "language": "en"},
    {"raw_term": "acetylsalicylic acid", "canonical_term": "aspirin", "category": "drug", "language": "en"},
    {"raw_term": "แอสไพริน", "canonical_term": "aspirin", "category": "drug", "language": "th"},
    {"raw_term": "aspent", "canonical_term": "aspirin", "category": "drug", "language": "en"},
    {"raw_term": "aspirin", "canonical_term": "aspirin", "category": "drug", "language": "en"},
    {"raw_term": "plavix", "canonical_term": "clopidogrel", "category": "drug", "language": "en"},
    {"raw_term": "clopidogrel", "canonical_term": "clopidogrel", "category": "drug", "language": "en"},
    {"raw_term": "โคลพิโดเกรล", "canonical_term": "clopidogrel", "category": "drug", "language": "th"},
    {"raw_term": "glucophage", "canonical_term": "metformin", "category": "drug", "language": "en"},
    {"raw_term": "metformin", "canonical_term": "metformin", "category": "drug", "language": "en"},
    {"raw_term": "เมทฟอร์มิน", "canonical_term": "metformin", "category": "drug", "language": "th"},
    {"raw_term": "minidiab", "canonical_term": "glipizide", "category": "drug", "language": "en"},
    {"raw_term": "glipizide", "canonical_term": "glipizide", "category": "drug", "language": "en"},
    {"raw_term": "ไกลพิไซด์", "canonical_term": "glipizide", "category": "drug", "language": "th"},
    {"raw_term": "renitec", "canonical_term": "enalapril", "category": "drug", "language": "en"},
    {"raw_term": "enalapril", "canonical_term": "enalapril", "category": "drug", "language": "en"},
    {"raw_term": "norvasc", "canonical_term": "amlodipine", "category": "drug", "language": "en"},
    {"raw_term": "amlodipine", "canonical_term": "amlodipine", "category": "drug", "language": "en"},
    {"raw_term": "แอมโลดิพีน", "canonical_term": "amlodipine", "category": "drug", "language": "th"},
    {"raw_term": "lipitor", "canonical_term": "atorvastatin", "category": "drug", "language": "en"},
    {"raw_term": "atorvastatin", "canonical_term": "atorvastatin", "category": "drug", "language": "en"},
    {"raw_term": "อะทอร์วาสแตติน", "canonical_term": "atorvastatin", "category": "drug", "language": "th"},
    {"raw_term": "zocor", "canonical_term": "simvastatin", "category": "drug", "language": "en"},
    {"raw_term": "simvastatin", "canonical_term": "simvastatin", "category": "drug", "language": "en"},
    {"raw_term": "ซิมวาสแตติน", "canonical_term": "simvastatin", "category": "drug", "language": "th"},
    {"raw_term": "losec", "canonical_term": "omeprazole", "category": "drug", "language": "en"},
    {"raw_term": "miracid", "canonical_term": "omeprazole", "category": "drug", "language": "en"},
    {"raw_term": "omeprazole", "canonical_term": "omeprazole", "category": "drug", "language": "en"},
    {"raw_term": "โอมีพราโซล", "canonical_term": "omeprazole", "category": "drug", "language": "th"},
    {"raw_term": "rocephin", "canonical_term": "ceftriaxone", "category": "drug", "language": "en"},
    {"raw_term": "ceftriaxone", "canonical_term": "ceftriaxone", "category": "drug", "language": "en"},
    {"raw_term": "activase", "canonical_term": "alteplase", "category": "drug", "language": "en"},
    {"raw_term": "actilyse", "canonical_term": "alteplase", "category": "drug", "language": "en"},
    {"raw_term": "rt-pa", "canonical_term": "alteplase", "category": "drug", "language": "en"},
    {"raw_term": "rtpa", "canonical_term": "alteplase", "category": "drug", "language": "en"},
    {"raw_term": "recombinant tissue plasminogen activator", "canonical_term": "alteplase", "category": "drug", "language": "en"},
    {"raw_term": "alteplase", "canonical_term": "alteplase", "category": "drug", "language": "en"},
    {"raw_term": "ntg", "canonical_term": "nitroglycerin", "category": "drug", "language": "en"},
    {"raw_term": "nitroglycerin", "canonical_term": "nitroglycerin", "category": "drug", "language": "en"},
    {"raw_term": "ไนโตรกลีเซอรีน", "canonical_term": "nitroglycerin", "category": "drug", "language": "th"},
    {"raw_term": "lasix", "canonical_term": "furosemide", "category": "drug", "language": "en"},
    {"raw_term": "furosemide", "canonical_term": "furosemide", "category": "drug", "language": "en"},
    {"raw_term": "ฟูโรเซไมด์", "canonical_term": "furosemide", "category": "drug", "language": "th"},
    {"raw_term": "aldactone", "canonical_term": "spironolactone", "category": "drug", "language": "en"},
    {"raw_term": "spironolactone", "canonical_term": "spironolactone", "category": "drug", "language": "en"},
    {"raw_term": "cozaar", "canonical_term": "losartan", "category": "drug", "language": "en"},
    {"raw_term": "losartan", "canonical_term": "losartan", "category": "drug", "language": "en"},
    {"raw_term": "warfarin", "canonical_term": "warfarin", "category": "drug", "language": "en"},
    {"raw_term": "coumadin", "canonical_term": "warfarin", "category": "drug", "language": "en"},
    {"raw_term": "วาร์ฟาริน", "canonical_term": "warfarin", "category": "drug", "language": "th"},
    {"raw_term": "allopurinol", "canonical_term": "allopurinol", "category": "drug", "language": "en"},
    {"raw_term": "zyloric", "canonical_term": "allopurinol", "category": "drug", "language": "en"},
    {"raw_term": "linagliptin", "canonical_term": "linagliptin", "category": "drug", "language": "en"},
    {"raw_term": "trajenta", "canonical_term": "linagliptin", "category": "drug", "language": "en"},

    # ==========================================
    # 9. CLINICAL UNITS & MEASUREMENTS
    # ==========================================
    {"raw_term": "mg/dl", "canonical_term": "mg/dl", "category": "unit", "language": "en"},
    {"raw_term": "มก./ดล.", "canonical_term": "mg/dl", "category": "unit", "language": "th"},
    {"raw_term": "มก/ดล", "canonical_term": "mg/dl", "category": "unit", "language": "th"},
    {"raw_term": "mg %", "canonical_term": "mg/dl", "category": "unit", "language": "en"},
    {"raw_term": "meq/l", "canonical_term": "meq/l", "category": "unit", "language": "en"},
    {"raw_term": "mmol/l", "canonical_term": "mmol/l", "category": "unit", "language": "en"},
    {"raw_term": "g/dl", "canonical_term": "g/dl", "category": "unit", "language": "en"},
    {"raw_term": "gm/dl", "canonical_term": "g/dl", "category": "unit", "language": "en"},
    {"raw_term": "ก./ดล.", "canonical_term": "g/dl", "category": "unit", "language": "th"},
    {"raw_term": "mmhg", "canonical_term": "mmhg", "category": "unit", "language": "en"},
    {"raw_term": "มม.ปรอท", "canonical_term": "mmhg", "category": "unit", "language": "th"},
    {"raw_term": "bpm", "canonical_term": "bpm", "category": "unit", "language": "en"},
    {"raw_term": "beats/min", "canonical_term": "bpm", "category": "unit", "language": "en"},
    {"raw_term": "ครั้ง/นาที", "canonical_term": "bpm", "category": "unit", "language": "th"},

    # ==========================================
    # 10. CLINICAL SIGNS & SYMPTOMS
    # ==========================================
    {"raw_term": "kussmaul breathing", "canonical_term": "kussmaul_respiration", "category": "symptom", "language": "en"},
    {"raw_term": "kussmaul respiration", "canonical_term": "kussmaul_respiration", "category": "symptom", "language": "en"},
    {"raw_term": "หายใจเหนื่อยหอบลึก", "canonical_term": "kussmaul_respiration", "category": "symptom", "language": "th"},
    {"raw_term": "dyspnea", "canonical_term": "dyspnea", "category": "symptom", "language": "en"},
    {"raw_term": "shortness of breath", "canonical_term": "dyspnea", "category": "symptom", "language": "en"},
    {"raw_term": "sob", "canonical_term": "dyspnea", "category": "symptom", "language": "en"},
    {"raw_term": "หายใจไม่อิ่ม", "canonical_term": "dyspnea", "category": "symptom", "language": "th"},
    {"raw_term": "เหนื่อยหอบ", "canonical_term": "dyspnea", "category": "symptom", "language": "th"},
    {"raw_term": "chest pain", "canonical_term": "chest_pain", "category": "symptom", "language": "en"},
    {"raw_term": "เจ็บแน่นหน้าอก", "canonical_term": "chest_pain", "category": "symptom", "language": "th"},
    {"raw_term": "แน่นหน้าอก", "canonical_term": "chest_pain", "category": "symptom", "language": "th"},
    {"raw_term": "edema", "canonical_term": "edema", "category": "symptom", "language": "en"},
    {"raw_term": "อาการบวม", "canonical_term": "edema", "category": "symptom", "language": "th"},
    {"raw_term": "ขาบวม", "canonical_term": "edema", "category": "symptom", "language": "th"},
]


def harvest_terms_from_case_studies(rag_dir: Path) -> List[Dict[str, Any]]:
    """Scan MedMate case studies in RAG directory to harvest real clinical terms."""
    harvested = []
    case_files = sorted(rag_dir.glob("case_study_*.txt"))
    print(f"[*] Scanning {len(case_files)} case studies from {rag_dir}...")

    # Pattern for medications: Name (dose)
    med_pattern = re.compile(r'\b([A-Z][a-z]{3,20})\s*\(([0-9]+(?:\s*mg)?)\)')
    # Pattern for common clinical acronyms
    acronym_pattern = re.compile(r'\b([A-Z]{2,6})\b')

    known_terms = {t["raw_term"].lower() for t in CURATED_BOOTSTRAP_TERMS}

    for path in case_files:
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue

        # 1. Harvest medications
        for med_match in med_pattern.finditer(content):
            drug_name = med_match.group(1).strip()
            drug_lower = drug_name.lower()
            if drug_lower not in known_terms:
                harvested.append({
                    "raw_term": drug_lower,
                    "canonical_term": drug_lower,
                    "category": "drug",
                    "language": "en",
                    "prevent_merge": False,
                    "source": f"rag_{path.stem}"
                })
                known_terms.add(drug_lower)

        # 2. Harvest clinical acronyms
        for ac_match in acronym_pattern.finditer(content):
            ac = ac_match.group(1).strip()
            ac_lower = ac.lower()
            # Skip technical or non-clinical uppercase tokens
            if ac in ("CASE", "CONFIDENTIAL", "DIS", "ID", "RR", "HR", "BP", "HEENT", "CBC"):
                continue
            if ac_lower not in known_terms:
                harvested.append({
                    "raw_term": ac_lower,
                    "canonical_term": ac_lower,
                    "category": "clinical_acronym",
                    "language": "en",
                    "prevent_merge": False,
                    "source": f"rag_{path.stem}"
                })
                known_terms.add(ac_lower)

    print(f"[*] Harvested {len(harvested)} additional clinical terms from case studies.")
    return harvested


def seed_lexicon_database(db_path: Path, rebuild: bool = False) -> None:
    """Seed the SQLite master lexicon database."""
    print(f"=== MedMate Clinical Lexicon Master Seeder ===")
    print(f"Target Database: {db_path}")

    if rebuild and db_path.exists():
        print(f"[-] Removing existing database {db_path} for clean rebuild...")
        db_path.unlink()

    normalizer = ClinicalNormalizer(db_path=db_path)

    # 1. Import curated bootstrap dictionary
    print(f"[*] Importing {len(CURATED_BOOTSTRAP_TERMS)} curated bootstrap clinical entries...")
    imported_curated = normalizer.bulk_import(CURATED_BOOTSTRAP_TERMS)
    print(f"[+] Imported {imported_curated} curated terms successfully.")

    # 2. Harvest and import terms from MedMate RAG case studies
    rag_dir = PROJECT_ROOT / "RAG"
    if rag_dir.exists():
        harvested_terms = harvest_terms_from_case_studies(rag_dir)
        if harvested_terms:
            imported_harvested = normalizer.bulk_import(harvested_terms)
            print(f"[+] Imported {imported_harvested} case-study terms successfully.")

    # 3. Print stats
    stats = normalizer.get_stats()
    print("\n--- Lexicon Summary Statistics ---")
    print(f"Total Terms:          {stats['total_terms']}")
    print(f"Canonical Concepts:   {stats['canonical_concepts']}")
    print(f"Safety Guarded:       {stats['prevent_merge_terms']} (prevent_merge=1)")
    print(f"Categories:           {stats['categories']}")
    print(f"Languages:            {stats['languages']}")
    print(f"Database Size:        {db_path.stat().st_size / 1024:.2f} KB")

    # 4. Run sanity normalization verification
    print("\n--- Sanity Normalization Checks ---")
    test_queries = [
        ("ผู้ป่วยโรคเบาหวานชนิดที่ 2 มีภาวะกรดเกินในเลือดจากเบาหวาน Scr 2.1 mg/dL",
         "t2dm dka creatinine 2.1 mg/dl"),
        ("serum creatinine normal range mg/dl",
         "creatinine dl mg normal range serum"),
        ("st-elevation myocardial infarction vs non-st-elevation myocardial infarction",
         "infarction myocardial nstemi stemi vs"),
        ("acetaminophen 500mg glucophage plavix",
         "500mg clopidogrel metformin paracetamol")
    ]
    for q_in, q_expected in test_queries:
        out = normalizer.normalize(q_in)
        print(f"In:  {q_in}")
        print(f"Out: {out}\n")

    print("[✔] Master Clinical Lexicon seeded and verified successfully.")


if __name__ == "__main__":
    rebuild_flag = "--rebuild" in sys.argv
    db_target = PROJECT_ROOT / "medical_skill" / "data" / "clinical_lexicon.db"
    seed_lexicon_database(db_target, rebuild=rebuild_flag)
