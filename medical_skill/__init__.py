"""MedMate Medical Skill & Clinical Cache Module"""

def __getattr__(name: str):
    valid_exports = (
        "MedicalMcpCache", "ClinicalPayloadDistiller", "default_medical_cache",
        "ClinicalNormalizer", "default_normalizer", "ClinicalSafetyViolationError",
        "MedicalMcpRouter", "default_mcp_router",
        "audit_clinical_response", "sanitize_hallucinated_pmids",
        "detect_unverified_pmid_citations", "detect_unverified_clinical_codes"
    )
    if name in valid_exports:
        if name in ("MedicalMcpCache", "ClinicalPayloadDistiller", "default_medical_cache"):
            from .medical_mcp_cache import MedicalMcpCache, ClinicalPayloadDistiller, default_medical_cache
            return locals()[name]
        elif name in ("ClinicalNormalizer", "default_normalizer", "ClinicalSafetyViolationError"):
            from .clinical_normalizer import ClinicalNormalizer, default_normalizer, ClinicalSafetyViolationError
            return locals()[name]
        elif name in ("MedicalMcpRouter", "default_mcp_router"):
            from .mcp_router import MedicalMcpRouter, default_mcp_router
            return locals()[name]
        elif name in ("audit_clinical_response", "sanitize_hallucinated_pmids", "detect_unverified_pmid_citations", "detect_unverified_clinical_codes"):
            from .clinical_verifier import audit_clinical_response, sanitize_hallucinated_pmids, detect_unverified_pmid_citations, detect_unverified_clinical_codes
            return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "MedicalMcpCache", "ClinicalPayloadDistiller", "default_medical_cache",
    "ClinicalNormalizer", "default_normalizer", "ClinicalSafetyViolationError",
    "MedicalMcpRouter", "default_mcp_router",
    "audit_clinical_response", "sanitize_hallucinated_pmids",
    "detect_unverified_pmid_citations", "detect_unverified_clinical_codes"
]
