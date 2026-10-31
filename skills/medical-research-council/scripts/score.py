#!/usr/bin/env python3
"""Score a Medical Research Council session.

Usage:
    python3 score.py <session-folder> [--previous <old-session-folder>]

Reads <session-folder>/scores.json (format in references/scoring.md), applies
weights, the 4.0 veto cap, verdict labels, and the SPLIT flag, prints a
markdown scoreboard, and writes <session-folder>/scores-result.json.
"""
import argparse
import json
import sys
from pathlib import Path

ROSTER = Path(__file__).resolve().parent.parent / "roster.json"
VETO_CAP = 4.0
SPLIT_SPREAD = 4.0


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"{path} not found")
    except json.JSONDecodeError as e:
        fail(f"{path} is not valid JSON: {e}")


def resolve_weights(data, roster):
    seats = list(data["seats"])
    weights = data.get("weights")
    if not weights:
        board = roster["boards"].get(data.get("type", ""), {}).get("full")
        if board is None:
            fail(f"no 'weights' given and unknown type {data.get('type')!r}")
        weights = {s: board.get(s, roster["on_call_default_weight"]) for s in seats}
    missing = [s for s in seats if s not in weights]
    if missing:
        fail(f"no weight for seat(s): {', '.join(missing)}")
    total = sum(weights[s] for s in seats)
    if total <= 0:
        fail("weights sum to zero")
    return {s: weights[s] * 100.0 / total for s in seats}


def label_for(score, vetoed, min_seat):
    if vetoed or score <= VETO_CAP:
        return "NO-GO: REDESIGN REQUIRED"
    if score >= 7.5 and min_seat >= 5.0:
        return "GO"
    if score >= 6.0:
        return "GO WITH CONDITIONS"
    return "MAJOR REVISION"


def score_session(data, roster):
    options = data.get("options")
    if not options:
        fail("scores.json has no 'options'")
    veto_seats = set(roster["veto_seats"])
    weights = resolve_weights(data, roster)

    for seat, entry in data["seats"].items():
        for opt, val in entry.get("scores", {}).items():
            if opt not in options:
                fail(f"seat {seat} scored unknown option {opt!r}")
            if not 1.0 <= float(val) <= 10.0:
                fail(f"seat {seat} score for {opt} is {val}; must be 1.0-10.0")
        if entry.get("vetoes") and seat not in veto_seats:
            print(f"WARNING: {seat} is not a veto seat; its vetoes are ignored", file=sys.stderr)

    results = {}
    for opt in options:
        rated = {s: float(e["scores"][opt]) for s, e in data["seats"].items() if opt in e.get("scores", {})}
        if not rated:
            fail(f"no seat scored option {opt}")
        wsum = sum(weights[s] for s in rated)
        raw = sum(weights[s] * v for s, v in rated.items()) / wsum
        vetoed_by = [s for s, e in data["seats"].items() if s in veto_seats and opt in e.get("vetoes", [])]
        final = min(raw, VETO_CAP) if vetoed_by else raw
        spread = max(rated.values()) - min(rated.values())
        results[opt] = {
            "label": options[opt],
            "raw": round(raw, 2),
            "final": round(final, 2),
            "vetoed_by": vetoed_by,
            "cap_fired": bool(vetoed_by) and raw > VETO_CAP,
            "min_seat": min(rated.values()),
            "spread": round(spread, 2),
            "split": spread >= SPLIT_SPREAD,
            "seat_scores": rated,
        }
        results[opt]["verdict"] = label_for(final, bool(vetoed_by), results[opt]["min_seat"])

    ranking = sorted(results, key=lambda o: (-results[o]["final"], o))
    return {"weights": {s: round(w, 1) for s, w in weights.items()}, "options": results, "ranking": ranking}


def print_board(result, previous=None):
    opts = list(result["options"])
    print("| Seat | Weight | " + " | ".join(opts) + " |")
    print("|---|---|" + "---|" * len(opts))
    for seat, w in result["weights"].items():
        cells = []
        for o in opts:
            v = result["options"][o]["seat_scores"].get(seat)
            cell = "-" if v is None else f"{v:.1f}"
            if previous and v is not None:
                old = previous["options"].get(o, {}).get("seat_scores", {}).get(seat)
                if old is not None:
                    cell += f" ({v - old:+.1f})"
            cells.append(cell)
        print(f"| {seat} | {w:.0f}% | " + " | ".join(cells) + " |")
    finals = []
    for o in opts:
        r = result["options"][o]
        cell = f"**{r['final']:.2f}**"
        if previous and o in previous["options"]:
            cell += f" ({r['final'] - previous['options'][o]['final']:+.2f})"
        finals.append(cell)
    print("| **Weighted** | 100% | " + " | ".join(finals) + " |")
    print()
    for o in result["ranking"]:
        r = result["options"][o]
        notes = []
        if r["vetoed_by"]:
            notes.append(f"VETO by {', '.join(r['vetoed_by'])}" + (f", cap fired (raw {r['raw']:.2f})" if r["cap_fired"] else ""))
        if r["split"]:
            notes.append(f"SPLIT (spread {r['spread']:.1f})")
        extra = f" [{'; '.join(notes)}]" if notes else ""
        print(f"{o}. {r['label']}: {r['final']:.2f} -> {r['verdict']}{extra}")
    top = result["ranking"][0]
    print()
    print(f"TOP OPTION: {top} ({result['options'][top]['label']}) - {result['options'][top]['verdict']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("session")
    ap.add_argument("--previous", help="earlier session folder, to show score changes (rerun mode)")
    args = ap.parse_args()

    roster = load_json(ROSTER)
    session = Path(args.session)
    result = score_session(load_json(session / "scores.json"), roster)

    previous = None
    if args.previous:
        previous = score_session(load_json(Path(args.previous) / "scores.json"), roster)

    (session / "scores-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print_board(result, previous)


if __name__ == "__main__":
    main()
