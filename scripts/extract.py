"""Extract structured metadata rows from the scenario-labs/3d-collection parquet."""
import json
import sys

import pandas as pd

PARQUET = sys.argv[1]
OUT = sys.argv[2]

df = pd.read_parquet(PARQUET)
rows = []
for i, r in df.iterrows():
    outputs = r["outputs"]
    if outputs is None or (isinstance(outputs, float) and pd.isna(outputs)):
        outputs = []
    files = []
    for o in outputs:
        path = o.get("path")
        fmt = o.get("format") or (path.rsplit(".", 1)[-1] if path else "")
        role = o.get("role") or ""
        if path:
            files.append({"role": str(role), "format": str(fmt), "path": str(path)})
    preview_path = None
    pf = r.get("preview_file")
    if pf is not None and not (isinstance(pf, float) and pd.isna(pf)):
        preview_path = pf.get("path") if isinstance(pf, dict) else str(pf)
    prompt = r.get("prompt")
    if prompt is None or (isinstance(prompt, float) and pd.isna(prompt)):
        prompt = None
    # fallback: prompt may live inside inputs struct
    if prompt is None:
        inputs = r.get("inputs")
        if isinstance(inputs, dict) and inputs.get("prompt"):
            prompt = str(inputs["prompt"])
    rows.append({
        "idx": int(i),
        "id": str(r.get("id")),
        "workflow": str(r.get("workflow") or ""),
        "model": str(r.get("model") or ""),
        "prompt": prompt,
        "formats": str(r.get("formats") or ""),
        "preview_path": preview_path,
        "files": files,
    })

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False)

n_prompt = sum(1 for x in rows if x["prompt"])
n_prev = sum(1 for x in rows if x["preview_path"])
n_glb = sum(1 for x in rows if any("glb" in f["format"].lower() or f["path"].endswith(".glb") for f in x["files"]))
print(json.dumps({
    "rows": len(rows),
    "with_prompt": n_prompt,
    "with_preview": n_prev,
    "with_glb": n_glb,
    "workflows": pd.Series([x["workflow"] for x in rows]).value_counts().to_dict(),
    "models": pd.Series([x["model"] for x in rows]).value_counts().to_dict(),
    "formats": pd.Series([x["formats"] for x in rows]).value_counts().to_dict(),
}, ensure_ascii=False, indent=1))
