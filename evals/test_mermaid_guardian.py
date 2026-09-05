"""
Unit Test Suite for Mermaid Unicode & Non-ASCII Guardian
MedMate - Thai Clinical Intelligence & Knowledge Harness
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from medical_skill.mermaid_guardian import (
    MermaidUnicodeGuardian,
    sanitize_mermaid,
    validate_mermaid
)


def test_valid_thai_flowchart():
    """Test that a correctly formatted Mermaid flowchart with Thai passes with 0 errors."""
    valid_code = """
    flowchart TD
        NodeA["<b>คัดกรองอาการ FAST</b><br/>ประเมิน Onset ทันที"] --> NodeB{"ระยะเวลา < 4.5 ชม.?"}
        NodeB -- "ใช่" --> NodeC["พิจารณาให้ยา IV rt-PA"]
        NodeB -- "ไม่ใช่" --> NodeD["พิจารณา MRI DWI-FLAIR"]
    """
    res = validate_mermaid(valid_code)
    assert res["passed"] is True, f"Expected pass, got errors: {res['errors']}"
    assert len(res["errors"]) == 0
    print("[PASS] test_valid_thai_flowchart")


def test_incompatible_class_diagram_with_thai():
    """Test that classDiagram with Thai triggers FATAL error and auto-converts to flowchart TD."""
    invalid_code = """
    classDiagram
        class ผู้ป่วย_นายสมชาย {
            +อายุ: 62
            +อาการ: แขนขาอ่อนแรง
        }
    """
    res = validate_mermaid(invalid_code)
    assert res["passed"] is False, "Expected failure for classDiagram with Thai"
    assert any(e["severity"] == "FATAL" for e in res["errors"])

    sanitized, fixes = sanitize_mermaid(invalid_code)
    assert "flowchart TD" in sanitized, f"Expected conversion to flowchart TD, got: {sanitized}"
    assert len(fixes) > 0
    print("[PASS] test_incompatible_class_diagram_with_thai")


def test_unquoted_thai_labels():
    """Test that unquoted Thai labels like NodeA[ตรวจร่างกาย] are flagged and auto-quoted."""
    code_with_unquoted = """
    flowchart TD
        Step1[เริ่มประเมินอาการ] --> Step2(เจาะตรวจน้ำตาล DTX)
    """
    res = validate_mermaid(code_with_unquoted)
    assert res["passed"] is False, "Expected failure for unquoted Thai labels"
    assert len(res["errors"]) == 2

    sanitized, fixes = sanitize_mermaid(code_with_unquoted)
    assert 'Step1["เริ่มประเมินอาการ"]' in sanitized
    assert 'Step2("เจาะตรวจน้ำตาล DTX")' in sanitized
    assert len(fixes) == 2
    print("[PASS] test_unquoted_thai_labels")


def test_thai_node_ids():
    """Test that Thai characters in Node IDs are detected and replaced with ASCII IDs."""
    code_with_thai_ids = """
    flowchart TD
        คนไข้["นาย ก"] --> หมอ["แพทย์เวร"]
    """
    res = validate_mermaid(code_with_thai_ids)
    assert res["passed"] is False, "Expected failure for Thai node IDs"

    sanitized, fixes = sanitize_mermaid(code_with_thai_ids)
    assert "คนไข้[" not in sanitized
    assert "หมอ[" not in sanitized
    assert '["นาย ก"]' in sanitized
    assert '["แพทย์เวร"]' in sanitized
    assert len(fixes) > 0
    print("[PASS] test_thai_node_ids")


def test_subgraph_thai_formatting():
    """Test that subgraphs with Thai without quotes are flagged and properly formatted."""
    code_with_subgraph = """
    flowchart TD
        subgraph แผนกฉุกเฉิน
            NodeA["รับผู้ป่วย"] --> NodeB["ตรวจประเมิน"]
        end
    """
    res = validate_mermaid(code_with_subgraph)
    assert res["passed"] is False, "Expected failure for unquoted Thai subgraph ID"

    sanitized, fixes = sanitize_mermaid(code_with_subgraph)
    assert '["แผนกฉุกเฉิน"]' in sanitized
    print("[PASS] test_subgraph_thai_formatting")


def test_markdown_audit_and_auto_healing():
    """Test scanning a full markdown document containing both valid and invalid Mermaid blocks."""
    doc = """
    # รายงานคลินิก
    นี่คือผังการตรวจ:
    ```mermaid
    flowchart TD
        A[รับผู้ป่วย ER] --> B["ส่งทำ CT Brain"]
    ```
    และผังบุคลากร:
    ```mermaid
    classDiagram
        class บุคลากร {
            +ชื่อ: สมชาย
        }
    ```
    """
    audit = MermaidUnicodeGuardian.audit_markdown_text(doc)
    assert audit["has_mermaid"] is True
    assert audit["block_count"] == 2
    assert audit["passed"] is False  # Second block has classDiagram with Thai

    # Check auto-sanitized markdown
    sanitized_doc = audit["sanitized_markdown"]
    re_audit = MermaidUnicodeGuardian.audit_markdown_text(sanitized_doc)
    assert re_audit["passed"] is True, f"Expected sanitized markdown to pass, but got: {re_audit['reports']}"
    print("[PASS] test_markdown_audit_and_auto_healing")


if __name__ == "__main__":
    print("============================================================")
    print(" Running Mermaid Unicode & Non-ASCII Guardian Test Suite")
    print("============================================================")
    test_valid_thai_flowchart()
    test_incompatible_class_diagram_with_thai()
    test_unquoted_thai_labels()
    test_thai_node_ids()
    test_subgraph_thai_formatting()
    test_markdown_audit_and_auto_healing()
    print("============================================================")
    print("All Mermaid Guardian Unit Tests Passed Successfully! (6/6)")
    print("============================================================")
