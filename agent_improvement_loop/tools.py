from pathlib import Path

CHECK_EVIDENCE_COVERAGE = r'''#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit whether drafted claims cite existing dataroom files.")
    parser.add_argument("--claims-json", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, default=Path("outputs/evidence_coverage.json"))
    args = parser.parse_args()

    claims = json.loads(args.claims_json.read_text(encoding="utf-8"))
    if not isinstance(claims, list):
        raise ValueError("--claims-json must contain a JSON list of claim objects")

    result = check_evidence_coverage(claims, args.dataset_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


def check_evidence_coverage(claims: list[dict], dataset_root: Path) -> dict:
    supported = []
    unsupported = []
    missing_citations = []

    for raw in claims:
        claim = str(raw.get("claim") or "").strip()
        claim_type = str(raw.get("claim_type") or "claim")
        citations = [str(item).strip().removeprefix("data/") for item in raw.get("citations") or [] if str(item).strip()]
        row = {"claim": claim, "claim_type": claim_type, "citations": citations}
        if not citations:
            missing_citations.append({**row, "issue": "No citation provided."})
            continue
        missing = [citation for citation in citations if not (dataset_root / citation).exists()]
        if missing:
            unsupported.append({**row, "issue": f"Missing cited file(s): {', '.join(missing)}"})
        else:
            supported.append(row)

    return {
        "supported_claims": supported,
        "unsupported_claims": unsupported,
        "missing_citations": missing_citations,
        "recommended_caveats": [
            "Add valid source filenames or mark unsupported claims as unknown before final answer."
        ],
        "passed": not unsupported and not missing_citations,
    }


if __name__ == "__main__":
    main()
'''


VALIDATE_OUTPUT_CONTRACT = r'''#!/usr/bin/env python3

import argparse
import csv
import json
from pathlib import Path


REQUIRED_FILES = [
    "summary_answer.md",
    "investment_memo.md",
    "risk_register.json",
    "open_questions.md",
    "citations.json",
    "evidence_table.csv",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate diligence output artifacts before final answer.")
    parser.add_argument("--outputs", type=Path, default=Path("outputs"))
    parser.add_argument("--dataset-root", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, default=Path("outputs/output_contract_validation.json"))
    args = parser.parse_args()

    result = validate_output_contract(args.outputs, args.dataset_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


def validate_output_contract(outputs: Path, dataset_root: Path) -> dict:
    issues = []
    for filename in REQUIRED_FILES:
        path = outputs / filename
        if not path.exists():
            issues.append({"file": filename, "issue": "missing required artifact"})
        elif path.stat().st_size == 0:
            issues.append({"file": filename, "issue": "empty required artifact"})

    risks = _read_json(outputs / "risk_register.json", default=[])
    citations = _read_json(outputs / "citations.json", default=[])
    if not isinstance(risks, list):
        issues.append({"file": "risk_register.json", "issue": "must be a JSON list"})
        risks = []
    if not isinstance(citations, list):
        issues.append({"file": "citations.json", "issue": "must be a JSON list"})
        citations = []

    for index, risk in enumerate(risks):
        evidence = risk.get("evidence") if isinstance(risk, dict) else None
        if not evidence:
            issues.append({"file": "risk_register.json", "risk_index": index, "issue": "risk lacks evidence"})
            continue
        missing = [str(item).removeprefix("data/") for item in evidence if not (dataset_root / str(item).removeprefix("data/")).exists()]
        if missing:
            issues.append({"file": "risk_register.json", "risk_index": index, "issue": f"missing evidence file(s): {', '.join(missing)}"})

    for index, citation in enumerate(citations):
        sources = citation.get("sources") if isinstance(citation, dict) else None
        if not sources:
            issues.append({"file": "citations.json", "citation_index": index, "issue": "citation lacks sources"})
            continue
        missing = [str(item).removeprefix("data/") for item in sources if not (dataset_root / str(item).removeprefix("data/")).exists()]
        if missing:
            issues.append({"file": "citations.json", "citation_index": index, "issue": f"missing source file(s): {', '.join(missing)}"})

    try:
        with (outputs / "evidence_table.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        if rows and not {"claim_id", "claim", "sources"}.issubset(rows[0].keys()):
            issues.append({"file": "evidence_table.csv", "issue": "must include claim_id, claim, and sources columns"})
    except FileNotFoundError:
        pass

    return {"passed": not issues, "issues": issues, "required_files": REQUIRED_FILES}


def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    main()
'''


def write_runtime_tools(dataset_dir: Path) -> list[str]:
    tools_dir = dataset_dir / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "check_evidence_coverage.py": CHECK_EVIDENCE_COVERAGE,
        "validate_output_contract.py": VALIDATE_OUTPUT_CONTRACT,
    }
    written: list[str] = []
    for filename, content in files.items():
        path = tools_dir / filename
        path.write_text(content, encoding="utf-8")
        try:
            path.chmod(0o755)
        except Exception:
            pass
        written.append(str(path.relative_to(dataset_dir)))
    return written
