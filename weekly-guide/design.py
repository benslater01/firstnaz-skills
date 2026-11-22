#!/usr/bin/env python3
"""Designed (Gloo-style) Weekly Guide HTML, sent through Ben's Power Automate flow.

  python3 design.py email  guide.json                 > guide.html   (preview)
  python3 design.py proof  guide.json notes.json      > proof.html
  python3 design.py outbox guide.json recipients.txt  > outbox.json  (the real send)
  python3 design.py outbox-proof guide.json notes.json > outbox.json (proof to Ben only)

The outbox JSON is what goes in OneDrive "Weekly Guide/Outbox". Its shape is
{"to": "...", "bcc": "a@x;b@y", "subject": "...", "html": "..."}.
recipients.txt: one email per line (from `build.py batches`, flattened).
Image "src" in guide.json is a file name under img/ (see img.py) or a full https URL.
Layout mirrors the Gloo/Unlayer guide, rebuilt with plain tables so Outlook
desktop renders it too: 500px column, #F7F8F9 background, Arial.
"""
import html, json, sys
from datetime import date

BEN = "Bslater@firstnaz.net"
IMG = "https://benslater01.github.io/sermon-notes/weekly-guide/img/"
LOGO = IMG + "logo-1n.png"
FONT = "arial,helvetica,sans-serif"
HEAVY = "'arial black',AvenirNext-Heavy,'avant garde',arial"


def e(s):
    return html.escape(s, quote=True)


def row(inner, pad="10px"):
    return f'<tr><td style="padding:{pad};font-family:{FONT};">{inner}</td></tr>'


def divider():
    return row('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
               '<tr><td style="border-top:1px solid #BBBBBB;font-size:0;line-height:0;">&nbsp;</td></tr></table>')


def button(label, url, bg="#000000", fg="#ffffff"):
    return row(
        '<table role="presentation" align="center" cellpadding="0" cellspacing="0" border="0"><tr>'
        f'<td align="center" bgcolor="{bg}" style="background-color:{bg};border-radius:4px;">'
        f'<a href="{e(url)}" target="_blank" style="display:inline-block;padding:8px 20px;font-family:{FONT};'
        f'font-size:14px;line-height:120%;color:{fg};text-decoration:none;"><strong>{e(label)}</strong></a>'
        '</td></tr></table>', pad="12px")


def image(src, width, href=None, alt=""):
    img = (f'<img src="{e(src)}" width="{width}" alt="{e(alt)}" border="0" '
           f'style="display:block;width:100%;max-width:{width}px;height:auto;border:0;outline:none;margin:0 auto;">')
    if href:
        img = f'<a href="{e(href)}" target="_blank">{img}</a>'
    return row(f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center">{img}</td></tr></table>')


def text(paras, size=14, align="left", color="#000000"):
    body = "".join(f'<p style="margin:0 0 14px 0;line-height:140%;">{p}</p>' for p in paras)
    return row(f'<div style="font-family:{FONT};font-size:{size}px;color:{color};line-height:140%;text-align:{align};">{body}</div>')


def heading(t, size=22, align="left", heavy=False, tag="h1"):
    fam = HEAVY if heavy else FONT
    return row(f'<{tag} style="margin:0;line-height:140%;text-align:{align};font-family:{fam};'
               f'font-size:{size}px;font-weight:400;color:#000000;">{t}</{tag}>')


def build(g, notes=None):
    today = date.fromisoformat(g["sendDate"])
    r = []
    if notes is not None:
        items = "".join(f'<li style="margin:0 0 6px 0;">{e(x)}</li>' for x in notes.get("items", []))
        r.append(row(
            '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td bgcolor="#FFF4CC" style="background-color:#FFF4CC;border:1px solid #E6C34D;border-radius:6px;padding:14px;font-family:{FONT};font-size:14px;line-height:140%;color:#000;">'
            '<p style="margin:0 0 8px 0;"><strong>Weekly Guide proof</strong> (not sent yet)</p>'
            f'<ul style="margin:0 0 8px 0;padding-left:18px;">{items}</ul>'
            '<p style="margin:0;">Reply <strong>SEND</strong> to approve, or reply with changes. Approved guides go out Friday around 2 PM.</p>'
            '</td></tr></table>', pad="20px 10px 0 10px"))
    r.append(image(LOGO, 126, alt="FirstNaz"))
    r.append(heading("WEEKLY GUIDE", 22, "center", heavy=True))
    intro = [e(g["greeting"])] + [e(p) for p in g["intro"]] + ["<br>".join(e(x) for x in g["signoff"])]
    r.append(text(intro))
    r.append(divider())

    r.append(heading("What's Coming Up?", 22))
    lines = [f"<em>{e(x)}</em>" for x in g.get("recurring", [])]
    ups = sorted([u for u in g.get("upcoming", []) if date.fromisoformat(u["date"]) >= today], key=lambda u: u["date"])
    block = '<p style="margin:0;line-height:140%;">' + "<br>".join(lines) + "</p>" if lines else ""
    if ups:
        ul = []
        for u in ups:
            s = f"<strong>{e(u['label'])} | {e(u['title'])}</strong>"
            if u.get("detail"):
                s += f" {e(u['detail'])}"
            if u.get("note"):
                s += f"<br>{e(u['note'])}"
            ul.append(s)
        block += '<p style="margin:14px 0 0 0;line-height:140%;">' + "<br>".join(ul) + "</p>"
    r.append(row(f'<div style="font-family:{FONT};font-size:14px;line-height:140%;color:#000;">{block}</div>'))
    r.append(button("View Church Calendar", g["calendarUrl"]))
    r.append(divider())

    for s in g.get("seasonal", []):
        if s.get("until") and date.fromisoformat(s["until"]) < today:
            continue
        if s.get("heading"):
            r.append(heading(e(s["heading"]), 22))
        lead = ""
        if s.get("bold"):
            lead += f"<strong>{e(s['bold'])}</strong>"
        if s.get("text"):
            lead += (" " if lead else "") + e(s["text"])
        if lead:
            r.append(heading(lead, 18, tag="h3"))
        if s.get("paragraphs"):
            r.append(text([e(p) for p in s["paragraphs"]]))
        for im in s.get("images", []):
            if im.get("until") and date.fromisoformat(im["until"]) < today:
                continue
            src = im["src"] if im["src"].startswith("https://") else IMG + im["src"]
            r.append(image(src, 480, im.get("href"), im.get("alt", "")))
        if s.get("link"):
            r.append(button(s["link"]["label"], s["link"]["url"], bg=s["link"].get("color", "#ff914d"), fg="#000000"))
        r.append(divider())

    sm = g.get("sermon")
    if sm and sm.get("videoId"):
        url = f"https://youtu.be/{sm['videoId']}"
        r.append(heading("Last Week's Sermon", 20, heavy=True, tag="h2"))
        r.append(image(f"https://i.ytimg.com/vi/{sm['videoId']}/hqdefault.jpg", 440, url, alt=f"Watch: {sm['title']}"))
        r.append(text([f'<a href="{e(url)}" target="_blank" style="color:#000000;font-weight:bold;">{e(sm["title"])}</a>', e(sm["blurb"])], align="center"))

    foot = "<br>".join(e(x) for x in g["footer"])
    rows = "\n".join(r)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(g['subject'])}</title>
<style>body{{margin:0;padding:0}} table,td{{border-collapse:collapse}} a[x-apple-data-detectors=true]{{color:inherit!important;text-decoration:none!important}}
@media only screen and (max-width:520px){{ .wg-col{{width:100%!important}} }}</style></head>
<body style="margin:0;padding:0;background-color:#F7F8F9;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#F7F8F9" style="background-color:#F7F8F9;">
<tr><td align="center" style="padding:20px 0;">
<table role="presentation" class="wg-col" width="500" cellpadding="0" cellspacing="0" border="0" style="width:500px;max-width:500px;">
{rows}
<tr><td align="center" style="padding:30px 10px 20px;font-family:{FONT};font-size:11px;line-height:150%;color:#666666;border-top:1px solid #eeeeee;">{foot}</td></tr>
</table></td></tr></table></body></html>"""


if __name__ == "__main__":
    mode = sys.argv[1]
    g = json.load(open(sys.argv[2]))
    if mode == "email":
        print(build(g))
    elif mode == "proof":
        print(build(g, json.load(open(sys.argv[3]))))
    elif mode == "outbox":
        rcpts = [l.strip() for l in open(sys.argv[3]) if l.strip()]
        if not rcpts or len(rcpts) > 450:
            sys.exit("design.py: recipient count looks wrong: %d" % len(rcpts))
        print(json.dumps({"to": BEN, "bcc": ";".join(rcpts), "subject": g["subject"], "html": build(g)}))
    elif mode == "outbox-proof":
        print(json.dumps({"to": BEN, "bcc": BEN, "subject": f"Weekly Guide proof: {g['sendDate']}",
                          "html": build(g, json.load(open(sys.argv[3])))}))
