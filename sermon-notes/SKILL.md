---
name: sermon-notes
description: Weekly interactive sermon notes for firstnaz.net/sermon-notes: build the Friday preview from Joe/Austin/Ben notes in Outlook, handle Saturday duplicates, publish Sunday 12:01 AM.
---

# Weekly sermon notes update

All paths below are relative to this `sermon-notes/` folder (repo: benslater01/firstnaz-skills).
- Live page: https://www.firstnaz.net/sermon-notes (embeds https://benslater01.github.io/firstnaz-skills/sermon-notes/widget.js)
- Preview link for Ben: https://benslater01.github.io/firstnaz-skills/sermon-notes/preview/

Each week only `content.json` changes. `widget.js` holds the layout and should not need edits.

## Weekly flow

**Friday (prepare preview)**
1. Search Bslater@firstnaz.net's Outlook for this week's notes, received since Wednesday, from trusted senders only: Pastor Joe Proudfoot (jproudfoot@firstnaz.net), Austin Swallow Jr. (aswallow819@gmail.com), or Ben himself (Bslater@firstnaz.net) with "Sermon Notes" in the subject. Read the body and any attachment. If nothing yet, stop quietly.
2. Write the new week into `preview/content.json` using the rules below. Do not touch `content.json`.
3. Check `preview/index.html` renders in a browser with no console errors.
4. Commit and push to `main`.
5. Email Bslater@firstnaz.net a preview: the preview link, the sermon title, and every blank with its answer, so typos are easy to spot. Say it goes live Sunday 12:01 AM and that replying with corrections (or "hold") will be picked up.

**Sunday 12:01 AM (go live)**
1. Check Ben's inbox. If he replied "hold", or a "which version?" question is unanswered, publish nothing and tell him. Apply any corrections he sent. If Ben himself emailed notes late Saturday (after the last preview), build from them and publish without a preview: he approved this exception. Late notes from Joe or Austin alone don't qualify; ask Ben instead.
2. Copy the current `content.json` to `archive/<previous sermon date>.json`.
3. Copy `preview/content.json` to `content.json`. Commit and push.
4. Email Ben a short confirmation.

**Saturday 12:47 PM and 7:47 PM (Austin's notes and late notes)**
Austin always sends notes Saturday morning. Most weeks they duplicate Joe's Friday notes.
- Same sermon and content as the preview: usual duplicate. Do nothing, no email.
- Different sermon, or no preview yet: build the preview from them and email Ben.
- Same sermon but real differences, or unclear which is for tomorrow: leave the preview alone and ask Ben which version ("Sermon notes: which version?"). One reminder on the evening run if unanswered.
- No notes at all: remind Ben (midday, then a final evening reminder).

**Never guess.** When anything is unclear, ask Ben a short, specific question by email.

## Formatting rules (from the original template)
BLANKS
Any word or phrase that's underlined in your sermon notes doc becomes
a fill-in blank people type into (in addition to the discussion
questions). To mark one, write {blank} in place of that word/phrase
in the "template" or "detail" string, and put the actual word in the
matching "answer" field. See the building blocks list and the "Their
Faith Story" points below for examples.


BRANDING
Fonts and background are set to "inherit" so this automatically
matches whatever font and page background firstnaz.net is already
using. There's one accent color (--bb-accent, near the top of the
<style> block) used for section markers, blanks, and buttons — change
that single hex value to match your brand color exactly if you'd like
it closer.

PERSISTENCE NOTE
There's no login on the site, so nothing is saved automatically. People
fill in their answers, then use "Print" (to paper or Save as PDF) or
"Download notes" (a text file) to keep what they wrote.

SERIES-TO-SERIES NOTE
The outline shape (how points/subpoints are grouped) is not fixed —
it's expected to change from series to series as sermon notes are
structured differently. Only the overall CSS/layout and the two rules
below stay constant: (1) anything underlined in the source notes doc
becomes a {blank}, and (2) outline.points is always an array of
{ label, ref, subpoints: [{ template, detail }] } — flexible enough to
represent a point/subpoint outline, a statement-plus-quote pairing, or
a short list, whatever that week's notes call for. When mapping a new
week, preserve the source document's own formatting/structure as
closely as this shape allows, rather than normalizing it to match a
previous week. A subpoint's "detail" line is always the supporting
scripture/quote shown under its statement, even if the source document
prints the quote above the statement — the quote supports the point,
so it stays in the detail slot regardless of print order.

A NOTE ON point.label
point.label renders as plain text (no {blank} support), so if a
statement has an underlined word, it needs to live in a subpoint's
"template" (which does support blanks), not in the point's own label.
Use the label for a short, blank-free summary of the point instead.

STANDALONE SERMONS (not part of a series)
Some weeks are a one-off message rather than part of a running series
(e.g. a guest speaker). For those, there is no series name to put in
the small caps "series" line at the top — use that slot for the
speaker's name instead (e.g. "Pastor David Husko"), put the date alone
in weekDate (no "Week N ·" prefix), and leave buildingBlocksTitle/
buildingBlocks empty as usual.
