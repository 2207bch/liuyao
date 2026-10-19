# -*- coding: utf-8 -*-
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
src = Image.open(os.path.join(HERE, "icons", "icon-512.png")).convert("RGBA")

DENS = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}
base = os.path.join(HERE, "android", "app", "src", "main", "res")
for d, s in DENS.items():
    od = os.path.join(base, d)
    os.makedirs(od, exist_ok=True)
    im = src.resize((s, s), Image.LANCZOS)
    p = os.path.join(od, "ic_launcher.png")
    im.save(p)
    print("saved", p)
