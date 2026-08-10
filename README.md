# 服饰行业创意分析站

## 站点结构

- 总站：`/`
  - 仅展示 **4 个行业入口** 与 **服饰行业整体标签树结构**。
- 箱包鞋靴入口：直达既有深度站，不改动原有 3 个 Tab 内容。
- 内衣、男装、女装入口：各自独立深度页，均包含：
  1. `素材标签树结构`
  2. `标签分析和结论`
  3. `素材内容 · 逐帧剖析`

## 数据来源

- 内衣 / 男装 / 女装：`/Users/chenxiaomei/Desktop/服饰大盘.xlsx` 对应 Sheet。
- 箱包鞋靴：链接至原有深度站：
  `https://chenxiaomei19960125-glitch.github.io/bag-shoes-creative-report/`

## 创意标签与关键帧

- 基于有效视频 URL 去重；CTR、3 秒完播与浅层 CVR 按日均消耗加权聚合。
- `extract_sector_frames.py` 为三行业消耗 Top12 素材抽取 6 张关键帧。
- `data/manual_visual_tags.json` 保存人工根据关键帧核验的「视频结构类型 / 出镜角色 / 拍摄场景」标签，优先级高于类目创意基线。
- 其他创意维度（卖点表达、产品功效、情绪钩子、场景人群、用户痛点）以行业类目创意基线补齐，后续可随人工逐帧复核持续校正。

## 构建与发布

```bash
pip3 install -r requirements.txt
python3 build_multisector_site.py

git add .
git commit -m "update: refresh apparel creative analysis"
git push
```

输出：

- `docs/index.html`：GitHub Pages 总站
- `docs/underwear/index.html`：内衣深度页
- `docs/menswear/index.html`：男装深度页
- `docs/womenswear/index.html`：女装深度页
- `docs/assets/frames/`：深度页逐帧图片
- `data/sector_snapshot.json`：本期标准化数据快照
