"""Build labeled contact sheets for visual classification."""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROWS = sys.argv[1]
THUMB_DIR = sys.argv[2]
OUT_DIR = sys.argv[3]

CELL_W, IMG_H, LABEL_H = 170, 116, 24
COLS, MARGIN = 8, 6
try:
    FONT = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 11)
    FONT_B = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 12)
except OSError:
    FONT = FONT_B = ImageFont.load_default()

with open(ROWS, encoding="utf-8") as f:
    rows = json.load(f)

PER_SHEET = COLS * 8
os.makedirs(OUT_DIR, exist_ok=True)
sheet_w = COLS * CELL_W + MARGIN * (COLS + 1)

for s in range(0, len(rows), PER_SHEET):
    chunk = rows[s:s + PER_SHEET]
    sheet_h = MARGIN + len(chunk) // COLS * (IMG_H + LABEL_H + MARGIN) + MARGIN
    sheet = Image.new("RGB", (sheet_w, sheet_h), (18, 18, 22))
    draw = ImageDraw.Draw(sheet)
    for j, row in enumerate(chunk):
        cx = MARGIN + (j % COLS) * (CELL_W + MARGIN)
        cy = MARGIN + (j // COLS) * (IMG_H + LABEL_H + MARGIN)
        tp = os.path.join(THUMB_DIR, f"{row['idx']}.jpg")
        im = Image.open(tp)
        w, h = im.size
        scale = min(CELL_W / w, IMG_H / h)
        im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
        sheet.paste(im, (cx + (CELL_W - im.width) // 2, cy + (IMG_H - im.height) // 2))
        label = f"#{row['idx']}"
        draw.text((cx + 2, cy + IMG_H + 2), label, fill=(255, 210, 80), font=FONT_B)
        note = row["prompt"] or row["model"]
        if note:
            draw.text((cx + 2, cy + IMG_H + 13), note[:48], fill=(190, 190, 195), font=FONT)
    out = os.path.join(OUT_DIR, f"sheet_{s // PER_SHEET:02d}.png")
    sheet.save(out, "PNG")
    print(out, f"{len(chunk)} cells")
