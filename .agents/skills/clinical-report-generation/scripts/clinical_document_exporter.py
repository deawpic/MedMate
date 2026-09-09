# -*- coding: utf-8 -*-
"""
Markdown-Native Clinical Document & Report Exporter
MedMate - Thai Clinical Intelligence & Knowledge Harness

Architecture:
- Native UTF-8 Markdown (.md) and Structured JSON export into ./output/ (Rule 2.6)
- 100% Preservation of Clinical Math (LaTeX / KaTeX) & Chemical Equations (e.g., pH, electrolytes, Anion Gap)
- Subprocess multi-line execution safety (sys.executable + NamedTemporaryFile)
- Built-in PDF/Printing Advisory for clinicians and users recommending standardized external viewers
  (Obsidian, VS Code Markdown PDF, Typora, Browser Markdown Extensions)
"""

import logging
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("MedMate.DocumentExporter")


def get_pdf_export_guidance() -> str:
    """
    Returns standardized guidance for clinicians and users on how to print or
    export Markdown clinical documents to PDF using modern tools with full
    LaTeX / KaTeX math and chemistry rendering.
    """
    return (
        "> 💡 **คำแนะนำสำหรับการพิมพ์หรือแปลงเป็น PDF (Printing & PDF Export Guide):**\n"
        "> เอกสารเวชระเบียนนี้ถูกจัดทำในรูปแบบ Markdown (`.md`) มาตรฐานสากล เพื่อรักษาความถูกต้องของสูตรคำนวณทางการแพทย์และสมการเคมีคลินิก ($\\LaTeX$ / KaTeX) ไว้อย่างแม่นยำสูงสุด\n"
        ">\n"
        "> หากต้องการพิมพ์เป็นเอกสารกระดาษหรือบันทึกเป็น PDF ทางการแพทย์ แนะนำให้เปิดไฟล์ `.md` ผ่านโปรแกรมดังต่อไปนี้:\n"
        "> 1. **Obsidian** (ฟรี - แนะนำสูงสุด): เปิดไฟล์ `.md` แล้วเลือกเมนู `Export to PDF` (รองรับภาษาไทย, แผนภาพ Mermaid และสูตร $\\LaTeX$ อัตโนมัติ 100%)\n"
        "> 2. **VS Code**: ติดตั้งส่วนขยาย *Markdown PDF* หรือ *Markdown Preview Enhanced* แล้วคลิกขวาเลือก `Export (pdf)`\n"
        "> 3. **Typora**: เลือกเมนู `File -> Export -> PDF` จัดหน้าเอกสารได้สวยงามตามมาตรฐานงานสารบรรณ\n"
        "> 4. **Google Chrome / Microsoft Edge**: ติดตั้ง Extension เช่น *Markdown Viewer* หรือเปิดดูผ่าน GitHub แล้วกด `Ctrl + P` (Print -> Save as PDF)\n"
    )


def export_clinical_markdown(
    title: str,
    markdown_content: str,
    filename: str,
    output_dir: Optional[Path] = None,
    include_pdf_guidance: bool = True
) -> Path:
    """
    Saves clinical report into ./output/<filename>.md with UTF-8 encoding (Rule 2.6).
    Optionally appends the standardized PDF/Print guidance callout box.
    """
    base_dir = output_dir or (Path(__file__).resolve().parents[1] / "output")
    base_dir.mkdir(parents=True, exist_ok=True)

    if not filename.endswith(".md"):
        filename += ".md"

    target_file = base_dir / filename

    content_parts = [f"# {title}\n"]
    content_parts.append(markdown_content.strip())

    if include_pdf_guidance:
        content_parts.append("\n---\n")
        content_parts.append(get_pdf_export_guidance())

    full_text = "\n\n".join(content_parts) + "\n"

    with open(target_file, "w", encoding="utf-8") as f:
        f.write(full_text)

    logger.info(f"Exported clinical markdown to: {target_file}")
    return target_file


def run_safe_python_script(
    script_code: str,
    args: Optional[List[str]] = None,
    timeout: int = 30
) -> subprocess.CompletedProcess:
    """
    Multi-OS Subprocess Execution Safety:
    - Enforces sys.executable (never hardcodes 'python' or 'python3')
    - Writes script to tempfile.NamedTemporaryFile (never multi-line inline -c)
    """
    with tempfile.NamedTemporaryFile("w", suffix=".py", encoding="utf-8", delete=False) as f:
        f.write(script_code)
        temp_script_path = Path(f.name)

    try:
        cmd = [sys.executable, str(temp_script_path)]
        if args:
            cmd.extend(args)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result
    finally:
        temp_script_path.unlink(missing_ok=True)
