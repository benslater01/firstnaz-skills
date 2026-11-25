---
name: video-edit
description: Edit FirstNaz talking-head videos from raw camera files. Syncs two angles to the lav audio, matches color, cuts on the transcript, works in b-roll, adds ducked royalty-free music, logo intro/outro, name labels and captions, and renders a 1080p MP4 plus an optional vertical short with captions. Runs on Ben's Mac with free local tools.
---

# Video Edit

Ben drops raw camera files in a project folder, gives some creative direction, and gets back a finished MP4. Most projects: two angles of a person talking, audio from a lav on one camera, simple color matching, music underneath. Sometimes b-roll. Often a vertical short with captions for socials.

**Everything heavy runs locally on Ben's Mac with free tools** (ffmpeg, numpy, Whisper). Claude never looks at video. Claude reads a text transcript, writes a small `plan.json`, and looks at one contact-sheet image. That keeps each edit to a few cents of Claude usage, and footage never leaves the Mac.

**This repo is public.** Footage, music files and transcripts stay in `~/FirstNaz Video` on the Mac. Never commit them.

## Where it runs

On the Mac, in the folder `~/FirstNaz Video` (made by `setup-mac.sh`). Either:
- Claude desktop app, a Claude Code session opened on that folder, or
- a cloud session connected to that folder through Remote Control (Claude desktop app: Settings, Claude Code, Remote Control).

If this session is in the cloud and not attached, use `list_computer_folders` / `request_computer_folder` to attach "FirstNaz Video". Don't try to pull footage into the cloud.

Run the tool as `./edit <command>` from `~/FirstNaz Video` (a wrapper setup made). In this repo it's `python3 video-edit/edit.py`.

```
~/FirstNaz Video/
  edit                      wrapper script
  firstnaz-skills/          this repo (setup clones it; re-run setup to update)
  music/library.json        royalty-free tracks + tags
  projects/<name>/
    brief.md                Ben's creative direction
    raw/                    camera files
    broll/                  b-roll clips and photos (optional)
    work/                   inventory, transcript, plan.json, stills.jpg
    out/                    main.mp4, short.mp4, *_preview.mp4
```

## Workflow

Keep chat short. Ben reads previews, not essays.

1. **Set up the project.** `./edit new 2026-12-06-jane-testimony` (date + short slug), or use the folder Ben made. Read `brief.md`. If Ben gave direction in chat instead, write it into `brief.md` so it's kept with the project. Ask only what really blocks you (usually nothing: defaults are below).
2. **Inventory.** `./edit probe <project>`. It lists every file and scores audio clarity; the highest score is the lav camera. Write `work/plan.json` with the `angles` block (below). Name the lav camera's angle `A` and make it `master`. Several files from one camera that are chunks of one recording go in order in its `files` list. If a camera was stopped and restarted mid-shoot, tell Ben: v1 handles one continuous take per angle.
3. **Sync.** `./edit sync <project>`. Writes each angle's `offset`. Confidence under 15 means look closer (stills at a clap or hard consonant).
4. **Transcribe.** `./edit transcribe <project>`. Read `work/transcript.txt` (this is the main thing you read; it's cheap).
5. **Color.** `./edit color <project>`, then `./edit stills <project> 40 120` and look at `work/stills.jpg` once. If the graded B angle still looks off, nudge `angles.B.adjust`. If the brief asks for a look ("warmer"), put it in `look`. Simple adjustments only.
6. **Plan the edit** in `plan.json` `main` (and `short` if wanted). Rules below. Then `./edit check <project>`.
7. **Preview and approve.** `./edit render <project> --preview` (and `--short --preview`). Send Ben a short plan: length, what was cut, b-roll spots, music track, then the preview path(s). Wait for his go.
8. **Final.** `./edit render <project>` and `./edit render <project> --short`. Tell Ben the `out/` paths. If the track needs attribution, the render writes `out/music-credit.txt`: remind him to paste it in the YouTube description.
9. Revisions: change `plan.json`, re-render. Don't redo sync/transcribe.

## Editing rules

**Cuts (main).**
- Trim dead air before the first word and after the last (keep ~0.3s of breath on each side).
- Cut flubs, false starts, retakes ("let me try that again"), long ums, and gaps over ~1.5s. When Ben did a line twice, keep the better (usually the last) take.
- Cut between words, using transcript times. Start a segment ~0.1s before a word and end ~0.15s after.
- Respect the target length. If it's way over, cut tangents and repeats, never the point of the story. Tell Ben what you cut.

**Angle switching.**
- Every cut that jumps in time must change angle, punch in (`zoom`), or be covered by b-roll. That hides the jump. `check` warns about bare jump cuts.
- Within continuous speech, switch at sentence or thought boundaries, roughly every 8 to 20 seconds. Vary the rhythm. Favor the angle with better eye line (usually the front/tight one) about 60% of the time.
- Emotional or key lines: go tight (the closer angle or `zoom: 1.2`).
- Punch-ins are a free third angle when a source is 4K or wide. Keep `zoom` at 1.3 or under on 1080p sources so it stays sharp; up to 1.8 on 4K. Use `center: [x, y]` (0 to 1) to frame the face when zoomed.

**B-roll.**
- Use it when the speaker names something that's in `broll/` (the building, an event, a person), to cover a jump cut, or to give a long single-angle stretch some air. 3 to 6 seconds each. Picture only, the voice keeps playing.
- Photos get a slow push-in automatically.
- Don't cover the first few seconds of someone's face, emotional moments, or the payoff line.
- Look at a b-roll clip only if its name doesn't tell you what it is (`./edit stills` doesn't cover b-roll; grab one frame with ffmpeg if needed).

**Music.**
- Default on under talking heads unless the brief says no. Pick from `music/library.json` by mood and energy that fits the brief. Don't reuse the same track as the last few projects unless Ben asks.
- Defaults: `gain_db: -14`, ducked under the voice so it swells in pauses, intro and outro. Raise toward -10 for upbeat recaps, drop to -18 for heavy testimony.
- Use `start` to skip a slow intro in the track.
- Only tracks whose license allows YouTube, Facebook and Instagram use.

**Intro/outro.** Logo intro (3s) and outro (4s, with "firstnaz.net") when the brief says so. Default: on for YouTube/website, off for Sunday screens and shorts.

**Name labels.** `lower_thirds` at the speaker's first on-camera moment after the intro, ~5s. Only when the brief gives the name, or Ben confirms the spelling. Never guess a spelling from the transcript.

**Captions.** `captions: true` on main when the brief asks. Always on for shorts. Check names and church words in the transcript first (Whisper mishears names): fix the words in `work/transcript.json` before rendering.

**Vertical short.**
- 30 to 60 seconds (or what the brief says). Find the strongest self-contained moment: a hook in the first 3 seconds, one clear idea, a natural ending. It can join two or three non-adjacent bits if it flows.
- Same angle rules. Use `crop_x` (0 to 1) per angle or segment to keep the face centered in the 9:16 crop: decide from the stills (0.5 is center).
- Big word-by-word captions are automatic. Usually no intro; the outro is optional.

## plan.json

All times are master-clock seconds, the same clock as the transcript.

```json
{
  "master": "A",
  "fps": 30,
  "angles": {
    "A": {"files": ["/Users/.../raw/C0012.MP4"], "offset": 0, "adjust": {}, "crop_x": 0.5},
    "B": {"files": ["/Users/.../raw/B001.MOV"], "offset": 2.37,
          "color_match": {"r": [1.02, -4.1], "g": [1.0, 0], "b": [0.95, 6.2]},
          "adjust": {"brightness": 0.02, "contrast": 1.0, "saturation": 1.0, "warmth": 0.1}, "crop_x": 0.45}
  },
  "look": {"warmth": 0.1, "saturation": 1.05},
  "denoise": true,
  "main": {
    "intro": true, "outro": true, "captions": false,
    "segments": [
      {"start": 3.2, "end": 18.4, "angle": "A"},
      {"start": 18.4, "end": 31.0, "angle": "B"},
      {"start": 35.6, "end": 52.1, "angle": "A", "zoom": 1.2, "center": [0.5, 0.4]}
    ],
    "broll": [
      {"file": "/Users/.../broll/exterior.mp4", "at": 40.0, "dur": 4, "src_in": 2.0},
      {"file": "/Users/.../broll/photo.jpg", "at": 47.0, "dur": 4}
    ],
    "lower_thirds": [{"at": 4.0, "dur": 5, "name": "Jane Smith", "title": "Member since 2019"}],
    "music": {"file": "/Users/.../music/hopeful_piano.mp3", "gain_db": -14, "start": 0,
              "fade_in": 1.5, "fade_out": 3, "duck": true, "credit": null}
  },
  "short": {
    "captions": true, "outro": false,
    "segments": [{"start": 60.2, "end": 78.0, "angle": "B", "crop_x": 0.4}],
    "music": {"file": "/Users/.../music/hopeful_piano.mp3", "gain_db": -12}
  }
}
```

- `offset`: source time = master time + offset (`sync` fills it in).
- `color_match`: per channel [gain, offset] on 0 to 255 (`color` fills it in). `adjust`/`look`: brightness -0.1 to 0.1, contrast 0.9 to 1.1, saturation 0.9 to 1.2, gamma, warmth -1 to 1. Stay subtle.
- `broll.at` must land inside a kept segment. `src_in` is where to start inside the clip.

## Output

- `out/main.mp4`: 1920x1080, H.264 CRF 18, AAC 192k, -16 LUFS (YouTube/web standard).
- `out/short.mp4`: 1080x1920, -14 LUFS, captions burned in.
- `*_preview.mp4`: 640x360 / 360x640, fast and rough. For approval only.
- Audio: high-pass at 80 Hz and light denoise on the voice (`"denoise": false` to skip), then loudness normalized.

## Music library

`~/FirstNaz Video/music/`. Drop tracks in, run `./edit music --scan`, then tag each new entry in `library.json`: `mood` (e.g. hopeful, reflective, joyful, upbeat, somber, cinematic), `energy` 1 to 5, `source`, `license`, and `credit` (the attribution line, or null if none needed).

Good free sources, safe for church social and YouTube:
- **Pixabay Music**: no attribution, commercial OK. First choice.
- **YouTube Audio Library** (YouTube Studio > Audio Library): filter "No attribution required".
- **Uppbeat** free tier and **Incompetech** (Kevin MacLeod): attribution required, so fill in `credit`.

Worship songs are not royalty free. CCLI streaming licenses cover live services, not edited videos with recorded tracks. Don't use them as beds.

## Setup (once, on the Mac)

```bash
curl -fsSL https://raw.githubusercontent.com/benslater01/firstnaz-skills/main/video-edit/setup-mac.sh | bash
```

Installs ffmpeg and Python via Homebrew, makes a private Python env with numpy and mlx-whisper, downloads the Whisper model (~1.5 GB, one time), and clones this repo into `~/FirstNaz Video`. Re-run it to update. Then add `~/FirstNaz Video` as a Remote Control folder in the Claude desktop app if Ben wants to run edits from a cloud session or his phone.

## Defaults when the brief is silent

1080p main, music on (ducked), no captions on main, no names, intro/outro on for YouTube, short only if asked, target length: as tight as the content allows with no lost meaning.
