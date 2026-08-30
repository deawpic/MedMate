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

if __name__ == "__main__":
    main()
