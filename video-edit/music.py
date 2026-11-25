"""Hands-off music library: seeds itself, grows itself, picks a fitting track per project.

  music                 list the library
  music seed            download the curated starter set (music-seed.json)
  music fetch MOOD [N]  find N more tracks for a mood on Openverse (CC0 / CC BY only)
  music scan            add tracks Ben dropped into music/ by hand
  music pick MOOD [ENERGY]   show what auto-pick would choose

In plan.json, "music": {"mood": "hopeful", "energy": 2} is enough. The render resolves it to a
track (fitting mood, least recently used, long enough), records the use, and writes the credit line.
"""
import json, subprocess, sys, urllib.parse, urllib.request
from pathlib import Path

UA = {"User-Agent": "church-video-editor/1.0"}
LIB = None  # set by init()


def init(root):
    global LIB
    LIB = Path(root) / "music"
    LIB.mkdir(parents=True, exist_ok=True)


def load():
    p = LIB / "library.json"
    return json.loads(p.read_text()) if p.exists() else {"tracks": []}


def save(lib):
    (LIB / "library.json").write_text(json.dumps(lib, indent=2))


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except ValueError: return 0.0


def bed_ok(path):
    """Usable as a bed under speech: real audio, not wildly dynamic, not near-silent."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-t", "240", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True)
    txt = r.stderr[r.stderr.rfind("Summary:"):]
    try:
        i = float(txt.split("I:")[1].split("LUFS")[0]); lra = float(txt.split("LRA:")[1].split("LU")[0])
    except (IndexError, ValueError):
        return False, "unreadable"
    if i < -38: return False, f"too quiet ({i} LUFS)"
    if lra > 18: return False, f"too dynamic for a bed (LRA {lra})"
    return True, f"{i} LUFS, LRA {lra}"


def download(url, dest):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        while chunk := r.read(1 << 16): f.write(chunk)


def add(lib, dest, entry):
    d = duration(dest)
    ok, why = bed_ok(dest) if d else (False, "not audio")
    if not ok or d < 60:
        dest.unlink(missing_ok=True)
        print(f"  skip {entry['title']}: {why if not ok else 'shorter than 60s'}")
        return False
    entry.update(file=dest.name, duration=round(d, 1), used=[])
    lib["tracks"].append(entry)
    print(f"  + {entry['title']}  ({int(d // 60)}:{int(d % 60):02d}, {', '.join(entry['mood'])}, energy {entry['energy']})")
    return True


def seed():
    """Curated starter set: Kevin MacLeod (incompetech.com), CC BY 4.0. Consistent pro quality,
    fine for YouTube/Facebook/Instagram with the credit line in the description."""
    lib = load(); have = {t.get("source_url") for t in lib["tracks"]}
    seeds = json.loads((Path(__file__).parent / "music-seed.json").read_text())
    got = 0
    for s in seeds["tracks"]:
        url = seeds["base_url"] + urllib.parse.quote(s["title"]) + ".mp3"
        if url in have: continue
        dest = LIB / f"{s['title']}.mp3"
        try:
            download(url, dest)
        except Exception as e:
            print(f"  skip {s['title']}: {e}"); dest.unlink(missing_ok=True); continue
        got += add(lib, dest, {"title": s["title"], "artist": "Kevin MacLeod", "mood": s["mood"], "energy": s["energy"],
                               "source": "incompetech", "source_url": url, "license": "CC BY 4.0", "curated": True,
                               "credit": seeds["credit"].format(title=s["title"])})
        save(lib)
    print(f"{got} tracks added, {len(lib['tracks'])} in library")


def fetch(mood, n=3):
    """Grow the library from Openverse (Creative Commons search). Commercial-safe licenses only."""
    lib = load(); have = {t.get("source_url") for t in lib["tracks"]}
    q = urllib.parse.urlencode({"q": f"{mood} instrumental", "license": "cc0,by", "category": "music",
                                "page_size": 40, "mature": "false"})
    req = urllib.request.Request(f"https://api.openverse.org/v1/audio/?{q}", headers=UA)
    try:
        results = json.load(urllib.request.urlopen(req, timeout=30))["results"]
    except Exception as e:
        sys.exit(f"Openverse search failed: {e}")
    got = 0
    for r in results:
        if got >= n: break
        dur = (r.get("duration") or 0) / 1000
        if r.get("url") in have or not (90 <= dur <= 600): continue
        if any(w in (r.get("title") or "").lower() for w in ("vocal", "rap", "remix", "sfx", "noise")): continue
        ext = (r.get("filetype") or Path(urllib.parse.urlparse(r["url"]).path).suffix.lstrip(".") or "mp3")
        safe = "".join(c for c in r["title"] if c.isalnum() or c in " -_")[:60].strip() or r["id"]
        dest = LIB / f"{safe}.{ext}"
        try:
            download(r["url"], dest)
        except Exception as e:
            print(f"  skip {r['title']}: {e}"); continue
        credit = None if r["license"] == "cc0" else (r.get("attribution") or
                 f"\"{r['title']}\" by {r.get('creator')} ({r.get('foreign_landing_url')}), CC BY {r.get('license_version')}")
        got += add(lib, dest, {"title": r["title"], "artist": r.get("creator"), "mood": [mood], "energy": None,
                               "source": f"openverse/{r.get('provider')}", "source_url": r["url"],
                               "license": f"{r['license'].upper()} {r.get('license_version') or ''}".strip(),
                               "curated": False, "credit": credit})
        save(lib)
    print(f"{got} tracks added for '{mood}'")


def scan():
    lib = load(); known = {t["file"] for t in lib["tracks"]}
    for f in sorted(LIB.iterdir()):
        if f.suffix.lower() in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".aif", ".aiff"} and f.name not in known \
                and not f.name.startswith("."):
            lib["tracks"].append({"file": f.name, "title": f.stem, "duration": round(duration(f), 1), "mood": [],
                                  "energy": None, "source": "manual", "license": "", "curated": True, "credit": None, "used": []})
            print(f"added {f.name}: tag its mood/energy (and credit if the license needs one) in library.json")
    save(lib)


def pick(mood, energy=None, need=0.0, project=None):
    """Best fit: mood match, then energy closeness, curated first, least recently used, long enough
    (short tracks loop, but a loop seam is worse than a different track)."""
    lib = load()
    if not lib["tracks"]: sys.exit("music library is empty: run `edit music seed`")
    order = {p: i for i, p in enumerate(lib.get("history", []))}
    def score(t):
        m = 0 if mood in t.get("mood", []) else 1
        e = abs((t.get("energy") or 3) - energy) if energy else 0
        short = 0 if t.get("duration", 0) >= need else 1
        recent = -order.get(t["file"], -1)  # never used = best
        return (m, short, e, 0 if t.get("curated") else 1, recent)
    t = min(lib["tracks"], key=score)
    if mood not in t.get("mood", []):
        print(f"note: no '{mood}' track in the library; using closest. Run `edit music fetch {mood}` to add some.")
    return t


def record_use(file, project):
    lib = load()
    h = [f for f in lib.get("history", []) if f != file]
    lib["history"] = [file] + h[:200]
    for t in lib["tracks"]:
        if t["file"] == file: t.setdefault("used", []).append(project)
    save(lib)


def resolve(m, need, project):
    """plan.json music block -> (file path, credit). 'file' wins; else auto-pick by mood/energy."""
    if m.get("file"):
        f = Path(m["file"]); f = f if f.is_absolute() else LIB / f
        t = next((t for t in load()["tracks"] if t["file"] == f.name), {})
        return f, m.get("credit", t.get("credit"))
    t = pick(m.get("mood", "hopeful"), m.get("energy"), need, project)
    m["file"] = t["file"]  # pin the choice so previews and finals match
    return LIB / t["file"], t.get("credit")


def listing():
    lib = load()
    for t in lib["tracks"]:
        print(f"{t['title'][:40]:<40} {int(t.get('duration', 0) // 60)}:{int(t.get('duration', 0) % 60):02d}  "
              f"energy={t.get('energy')}  mood={','.join(t.get('mood', []))}  used={len(t.get('used', []))}  [{t.get('source')}]")
    print(f"\n{len(lib['tracks'])} tracks in {LIB}")


def main(args):
    c = args[0] if args else "list"
    if c == "seed": seed()
    elif c == "fetch": fetch(args[1], int(args[2]) if len(args) > 2 else 3)
    elif c in ("scan", "--scan"): scan(); listing()
    elif c == "pick":
        t = pick(args[1], int(args[2]) if len(args) > 2 else None)
        print(json.dumps(t, indent=2))
    else: listing()
