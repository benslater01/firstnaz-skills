#!/bin/bash
# One-time setup on the Mac that renders. Safe to re-run (also updates the tools).
set -e
ROOT="$HOME/FirstNaz Video"
mkdir -p "$ROOT/projects" "$ROOT/music"
command -v brew >/dev/null || { echo "Install Homebrew first: https://brew.sh"; exit 1; }
brew list ffmpeg >/dev/null 2>&1 || brew install ffmpeg
brew list python@3.12 >/dev/null 2>&1 || brew install python@3.12
if [ -d "$ROOT/firstnaz-skills/.git" ]; then git -C "$ROOT/firstnaz-skills" pull --ff-only
else git clone https://github.com/benslater01/firstnaz-skills.git "$ROOT/firstnaz-skills"; fi
[ -d "$ROOT/.venv" ] || "$(brew --prefix python@3.12)/bin/python3.12" -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/pip" install -q --upgrade pip numpy mlx-whisper
# warm the Whisper model once (about 1.5 GB download) so the first edit doesn't stall
"$ROOT/.venv/bin/python" -c "from huggingface_hub import snapshot_download; snapshot_download('mlx-community/whisper-large-v3-turbo')"
cat > "$ROOT/edit" <<'SH'
#!/bin/bash
exec "$HOME/FirstNaz Video/.venv/bin/python" "$HOME/FirstNaz Video/firstnaz-skills/video-edit/edit.py" "$@"
SH
chmod +x "$ROOT/edit"
echo "Ready. Projects go in: $ROOT/projects   Music goes in: $ROOT/music"
