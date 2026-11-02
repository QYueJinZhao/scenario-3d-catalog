# Scenario 3D 语义分类目录（scenario-3d-catalog）

[Scenario 官方 3D Collection](https://huggingface.co/datasets/scenario-labs/3d-collection)（1,342 个 AI 生成的 3D 资产，CC-BY-4.0）的**语义分类浏览目录**。

原数据集只有 `workflow` / `model` 等生成维度字段、没有语义类别，本仓库把全部 1,342 个资产按预览图内容整理为 9 个语义分类，方便按需找素材：

| 分类 | 数量 | 分类 | 数量 |
|---|---:|---|---:|
| 角色人物 character | 318 | 家具日用 furniture | 80 |
| 载具机甲 vehicle | 315 | 植物 plant | 42 |
| 道具武器 prop | 266 | 其他 other | 23 |
| 动物生物 animal | 199 | 食物 food | 14 |
| 建筑场景 building | 85 | | |

## 使用

- **在线浏览**：GitHub Pages 上的 `index.html`（分类 tab + 搜索 + 卡片点击查看详情/下载）
- **程序读取**：[`data/catalog.json`](data/catalog.json) —— 每条含 `id / cat / catZh / workflow / model / prompt / thumb / glb / files[]`，`glb` 与 `files[].url` 均为 Hugging Face 直链
- 文件本体（`output.glb` 等）**不放在本仓库**，只存缩略图与直链，点击即从 HF 下载

```js
const catalog = await (await fetch("data/catalog.json")).json();
const characters = catalog.items.filter(i => i.cat === "character");
```

## 仓库结构

```
index.html          # 静态浏览页（原生 JS，无依赖）
data/catalog.json   # 全量元数据 + 语义分类（1342 条）
previews/           # 400px 缩略图（1342 张，按行序号命名）
scripts/            # 构建脚本（提取/下载/分类合并）
```

## 许可与署名

- 数据集原始许可：**CC-BY-4.0**（版权归 Scenario / scenario-labs 所有），可自由使用、商用、二次分发，但需署名。
- 使用这些模型请在你的作品中注明：*3D assets by Scenario (scenario-labs/3d-collection), CC-BY-4.0*。
- 注意：数据集由多个第三方生成模型产出（Meshy / Tripo / Rodin / TRELLIS / Direct3D / Sparc3D 等），各自服务条款可能有额外要求，重要项目请先复核。
- 本目录（分类标注、缩略图重打包、代码）：同样 CC-BY-4.0。

## 复现

```bash
# 1. 提取元数据（Parquet 来自 HF）
python scripts/extract.py <train.parquet> rows.json
# 2. 下载缩略图
python scripts/download_previews.py rows.json raw_previews previews
# 3. 拼贴 + 人工/模型分类得到 codes.txt 后合并
python scripts/merge.py rows.json codes.txt data/catalog.json
```

分类方式：370 条有 prompt 的按文本规则、其余 972 条按预览图逐张目检归类（错误在所难免，欢迎 issue/PR 修正 `codes` 后重跑 merge）。
