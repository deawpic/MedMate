"""
Clinical Lexicon Auto-Enrichment Engine
MedMate - Thai Clinical Intelligence & Knowledge Harness

Automated harvesting and enrichment of clinical terms, brand-to-generic drug pairs,
and standardized terminology concepts from external MCP servers:
1. 'medical-mcp' (FDA OpenFDA Drug Database, Drug Search, Drug Nomenclature)
2. 'medical-terminologies-mcp' (RxNorm, LOINC, MeSH, ATC, ICD-11)

Clinical Safety & Design:
- Dual payload parser: Handles both structured JSON (dict/list) and markdown text responses.
- Pharmaceutical Normalizer: Strips salt suffixes, dosage forms, routes, and numerical strengths.
- Anti-Hallucination & Clinical Safety Gates: Strictly validates candidates through
  ClinicalNormalizer.validate_safety() before insertion into the SQLite master lexicon.
- Idempotent & Non-blocking: Prevents duplicate pairs, gracefully skips unsafe or invalid
  terms without throwing runtime exceptions to calling clinical agents.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("MedMate.ClinicalEnricher")


class ClinicalLexiconEnricher:
    """
    Automated Extraction & Normalization Harvester for MCP Payloads.
    Converts raw text/markdown or structured JSON responses into validated
    candidate lexicon entries: (raw_term, canonical_term, category, language, source).
    """

    # Common pharmaceutical salt suffixes to strip when determining canonical generic name
    PHARMA_SALTS: Set[str] = {
        "hydrochloride", "hcl", "calcium", "sodium", "potassium", "besylate",
        "mesylate", "succinate", "tartrate", "fumarate", "maleate", "phosphate",
        "sulfate", "sulphate", "acetate", "citrate", "nitrate", "gluconate",
        "monohydrate", "dihydrate", "trihydrate", "magnesium", "bisulfate",
        "disodium", "dipotassium", "dipivoxil", "valerate", "propionate",
        "chlorhydrate", "carbonate", "bromide", "chloride"
    }

    # Dosage forms and route terms to clean from drug names
    DOSAGE_FORMS: Set[str] = {
        "oral", "tablet", "tablets", "capsule", "capsules", "solution", "suspension",
        "injection", "extended", "release", "delayed", "film-coated", "chewable",
        "topical", "cream", "ointment", "drops", "elixir", "patch", "inhalation",
        "er", "xr", "cr", "dr", "sr", "ir", "hr", "hour", "hours", "otc", "rx"
    }

    @classmethod
    def clean_generic_name(cls, raw: str) -> str:
        """
        Normalize generic drug substance by stripping strengths, dosage forms, and salt suffixes.
        Example: 'ATORVASTATIN CALCIUM' -> 'atorvastatin'
                 'metformin hydrochloride 500 MG Oral Tablet' -> 'metformin'
        """
        if not raw or not isinstance(raw, str):
            return ""
        text = raw.lower()
        # Remove numerical dosages/strengths (e.g. 500 mg, 1000 mg, 2.5/1000, 24 hr, 10%)
        text = re.sub(r"\b\d+(?:\.\d+)?\s*(?:mg|g|mcg|ml|hr|hour|hours|%)\b", " ", text)
        text = re.sub(r"\b\d+/\d+\b", " ", text)
        # Remove punctuation except hyphen and forward slash
        text = re.sub(r"[^\w\s\-/]", " ", text)
        tokens = [t.strip() for t in text.split() if t.strip()]

        # Filter out dosage forms, salts, and pure digits
        cleaned_tokens = []
        for t in tokens:
            if t in cls.DOSAGE_FORMS or t in cls.PHARMA_SALTS or t.isdigit():
                continue
            cleaned_tokens.append(t)

        return " ".join(cleaned_tokens).strip()

    @classmethod
    def clean_brand_name(cls, raw: str) -> str:
        """
        Clean brand/trade name string.
        Example: 'Lipitor (atorvastatin)' -> 'lipitor'
                 'Glucophage 500 MG Oral Tablet' -> 'glucophage'
                 'Kombiglyze 2.5/1000 24 HR Extended Release' -> 'kombiglyze'
        """
        if not raw or not isinstance(raw, str):
            return ""
        text = raw.strip()
        # Remove parenthesized ingredients or explanations
        text = re.sub(r"\(.*?\)", " ", text)
        # Strip trailing strengths/forms
        text = re.sub(r"\b\d+(?:\.\d+)?\s*(?:mg|g|mcg|ml|hr|%)\b.*$", "", text, flags=re.IGNORECASE)
        # Remove slash numbers or ratios like 2.5/1000, 50/500
        text = re.sub(r"\b\d+[\./]\d+\b", " ", text)
        # Replace non-alphanumeric (except hyphen) with space
        text = re.sub(r"[^\w\s\-]", " ", text)
        tokens = text.split()
        if not tokens:
            return ""
        dosage_forms = {"oral", "tablet", "capsule", "extended", "release", "xr", "er", "cr", "dr", "sr", "hr", "hours", "solution", "suspension", "injection"}
        filtered = []
        for t in tokens:
            t_low = t.lower()
            if t_low in dosage_forms or any(c.isdigit() for c in t):
                break
            filtered.append(t)
        return " ".join(filtered).strip().lower()

    @classmethod
    def extract_from_mcp(
        cls,
        provider: str,
        tool_name: str,
        arguments: Dict[str, Any],
        payload: Any
    ) -> List[Dict[str, Any]]:
        """
        Harvest candidate lexicon terms from MCP payload.
        Returns list of dicts:
        [{"raw_term": str, "canonical_term": str, "category": str, "language": str, "source": str}]
        """
        results: List[Dict[str, Any]] = []

        if provider == "medical-mcp":
            results.extend(cls._extract_medical_mcp(tool_name, arguments, payload))
        elif provider == "medical-terminologies-mcp":
            results.extend(cls._extract_terminologies_mcp(tool_name, arguments, payload))

        # Filter and sanitize candidates
        validated_candidates: List[Dict[str, Any]] = []
        seen: Set[Tuple[str, str]] = set()

        for item in results:
            raw = item.get("raw_term", "").strip().lower()
            canon = item.get("canonical_term", "").strip().lower()

            if not raw or not canon or raw == canon:
                continue
            if len(raw) < 2 or len(canon) < 2 or len(raw) > 80 or len(canon) > 80:
                continue
            if raw.isdigit() or canon.isdigit():
                continue

            pair_key = (raw, canon)
            if pair_key in seen:
                continue
            seen.add(pair_key)
            validated_candidates.append(item)

        return validated_candidates

    @classmethod
    def _extract_medical_mcp(
        cls,
        tool_name: str,
        arguments: Dict[str, Any],
        payload: Any
    ) -> List[Dict[str, Any]]:
        """Extract brand-to-generic drug pairs from medical-mcp (FDA OpenFDA)."""
        entries: List[Dict[str, Any]] = []
        source_label = f"mcp:medical-mcp:{tool_name}"

        # 1. Text/Markdown payload handling
        if isinstance(payload, str):
            matches = re.findall(
                r"\d+\.\s+\*\*([^*]+)\*\*\s*(?:\n|\r\n)\s*(?:Generic Name|Active Ingredient):\s*([^\n\r]+)",
                payload,
                re.IGNORECASE
            )
            for brand_raw, generic_raw in matches:
                brand_clean = cls.clean_brand_name(brand_raw)
                generic_clean = cls.clean_generic_name(generic_raw)
                if brand_clean and generic_clean:
                    entries.append({
                        "raw_term": brand_clean,
                        "canonical_term": generic_clean,
                        "category": "medication",
                        "language": "en",
                        "source": source_label
                    })

        # 2. Structured JSON / Dict payload handling
        elif isinstance(payload, dict):
            if "drug_info" in payload and isinstance(payload["drug_info"], dict):
                dinfo = payload["drug_info"]
                brand = cls.clean_brand_name(dinfo.get("brand_name", ""))
                generic = cls.clean_generic_name(dinfo.get("generic_name", ""))
                if brand and generic:
                    entries.append({
                        "raw_term": brand,
                        "canonical_term": generic,
                        "category": "medication",
                        "language": "en",
                        "source": source_label
                    })

            items = payload.get("results") or payload.get("drugs") or payload.get("data")
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        brand = cls.clean_brand_name(
                            item.get("brand_name") or item.get("brand") or item.get("name") or ""
                        )
                        generic = cls.clean_generic_name(
                            item.get("generic_name") or item.get("generic") or item.get("active_ingredient") or ""
                        )
                        openfda = item.get("openfda", {})
                        if isinstance(openfda, dict):
                            if not brand and openfda.get("brand_name"):
                                brand = cls.clean_brand_name(openfda["brand_name"][0])
                            if not generic and openfda.get("generic_name"):
                                generic = cls.clean_generic_name(openfda["generic_name"][0])

                        if brand and generic:
                            entries.append({
                                "raw_term": brand,
                                "canonical_term": generic,
                                "category": "medication",
                                "language": "en",
                                "source": source_label
                            })

        elif isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    brand = cls.clean_brand_name(item.get("brand_name") or item.get("brand") or "")
                    generic = cls.clean_generic_name(item.get("generic_name") or item.get("generic") or "")
                    if brand and generic:
                        entries.append({
                            "raw_term": brand,
                            "canonical_term": generic,
                            "category": "medication",
                            "language": "en",
                            "source": source_label
                        })

        return entries

    @classmethod
    def _extract_terminologies_mcp(
        cls,
        tool_name: str,
        arguments: Dict[str, Any],
        payload: Any
    ) -> List[Dict[str, Any]]:
        """Extract clinical entities and synonyms from medical-terminologies-mcp."""
        entries: List[Dict[str, Any]] = []
        source_label = f"mcp:medical-terminologies-mcp:{tool_name}"

        # ---------------------------------------------------------------------
        # RxNorm Tools (rxnorm_search, rxnorm_concept, rxnorm_ingredients)
        # ---------------------------------------------------------------------
        if "rxnorm" in tool_name:
            if isinstance(payload, str):
                # Pattern 1: Bracketed brand format:
                # 1. **1043567** - 24 HR metformin hydrochloride ... [Kombiglyze]
                bracket_matches = re.findall(r"-\s*(.*?)\s*\[([A-Za-z0-9\s\-]+)\]", payload)
                for desc, brand in bracket_matches:
                    brand_clean = cls.clean_brand_name(brand)
                    generic_clean = cls.clean_generic_name(desc)
                    if brand_clean and generic_clean:
                        entries.append({
                            "raw_term": brand_clean,
                            "canonical_term": generic_clean,
                            "category": "medication",
                            "language": "en",
                            "source": source_label
                        })

                # Pattern 2: Synonym: <Brand> <strength> <form>
                synonym_matches = re.findall(r"Synonym:\s*([^\n\r|]+)", payload)
                for syn in synonym_matches:
                    brand_clean = cls.clean_brand_name(syn)
                    q = arguments.get("query") or arguments.get("term") or ""
                    q_clean = cls.clean_generic_name(str(q))
                    if brand_clean and q_clean and brand_clean != q_clean:
                        entries.append({
                            "raw_term": brand_clean,
                            "canonical_term": q_clean,
                            "category": "medication",
                            "language": "en",
                            "source": source_label
                        })

            elif isinstance(payload, dict):
                props = []
                if "conceptGroup" in payload:
                    for cg in payload.get("conceptGroup", []):
                        props.extend(cg.get("conceptProperties", []))
                elif "conceptProperties" in payload:
                    props = payload.get("conceptProperties", [])
                elif "results" in payload:
                    props = payload.get("results", [])

                for prop in props:
                    if isinstance(prop, dict):
                        name = prop.get("name", "")
                        brand_match = re.search(r"\[([A-Za-z0-9\s\-]+)\]", name)
                        if brand_match:
                            brand_clean = cls.clean_brand_name(brand_match.group(1))
                            generic_clean = cls.clean_generic_name(name)
                            if brand_clean and generic_clean:
                                entries.append({
                                    "raw_term": brand_clean,
                                    "canonical_term": generic_clean,
                                    "category": "medication",
                                    "language": "en",
                                    "source": source_label
                                })

        # ---------------------------------------------------------------------
        # MeSH Tools (mesh_search, mesh_descriptor)
        # ---------------------------------------------------------------------
        elif "mesh" in tool_name:
            if isinstance(payload, str):
                table_rows = re.findall(r"\|\s*([D\d]+)\s*\|\s*([^|\n\r]+)\s*\|", payload)
                q = str(arguments.get("query") or arguments.get("term") or "").strip().lower()
                for mesh_id, label in table_rows:
                    label_clean = label.strip()
                    if label_clean and label_clean != "Label":
                        label_lower = label_clean.lower()
                        if q and q != label_lower and len(q) >= 2:
                            entries.append({
                                "raw_term": q,
                                "canonical_term": label_lower,
                                "category": "disease",
                                "language": "en",
                                "source": source_label
                            })
            elif isinstance(payload, dict):
                descriptors = payload.get("descriptors") or payload.get("results") or []
                q = str(arguments.get("query") or "").strip().lower()
                for desc in descriptors:
                    if isinstance(desc, dict):
                        label = desc.get("label", "").strip().lower()
                        if q and label and q != label:
                            entries.append({
                                "raw_term": q,
                                "canonical_term": label,
                                "category": "disease",
                                "language": "en",
                                "source": source_label
                            })

        # ---------------------------------------------------------------------
        # ATC Tools (atc_classify, atc_lookup)
        # ---------------------------------------------------------------------
        elif "atc" in tool_name:
            if isinstance(payload, str):
                atc_rows = re.findall(r"\|\s*([A-Z]\d{2}[A-Z\d]*)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|", payload)
                for code, class_name, drug in atc_rows:
                    code_clean = code.strip()
                    class_clean = class_name.strip().lower()
                    drug_clean = cls.clean_generic_name(drug.strip())
                    if code_clean != "ATC code" and drug_clean and class_clean:
                        entries.append({
                            "raw_term": drug_clean,
                            "canonical_term": class_clean,
                            "category": "drug_class",
                            "language": "en",
                            "source": source_label
                        })

        # ---------------------------------------------------------------------
        # LOINC Tools (loinc_search, loinc_details)
        # ---------------------------------------------------------------------
        elif "loinc" in tool_name:
            if isinstance(payload, str):
                loinc_matches = re.findall(r"\d+\.\s+\*\*([\d\-]+)\*\*\s*-\s*([^\n\r]+)", payload)
                q = str(arguments.get("query") or "").strip().lower()
                for code, desc in loinc_matches:
                    if q and len(q) >= 2:
                        comp_match = re.search(r"Component:\s*([^|\n\r]+)", desc)
                        if comp_match:
                            comp = comp_match.group(1).strip().lower()
                            if comp and comp != q:
                                entries.append({
                                    "raw_term": q,
                                    "canonical_term": comp,
                                    "category": "lab",
                                    "language": "en",
                                    "source": source_label
                                })

        return entries

    @classmethod
    def enrich(
        cls,
        normalizer: Any,
        provider: str,
        tool_name: str,
        arguments: Dict[str, Any],
        payload: Any
    ) -> int:
        """
        Execute end-to-end auto-enrichment into the clinical normalizer.
        Enforces ClinicalSafetyViolation checks on every candidate pair.
        Returns total number of newly added or updated terms.
        """
        candidates = cls.extract_from_mcp(provider, tool_name, arguments, payload)
        if not candidates:
            return 0

        saved_count = 0
        for item in candidates:
            raw = item["raw_term"]
            canon = item["canonical_term"]
            category = item.get("category", "general")
            language = item.get("language", "en")
            source = item.get("source", "mcp:auto_enrich")

            try:
                normalizer.validate_safety(raw, canon)
                success = normalizer.add_term(
                    raw_term=raw,
                    canonical_term=canon,
                    category=category,
                    language=language,
                    prevent_merge=False,
                    source=source
                )
                if success:
                    saved_count += 1
            except Exception as e:
                logger.debug(f"Auto-enrichment skipped candidate '{raw}' -> '{canon}': {e}")

        return saved_count


default_enricher = ClinicalLexiconEnricher()
