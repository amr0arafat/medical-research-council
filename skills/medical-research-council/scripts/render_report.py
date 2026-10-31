#!/usr/bin/env python3
"""Render a council session as one self-contained HTML page.

Usage:
    python3 render_report.py <session-folder>

Reads verdict.md, scores-result.json (from score.py), round-1.md, and
round-2.md, and writes <session-folder>/report.html with no external
requests. Run score.py and write verdict.md first.
"""
import html
import json
import re
import sys
from pathlib import Path

BADGES = {
    "GO": ("#1a7f37", "#e6f4ea"),
    "GO WITH CONDITIONS": ("#9a6700", "#fff4d6"),
    "MAJOR REVISION": ("#bc4c00", "#fff1e5"),
    "NO-GO: REDESIGN REQUIRED": ("#cf222e", "#ffebe9"),
}


def inline(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"\bPMID:?\s*(\d{4,9})\b",
                  r'<a href="https://pubmed.ncbi.nlm.nih.gov/\1/">PMID \1</a>', text)
    text = re.sub(r"\b(NCT\d{8})\b", r'<a href="https://clinicaltrials.gov/study/\1">\1</a>', text)
    return text


def markdown(md):
    """Small Markdown subset: headings, lists, tables, paragraphs, rules."""
    out, para, lst, table = [], [], None, []

    def flush():
        nonlocal para, lst, table
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []
        if lst:
            tag, items = lst
            out.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{tag}>")
            lst = None
        if table:
            rows = [[c.strip() for c in r.strip("|").split("|")] for r in table if not re.match(r"^\|[\s|:-]+\|$", r)]
            head, body = rows[0], rows[1:]
            out.append('<div class="scroll"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in head)
                       + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
                       + "</tbody></table></div>")
            table = []

    for line in md.splitlines():
        s = line.rstrip()
        if s.startswith("|"):
            if para or lst:
                flush()
            table.append(s)
            continue
        if table:
            flush()
        m = re.match(r"^(#{1,4})\s+(.*)", s)
        if m:
            flush()
            level = min(len(m.group(1)) + 1, 4)
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
        elif re.match(r"^\s*[-*]\s+", s):
            if para:
                flush()
            item = re.sub(r"^\s*[-*]\s+", "", s)
            if lst and lst[0] == "ul":
                lst[1].append(item)
            else:
                flush()
                lst = ("ul", [item])
        elif re.match(r"^\s*\d+\.\s+", s):
            if para:
                flush()
            item = re.sub(r"^\s*\d+\.\s+", "", s)
            if lst and lst[0] == "ol":
                lst[1].append(item)
            else:
                flush()
                lst = ("ol", [item])
        elif s.strip() == "---":
            flush()
            out.append("<hr>")
        elif not s.strip():
            flush()
        else:
            if lst:
                flush()
            para.append(s.strip())
    flush()
    return "\n".join(out)


def sections(md):
    parts = re.split(r"^## (.+)$", md, flags=re.M)
    return {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


def cell_colour(v):
    # Light tints keep the printed number readable; colour is never the only signal.
    if v >= 7:
        return "#d8f0dc"
    if v >= 5:
        return "#fdf0c8"
    if v > 4:
        return "#fde2cc"
    return "#fbd5d5"


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    s = Path(sys.argv[1])
    try:
        verdict = (s / "verdict.md").read_text(encoding="utf-8")
        result = json.loads((s / "scores-result.json").read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        print(f"ERROR: {e.filename} not found. Run score.py and write verdict.md first.", file=sys.stderr)
        sys.exit(1)

    title_m = re.search(r"^# (.+)$", verdict, re.M)
    title = title_m.group(1) if title_m else "Medical Research Council Verdict"
    meta_m = re.search(r"^# .+\n\n(.+)$", verdict, re.M)
    meta = meta_m.group(1) if meta_m else ""
    secs = sections(verdict)
    top = result["ranking"][0]
    label = result["options"][top]["verdict"]
    fg, bg = BADGES.get(label, ("#444", "#eee"))
    call_key = next((k for k in secs if "call" in k.lower()), None)
    call_text = secs.get(call_key, "") if call_key else ""
    call_text = re.sub(r"^\*\*.+?\*\*:\s*", "", call_text)

    bars = []
    for o in result["ranking"]:
        r = result["options"][o]
        pct = r["final"] * 10
        cap = (f'<span class="capnote">veto cap fired (raw {r["raw"]:.2f})</span>' if r["cap_fired"] else "")
        bars.append(f'<div class="bar-row"><div class="bar-label"><strong>{o}</strong> {html.escape(r["label"])}</div>'
                    f'<div class="bar-track"><div class="bar" style="width:{pct:.0f}%;background:{BADGES.get(r["verdict"], ("#444",))[0]}"></div></div>'
                    f'<div class="bar-val">{r["final"]:.2f} · {html.escape(r["verdict"])} {cap}</div></div>')

    opts = list(result["options"])
    heat = ['<div class="scroll"><table class="heat"><thead><tr><th>Seat</th><th>Weight</th>'
            + "".join(f"<th>{o}</th>" for o in opts) + "</tr></thead><tbody>"]
    for seat, w in result["weights"].items():
        row = f"<tr><th>{html.escape(seat.title())}</th><td>{w:.0f}%</td>"
        for o in opts:
            v = result["options"][o]["seat_scores"].get(seat)
            vetoed = seat in result["options"][o]["vetoed_by"]
            row += ("<td>-</td>" if v is None else
                    f'<td style="background:{cell_colour(v)}">{v:.1f}{" <b>VETO</b>" if vetoed else ""}</td>')
        heat.append(row + "</tr>")
    heat.append("<tr class='total'><th>Weighted</th><td>100%</td>"
                + "".join(f"<td>{result['options'][o]['final']:.2f}</td>" for o in opts) + "</tr></tbody></table></div>")

    body_secs = []
    for name, text in secs.items():
        if name == call_key or "scoreboard" in name.lower():
            continue
        body_secs.append(f"<section><h2>{inline(name)}</h2>{markdown(text)}</section>")

    details = []
    for fname, heading in (("round-1.md", "Round 1 cards"), ("round-2.md", "Peer review (anonymisation map revealed)")):
        f = s / fname
        if f.exists():
            for name, text in sections(f.read_text(encoding="utf-8")).items():
                details.append(f"<details><summary>{heading}: {html.escape(name)}</summary>{markdown(text)}</details>")

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Council Verdict</title>
<style>
:root{{--fg:#1f2328;--muted:#59636e;--line:#d1d9e0;--bg:#ffffff;--soft:#f6f8fa}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
main{{max-width:960px;margin:0 auto;padding:24px 16px 64px}}
h1{{font-size:1.6rem;line-height:1.25;margin:0 0 4px}} h2{{font-size:1.2rem;margin:28px 0 8px;border-bottom:1px solid var(--line);padding-bottom:4px}}
h3,h4{{font-size:1rem}} .meta{{color:var(--muted);margin:0 0 20px}}
.call{{border:1px solid var(--line);border-radius:10px;padding:16px;background:var(--soft)}}
.badge{{display:inline-block;font-weight:700;padding:4px 10px;border-radius:999px;color:{fg};background:{bg};border:1px solid {fg};margin-bottom:8px}}
.bar-row{{display:grid;grid-template-columns:minmax(120px,1fr) 2fr;gap:4px 12px;margin:10px 0}}
.bar-track{{background:var(--soft);border:1px solid var(--line);border-radius:6px;height:18px;overflow:hidden}}
.bar{{height:100%}} .bar-val{{grid-column:2;color:var(--muted);font-size:.9rem}} .capnote{{color:#cf222e;font-weight:600}}
.scroll{{overflow-x:auto}} table{{border-collapse:collapse;width:100%;font-size:.92rem}}
th,td{{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}} thead th{{background:var(--soft)}}
.heat td{{text-align:center;font-variant-numeric:tabular-nums}} .heat tr.total td{{font-weight:700}}
details{{border:1px solid var(--line);border-radius:8px;padding:8px 12px;margin:8px 0}} summary{{cursor:pointer;font-weight:600}}
a{{color:#0969da}} code{{background:var(--soft);padding:0 4px;border-radius:4px}} footer{{color:var(--muted);font-size:.85rem;margin-top:32px}}
@media (max-width:560px){{.bar-row{{grid-template-columns:1fr}} .bar-val{{grid-column:1}}}}
</style></head><body><main>
<h1>{inline(title)}</h1><p class="meta">{inline(meta)}</p>
<div class="call"><div class="badge">{html.escape(label)}</div>{markdown(call_text)}</div>
<h2>Option scores</h2>{''.join(bars)}
<h2>Seat by option</h2>{''.join(heat)}
{''.join(body_secs)}
<h2>Full council record</h2>{''.join(details)}
<footer>Generated by the medical-research-council skill. Simulated specialist review, not ethics, regulatory, or statistical sign-off.</footer>
</main></body></html>
"""
    (s / "report.html").write_text(page, encoding="utf-8")
    print(f"Wrote {s / 'report.html'}")


if __name__ == "__main__":
    main()
