#!/usr/bin/env python3
"""Sunday announcements builder.

  python3 build.py proposal weeks/<sunday>.json   > proposal.html   (email body to Ben)
  python3 build.py final    weeks/<sunday>.json   > final.html      (email body to Joe/Mark/host)
  python3 build.py docx     weeks/<sunday>.json   docs/<sunday>.docx
  python3 build.py draft    weeks/<sunday>.json   draft.docx       (New Here + recommended picks, for the proposal)

Week file: see SKILL.md. "New Here" always comes from new-here.json and always runs first.
HTML sticks to tags the Outlook connector allows (h2, h3, p, ul, li, b, i, hr, a).
"""
import copy, html, json, sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGES = "https://benslater01.github.io/firstnaz-skills/announcements/docs/"


def e(s):
    return html.escape(s, quote=False)


def short(d):
    d = date.fromisoformat(d)
    return f"{d.month}.{d.day}"


def long(d):
    d = date.fromisoformat(d)
    return d.strftime("%B ") + str(d.day)


def new_here():
    return json.loads((HERE / "new-here.json").read_text())


def block(title, bullets):
    items = "".join(f"<li>{e(b)}</li>" for b in bullets)
    return f"<h3>{e(title)}</h3><ul>{items}</ul>"


def proposal(w):
    nh = new_here()
    out = [f"<p>Here are this week's options for Sunday, {long(w['sunday'])}. "
           "New Here runs every week. Pick up to 2 more.</p>"]
    if w.get("host"):
        out.append(f"<p><b>Service host:</b> {e(w['host'])}</p>")
    rec = w.get("recommended") or [o["id"] for o in w["options"][:2]]
    if w.get("draftUrl"):
        out.append(f"<p><b>Draft doc:</b> <a href=\"{w['draftUrl']}\">Sunday Announcements {short(w['sunday'])} (DRAFT)</a>. "
                   f"That's exactly what goes out if you pick {' and '.join(rec)}. "
                   "Your picks and edits replace it in the final.</p>")
    out.append("<hr><h2>Always: New Here</h2>")
    out.append(block(nh["title"], nh["bullets"]))
    out.append("<hr><h2>Options</h2>")
    for o in w["options"]:
        out.append(f"<h3>{e(o['id'])}. {e(o['title'])}</h3>")
        meta = [f"<b>When:</b> {e(o['when'])}" if o.get("when") else "",
                f"<b>Source:</b> {e(o['source'])}" if o.get("source") else "",
                f"<b>Why now:</b> {e(o['why'])}" if o.get("why") else ""]
        out.append("<p>" + "<br>".join(m for m in meta if m) + "</p>")
        out.append("<ul>" + "".join(f"<li>{e(b)}</li>" for b in o["bullets"]) + "</ul>")
        for f in o.get("flags", []):
            out.append(f"<p><i>Check: {e(f)}</i></p>")
    if w.get("skipped"):
        out.append("<hr><h2>Looked at, didn't make the cut</h2><ul>"
                   + "".join(f"<li>{e(s)}</li>" for s in w["skipped"]) + "</ul>")
    if w.get("notes"):
        out.append("<hr><h2>Notes</h2><ul>" + "".join(f"<li>{e(n)}</li>" for n in w["notes"]) + "</ul>")
    out.append("<hr><p><b>Reply with your picks</b> (for example: \"A and C\"), plus any edits. "
               "You can also paste your own wording or add something new. "
               "Final goes out Friday afternoon once you reply.</p>")
    return "".join(out)


def recommended(w):
    ids = w.get("recommended") or [o["id"] for o in w["options"][:2]]
    return [{"title": o["title"], "bullets": o["bullets"]} for o in w["options"] if o["id"] in ids]


def final_blocks(w, draft=False):
    nh = new_here()
    return [{"title": nh["title"], "bullets": nh["bullets"]}] + (recommended(w) if draft else w["final"])


def final(w):
    out = [f"<p>Here are the announcements for Sunday, {long(w['sunday'])}. "
           "These are a guide, not a script. Say it your way.</p>"]
    for b in final_blocks(w):
        out.append(block(b["title"], b["bullets"]))
    out.append(f"<p>Word version: <a href=\"{PAGES}{w['sunday']}.docx\">Sunday Announcements {short(w['sunday'])}</a></p>")
    out.append("<p>Thanks!<br>Ben</p>")
    return "".join(out)


def set_bullet(p, num_id):
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    ppr = p._p.get_or_add_pPr()
    num = OxmlElement("w:numPr")
    ilvl = OxmlElement("w:ilvl"); ilvl.set(qn("w:val"), "0")
    nid = OxmlElement("w:numId"); nid.set(qn("w:val"), str(num_id))
    num.append(ilvl); num.append(nid)
    ppr.append(num)


def make_docx(w, out_path, draft=False):
    import docx
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    d = docx.Document(str(HERE / "template.docx"))
    t = d.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t.add_run(f"Sunday Announcements {short(w['sunday'])}" + (" (DRAFT)" if draft else "")).bold = True
    for i, b in enumerate(final_blocks(w, draft)):
        d.add_paragraph(b["title"])
        for line in b["bullets"]:
            p = d.add_paragraph(line, style="List Paragraph")
            set_bullet(p, min(i + 1, 5))
    d.save(out_path)


if __name__ == "__main__":
    mode, path = sys.argv[1], sys.argv[2]
    w = json.loads(Path(path).read_text())
    if mode == "proposal":
        print(proposal(w))
    elif mode == "final":
        print(final(w))
    elif mode == "docx":
        make_docx(w, sys.argv[3])
    elif mode == "draft":
        make_docx(w, sys.argv[3], draft=True)
    else:
        sys.exit("mode must be proposal, final or docx")
