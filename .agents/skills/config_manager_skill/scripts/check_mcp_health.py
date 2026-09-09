"""
Cross-Platform MCP & Environment Configuration Health Checker & Auto-Fixer
Supports Windows, macOS, and Linux
"""

import json
import os
import shutil
import sys
from pathlib import Path

def check_command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None

def inspect_and_fix_mcp_config(config_path: Path, auto_fix: bool = False):
    print(f"[*] Checking MCP config at: {config_path}")
    data = {}
    needs_save = False

    if not config_path.exists():
        if auto_fix:
            print(f"[!] Config file missing. Creating new config: {config_path}")
            config_path.parent.mkdir(parents=True, exist_ok=True)
            data = {"mcpServers": {}}
            needs_save = True
        else:
            print(f"[-] Config file does not exist: {config_path}")
            return False
    else:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    data = {"mcpServers": {}}
                    needs_save = True
                else:
                    data = json.loads(content)
        except Exception as e:
            print(f"[!] JSON parsing error in {config_path}: {e}")
            if auto_fix:
                print(f"[+] Re-initializing corrupt JSON file with valid structure...")
                data = {"mcpServers": {}}
                needs_save = True
            else:
                return False

    if "mcpServers" not in data or not isinstance(data["mcpServers"], dict):
        data["mcpServers"] = {}
        needs_save = True

    mcp_servers = data["mcpServers"]
    print(f"[+] Found {len(mcp_servers)} MCP server definition(s).")

    for name, srv_conf in list(mcp_servers.items()):
        cmd = srv_conf.get("command", "")
        args = srv_conf.get("args", [])
        cmd_available = check_command_exists(cmd)
        
        # Check for outdated or known broken package names / inspector usage
        if auto_fix and ("medical-terminologies" in name or name == "medical-terminologies-mcp"):
            if args and ("@sidneybissoli/medical-terminologies-mcp" in args or "@modelcontextprotocol/inspector" in args):
                print(f"    [FIX] Updating '{name}' args to official 'medical-terminologies-mcp@latest'...")
                srv_conf["args"] = ["-y", "medical-terminologies-mcp@latest"]
                needs_save = True

        status_symbol = "+" if cmd_available else "!"
        print(f"  [{status_symbol}] {name}: command='{cmd}' (available: {cmd_available})")
        if not cmd_available:
            print(f"      -> Warning: '{cmd}' is not found in system PATH.")

    if auto_fix and needs_save:
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[SUCCESS] Successfully repaired/updated: {config_path}")
        except Exception as e:
            print(f"[!] Failed to write auto-fix to {config_path}: {e}")

    return True

def inspect_medical_cache(workspace_root: Path, auto_fix: bool = False):
    print("[*] Checking Medical MCP Cache & Master Lexicon Layer...")
    try:
        sys.path.insert(0, str(workspace_root))
        from medical_skill.medical_mcp_cache import default_medical_cache, check_cache_file
        from medical_skill.clinical_normalizer import default_normalizer

        # Check cache file existence and auto-creation status
        cache_db_path = default_medical_cache.db_path
        res = getattr(default_medical_cache, "_last_ensure_result", {})
        if res.get("created_now"):
            print(f"  [!] Cache file was missing: {cache_db_path}")
            print(f"  [SUCCESS] Auto-created cache database and initialized schema at: {cache_db_path}")
        else:
            print(f"  [+] Cache File Exists: {cache_db_path}")

        stats = default_medical_cache.get_telemetry_stats()
        print(f"  [+] Cache Status: {stats['status']}")
        print(f"  [+] Cache DB: {stats['db_path']}")
        print(f"  [+] Entries: {stats['total_cached_entries']}, Hits: {stats['total_cache_hits']}")
        print(f"  [+] Tokens Saved: {stats['total_ai_tokens_saved']}, Disk: {stats['disk_file_size_mb']} MB / {stats['disk_budget_limit_mb']} MB")
        print(f"  [+] Grounding Oracle: {stats['verified_pmids_count']} PMIDs, {stats['verified_codes_count']} codes")

        lex_stats = default_normalizer.get_stats()
        print(f"  [+] Master Lexicon DB: {lex_stats['db_path']}")
        print(f"  [+] Lexicon Terms: {lex_stats['total_terms']} ({lex_stats['canonical_concepts']} concepts), Safety Guarded: {lex_stats['prevent_merge_terms']}")
        return True
    except Exception as e:
        print(f"  [!] Cache/Lexicon inspection failed: {e}")
        return False

def inspect_document_and_pdf_system(workspace_root: Path):
    print("[*] Checking Multi-OS Thai Typography, PDF & Subprocess System...")
    try:
        sys.path.insert(0, str(workspace_root))
        from medical_skill.clinical_document_exporter import check_document_system_health
        health = check_document_system_health()
        print(f"  [+] Python Executable: {health['python_executable']} (sys.executable)")
        print(f"  [+] Platform: {health['platform']}")
        if health['chromium_available']:
            print(f"  [+] Headless Chromium Binary: {health['chromium_binary']}")
            print(f"  [+] PDF Engine Status: READY (HarfBuzz + ICU Thai Line Breaking)")
        else:
            print(f"  [!] Headless Chromium Binary: NOT FOUND")
            print(f"      -> Warning: PDF export requires Chromium/Chrome/Edge. Install chromium via system package manager.")
        
        if health['thai_fonts_detected']:
            print(f"  [+] Thai Fonts: DETECTED ({health['font_details']})")
        else:
            print(f"  [!] Thai Fonts: NOT DETECTED ({health['font_details']})")
            print(f"      -> Recommendation: Install fonts-thai-tlwg or fonts-noto-cjk to prevent tofu boxes.")
        return health['chromium_available']
    except Exception as e:
        print(f"  [!] Document system inspection failed: {e}")
        return False

def main():
    auto_fix = "--fix" in sys.argv or "-f" in sys.argv
    print("=" * 60)
    print(f" Antigravity & MCP Health Check {'[AUTO-FIX MODE]' if auto_fix else '[INSPECT MODE]'}")
    print("=" * 60)
    print(f"Platform: {sys.platform}")
    print(f"Python: {sys.version.split()[0]}")
    
    node_ok = check_command_exists("node")
    npx_ok = check_command_exists("npx")
    print(f"Node.js available: {node_ok}")
    print(f"NPX available: {npx_ok}")
    print("-" * 60)

    # Workspace config
    workspace_root = Path(__file__).resolve().parents[4]
    workspace_mcp_config = workspace_root / ".agents" / "mcp_config.json"
    inspect_and_fix_mcp_config(workspace_mcp_config, auto_fix=auto_fix)
    print("-" * 60)
    inspect_medical_cache(workspace_root, auto_fix=auto_fix)
    print("-" * 60)
    inspect_document_and_pdf_system(workspace_root)
    print("=" * 60)

if __name__ == "__main__":
    main()
