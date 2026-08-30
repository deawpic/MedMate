---
name: config_manager_skill
description: >-
  Inspect, validate, and manage MCP configurations, skills, and environment health
  across Windows, macOS, and Linux platforms.
---

# Config & Environment Manager Skill

This skill provides operational workflows and automated health check scripts to validate, repair, and maintain Antigravity MCP servers, workspace skill definitions, and configuration files across **Windows**, **macOS**, and **Linux**.

---

## 1. Automated Health Check (Cross-Platform)

Run the bundled diagnostic script to verify execution environments, node/npx binaries, and MCP configuration syntax:

```bash
python .agents/skills/config_manager_skill/scripts/check_mcp_health.py
```

### What this checks:
- Current OS & Python environment
- Availability of `node` and `npx` in system PATH
- Validity of JSON structure in `.agents/mcp_config.json` and `~/.gemini/config/mcp_config.json`
- Command availability for each declared MCP server

---

## 2. MCP Server Configuration Standard

When adding or updating MCP servers, ensure configurations follow cross-platform standards:

```json
{
  "mcpServers": {
    "medical-terminologies": {
      "command": "npx",
      "args": ["-y", "medical-terminologies-mcp@latest"]
    },
    "local-rag": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./RAG"]
    }
  }
}
```

### Best Practices for Cross-Platform:
1. **Prefer `npx` with `-y`**: Avoid platform-specific binaries like `cmd.exe /c` or shell wrappers unless strictly necessary.
2. **Relative Paths**: Always use forward slashes `/` (e.g., `./RAG`) for directory arguments so they resolve seamlessly on Windows, macOS, and Linux.
3. **UTF-8 Encoding**: All JSON and Markdown configuration files must be saved with UTF-8 encoding.

---

## 3. Skill & Agent Validation Checklist

- [ ] **YAML Frontmatter**: All `SKILL.md` files must start with valid YAML (`---`) specifying `name` and `description`.
- [ ] **Tool Alignment**: Ensure tool names mapped in `AGENTS.md` and `SKILL.md` match the available tools exposed by active MCP servers.
- [ ] **File Permissions & Protection**: Workspace-level configs reside in `.agents/`, while user-level global configs reside in `~/.gemini/config/`.
