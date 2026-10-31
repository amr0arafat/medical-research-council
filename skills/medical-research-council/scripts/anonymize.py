#!/usr/bin/env python3
"""Anonymise Round 1 cards for peer review.

Usage:
    python3 anonymize.py <session-folder> [--seed N]

Reads <session-folder>/round-1.md (one "## <Seat>" heading per card, then
"## Chair notes"), shuffles the cards, numbers them Response 1..N, writes
<session-folder>/round-2-anon.md for the reviewers, and prints the
number-to-seat map for round-2.md. Never give the map to reviewers.
"""
import argparse
import random
import re
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("session")
    ap.add_argument("--seed", type=int, help="fix the shuffle (tests only)")
    args = ap.parse_args()

    session = Path(args.session)
    src = session / "round-1.md"
    if not src.exists():
        print(f"ERROR: {src} not found", file=sys.stderr)
        sys.exit(1)

    text = src.read_text(encoding="utf-8") + "\n## END\n"
    cards = [(seat, body.strip()) for seat, body in re.findall(r"^## (.+?)\n(.*?)(?=^## )", text, re.S | re.M)
             if seat.strip().lower() not in ("chair notes", "end")]
    if len(cards) < 2:
        print("ERROR: found fewer than two seat cards in round-1.md", file=sys.stderr)
        sys.exit(1)

    random.Random(args.seed).shuffle(cards)
    parts = ["# Round 2 input: anonymised Round 1 responses\n",
             "Options are lettered (A, B, C...). Responses are numbered.\n"]
    for i, (_, body) in enumerate(cards, 1):
        parts.append(f"## Response {i}\n{body}\n")
    (session / "round-2-anon.md").write_text("\n".join(parts), encoding="utf-8")

    print("Wrote round-2-anon.md. Map (keep out of reviewer prompts):")
    for i, (seat, _) in enumerate(cards, 1):
        print(f"  Response {i} = {seat}")


if __name__ == "__main__":
    main()
