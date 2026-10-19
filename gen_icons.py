# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ODIR = os.path.join(HERE, "icons")
os.makedirs(ODIR, exist_ok=True)

RED = (139, 37, 0, 255)
LIGHT = (245, 240, 230, 255)   # 阳 米黄
DARK = (44, 24, 16, 255)       # 阴 深棕


def make(size):
    img = Image.new("RGBA", (size, size), RED)
    d = ImageDraw.Draw(img)
    cx = cy = size / 2
    R = size * 0.30                    # 太极外半径（留安全区，maskable 友好）
    x0, y0, x1, y1 = cx - R, cy - R, cx + R, cy + R

    # 外描边圆（米黄圈）
    d.ellipse([x0 - size*0.012, y0 - size*0.012,
               x1 + size*0.012, y1 + size*0.012], fill=LIGHT)
    # 整圆深色
    d.ellipse([x0, y0, x1, y1], fill=DARK)
    # 左半圆浅色
    d.pieslice([x0, y0, x1, y1], 90, 270, fill=LIGHT)
    # 中圆
    r2 = R / 2
    d.ellipse([cx - r2, cy - R - r2 + R], fill=LIGHT)  # placeholder, replaced below
    return img


def draw_taiji(size):
    img = Image.new("RGBA", (size, size), RED)
    d = ImageDraw.Draw(img)
    cx = cy = size / 2
    R = size * 0.30

    # 米黄外圈
    ring = size * 0.014
    d.ellipse([cx-R-ring, cy-R-ring, cx+R+ring, cy+R+ring], fill=LIGHT)
    # 整圆深
    d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=DARK)
    # 左半浅
    d.pieslice([cx-R, cy-R, cx+R, cy+R], 90, 270, fill=LIGHT)
    r2 = R / 2
    # 上中圆浅（中心 cy-R/2，bbox 上边 cy-R、下边 cy）
    d.ellipse([cx-r2, cy-R, cx+r2, cy], fill=LIGHT)
    # 下中圆深（中心 cy+R/2，bbox 上边 cy、下边 cy+R）
    d.ellipse([cx-r2, cy, cx+r2, cy+R], fill=DARK)
    # 鱼眼
    re = R / 7
    d.ellipse([cx-re, cy-R/2-re, cx+re, cy-R/2+re], fill=DARK)  # 上中浅里的深眼
    d.ellipse([cx-re, cy+R/2-re, cx+re, cy+R/2+re], fill=LIGHT) # 下中深里的浅眼
    return img


for s in (192, 512):
    im = draw_taiji(s)
    p = os.path.join(ODIR, f"icon-{s}.png")
    im.save(p)
    print("saved", p)
