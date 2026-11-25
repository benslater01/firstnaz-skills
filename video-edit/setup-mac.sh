#!/bin/bash
# One-time setup on the Mac. Safe to re-run (also updates the tools).
#   bash setup-mac.sh "/Volumes/YourDrive"      footage, music and renders on the external drive
#   bash setup-mac.sh                           everything in ~/FirstNaz Video
# Tools (Python env + this repo) always live on the internal disk in ~/.firstnaz-video:
# external drives (exFAT) can't hold a Python env, and edits should still start if the drive is renamed.
set -e
DRIVE="${1%/}"
if [ -n "$DRIVE" ]; then
  [ -d "$DRIVE" ] || { echo "$DRIVE not found. Plug in the drive, or check the name in Finder (it's /Volumes/<drive name>)."; exit 1; }
  ROOT="$DRIVE/FirstNaz Video"
else
  ROOT="$HOME/FirstNaz Video"
fi
TOOLS="$HOME/.firstnaz-video"
mkdir -p "$ROOT/projects" "$ROOT/music" "$TOOLS"
command -v brew >/dev/null || { echo "Install Homebrew first: https://brew.sh"; exit 1; }
brew list ffmpeg >/dev/null 2>&1 || brew install ffmpeg
brew list python@3.12 >/dev/null 2>&1 || brew install python@3.12
if [ -d "$TOOLS/firstnaz-skills/.git" ]; then git -C "$TOOLS/firstnaz-skills" pull --ff-only
else git clone https://github.com/benslater01/firstnaz-skills.git "$TOOLS/firstnaz-skills"; fi
[ -d "$TOOLS/venv" ] || "$(brew --prefix python@3.12)/bin/python3.12" -m venv "$TOOLS/venv"
"$TOOLS/venv/bin/pip" install -q --upgrade pip numpy mlx-whisper
# warm the Whisper model once (about 1.5 GB download) so the first edit doesn't stall
"$TOOLS/venv/bin/python" -c "from huggingface_hub import snapshot_download; snapshot_download('mlx-community/whisper-large-v3-turbo')"
# the wrapper sits next to the projects and points the tool at its own folder
cat > "$ROOT/edit" <<'SH'
#!/bin/bash
export FIRSTNAZ_VIDEO_ROOT="$(cd "$(dirname "$0")" && pwd)"
exec "$HOME/.firstnaz-video/venv/bin/python" "$HOME/.firstnaz-video/firstnaz-skills/video-edit/edit.py" "$@"
SH
chmod +x "$ROOT/edit"
echo "Ready. Projects: $ROOT/projects   Music: $ROOT/music"
echo "In the Claude desktop app, add \"$ROOT\" as a Remote Control folder (Settings, Claude Code, Remote Control)."
