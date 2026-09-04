"""
Medical MCP Router & Transparent Cache Interceptor
MedMate - Thai Clinical Intelligence & Knowledge Harness (Phase 2 Component)

Provides high-level programmatic access to Medical MCP servers:
1. 'medical-mcp' (PubMed literature, FDA drug details, DDI interactions)
2. 'medical-terminologies-mcp' (LOINC, RxNorm, ICD-10/11, MeSH)
3. 'local-rag' (Local patient records, case studies in ./RAG/)

Every call is intercepted by MedicalMcpCache (Tier-0 Interceptor):
- Cache Hit -> returns distilled payload in <0.2ms (L1) or <2.0ms (L2)
- Cache Miss -> executes external handler, distills technical junk, indexes PMIDs/codes, and caches result.
"""

import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from medical_skill.medical_mcp_cache import MedicalMcpCache, default_medical_cache

logger = logging.getLogger("MedMate.McpRouter")


class MedicalMcpRouter:
    """
    Client-Facing Clinical MCP Router with Integrated Tier-0 Cache Interceptor.
    """

    def __init__(self, cache: Optional[MedicalMcpCache] = None, workspace_root: Optional[Path] = None):
        self.cache = cache or default_medical_cache
        self.workspace_root = workspace_root or Path(__file__).resolve().parents[1]
        self._custom_handlers: Dict[str, Callable[..., Any]] = {}

    def register_handler(self, provider: str, tool_name: str, handler: Callable[..., Any]) -> None:
        """Register custom execution handler for specific MCP tools (e.g. MCP stdio client)."""
        key = f"{provider}:{tool_name}"
        self._custom_handlers[key] = handler

    def _execute_or_fallback(
        self,
        provider: str,
        tool_name: str,
        arguments: Dict[str, Any],
        fallback_factory: Optional[Callable[[], Any]] = None
    ) -> Any:
        """Executes registered MCP handler, or executes fallback factory."""
        handler_key = f"{provider}:{tool_name}"
        if handler_key in self._custom_handlers:
            return self._custom_handlers[handler_key](**arguments)
        
        if fallback_factory is not None:
            return fallback_factory()

        return {
            "status": "success",
            "provider": provider,
            "tool": tool_name,
            "arguments": arguments,
            "message": "Default mock response (Handler not registered)"
        }

    # =========================================================================
    # 1. Literature & Research Suite (`medical-mcp`)
    # =========================================================================
    def search_medical_literature(
        self,
        query: str,
        max_results: int = 5,
        force_refresh: bool = False,
        executor: Optional[Callable[[], Any]] = None
    ) -> Dict[str, Any]:
        """Search PubMed literature with caching interceptor (TTL: 365 days)."""
        provider = "medical-mcp"
        tool_name = "search-medical-literature"
        args = {"query": query, "max_results": max_results}

        cached = self.cache.get(provider, tool_name, args, force_refresh=force_refresh)
        if cached is not None:
            return cached

        # Execute external fetch
        raw_result = executor() if executor else self._execute_or_fallback(provider, tool_name, args)
        self.cache.set(provider, tool_name, args, raw_result)
        return self.cache.get(provider, tool_name, args) or raw_result

    # =========================================================================
    # 2. Pharmacology & Drug Interactions (`medical-mcp`)
    # =========================================================================
    def check_drug_interactions(
        self,
        drug1: str,
        drug2: str,
        force_refresh: bool = False,
        executor: Optional[Callable[[], Any]] = None
    ) -> Dict[str, Any]:
        """Check drug-drug interactions with caching interceptor (TTL: 60 days)."""
        provider = "medical-mcp"
        tool_name = "check-drug-interactions"
        args = {"drug1": drug1, "drug2": drug2}

        cached = self.cache.get(provider, tool_name, args, force_refresh=force_refresh)
        if cached is not None:
            return cached

        raw_result = executor() if executor else self._execute_or_fallback(provider, tool_name, args)
        self.cache.set(provider, tool_name, args, raw_result)
        return self.cache.get(provider, tool_name, args) or raw_result

    def get_drug_details(
        self,
        drug_name: str,
        force_refresh: bool = False,
        executor: Optional[Callable[[], Any]] = None
    ) -> Dict[str, Any]:
        """Retrieve FDA drug details, dosages, and warnings (TTL: 60 days)."""
        provider = "medical-mcp"
        tool_name = "get-drug-details"
        args = {"drug_name": drug_name}

        cached = self.cache.get(provider, tool_name, args, force_refresh=force_refresh)
        if cached is not None:
            return cached

        raw_result = executor() if executor else self._execute_or_fallback(provider, tool_name, args)
        self.cache.set(provider, tool_name, args, raw_result)
        return self.cache.get(provider, tool_name, args) or raw_result

    # =========================================================================
    # 3. Standard Medical Terminologies (`medical-terminologies-mcp`)
    # =========================================================================
    def search_loinc(
        self,
        query: str,
        force_refresh: bool = False,
        executor: Optional[Callable[[], Any]] = None
    ) -> Dict[str, Any]:
        """Search LOINC lab codes, units, and reference intervals (TTL: 90 days)."""
        provider = "medical-terminologies-mcp"
        tool_name = "loinc_search"
        args = {"query": query}

        cached = self.cache.get(provider, tool_name, args, force_refresh=force_refresh)
        if cached is not None:
            return cached

        raw_result = executor() if executor else self._execute_or_fallback(provider, tool_name, args)
        self.cache.set(provider, tool_name, args, raw_result)
        return self.cache.get(provider, tool_name, args) or raw_result

    def search_rxnorm(
        self,
        query: str,
        force_refresh: bool = False,
        executor: Optional[Callable[[], Any]] = None
    ) -> Dict[str, Any]:
        """Search RxNorm clinical drugs and active ingredients (TTL: 90 days)."""
        provider = "medical-terminologies-mcp"
        tool_name = "rxnorm_search"
        args = {"query": query}

        cached = self.cache.get(provider, tool_name, args, force_refresh=force_refresh)
        if cached is not None:
            return cached

        raw_result = executor() if executor else self._execute_or_fallback(provider, tool_name, args)
        self.cache.set(provider, tool_name, args, raw_result)
        return self.cache.get(provider, tool_name, args) or raw_result

    # =========================================================================
    # 4. Local RAG & Hospital Knowledge (`local-rag`)
    # =========================================================================
    def read_local_rag(
        self,
        filename: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Read local case records or clinical guidelines from ./RAG/ (TTL: 7 days)."""
        provider = "local-rag"
        tool_name = "read_file"
        args = {"path": filename}

        cached = self.cache.get(provider, tool_name, args, force_refresh=force_refresh)
        if cached is not None:
            return cached

        rag_file = self.workspace_root / "RAG" / filename
        if not rag_file.exists():
            return {"status": "error", "message": f"File not found: {filename}"}

        try:
            with open(rag_file, "r", encoding="utf-8") as f:
                content = f.read()
            raw_result = {"status": "success", "filename": filename, "content": content}
            self.cache.set(provider, tool_name, args, raw_result)
            return self.cache.get(provider, tool_name, args) or raw_result
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Singleton instance
default_mcp_router = MedicalMcpRouter()
