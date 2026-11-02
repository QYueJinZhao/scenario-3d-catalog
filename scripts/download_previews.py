"""Download all preview images and produce 400px thumbnails."""
import concurrent.futures as cf
import io
import json
import os
import sys
import urllib.request

ROWS = sys.argv[1]
RAW_DIR = sys.argv[2]
THUMB_DIR = sys.argv[3]
BASE = "https://huggingface.co/datasets/scenario-labs/3d-collection/resolve/main/"

with open(ROWS, encoding="utf-8") as f:
    rows = json.load(f)

UA = {"User-Agent": "Mozilla/5.0 (catalog-builder)"}


def fetch(row):
    idx = row["idx"]
    raw_path = os.path.join(RAW_DIR, f"{idx}.jpg")
    thumb_path = os.path.join(THUMB_DIR, f"{idx}.jpg")
    if os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
        return idx, "cached"
    url = BASE + row["preview_path"].lstrip("/")
    data = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            break
        except Exception:
            if attempt == 2:
                return idx, f"FAIL {url}"
    with open(raw_path, "wb") as f:
        f.write(data)
    from PIL import Image
    im = Image.open(io.BytesIO(data)).convert("RGB")
    w, h = im.size
    if w > 400:
        im = im.resize((400, round(h * 400 / w)), Image.LANCZOS)
    im.save(thumb_path, "JPEG", quality=82)
    return idx, "ok"


ok = fail = cached = 0
failures = []
with cf.ThreadPoolExecutor(max_workers=16) as ex:
    for idx, status in ex.map(fetch, rows):
        if status == "ok":
            ok += 1
        elif status == "cached":
            cached += 1
        else:
            fail += 1
            failures.append((idx, status))

print(json.dumps({"ok": ok, "cached": cached, "fail": fail}))
for idx, msg in failures[:20]:
    print("FAIL", idx, msg[:160])
