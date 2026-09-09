"""MedMate Medical Skill & Clinical Cache Module"""

def __getattr__(name: str):
    valid_exports = (
        "MedicalMcpCache", "ClinicalPayloadDistiller", "default_medical_cache",
        "check_cache_file", "ensure_cache_file",
        "ClinicalNormalizer", "default_normalizer", "ClinicalSafetyViolationError",
        "ClinicalLexiconEnricher", "default_enricher",
        "MedicalMcpRouter", "default_mcp_router",
        "audit_clinical_response", "sanitize_hallucinated_pmids",
        "detect_unverified_pmid_citations", "detect_unverified_clinical_codes",
        "MermaidUnicodeGuardian", "sanitize_mermaid", "validate_mermaid",
        "find_system_chromium_binary", "generate_clinical_html", "convert_html_to_thai_pdf",
        "export_clinical_markdown", "run_safe_python_script", "export_clinical_docx",
        "export_clinical_odt", "check_document_system_health", "THAI_FONT_STACK", "get_thai_clinical_css",
        "convert_markdown_file_to_pdf", "render_mermaid_to_svg"
    )
    if name in valid_exports:
        if name in ("MedicalMcpCache", "ClinicalPayloadDistiller", "default_medical_cache", "check_cache_file", "ensure_cache_file"):
            from .medical_mcp_cache import MedicalMcpCache, ClinicalPayloadDistiller, default_medical_cache, check_cache_file, ensure_cache_file
            return locals()[name]
        elif name in ("ClinicalNormalizer", "default_normalizer", "ClinicalSafetyViolationError"):
            from .clinical_normalizer import ClinicalNormalizer, default_normalizer, ClinicalSafetyViolationError
            return locals()[name]
        elif name in ("ClinicalLexiconEnricher", "default_enricher"):
            from .clinical_enricher import ClinicalLexiconEnricher, default_enricher
            return locals()[name]
        elif name in ("MedicalMcpRouter", "default_mcp_router"):
            from .mcp_router import MedicalMcpRouter, default_mcp_router
            return locals()[name]
        elif name in ("audit_clinical_response", "sanitize_hallucinated_pmids", "detect_unverified_pmid_citations", "detect_unverified_clinical_codes"):
            from .clinical_verifier import audit_clinical_response, sanitize_hallucinated_pmids, detect_unverified_pmid_citations, detect_unverified_clinical_codes
            return locals()[name]
        elif name in ("MermaidUnicodeGuardian", "sanitize_mermaid", "validate_mermaid"):
            from .mermaid_guardian import MermaidUnicodeGuardian, sanitize_mermaid, validate_mermaid
            return locals()[name]
        elif name in (
            "find_system_chromium_binary", "generate_clinical_html", "convert_html_to_thai_pdf",
            "export_clinical_markdown", "run_safe_python_script", "export_clinical_docx",
            "export_clinical_odt", "check_document_system_health", "THAI_FONT_STACK", "get_thai_clinical_css",
            "convert_markdown_file_to_pdf", "render_mermaid_to_svg"
        ):
            from .clinical_document_exporter import (
                find_system_chromium_binary, generate_clinical_html, convert_html_to_thai_pdf,
                export_clinical_markdown, run_safe_python_script, export_clinical_docx,
                export_clinical_odt, check_document_system_health, THAI_FONT_STACK, get_thai_clinical_css,
                convert_markdown_file_to_pdf, render_mermaid_to_svg
            )
            return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "MedicalMcpCache", "ClinicalPayloadDistiller", "default_medical_cache",
    "check_cache_file", "ensure_cache_file",
    "ClinicalNormalizer", "default_normalizer", "ClinicalSafetyViolationError",
    "ClinicalLexiconEnricher", "default_enricher",
    "MedicalMcpRouter", "default_mcp_router",
    "audit_clinical_response", "sanitize_hallucinated_pmids",
    "detect_unverified_pmid_citations", "detect_unverified_clinical_codes",
    "MermaidUnicodeGuardian", "sanitize_mermaid", "validate_mermaid",
    "find_system_chromium_binary", "generate_clinical_html", "convert_html_to_thai_pdf",
    "export_clinical_markdown", "run_safe_python_script", "export_clinical_docx",
    "export_clinical_odt", "check_document_system_health", "THAI_FONT_STACK", "get_thai_clinical_css",
    "convert_markdown_file_to_pdf", "render_mermaid_to_svg"
]
