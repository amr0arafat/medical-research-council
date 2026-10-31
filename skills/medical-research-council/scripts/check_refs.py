#!/usr/bin/env python3
"""Check that every reference in a council session comes from the evidence pack.

Usage:
    python3 check_refs.py <session-folder>

Collects PMIDs, NCT numbers, and DOIs from evidence.md, then scans the round
files, verdict.md, and report.html. Any ID not in evidence.md is reported as
unverified. Exit code 0 = all verified, 1 = unverified IDs found or files missing.
"""
import re
import sys
from pathlib import Path

PATTERNS = {
    "PMID": [
        re.compile(r"\bPMID[:\s#]*(\d{1,9})\b", re.I),
        re.compile(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d{1,9})"),
    ],
    "NCT": [re.compile(r"\b(NCT\d{8})\b", re.I)],
    "DOI": [re.compile(r"\b(10\.\d{4,9}/[^\s\"'<>()\]]+)", re.I)],
}
SCANNED = ["round-1.md", "round-2.md", "verdict.md", "report.html"]


def extract(text):
    found = set()
    for kind, regexes in PATTERNS.items():
        for rx in regexes:
            for m in rx.finditer(text):
                value = m.group(1).rstrip(".,;:")
                found.add((kind, value.upper() if kind != "PMID" else value))
    return found


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    session = Path(sys.argv[1])
    evidence_file = session / "evidence.md"
    if not evidence_file.exists():
        print(f"ERROR: {evidence_file} not found")
        sys.exit(1)
    known = extract(evidence_file.read_text(encoding="utf-8"))

    unverified = {}
    scanned = []
    for name in SCANNED:
        path = session / name
        if not path.exists():
            continue
        scanned.append(name)
        for ref in extract(path.read_text(encoding="utf-8")) - known:
            unverified.setdefault(ref, []).append(name)

    print(f"Evidence pack: {len(known)} IDs. Scanned: {', '.join(scanned) or 'nothing'}.")
    if "verdict.md" not in scanned:
        print("WARNING: verdict.md not found; run this after writing the verdict.")
    if not unverified:
        print("PASS: every reference is in evidence.md.")
        sys.exit(0)
    print(f"FAIL: {len(unverified)} reference(s) not in evidence.md:")
    for (kind, value), files in sorted(unverified.items()):
        print(f"  {kind} {value}  (in {', '.join(sorted(set(files)))})")
    print("Remove them, relabel the claim (expert judgment), or verify and add them to evidence.md.")
    sys.exit(1)


if __name__ == "__main__":
    main()
