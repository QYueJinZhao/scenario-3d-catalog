"""Merge visual classification codes with rows.json -> catalog.json (semantic categories)."""
import json
import sys

ROWS = sys.argv[1]
CODES = sys.argv[2]
OUT = sys.argv[3]

CODE2CAT = {
    "C": ("character", "角色人物"),
    "A": ("animal", "动物生物"),
    "V": ("vehicle", "载具机甲"),
    "B": ("building", "建筑场景"),
    "P": ("prop", "道具武器"),
    "F": ("furniture", "家具日用"),
    "T": ("plant", "植物"),
    "D": ("food", "食物"),
    "O": ("other", "其他"),
}
ORDER = ["character", "animal", "vehicle", "building", "prop", "furniture", "plant", "food", "other"]

codes = {}
for line in open(CODES, encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    start_s, rest = line.split(":", 1)
    start = int(start_s)
    vals = [v.strip() for v in rest.split(",") if v.strip()]
    for off, v in enumerate(vals):
        assert v in CODE2CAT, f"bad code {v} at idx {start+off}"
        codes[start + off] = v

with open(ROWS, encoding="utf-8") as f:
    rows = json.load(f)

missing = [r["idx"] for r in rows if r["idx"] not in codes]
extra = [k for k in codes if k not in {r["idx"] for r in rows}]
assert not missing and not extra, f"missing={missing[:5]} extra={extra[:5]}"

cat_counts = {}
out = []
for r in rows:
    slug, zh = CODE2CAT[codes[r["idx"]]]
    cat_counts[slug] = cat_counts.get(slug, 0) + 1
    glb = next((f["path"] for f in r["files"] if f["path"].endswith(".glb")), None)
    files = [
        {
            "format": f["format"],
            "url": "https://huggingface.co/datasets/scenario-labs/3d-collection/resolve/main/" + f["path"],
        }
        for f in r["files"]
    ]
    out.append({
        "id": r["id"],
        "cat": slug,
        "catZh": zh,
        "workflow": r["workflow"],
        "model": r["model"].replace("model_", ""),
        "prompt": r["prompt"],
        "thumb": "previews/" + str(r["idx"]) + ".jpg",
        "glb": ("https://huggingface.co/datasets/scenario-labs/3d-collection/resolve/main/" + glb) if glb else None,
        "files": files,
    })

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"count": len(out), "categories": ORDER, "items": out}, f, ensure_ascii=False)

print(json.dumps({"total": len(out), "categories": cat_counts}, ensure_ascii=False, indent=1))
