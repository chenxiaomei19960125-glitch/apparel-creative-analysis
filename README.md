# 服饰四大赛道创意分析站

## 覆盖行业

- 箱包鞋靴
- 内衣
- 男装
- 女装

页面通过 `?industry=bag-shoes`、`?industry=underwear`、`?industry=menswear`、`?industry=womenswear` 提供独立行业入口。

## 数据来源

- `箱包鞋靴`：`../history/2026-07-20.json` 的已验证深度分析归档。
- `内衣 / 男装 / 女装`：`/Users/chenxiaomei/Desktop/服饰大盘.xlsx` 对应 Sheet。

## 构建

```bash
pip3 install -r requirements.txt
python3 build_multisector_site.py
```

输出到：

- `dist/index.html`：静态站页面
- `data/apparel_snapshot.json`：本期标准化数据快照

## 数据口径

- 使用有效视频 URL 的素材记录。
- 同一 URL 去重，保留日均消耗更高的一行。
- CTR、3 秒完播、浅层 CVR 使用日均消耗加权聚合。
- 无明确类目字段的素材不参与类目结论；Top 素材仍可回看。
- 内衣、男装、女装页面当前展示真实数据和基于品类决策需求的策略方向；视觉标签与逐帧拆解需完成实际视频视觉识别后再补充，避免规则臆测。
