"""
Clinical Safety, Red Flag & Anti-Hallucination Verifier
MedMate - Thai Clinical Intelligence & Knowledge Harness (Phase 3 Component)

Enforces:
1. Anti-Hallucination Grounding Oracle (Rule 2.5 of AGENTS.md):
   Validates cited PMIDs, DOIs, ICD-10/11, and LOINC codes against Grounding Whitelist.
2. Medical Emergency & Red Flag Trigger (Rule 2.1 of AGENTS.md):
   Detects if emergency alerts (1669 / ER) are missing when life-threatening symptoms are present.
3. Mandatory Legal Disclaimer (Rule 3 of AGENTS.md for Tier 3 Patient Mode).
4. Citation Sanitization: Replaces hallucinated PMIDs with standard evidence disclaimers.
"""

import re
from typing import Any, Dict, List, Optional, Set

from medical_skill.medical_mcp_cache import (
    ClinicalPayloadDistiller,
    MedicalMcpCache,
    default_medical_cache
)

# Mandatory Disclaimer for Tier 3 (Rule 3 of AGENTS.md)
MANDATORY_DISCLAIMER_KEYWORD = "ข้อความแจ้งเตือนทางการแพทย์"

# Emergency Red Flag Keywords (Rule 2.1 of AGENTS.md)
RED_FLAG_SYMPTOMS = [
    (re.compile(r"เจ็บ(?:แน่น)?หน้าอก(?:ร้าวไปกราม|ร้าวไปแขน)?|แน่นหน้าอกรุนแรง", re.IGNORECASE), "Suspected Acute Coronary Syndrome / STEMI"),
    (re.compile(r"ปากเบี้ยว|แขนขาอ่อนแรง|พูดไม่ชัด(?:กะทันหัน)?", re.IGNORECASE), "Suspected Stroke / FAST"),
    (re.compile(r"หายใจหอบลึก|ซึมลงในผู้ป่วยเบาหวาน|สับสนรุนแรง", re.IGNORECASE), "Suspected Severe DKA / Sepsis"),
    (re.compile(r"หายใจมีเสียงหวีด|หน้าบวม|ลมพิษเฉียบพลันหลังทานยา", re.IGNORECASE), "Suspected Anaphylaxis")
]

EMERGENCY_ACTIONS = [
    re.compile(r"1669"),
    re.compile(r"ห้องฉุกเฉิน|er|โรงพยาบาลทันที|พบแพทย์ทันที")
]


def extract_pmids(text: str) -> List[str]:
    """Extract all cited PubMed IDs from text."""
    return ClinicalPayloadDistiller.extract_pmids(text)


def extract_clinical_codes(text: str) -> List[str]:
    """Extract all cited ICD-10, LOINC, and RxNorm codes."""
    return ClinicalPayloadDistiller.extract_clinical_codes(text)


def detect_unverified_pmid_citations(
    text: str,
    verified_pmids: Optional[Set[str]] = None,
    cache: Optional[MedicalMcpCache] = None
) -> List[str]:
    """
    Detects PMIDs cited in text that do not exist in the Grounding Oracle whitelist.
    """
    oracle = set(verified_pmids or [])
    active_cache = cache or default_medical_cache
    if hasattr(active_cache, "get_all_verified_pmids"):
        oracle.update(active_cache.get_all_verified_pmids())

    cited_pmids = extract_pmids(text)
    return [p for p in cited_pmids if p not in oracle]


def detect_unverified_clinical_codes(
    text: str,
    verified_codes: Optional[Set[str]] = None,
    cache: Optional[MedicalMcpCache] = None
) -> List[str]:
    """
    Detects medical codes (ICD/LOINC) cited in text not found in the Grounding Oracle.
    """
    oracle = set(verified_codes or [])
    active_cache = cache or default_medical_cache
    if hasattr(active_cache, "get_all_verified_codes"):
        oracle.update(active_cache.get_all_verified_codes())

    cited_codes = extract_clinical_codes(text)
    return [c for c in cited_codes if c not in oracle]


def sanitize_hallucinated_pmids(
    text: str,
    cache: Optional[MedicalMcpCache] = None
) -> str:
    """
    Replaces unverified/hallucinated PMIDs with standard evidence disclaimer.
    """
    unverified = detect_unverified_pmid_citations(text, cache=cache)
    if not unverified:
        return text

    sanitized = text
    for pmid in unverified:
        pattern = re.compile(rf"\b(?:pmid[:\s]*)?{pmid}\b", re.IGNORECASE)
        sanitized = pattern.sub("[งานวิจัยทางคลินิกที่พึงอ้างอิง]", sanitized)

    return sanitized


def check_red_flag_alert(query_text: str, response_text: str) -> Dict[str, Any]:
    """
    Enforces Rule 2.1: If user input mentions red flag symptoms, response MUST trigger 1669/ER alert.
    """
    detected_red_flags = []
    for pattern, description in RED_FLAG_SYMPTOMS:
        if pattern.search(query_text):
            detected_red_flags.append(description)

    has_emergency_alert = any(act.search(response_text) for act in EMERGENCY_ACTIONS)

    violation = bool(detected_red_flags and not has_emergency_alert)
    return {
        "red_flags_present": detected_red_flags,
        "has_emergency_action": has_emergency_alert,
        "is_violation": violation
    }


def audit_clinical_response(
    response_text: str,
    user_query: str = "",
    tier: int = 1,
    cache: Optional[MedicalMcpCache] = None,
    allow_unverified_citations: bool = False
) -> Dict[str, Any]:
    """
    Comprehensive Clinical Response Audit:
    - Grounding Oracle (PMIDs / ICD / LOINC)
    - Red Flag Emergency compliance (Rule 2.1)
    - Mandatory Patient Disclaimer compliance (Rule 3)
    """
    violations = []
    active_cache = cache or default_medical_cache

    # 1. Grounding Oracle Verification (Rule 2.5)
    unverified_pmids = detect_unverified_pmid_citations(response_text, cache=active_cache)
    if not allow_unverified_citations and unverified_pmids:
        violations.append({
            "rule": "Anti-Hallucination Oracle (Rule 2.5)",
            "severity": "CRITICAL",
            "message": f"Detected unverified/hallucinated PMIDs: {unverified_pmids}"
        })

    unverified_codes = detect_unverified_clinical_codes(response_text, cache=active_cache)
    if not allow_unverified_citations and unverified_codes:
        violations.append({
            "rule": "Clinical Codification Verification (Rule 2.5)",
            "severity": "HIGH",
            "message": f"Detected unverified clinical codes: {unverified_codes}"
        })

    # 2. Red Flag Emergency Gate (Rule 2.1)
    if user_query:
        rf_check = check_red_flag_alert(user_query, response_text)
        if rf_check["is_violation"]:
            violations.append({
                "rule": "Medical Emergency & Red Flag Trigger (Rule 2.1)",
                "severity": "CRITICAL",
                "message": f"Missing urgent ER/1669 emergency warning for symptoms: {rf_check['red_flags_present']}"
            })

    # 3. Mandatory Disclaimer Gate for Tier 3 (Rule 3)
    if tier == 3:
        if MANDATORY_DISCLAIMER_KEYWORD not in response_text:
            violations.append({
                "rule": "Mandatory Legal Disclaimer (Rule 3)",
                "severity": "HIGH",
                "message": f"Missing required patient disclaimer keyword: '{MANDATORY_DISCLAIMER_KEYWORD}'"
            })

    return {
        "passed": len(violations) == 0,
        "violations": violations,
        "detected_pmids": extract_pmids(response_text),
        "unverified_pmids": unverified_pmids,
        "detected_codes": extract_clinical_codes(response_text),
        "unverified_codes": unverified_codes
    }
