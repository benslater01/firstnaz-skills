#!/usr/bin/env python3
"""Build the Weekly Guide email from guide.json.

The Outlook connector only accepts these tags, with no attributes except
a[href]: p, br, a, b/strong, i/em, ul/ol/li, h1-h6, table parts, code,
pre, hr, div, strike. No images, styles, classes or spans. This script
only emits those and checks its own output before writing it.

  python3 build.py guide  [guide.json] > out.html
  python3 build.py proof  [guide.json] notes.json > proof.html
  python3 build.py batches recipients.json skip.json > batches.json

notes.json for a proof: {"items": ["line", ...]}  (plain text, one per bullet)
recipients.json: [{"id": "123", "name": "A B", "email": "a@b.com"}, ...]
"""
import html, json, re, sys
from datetime import date

ALLOWED = {"p", "br", "a", "b", "strong", "i", "em", "ul", "ol", "li",
           "h1", "h2", "h3", "h4", "h5", "h6", "table", "thead", "tbody",
           "tr", "th", "td", "code", "pre", "hr", "div", "strike"}
BEN = "Bslater@firstnaz.net"
BATCH = 49  # connector cap is 50 per message, Ben takes the To slot


def e(s):
    return html.escape(s, quote=False)


def validate(out):
    for m in re.finditer(r"<\s*(/?)\s*([a-zA-Z0-9]+)([^>]*)>", out):
        tag, attrs = m.group(2).lower(), m.group(3).strip().rstrip("/").strip()
        if tag not in ALLOWED:
            sys.exit(f"build.py: disallowed tag <{tag}>")
        if attrs and not (tag == "a" and re.fullmatch(r'href="https://[^"\s]+"', attrs)):
            sys.exit(f"build.py: disallowed attributes on <{tag}>: {attrs}")
    if "<!" in out or "<?" in out:
        sys.exit("build.py: comments/doctype not allowed")
    return out


def guide_html(g, today=None):
    today = today or date.fromisoformat(g["sendDate"])
    p = []
    p.append("<h1>WEEKLY GUIDE</h1>")
    p.append(f"<p>{e(g['greeting'])}</p>")
    for para in g["intro"]:
        p.append(f"<p>{e(para)}</p>")
    p.append("<p>" + "<br>".join(e(x) for x in g["signoff"]) + "</p>")
    p.append("<hr>")

    p.append("<h2>What's Coming Up?</h2>")
    if g.get("recurring"):
        p.append("<p>" + "<br>".join(f"<i>{e(x)}</i>" for x in g["recurring"]) + "</p>")
    items = [u for u in g.get("upcoming", []) if date.fromisoformat(u["date"]) >= today]
    if items:
        lines = []
        for u in sorted(items, key=lambda u: u["date"]):
            line = f"<b>{e(u['label'])} | {e(u['title'])}</b>"
            if u.get("detail"):
                line += f" {e(u['detail'])}"
            if u.get("note"):
                line += f"<br>{e(u['note'])}"
            lines.append(line)
        p.append("<p>" + "<br>".join(lines) + "</p>")
    p.append(f'<p><a href="{g["calendarUrl"]}"><b>View Church Calendar</b></a></p>')
    p.append("<hr>")

    for s in g.get("seasonal", []):
        if s.get("until") and date.fromisoformat(s["until"]) < today:
            continue
        if s.get("heading"):
            p.append(f"<h2>{e(s['heading'])}</h2>")
        body = ""
        if s.get("bold"):
            body += f"<b>{e(s['bold'])}</b>"
        if s.get("text"):
            body += (" " if body else "") + e(s["text"])
        if body:
            p.append(f"<h3>{body}</h3>" if not s.get("heading") else f"<p>{body}</p>")
        for para in s.get("paragraphs", []):
            p.append(f"<p>{e(para)}</p>")
        if s.get("link"):
            p.append(f'<p><a href="{s["link"]["url"]}"><b>{e(s["link"]["label"])}</b></a></p>')
        p.append("<hr>")

    sm = g.get("sermon")
    if sm and sm.get("videoId"):
        p.append("<h2>Last Week's Sermon</h2>")
        p.append(f'<p><a href="https://youtu.be/{sm["videoId"]}"><b>Watch: {e(sm["title"])}</b></a></p>')
        p.append(f"<p>{e(sm['blurb'])}</p>")
        p.append("<hr>")

    p.append("<p>" + "<br>".join(e(x) for x in g["footer"]) + "</p>")
    return validate("<div>" + "\n".join(p) + "</div>")


def proof_html(g, notes):
    p = ["<p><b>Weekly Guide proof</b> (not sent yet)</p>"]
    if notes.get("items"):
        p.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in notes["items"]) + "</ul>")
    p.append("<p>Reply <b>SEND</b> to approve, or reply with changes. "
             "Approved guides go out Friday around 2 PM.</p>")
    p.append("<hr><hr>")
    body = guide_html(g)
    return validate("<div>" + "\n".join(p) + "</div>" + body)


def batches(recipients, skip):
    skip_ids = {str(x) for x in skip.get("personIds", [])}
    seen, keep, skipped = set(), [], []
    for r in recipients:
        em = (r.get("email") or "").strip()
        if str(r.get("id")) in skip_ids:
            skipped.append(r["name"]); continue
        if not em or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", em):
            skipped.append(r["name"] + " (no email)"); continue
        if em.lower() in seen or em.lower() == BEN.lower():
            continue
        seen.add(em.lower()); keep.append(em)
    return {"total": len(keep), "skipped": skipped,
            "batches": [keep[i:i + BATCH] for i in range(0, len(keep), BATCH)]}


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "guide"
    if mode == "batches":
        r = json.load(open(sys.argv[2])); s = json.load(open(sys.argv[3]))
        print(json.dumps(batches(r, s), indent=1))
    else:
        g = json.load(open(sys.argv[2] if len(sys.argv) > 2 else "guide.json"))
        if mode == "proof":
            print(proof_html(g, json.load(open(sys.argv[3]))))
        else:
            print(guide_html(g))
