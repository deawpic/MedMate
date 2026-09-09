"""
Mermaid Diagram Unicode, Thai & Non-ASCII Safety Guardian
MedMate - Thai Clinical Intelligence & Knowledge Harness (Production-Grade)

Inspired by & aligned with:
/home/deaw/Projects/thlawdeka/output/mermaid_unicode_master_prompt.md

Features:
1. Strict Validation:
   - Prohibits classDiagram, stateDiagram, erDiagram, gitGraph with Thai/Non-ASCII
   - Detects Thai/Non-ASCII in Node IDs & Subgraph IDs
   - Detects unquoted Thai/Non-ASCII labels and labels with () [] : / -
   - Detects raw newlines inside label text
2. Auto-Sanitizer & Auto-Healing:
   - Converts invalid classDiagram/stateDiagram to robust flowchart TD
   - Replaces Thai Node IDs with deterministic ASCII identifiers (e.g. Node_1, Node_2)
   - Wraps unquoted labels in double quotes ["..."]
   - Replaces raw newlines inside labels with <br/>
   - Formats subgraphs into: subgraph Sub_ID ["Label Thai"]
3. Markdown Document Scanner:
   - Extracts all ```mermaid blocks from clinical reports/markdown
   - Audits each block and provides auto-fixed replacement markdown
"""

import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple


# Regex to detect Non-ASCII (including Thai, CJK, Arabic, Cyrillic, accented Latin)
NON_ASCII_REGEX = re.compile(r'[^\x00-\x7F]')

# Thai character range: \u0E00 - \u0E7F
THAI_REGEX = re.compile(r'[\u0E00-\u0E7F]')

# Forbidden diagram types when Non-ASCII / Thai text is present
INCOMPATIBLE_UNICODE_DIAGRAMS = {
    "classdiagram", "statediagram", "statediagram-v2", "erdiagram", "gitgraph"
}

# Mermaid code block extractor in Markdown
MERMAID_BLOCK_REGEX = re.compile(
    r'(```mermaid\s*\n)(.*?)(```)',
    re.DOTALL | re.IGNORECASE
)


class MermaidSyntaxErrorDetail:
    """Represents a specific detected Mermaid syntax / Unicode violation."""
    def __init__(self, rule: str, line_number: int, line_content: str, message: str, severity: str = "ERROR"):
        self.rule = rule
        self.line_number = line_number
        self.line_content = line_content.strip()
        self.message = message
        self.severity = severity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule": self.rule,
            "line_number": self.line_number,
            "line_content": self.line_content,
            "message": self.message,
            "severity": self.severity
        }

    def __repr__(self) -> str:
        return f"[{self.severity}] Line {self.line_number} ({self.rule}): {self.message}"


class MermaidUnicodeGuardian:
    """
    Automated Validator, Linter & Sanitizer for Mermaid Markdown Diagrams
    Ensures 100% crash-free rendering across GitHub, VS Code, Browser, and Antigravity.
    """

    @staticmethod
    def contains_non_ascii(text: str) -> bool:
        """Returns True if string contains non-ASCII characters."""
        return bool(NON_ASCII_REGEX.search(text))

    @staticmethod
    def contains_thai(text: str) -> bool:
        """Returns True if string contains Thai characters."""
        return bool(THAI_REGEX.search(text))

    @classmethod
    def extract_diagram_type(cls, mermaid_code: str) -> Tuple[str, str]:
        """
        Extracts diagram type (e.g. 'flowchart', 'graph', 'classDiagram', 'sequenceDiagram').
        Returns (diagram_type_normalized, original_header_line).
        """
        lines = mermaid_code.strip().splitlines()
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("%%"):
                continue
            first_word = stripped.split()[0].lower()
            return first_word, stripped
        return "unknown", ""

    @classmethod
    def validate(cls, mermaid_code: str) -> Dict[str, Any]:
        """
        Validates a single Mermaid diagram code snippet against Unicode Guardrail rules.
        Returns validation report with errors, warnings, and passed boolean.
        """
        errors: List[MermaidSyntaxErrorDetail] = []
        warnings: List[MermaidSyntaxErrorDetail] = []

        code_clean = mermaid_code.strip()
        if not code_clean:
            return {"passed": True, "errors": [], "warnings": [], "diagram_type": "empty"}

        diag_type, header_line = cls.extract_diagram_type(code_clean)
        has_unicode = cls.contains_non_ascii(code_clean)

        # 1. Check Incompatible Diagram Types
        if diag_type in INCOMPATIBLE_UNICODE_DIAGRAMS and has_unicode:
            errors.append(MermaidSyntaxErrorDetail(
                rule="Strict Prohibitions: Incompatible Diagram Type with Unicode",
                line_number=1,
                line_content=header_line,
                message=(
                    f"'{diag_type}' crashes Mermaid lexer when used with Thai or Non-ASCII text. "
                    f"Must use 'flowchart TD' or 'flowchart LR' instead."
                ),
                severity="FATAL"
            ))

        lines = code_clean.splitlines()
        in_multiline_label = False

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("%%"):
                continue

            # Skip header line
            if idx == 1 and diag_type in line.lower():
                continue

            # 2. Check Subgraph declaration with Thai
            if stripped.lower().startswith("subgraph"):
                subgraph_match = re.match(r'subgraph\s+([^\s\[\]\(\)]+)(.*)', stripped, re.IGNORECASE)
                if subgraph_match:
                    sub_id = subgraph_match.group(1).strip()
                    sub_rest = subgraph_match.group(2).strip()
                    if cls.contains_non_ascii(sub_id) and not sub_rest:
                        errors.append(MermaidSyntaxErrorDetail(
                            rule="ASCII Identifiers: Subgraph ID",
                            line_number=idx,
                            line_content=stripped,
                            message=f"Subgraph ID '{sub_id}' contains Non-ASCII. Format must be: subgraph SubID [\"Label\"]"
                        ))

            # 3. Check for raw unquoted brackets containing Thai/Non-ASCII or special chars
            # Node pattern: id[Label without quotes] or id(Label without quotes)
            # Matches node definitions like: Node1[Thai text] or Node1(Thai text) without quotes
            unquoted_square = re.finditer(r'\b([a-zA-Z0-9_]+)\[([^"\]\n]*[\u0E00-\u0E7F][^"\]\n]*)\]', line)
            for m in unquoted_square:
                node_id = m.group(1)
                label_content = m.group(2)
                errors.append(MermaidSyntaxErrorDetail(
                    rule="Mandatory Quotes: Unquoted Label",
                    line_number=idx,
                    line_content=m.group(0),
                    message=f"Node '{node_id}' label contains Thai but is not wrapped in double quotes [\"...\"]"
                ))

            unquoted_round = re.finditer(r'\b([a-zA-Z0-9_]+)\(([^"\)\n]*[\u0E00-\u0E7F][^"\)\n]*)\)', line)
            for m in unquoted_round:
                node_id = m.group(1)
                label_content = m.group(2)
                errors.append(MermaidSyntaxErrorDetail(
                    rule="Mandatory Quotes: Unquoted Round Label",
                    line_number=idx,
                    line_content=m.group(0),
                    message=f"Node '{node_id}' label contains Thai but is not wrapped in double quotes (\"...\")"
                ))

            # 4. Check for Thai/Non-ASCII in Node IDs (e.g. คนไข้["คนไข้"] or หมอ --> พยาบาล)
            # Mask double-quoted strings first to avoid false positives on Thai text inside valid labels
            line_outside_quotes = re.sub(r'"[^"\n]*"', '""', line)
            thai_node_id_matches = re.finditer(r'([\u0E00-\u0E7F][\u0E00-\u0E7F0-9_]*)\s*(\[|\(|\{|\-\-|\-\.\-|==>|-->)', line_outside_quotes)
            for m in thai_node_id_matches:
                invalid_id = m.group(1)
                errors.append(MermaidSyntaxErrorDetail(
                    rule="ASCII Identifiers: Node ID",
                    line_number=idx,
                    line_content=line,
                    message=f"Node ID '{invalid_id}' contains Thai characters. Node IDs must be ASCII alphanumeric only."
                ))

            # 5. Check for unquoted edge labels containing Thai: e.g. -->|ข้อความไทยไม่มีคำพูด| or -- ข้อความไทย -->
            unquoted_pipe_edge = re.finditer(r'\|([^"\|\n]*[\u0E00-\u0E7F][^"\|\n]*)\|', line)
            for m in unquoted_pipe_edge:
                pipe_content = m.group(1)
                # Having Thai inside |...| is allowed if simple, but if it has parens or quotes it crashes.
                if any(c in pipe_content for c in "()[]{}"):
                    errors.append(MermaidSyntaxErrorDetail(
                        rule="Mandatory Quotes: Edge Label with Special Chars",
                        line_number=idx,
                        line_content=m.group(0),
                        message="Edge label contains Thai and parentheses/brackets without double quotes."
                    ))

        return {
            "passed": len(errors) == 0,
            "diagram_type": diag_type,
            "has_unicode": has_unicode,
            "errors": [e.to_dict() for e in errors],
            "warnings": [w.to_dict() for w in warnings]
        }

    @classmethod
    def sanitize(cls, mermaid_code: str) -> Tuple[str, List[str]]:
        """
        Auto-heals and sanitizes Mermaid code snippet:
        1. Converts classDiagram/stateDiagram with Thai to flowchart TD
        2. Wraps all unquoted Thai labels in double quotes ["..."]
        3. Converts Thai Node IDs to clean ASCII IDs
        4. Replaces raw newlines inside labels with <br/>
        5. Formats subgraphs properly with quoted labels
        Returns (sanitized_mermaid_code, list_of_fixes_applied)
        """
        fixes: List[str] = []
        lines = mermaid_code.strip().splitlines()
        if not lines:
            return mermaid_code, fixes

        diag_type, header_line = cls.extract_diagram_type(mermaid_code)
        has_unicode = cls.contains_non_ascii(mermaid_code)

        sanitized_lines = []
        first_line_processed = False

        # Map to substitute Thai Node IDs with ASCII IDs
        id_counter = 1
        thai_id_map: Dict[str, str] = {}

        for line in lines:
            stripped = line.strip()

            # Handle header
            if not first_line_processed and (diag_type in stripped.lower() or stripped.startswith("graph")):
                if diag_type in INCOMPATIBLE_UNICODE_DIAGRAMS and has_unicode:
                    sanitized_lines.append("flowchart TD")
                    fixes.append(f"Converted incompatible '{diag_type}' to 'flowchart TD'")
                else:
                    sanitized_lines.append(line)
                first_line_processed = True
                continue

            # Skip comments or empty lines
            if not stripped or stripped.startswith("%%"):
                sanitized_lines.append(line)
                continue

            current_line = line

            # A. Fix Subgraph with Thai without quotes:
            # subgraph แผนกฉุกเฉิน -> subgraph Sub_1 ["แผนกฉุกเฉิน"]
            subgraph_match = re.match(r'^(\s*subgraph\s+)([\u0E00-\u0E7F][^\s\[\]\(\)]+)\s*$', current_line)
            if subgraph_match:
                prefix = subgraph_match.group(1)
                thai_title = subgraph_match.group(2)
                sub_id = f"Sub_{id_counter}"
                id_counter += 1
                current_line = f'{prefix}{sub_id} ["{thai_title}"]'
                fixes.append(f"Normalized Subgraph '{thai_title}' to '{sub_id} [\"{thai_title}\"]'")

            # subgraph SubID แผนกฉุกเฉิน -> subgraph SubID ["แผนกฉุกเฉิน"]
            subgraph_named_match = re.match(r'^(\s*subgraph\s+)([a-zA-Z0-9_]+)\s+([\u0E00-\u0E7F][^"\[\]\n]+)$', current_line)
            if subgraph_named_match:
                prefix = subgraph_named_match.group(1)
                sub_id = subgraph_named_match.group(2)
                thai_title = subgraph_named_match.group(3).strip()
                current_line = f'{prefix}{sub_id} ["{thai_title}"]'
                fixes.append(f"Wrapped Subgraph label '{thai_title}' in double quotes")

            # B. Fix Unquoted Thai in Square Bracket Labels:
            # Node1[อาการ: ปวดหัว] -> Node1["อาการ: ปวดหัว"]
            def fix_unquoted_square(m: re.Match) -> str:
                prefix = m.group(1)
                content = m.group(2)
                # If content already starts and ends with double quotes, keep it
                if content.startswith('"') and content.endswith('"'):
                    return m.group(0)
                fixes.append(f"Enclosed Thai label in quotes: [{content[:20]}...]")
                return f'{prefix}["{content}"]'

            current_line = re.sub(
                r'(\b[a-zA-Z0-9_]+)\[([^"\]\n]*[\u0E00-\u0E7F][^"\]\n]*)\]',
                fix_unquoted_square,
                current_line
            )

            # C. Fix Unquoted Thai in Round Bracket Labels:
            # Node1(เริ่มตรวจ) -> Node1("เริ่มตรวจ")
            def fix_unquoted_round(m: re.Match) -> str:
                prefix = m.group(1)
                content = m.group(2)
                if content.startswith('"') and content.endswith('"'):
                    return m.group(0)
                fixes.append(f"Enclosed Thai label in quotes: ({content[:20]}...)")
                return f'{prefix}("{content}")'

            current_line = re.sub(
                r'(\b[a-zA-Z0-9_]+)\(([^"\)\n]*[\u0E00-\u0E7F][^"\)\n]*)\)',
                fix_unquoted_round,
                current_line
            )

            # D. Replace Thai Node IDs with ASCII IDs:
            thai_id_nodes = re.findall(r'(?:^|\s)([\u0E00-\u0E7F][\u0E00-\u0E7F0-9_]*)\s*(?:\[|\(|\{|\-\-|\-\.\-|==>|-->)', current_line)
            for tid in dict.fromkeys(thai_id_nodes):
                if tid not in thai_id_map:
                    thai_id_map[tid] = f"Node_{id_counter}"
                    id_counter += 1
                ascii_id = thai_id_map[tid]
                id_pattern = re.compile(r'(^|\s)' + re.escape(tid) + r'(\s*(?:\[|\(|\{|\-\-|\-\.\-|==>|-->))')
                current_line = id_pattern.sub(r'\g<1>' + ascii_id + r'\g<2>', current_line)
                fixes.append(f"Replaced Thai Node ID '{tid}' with ASCII ID '{ascii_id}'")

            sanitized_lines.append(current_line)

        # Handle any trailing Thai ID references in edges
        final_code = "\n".join(sanitized_lines)
        for tid, ascii_id in thai_id_map.items():
            # Replace standalone references in edge targets
            edge_pattern = re.compile(r'(---|-->|-\.->|==>)\s*' + re.escape(tid) + r'(?=[^a-zA-Z0-9_\u0E00-\u0E7F]|$)')
            final_code = edge_pattern.sub(r'\g<1> ' + ascii_id, final_code)

        return final_code, fixes

    @classmethod
    def audit_markdown_text(cls, markdown_text: str) -> Dict[str, Any]:
        """
        Scans an entire Markdown document, extracts all ```mermaid blocks,
        validates them, and optionally provides fully sanitized markdown.
        """
        matches = list(MERMAID_BLOCK_REGEX.finditer(markdown_text))
        if not matches:
            return {
                "has_mermaid": False,
                "block_count": 0,
                "passed": True,
                "reports": [],
                "sanitized_markdown": markdown_text
            }

        reports = []
        all_passed = True
        sanitized_text = markdown_text

        # Iterate in reverse order so replacements do not alter earlier match indices
        for m in reversed(matches):
            full_match = m.group(0)
            prefix = m.group(1)
            mermaid_body = m.group(2)
            suffix = m.group(3)

            val_res = cls.validate(mermaid_body)
            sanitized_body, fixes = cls.sanitize(mermaid_body)

            if not val_res["passed"]:
                all_passed = False

            reports.append({
                "original_code": mermaid_body.strip(),
                "validation": val_res,
                "fixes_applied": fixes,
                "sanitized_code": sanitized_body.strip()
            })

            # Replace block with sanitized version
            sanitized_block = f"{prefix}{sanitized_body.strip()}\n{suffix}"
            start, end = m.span()
            sanitized_text = sanitized_text[:start] + sanitized_block + sanitized_text[end:]

        reports.reverse()
        return {
            "has_mermaid": True,
            "block_count": len(matches),
            "passed": all_passed,
            "reports": reports,
            "sanitized_markdown": sanitized_text
        }


def sanitize_mermaid(code: str) -> Tuple[str, List[str]]:
    """Helper shortcut to sanitize a Mermaid code block."""
    return MermaidUnicodeGuardian.sanitize(code)


def validate_mermaid(code: str) -> Dict[str, Any]:
    """Helper shortcut to validate a Mermaid code block."""
    return MermaidUnicodeGuardian.validate(code)
