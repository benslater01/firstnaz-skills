#!/usr/bin/env python3
"""Resize an image for the Weekly Guide and save it under weekly-guide/img/.

  python3 img.py <source file> <output name> [width]

Images come from Ben's OneDrive (Master Media/Slides, Sermon Graphics,
Logos): read the file with the Microsoft 365 read_resource tool, which saves
the original to a local file, then run this on that file. Output is served
publicly at https://benslater01.github.io/sermon-notes/weekly-guide/img/<name>
once pushed to main. Only use church graphics meant for the public.
"""
import os, sys
from PIL import Image

src, name = sys.argv[1], sys.argv[2]
width = int(sys.argv[3]) if len(sys.argv) > 3 else 960
im = Image.open(src)
if im.width > width:
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", name)
if name.lower().endswith((".jpg", ".jpeg")):
    bg = Image.new("RGB", im.size, "white")
    bg.paste(im, mask=im.convert("RGBA").split()[3])
    bg.save(out, quality=85, optimize=True, progressive=True)
else:
    im.save(out, optimize=True)
print(out, im.size, os.path.getsize(out), "bytes")
print("URL: https://benslater01.github.io/sermon-notes/weekly-guide/img/" + name)
