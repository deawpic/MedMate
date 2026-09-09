# -*- coding: utf-8 -*-
"""
Universal Cross-Platform Thai Clinical Document & PDF Exporter
MedMate - Thai Clinical Intelligence & Knowledge Harness (Multi-OS Architecture)

Implements Production-Grade Prevention for Bugs 1–6 (Rule 2.8 Protocol):

Key Architecture Standards:
1. Bug 1 (Tofu Box & Font Hierarchy): Universal OS Font Stack Fallback
2. Bug 2 (Tone Mark Preservation & Chromium Headless): HarfBuzz + ICU Thai Line Breaker with Docker flags
3. Bug 3 (Subprocess Multi-line Execution Safety): Enforces sys.executable and NamedTemporaryFile
4. Bug 4 (Saraban Standards & Collision-Free Metrics): 16pt body, line-height 1.5, A4 margins
5. Bug 5 (DOCX Left-Alignment): Rejects thaiDistribute to prevent character stretching
6. Bug 6 (ODF CTL Font Binding): Binds fontnamecomplex and fontsizecomplex
"""

import logging
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger("MedMate.DocumentExporter")

# Standard Thai Clinical & Government Font Stack (Bug 1 Universal Fallback)
THAI_FONT_STACK = (
    "'TH Sarabun New', 'Sarabun', 'Thonburi', 'Sukhumvit Set', "
    "'Loma', 'Garuda', 'Noto Sans Thai', 'Leelawadee UI', Tahoma, sans-serif"
)


def find_system_chromium_binary() -> Optional[str]:
    """
    Locates Chromium, Google Chrome, or Microsoft Edge across Windows, macOS, and Linux/Docker.
    Search order:
      1. System PATH via shutil.which
      2. OS-specific standard installation directories
    """
    cli_candidates = [
        "google-chrome", "google-chrome-stable", "chromium",
        "chromium-browser", "msedge", "microsoft-edge", "chrome"
    ]
    for cmd in cli_candidates:
        found_bin = shutil.which(cmd)
        if found_bin:
            return found_bin

    current_os = platform.system()

    if current_os == "Darwin":  # macOS
        mac_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        ]
        for p in mac_paths:
            if Path(p).exists():
                return p

    elif current_os == "Windows":  # Windows
        win_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe")
        ]
        for p in win_paths:
            if Path(p).exists():
                return p

    elif current_os == "Linux":  # Linux / Docker
        linux_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium"
        ]
        for p in linux_paths:
            if Path(p).exists():
                return p

    return None


def get_thai_clinical_css() -> str:
    """
    Returns standard CSS stylesheet complying with:
    - Bug 1: Complete Font Stack Fallback (Tofu-Free)
    - Bug 4: Thai Saraban Standard (16pt body, line-height 1.5, A4 margins, tone-collision free)
    """
    return f"""
@page {{
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
}}
@media print {{
    body {{
        background: #ffffff !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }}
}}
body {{
    font-family: {THAI_FONT_STACK};
    font-size: 16pt;
    line-height: 1.5;
    color: #1e293b;
    background-color: #ffffff;
    margin: 0;
    padding: 0;
    text-rendering: optimizeLegibility;
}}
h1, .doc-title {{
    font-size: 22pt;
    font-weight: bold;
    line-height: 1.25;
    color: #0f172a;
    margin-top: 0;
    margin-bottom: 12pt;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 6pt;
}}
h2 {{
    font-size: 18pt;
    font-weight: bold;
    line-height: 1.35;
    color: #1e3a8a;
    margin-top: 14pt;
    margin-bottom: 8pt;
}}
h3 {{
    font-size: 16pt;
    font-weight: bold;
    color: #334155;
    margin-top: 10pt;
    margin-bottom: 6pt;
}}
p {{
    margin-top: 0;
    margin-bottom: 8pt;
    text-align: left;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 10pt;
    margin-bottom: 12pt;
    font-size: 14pt;
    line-height: 1.4;
}}
th {{
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: bold;
    border: 1px solid #cbd5e1;
    padding: 6pt 8pt;
    text-align: left;
}}
td {{
    border: 1px solid #cbd5e1;
    padding: 6pt 8pt;
    text-align: left;
    vertical-align: top;
}}
.callout-box {{
    border-left: 4px solid #0284c7;
    background-color: #f0f9ff;
    padding: 10pt 12pt;
    margin: 10pt 0;
    font-size: 14pt;
    line-height: 1.4;
    border-radius: 4pt;
}}
.red-flag-box {{
    border-left: 4px solid #dc2626;
    background-color: #fef2f2;
    color: #991b1b;
    padding: 10pt 12pt;
    margin: 10pt 0;
    font-size: 14pt;
    line-height: 1.4;
    border-radius: 4pt;
    font-weight: bold;
}}
.patient-header {{
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6pt;
    padding: 10pt 12pt;
    margin-bottom: 14pt;
    font-size: 14pt;
    line-height: 1.4;
}}
.footer-note {{
    font-size: 11pt;
    color: #64748b;
    line-height: 1.3;
    border-top: 1px solid #e2e8f0;
    padding-top: 8pt;
    margin-top: 20pt;
}}
"""


def generate_clinical_html(
    title: str,
    content_html: str,
    patient_info: Optional[Dict[str, Any]] = None,
    custom_css: Optional[str] = None
) -> str:
    """
    Generates complete HTML5 document with Thai Saraban typography standards.
    """
    header_html = ""
    if patient_info:
        header_html = """
        <div class="patient-header">
            <strong>ข้อมูลผู้ป่วย (De-identified):</strong><br>
        """
        items = []
        if "patient_id" in patient_info:
            items.append(f"รหัส: {patient_info['patient_id']}")
        if "age" in patient_info and "gender" in patient_info:
            items.append(f"เพศ/อายุ: {patient_info['gender']} / {patient_info['age']}")
        if "admission_date" in patient_info:
            items.append(f"วันที่เข้ารับการรักษา: {patient_info['admission_date']}")
        if "attending_physician" in patient_info:
            items.append(f"แพทย์ผู้ดูแล: {patient_info['attending_physician']}")
        header_html += " | ".join(items) + "</div>"

    css_block = custom_css or get_thai_clinical_css()

    return f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{css_block}
    </style>
</head>
<body>
    <div class="doc-title">{title}</div>
    {header_html}
    {content_html}
    <div class="footer-note">
        เอกสารเวชระเบียนคลินิก MedMate Thai Medical Harness | เข้ารหัส UTF-8 ตามมาตรฐานงานสารบรรณไทย
    </div>
</body>
</html>
"""


def convert_html_to_thai_pdf(
    html_content: str,
    output_pdf_path: Union[str, Path],
    timeout_seconds: int = 30
) -> Path:
    """
    Converts HTML content to Thai PDF using Headless Chromium.
    Implements Bug 2 Universal Solution:
      - HarfBuzz OpenType Complex Text Shaping
      - Native ICU Thai dictionary word breaking
      - Safe Docker flags (--no-sandbox, --disable-dev-shm-usage, --disable-gpu)
      - Isolated temporary user data profile
    """
    output_pdf_path = Path(output_pdf_path).resolve()
    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    browser_executable = find_system_chromium_binary()
    if not browser_executable:
        raise FileNotFoundError(
            f"Chromium/Chrome/Edge executable not found on platform: {platform.system()}.\n"
            "For Linux/Docker: Run 'apt-get install -y chromium' or 'apt-get install -y google-chrome-stable'.\n"
            "For Windows: Install Microsoft Edge or Google Chrome.\n"
            "For macOS: Install Google Chrome in /Applications."
        )

    # 1. Write HTML to temporary file with strict UTF-8 encoding
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as f:
        f.write(html_content)
        temp_html_file = Path(f.name)

    # 2. Temporary isolated profile directory
    temp_profile_dir = tempfile.mkdtemp(prefix="medmate_chromium_pdf_")

    try:
        cmd = [
            browser_executable,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            f"--user-data-dir={temp_profile_dir}",
            "--no-pdf-header-footer",
            f"--print-to-pdf={output_pdf_path}",
            str(temp_html_file)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )

        if not output_pdf_path.exists() or output_pdf_path.stat().st_size == 0:
            raise RuntimeError(
                f"PDF generation failed (Exit Code: {result.returncode})\nStderr: {result.stderr}"
            )

        logger.info(f"Successfully generated Thai PDF at: {output_pdf_path} ({output_pdf_path.stat().st_size} bytes)")
        return output_pdf_path

    finally:
        temp_html_file.unlink(missing_ok=True)
        shutil.rmtree(temp_profile_dir, ignore_errors=True)


def export_clinical_markdown(
    title: str,
    markdown_content: str,
    filename: str,
    output_dir: Optional[Path] = None
) -> Path:
    """
    Saves clinical report into ./output/<filename>.md with UTF-8 encoding (Rule 2.6).
    """
    base_dir = output_dir or (Path(__file__).resolve().parents[1] / "output")
    base_dir.mkdir(parents=True, exist_ok=True)

    if not filename.endswith(".md"):
        filename += ".md"

    target_file = base_dir / filename
    full_text = f"# {title}\n\n{markdown_content.strip()}\n"

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
    Bug 3 Universal Solution:
    Executes Python script safely across Windows, macOS, and Linux.
      - Uses sys.executable (NEVER hardcode 'python' or 'python3')
      - Writes script to tempfile.NamedTemporaryFile (NEVER multi-line inline -c)
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


def export_clinical_docx(
    title: str,
    paragraphs: List[Tuple[str, str]],
    output_path: Union[str, Path]
) -> Path:
    """
    Bug 5 Universal Solution:
    Generates Word DOCX report enforcing WD_ALIGN_PARAGRAPH.LEFT instead of thaiDistribute.
    """
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Pt, Inches

        doc = Document()
        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        title_run = title_p.add_run(title)
        title_run.font.name = "TH Sarabun New"
        title_run.font.size = Pt(22)
        title_run.bold = True
        title_p.paragraph_format.space_after = Pt(12)

        for heading, body in paragraphs:
            if heading:
                hp = doc.add_paragraph()
                hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
                hrun = hp.add_run(heading)
                hrun.font.name = "TH Sarabun New"
                hrun.font.size = Pt(18)
                hrun.bold = True
                hp.paragraph_format.space_after = Pt(4)

            bp = doc.add_paragraph()
            # CRITICAL Bug 5 Rule: Use LEFT alignment, never thaiDistribute
            bp.alignment = WD_ALIGN_PARAGRAPH.LEFT
            bp.paragraph_format.line_spacing = 1.25
            bp.paragraph_format.space_after = Pt(6)
            brun = bp.add_run(body)
            brun.font.name = "TH Sarabun New"
            brun.font.size = Pt(16)

        doc.save(str(output_path))
        return output_path
    except ImportError:
        logger.warning("python-docx not installed, falling back to markdown export.")
        md_path = output_path.with_suffix(".md")
        md_text = f"# {title}\n\n" + "\n\n".join(f"## {h}\n{b}" if h else b for h, b in paragraphs)
        md_path.write_text(md_text, encoding="utf-8")
        return md_path


def export_clinical_odt(
    title: str,
    paragraphs: List[Tuple[str, str]],
    output_path: Union[str, Path]
) -> Path:
    """
    Bug 6 Universal Solution:
    Generates OpenDocument ODT report binding both Western and Complex Text Layout (CTL) properties.
    """
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from odf.opendocument import OpenDocumentText
        from odf.style import Style, TextProperties, ParagraphProperties
        from odf.text import P, H

        doc = OpenDocumentText()

        # Body Style with CTL binding (Bug 6)
        body_style = Style(name="ThaiBody", family="paragraph")
        body_style.addElement(
            TextProperties(
                fontname="TH Sarabun New",
                fontsize="16pt",
                fontnamecomplex="TH Sarabun New",
                fontsizecomplex="16pt"
            )
        )
        body_style.addElement(
            ParagraphProperties(lineheight="125%", marginbottom="0.15cm")
        )
        doc.styles.addElement(body_style)

        # Title Style
        title_style = Style(name="ThaiTitle", family="paragraph")
        title_style.addElement(
            TextProperties(
                fontname="TH Sarabun New",
                fontsize="22pt",
                fontweight="bold",
                fontnamecomplex="TH Sarabun New",
                fontsizecomplex="22pt",
                fontweightcomplex="bold"
            )
        )
        doc.styles.addElement(title_style)

        doc.text.addElement(P(stylename=title_style, text=title))

        for heading, body in paragraphs:
            if heading:
                doc.text.addElement(H(outlinelevel=2, text=heading))
            doc.text.addElement(P(stylename=body_style, text=body))

        doc.save(str(output_path))
        return output_path
    except ImportError:
        logger.warning("odfpy not installed, falling back to markdown export.")
        md_path = output_path.with_suffix(".md")
        md_text = f"# {title}\n\n" + "\n\n".join(f"## {h}\n{b}" if h else b for h, b in paragraphs)
        md_path.write_text(md_text, encoding="utf-8")
        return md_path


def check_document_system_health() -> Dict[str, Any]:
    """
    Checks multi-OS document generation prerequisites:
    - Python executable (sys.executable)
    - Chromium binary availability
    - Thai fonts installation status
    """
    current_os = platform.system()
    chromium_bin = find_system_chromium_binary()
    python_bin = sys.executable

    thai_fonts_detected = False
    font_details = "Not checked"

    if current_os == "Linux":
        fc_list_bin = shutil.which("fc-list")
        if fc_list_bin:
            try:
                res = subprocess.run([fc_list_bin, ":lang=th"], capture_output=True, text=True, timeout=5)
                thai_fonts_detected = len(res.stdout.strip()) > 0
                font_count = len(res.stdout.strip().splitlines()) if thai_fonts_detected else 0
                font_details = f"{font_count} Thai font face(s) found via fc-list"
            except Exception as e:
                font_details = f"fc-list error: {e}"
        else:
            font_details = "fc-list utility not in PATH"
    elif current_os == "Windows":
        thai_fonts_detected = Path(r"C:\Windows\Fonts\tahoma.ttf").exists() or Path(r"C:\Windows\Fonts\leelawad.ttf").exists()
        font_details = "Windows native Thai fonts detected" if thai_fonts_detected else "Default font check"
    elif current_os == "Darwin":
        thai_fonts_detected = Path("/System/Library/Fonts/Thonburi.ttc").exists()
        font_details = "Apple native Thai fonts detected" if thai_fonts_detected else "Default font check"

    return {
        "platform": current_os,
        "python_executable": python_bin,
        "chromium_binary": chromium_bin,
        "chromium_available": chromium_bin is not None,
        "thai_fonts_detected": thai_fonts_detected,
        "font_details": font_details,
        "status": "ready" if chromium_bin else "missing_chromium"
    }


def render_mermaid_to_svg(mermaid_code: str, timeout_seconds: int = 30) -> str:
    """
    Renders Mermaid diagram to SVG string using @mermaid-js/mermaid-cli via npx.
    Falls back to inline preformatted container if npx or mmdc is unavailable.
    """
    import re
    npx_bin = shutil.which("npx")
    if not npx_bin:
        logger.warning("npx not found, skipping SVG rendering of mermaid diagram.")
        return f'<div class="mermaid">{mermaid_code}</div>'

    with tempfile.NamedTemporaryFile("w", suffix=".mmd", encoding="utf-8", delete=False) as f_in:
        f_in.write(mermaid_code)
        temp_mmd = Path(f_in.name)

    temp_svg = temp_mmd.with_suffix(".svg")

    try:
        cmd = [npx_bin, "-y", "@mermaid-js/mermaid-cli", "-i", str(temp_mmd), "-o", str(temp_svg), "-b", "transparent"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds)
        if temp_svg.exists() and temp_svg.stat().st_size > 0:
            svg_text = temp_svg.read_text(encoding="utf-8")
            if "<?xml" in svg_text:
                svg_text = re.sub(r'<\?xml.*?\?>', '', svg_text, flags=re.DOTALL)
            if "<!DOCTYPE" in svg_text:
                svg_text = re.sub(r'<!DOCTYPE.*?>', '', svg_text, flags=re.DOTALL)
            svg_text = re.sub(r'style="[^"]*"', 'style="width: 100%; max-height: 235mm; height: auto; display: block; margin: 0 auto;"', svg_text, count=1)
            return svg_text
        else:
            logger.warning(f"Mermaid rendering returned {res.returncode}: {res.stderr}")
            return f'<div class="mermaid">{mermaid_code}</div>'
    except Exception as e:
        logger.warning(f"Failed to render mermaid diagram: {e}")
        return f'<div class="mermaid">{mermaid_code}</div>'
    finally:
        temp_mmd.unlink(missing_ok=True)
        temp_svg.unlink(missing_ok=True)


def convert_markdown_file_to_pdf(
    markdown_file_path: Union[str, Path],
    output_pdf_path: Optional[Union[str, Path]] = None,
    output_html_path: Optional[Union[str, Path]] = None,
    timeout_seconds: int = 45
) -> Tuple[Path, Path]:
    """
    Production-grade HTML-First Markdown to PDF Converter:
    1. Parses Markdown document, headers, tables, callouts, and lists.
    2. Automatically extracts and renders Mermaid diagrams to high-resolution vector SVGs.
    3. Wraps content with Universal OS Thai Font Stack and Saraban typography (16pt, line-height 1.5).
    4. Saves clean standalone HTML5 document.
    5. Converts HTML to print-ready PDF via Headless Chromium with HarfBuzz complex text shaping.
    """
    import re
    md_path = Path(markdown_file_path).resolve()
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    raw_text = md_path.read_text(encoding="utf-8")

    output_dir = md_path.parent
    base_name = md_path.stem

    if output_html_path is None:
        html_path = output_dir / f"{base_name}.html"
    else:
        html_path = Path(output_html_path).resolve()

    if output_pdf_path is None:
        pdf_path = output_dir / f"{base_name}.pdf"
    else:
        pdf_path = Path(output_pdf_path).resolve()

    # Extract Title
    title_match = re.search(r'^#\s+(.+)$', raw_text, re.MULTILINE)
    doc_title = title_match.group(1).strip() if title_match else base_name

    # 1. Process Mermaid blocks
    mermaid_blocks = []
    def replace_mermaid(match):
        code = match.group(1).strip()
        svg = render_mermaid_to_svg(code, timeout_seconds=timeout_seconds)
        mermaid_blocks.append(svg)
        return f"\n\n<!-- MERMAID_BLOCK_{len(mermaid_blocks)-1} -->\n\n"

    processed_text = re.sub(r'```mermaid\s*\n(.*?)\n```', replace_mermaid, raw_text, flags=re.DOTALL)

    # 2. Parse Markdown Tables
    def format_table(match):
        table_raw = match.group(0).strip()
        lines = [l.strip() for l in table_raw.splitlines() if l.strip().startswith("|")]
        if len(lines) < 2:
            return table_raw
        headers = [c.strip() for c in lines[0].strip("|").split("|")]
        data_rows = lines[2:]
        col_widths = ["15%", "25%", "60%"]
        html = ['<table class="clinical-table">', '  <thead>', '    <tr>']
        for i, h in enumerate(headers):
            w = col_widths[i] if i < len(col_widths) else "auto"
            html.append(f'      <th style="width: {w};">{h}</th>')
        html.extend(['    </tr>', '  </thead>', '  <tbody>'])
        for row in data_rows:
            cols = [c.strip() for c in row.strip("|").split("|")]
            html.append('    <tr>')
            for col in cols:
                cell_formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', col)
                cell_formatted = re.sub(r'`(.*?)`', r'<code>\1</code>', cell_formatted)
                html.append(f'      <td>{cell_formatted}</td>')
            html.append('    </tr>')
        html.extend(['  </tbody>', '</table>'])
        return "\n" + "\n".join(html) + "\n"

    table_pattern = re.compile(r'(?:^[ \t]*\|[^\n]+\|[ \t]*\n?)+', re.MULTILINE)
    processed_text = table_pattern.sub(format_table, processed_text)

    # 3. Process Headers
    processed_text = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', processed_text, flags=re.MULTILINE)
    processed_text = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', processed_text, flags=re.MULTILINE)
    processed_text = re.sub(r'^#\s+(.+)$', r'<div class="doc-title">\1</div>', processed_text, flags=re.MULTILINE)

    # 4. Inline Formatting (Code, Bold, Italics)
    processed_text = re.sub(r'`(.*?)`', r'<code>\1</code>', processed_text)
    processed_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', processed_text)
    processed_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', processed_text)

    # 5. Blockquotes / Callouts
    def format_blockquote(match):
        content = match.group(0).replace('>', '').strip()
        return f'<div class="callout-box">{content}</div>'
    processed_text = re.sub(r'(?:^>[^\n]+\n?)+', format_blockquote, processed_text, flags=re.MULTILINE)

    # 6. Re-insert Mermaid SVG blocks inside styled cards
    for idx, svg in enumerate(mermaid_blocks):
        placeholder = f"<!-- MERMAID_BLOCK_{idx} -->"
        card_html = (
            f'<div class="diagram-page-container">'
            f'  <div class="mermaid-diagram-card">\n{svg}\n  </div>'
            f'</div>'
        )
        processed_text = processed_text.replace(placeholder, card_html)

    # 7. Horizontal Rules
    processed_text = re.sub(r'^\s*---\s*$', r'<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 16pt 0;"/>', processed_text, flags=re.MULTILINE)

    # Wrap non-tagged lines into paragraphs
    content_lines = []
    for chunk in processed_text.split("\n\n"):
        c = chunk.strip()
        if not c:
            continue
        if c.startswith("<") or c.startswith("<!--"):
            content_lines.append(c)
        else:
            content_lines.append(f"<p>{c}</p>")
    body_content = "\n".join(content_lines)

    # Extra styling for Mermaid & Tables
    custom_css = get_thai_clinical_css() + """
.mermaid-diagram-card {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8pt;
    padding: 12pt;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    margin: 12pt 0;
    text-align: center;
}
.diagram-page-container {
    page-break-before: always;
    page-break-after: always;
}
.clinical-table {
    width: 100%;
    border-collapse: collapse;
    margin: 14pt 0;
    font-size: 13.5pt;
    line-height: 1.45;
}
.clinical-table th {
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: bold;
    border: 1px solid #cbd5e1;
    padding: 7pt 9pt;
    text-align: left;
}
.clinical-table td {
    border: 1px solid #cbd5e1;
    padding: 7pt 9pt;
    text-align: left;
    vertical-align: top;
}
.clinical-table tr:nth-child(even) td {
    background-color: #f8fafc;
}
"""

    full_html = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{doc_title}</title>
    <style>
{custom_css}
    </style>
</head>
<body>
    {body_content}
    <div class="footer-note">
        เอกสารเวชระเบียนคลินิก MedMate Thai Medical Harness | เข้ารหัส UTF-8 ตามมาตรฐานงานสารบรรณไทย
    </div>
</body>
</html>
"""
    html_path.write_text(full_html, encoding="utf-8")
    logger.info(f"Generated clinical HTML at: {html_path}")

    # Convert to PDF
    convert_html_to_thai_pdf(full_html, pdf_path, timeout_seconds=timeout_seconds)
    logger.info(f"Generated Thai PDF at: {pdf_path}")

    return html_path, pdf_path

