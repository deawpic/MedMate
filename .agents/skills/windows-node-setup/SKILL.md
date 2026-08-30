---
name: windows-node-setup
description: >-
  Step-by-step guide for Windows users to install, configure, and troubleshoot Node.js and npx
  using winget and NVM for Windows (nvm-windows). Use when a user on Windows OS encounters missing
  Node.js/npx errors or needs environment setup for MedMate MCP servers.
---

# Windows Node.js & NVM Setup Guide (for MedMate MCP Servers)

This skill provides a definitive, step-by-step procedure for Windows users to install and manage **Node.js** and **npx** using **NVM for Windows (nvm-windows)** via the Windows Package Manager (`winget`), ensuring compatibility with MedMate's MCP servers (`medical-mcp`, `medical-terminologies-mcp`, and `local-rag`).

---

## 1. When to Use This Skill
- The user is running Windows 10 / Windows 11.
- `check_mcp_health.py` reports: `Node.js available: False` or `NPX available: False`.
- The user asks how to set up Node.js, npx, or nvm on Windows.
- MCP servers fail to start on Windows due to missing binary paths.

---

## 2. Step-by-Step Installation Runbook

### Step 1: Install NVM for Windows via `winget`
Open **PowerShell** or **Windows Terminal** (preferably as Administrator) and run:

```powershell
winget install CoreyButler.NVMforWindows
```

> 💡 *Note*: If prompted with a source agreement, press `Y` and Enter.
> ⚠️ **Important**: After installation finishes, **close all open Terminal/PowerShell windows and open a new one** so that system environment variables take effect.

---

### Step 2: Install Node.js LTS via NVM
In a new PowerShell window, install the latest Long Term Support (LTS) version of Node.js:

```powershell
# 1. Install Node.js LTS (e.g. Node 20 or 22)
nvm install lts

# 2. List installed versions to see the exact version number
nvm list

# 3. Activate the installed LTS version (replace with actual installed version, e.g., 20.18.0)
nvm use 20.18.0
```

> 💡 *Tip*: When running `nvm use <version>`, Windows may display a User Account Control (UAC) prompt asking for permission to create the symlink. Click **Yes**.

---

### Step 3: Verify `node` and `npx` Installation
Run the following commands to confirm that Node.js and npx are ready:

```powershell
node -v
# Output should look like: v20.18.0 (or newer)

npx -v
# Output should look like: 10.8.2 (or newer)
```

---

### Step 4: Validate with MedMate MCP Health Check
Navigate to the MedMate project directory and run the diagnostic script:

```powershell
python .agents/skills/config_manager_skill/scripts/check_mcp_health.py
```

Expected output:
```text
Platform: win32
Node.js available: True
NPX available: True
[+] Found 3 MCP server definition(s).
  [+] medical-mcp: command='npx' (available: True)
  [+] medical-terminologies-mcp: command='npx' (available: True)
  [+] local-rag: command='npx' (available: True)
```

---

## 3. Windows Troubleshooting & Common Pitfalls

### Issue A: `nvm : The term 'nvm' is not recognized`
**Cause**: The PATH environment variable has not refreshed or NVM was installed in a non-standard location.  
**Fix**:
1. Restart PowerShell / Windows Terminal or reboot the machine.
2. Check that `C:\Users\<Username>\AppData\Roaming\nvm` and `C:\Program Files\nodejs` are in your System/User `PATH`.

### Issue B: `exit status 1: Access is denied` when running `nvm use`
**Cause**: Windows requires administrative or symlink creation privileges to create the `C:\Program Files\nodejs` symlink.  
**Fix**:
1. Open PowerShell by right-clicking and selecting **Run as administrator**.
2. Run `nvm use <version>` again.
3. (Optional) Enable **Developer Mode** in Windows Settings (`Settings > System > For developers > Developer Mode: ON`) to allow unprivileged symlink creation.

### Issue C: PowerShell Execution Policy error (`cannot be loaded because running scripts is disabled`)
**Cause**: Restricted PowerShell execution policy.  
**Fix**:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 4. Summary Checklist for Windows Setup
- [ ] Installed `CoreyButler.NVMforWindows` via `winget`
- [ ] Installed and activated Node.js LTS (`nvm install lts` & `nvm use <version>`)
- [ ] Verified `node -v` and `npx -v` output valid version numbers
- [ ] Tested MedMate MCP Health Check (`check_mcp_health.py`) with all `available: True`
