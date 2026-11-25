---
name: announcements
description: Sunday morning announcements: Tuesday options + proposal to Ben, Friday final (New Here plus up to 2, or up to 3 when Ben adds his own) to Joe, Mark and any alternate service host.
---

# Sunday Announcements

Ben Slater (Bslater@firstnaz.net) writes an outlined announcement guide for each Sunday. Every week: **New Here** (permanent, always first) plus **up to 2** more. Ben picks the extras. When Ben manually adds his own announcement(s), the week can go up to **4 total** (New Here plus 3); this automation finds the options, drafts them, and sends the final once he approves.

Read `STYLE.md` before writing a single bullet. Text must sound like a person wrote it: short, punchy, value first, one next step. No em dashes, anywhere (emails included).

Files:
- `new-here.json`: the permanent New Here bullets. Change only when Ben asks.
- `connections-calendar.json`: Ben's Connections/Hospitality calendar.
- `weeks/<sunday>.json`: one file per Sunday (state + options + final).
- `build.py`: builds the proposal email, the final email, and the Word doc.
- `template.docx`: styles from Ben's original Weekly Announcements doc.
- `docs/<sunday>.docx`: the Word version, served at https://benslater01.github.io/firstnaz-skills/announcements/docs/<sunday>.docx (live once it's on main).

**Service times.** Normally three services. From Sunday, Dec 13, 2026 until the new year there are two: 8:30 and 10:00 AM (the 11:30 is on break). Next Step U classes run after the 2nd and 3rd services when there are three, and only after the 10:00 service when there are two. Check the date before writing class times.

**This repo is public.** Never commit email addresses. Names of staff and the service host are fine.

## Week file
```json
{
  "sunday": "YYYY-MM-DD",
  "status": "draft | proposed | approved | sent | held | parked",
  "proposalSentAt": "ISO time or null",
  "host": "Name (Service Host in Planning Center)" ,
  "options": [{"id": "A", "title": "", "when": "", "source": "", "why": "", "bullets": [""], "flags": [""]}],
  "skipped": ["things considered and why not"],
  "notes": ["anything Ben should know or answer"],
  "picked": ["A", "C"],
  "final": [{"title": "", "bullets": [""]}],
  "sentAt": null,
  "sentTo": ["names only"]
}
```

## Tuesday: find options and send the proposal (about 2:47 PM Eastern)
Target Sunday = the coming Sunday.
1. If `weeks/<sunday>.json` already has `proposalSentAt`, stop quietly.
2. Gather candidates for the target Sunday. Look roughly 1 to 4 weeks ahead:
   - **Planning Center calendar**: `calendar_event_instances`, approved, next 6 weeks. Skip weekly services, youth, preteens, small groups, hot meal, safety team, and other recurring or subgroup items unless something about them is new.
   - **Weekly Guide**: `../weekly-guide/guide.json` (upcoming + seasonal), and the latest proof notes if any.
   - **Church newsletter (Sylvia Cook, Mailchimp)**: sent from churchoffice@firstnaz.net at some point in the week, usually titled "Church Newsletter" (special editions have other subjects), body starts "What's Happening at FirstNaz?". **Ben usually deletes it**, so search all folders including Deleted Items (sender churchoffice@firstnaz.net, last 10 days) and read the newest one or two. This is often the richest source of dates and details.
   - **Connections calendar**: `connections-calendar.json`.
   - **Announcement requests**: emails to Ben in the last 2 weeks asking for a Sunday announcement or slide (search "announcement", "announce", "slide", "Sunday"). Per policy, requests need 4 days' notice; mention late ones.
   - **Staff emails**: sermon series, big news from Joe (jproudfoot@firstnaz.net) or Mark (mowen@firstnaz.net).
   - **Slides**: Ben's OneDrive `Master Media/Slides`, the newest "Announcements" folder (sharepoint_folder_search). A slide existing is a strong signal Ben wants it pushed. Read an image only when you need its date/place.
3. Filter with the policy in STYLE.md (half the church, or a core ministry). Drop anything that happens before the target Sunday. Rank by: launches/happens this Sunday > needs sign-ups soon > church-wide event 1 to 3 weeks out > everything else.
4. Draft **3 to 5 options** (A, B, C...) following STYLE.md exactly. Each gets when/source/why. Put anything uncertain in `flags` (conflicting rooms, missing details, typos in source names). Never invent details. List what you looked at and skipped in `skipped`.
5. **Service host**: Planning Center Services, service type "Weekend Services" (id 83785). Find the plan for the target Sunday (services_plans) and its roster (services_plan_people, include person). Anyone with position "Service Host" who is not Ben (Benjamin Slater) is a host. Put their name(s) in `host`. If there's no host or only Ben, set `host` to null.
   Then find each host's email (see **Host emails** below). If you can't, ask Ben for it in `notes` ("Jadon is hosting. What's his email?").

## Host emails
Ben's rule: use the church staff page, and if the email isn't there, ask Ben. Don't guess and don't pull it from Planning Center or old emails.
1. **Saved answers**: Ben's OneDrive file `Weekly Guide/announcement-hosts.json` (drive id in ../weekly-guide/SKILL.md, Weekly Guide folder id `01JV6PCJKDHZHOBLH3E5EI7ZY4RPEJXLUA`). Shape: `{"Jadon Bird": "x@y"}`. Read it with read_resource; it may not exist yet.
2. **Staff page**: https://www.firstnaz.net/staff-leaders. It renders with JavaScript, so load it in Playwright (preinstalled), scroll to the bottom, and read the text and `mailto:` links. Match the host by full name. (As of Nov 2026 the page lists no staff, only churchoffice@. Check anyway; it may be filled in later.)
3. **Ask Ben** in the proposal `notes`. When he answers, save it to `announcement-hosts.json` (create with sharepoint_upload_file, or update it with sharepoint_update_file) so you never ask twice. Never put host emails in this repo.
On Friday, if a host's email is still unknown: send to Joe and Mark anyway (with Ben CC'd), and tell Ben in one line that the host wasn't included because you don't have their email.
6. **Draft doc.** Set `recommended` to your top 2 option ids (usually A and B). Build it with `python3 build.py draft weeks/<sunday>.json <scratchpad>/draft.docx`. Upload it to Ben's OneDrive folder **Sunday Announcements** (drive id in ../weekly-guide/SKILL.md, folder id `01JV6PCJKOXZC5LMZMWFFZVA722LSL4VEP`) as `<sunday> Sunday Announcements DRAFT.docx` (sharepoint_upload_file, contentBase64, conflictBehavior "replace"). Put the returned webUrl in `draftUrl`. The proposal email links it automatically. (Outlook here can't attach files, so it's a link.)
7. Write the week file with `status: "draft"`, build the email with `python3 build.py proposal weeks/<sunday>.json`, and send it to Bslater@firstnaz.net only with outlook_send_mail (bodyType html). Subject: `Announcements <M.D>: pick your 2`. Set `status: "proposed"` and `proposalSentAt`. Commit "Announcements proposal: <sunday>" and push.

## Friday: build and send the final (about 12:47 PM and 4:47 PM Eastern)
1. If `status` is "sent" or "held" for the target Sunday, stop quietly.
   If `status` is "approved", `final` is already built from Ben's reply (`approvedAt` says when). Use it as is, unless Ben sent a newer email about announcements after `approvedAt`; then apply that. Skip to the recipients step.
2. Read Ben's replies to the proposal (same subject, from Bslater@firstnaz.net) and any newer email from him about announcements. Only Ben's emails count.
3. **HOLD / no announcements this week**: set `status: "held"`, send Ben a one-line confirmation, commit, push.
4. **Ben picked** (e.g. "A and C", "just B", "A plus this: ..."):
   - `picked` = his choices from the options, at most 2. Anything Ben adds himself (his own announcement, not one of the options) also goes in `final`, up to **4 total including New Here**. If the total would go past 4, keep New Here plus the first 3 in the order he wrote them and say so in the confirmation.
   - `final` = those options' title and bullets, with his edits applied exactly. If he wrote his own wording, use it as written (just tidy into bullets; don't "improve" it). If he added something new, write it per STYLE.md.
   - If he answered a flag, fix the bullets to match.
   - If he picked nothing extra ("just New Here"), `final` is empty.
   - Recipients: Joe Proudfoot (jproudfoot@firstnaz.net) and Mark Owen (mowen@firstnaz.net), plus each host in `host`. Re-check the Service Host in Planning Center now (it can change during the week). Get host emails per **Host emails** (saved answers, staff page, or Ben's reply to the proposal; save new answers). Don't commit emails.
   - Build the doc: `python3 build.py docx weeks/<sunday>.json docs/<sunday>.docx`.
   - Build the email: `python3 build.py final weeks/<sunday>.json`. Send with outlook_send_mail (bodyType html) to those recipients, Ben in CC. Subject: `<M.D> Announcements`.
   - Set `status: "sent"`, `sentAt`, `sentTo` (names only). Commit "Announcements sent: <sunday>" and push (the doc link goes live when it's on main).
   - Send Ben nothing extra; he's CC'd.
5. **Ben asked a question or wants to see it again** before approving: answer or apply, send a revised proposal (same subject, "v2"), keep `status: "proposed"`, commit, push, stop.
6. **No reply yet**:
   - 12:47 PM run: one short reminder to Ben: "Reply with your picks by 4:30 and it goes out today. Otherwise I'll leave a draft for you." Don't send twice.
   - 4:47 PM run: don't send to the team. Build the final using **New Here plus the top-ranked option A only**, make the doc, and create an Outlook **draft** (outlook_create_draft) to the same recipients with Ben in CC. Set `status: "parked"`. Email Ben: it's waiting in his Drafts, edit and hit send. Commit, push.

## If Ben replies later (Saturday)
No run on Saturday. If Ben wants it sent after a park, he sends the draft himself.

## Style for emails to Ben
Short, friendly, plain. No em dashes. If something is blocked (a connector fails, can't find the plan), tell Ben in one line instead of guessing.
