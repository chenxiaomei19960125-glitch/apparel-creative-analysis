#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建服饰四大赛道创意洞察站。

数据来源：
- 箱包鞋靴：已有 2026-07-20 深度分析归档
- 内衣 / 男装 / 女装：桌面《服饰大盘.xlsx》对应 Sheet

运行：
    python3 build_multisector_site.py
产物：
    dist/index.html
    data/apparel_snapshot.json
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from collections import defaultdict
from pathlib import Path

from openpyxl import load_workbook

BASE = Path(__file__).resolve().parent
WORKSPACE = BASE.parent
XLSX = Path("/Users/chenxiaomei/Desktop/服饰大盘.xlsx")
BAG_HISTORY = WORKSPACE / "history" / "2026-07-20.json"
OUT = BASE / "dist"
DATA_OUT = BASE / "data"

INDUSTRIES = {
    "bag-shoes": {"name": "箱包鞋靴", "emoji": "👜", "sheet": None, "desc": "鞋靴 / 箱包 · 已接入标签与逐帧深度分析"},
    "underwear": {"name": "内衣", "emoji": "🩲", "sheet": "内衣", "desc": "贴身衣物 · 舒适度、支撑与功能表达"},
    "menswear": {"name": "男装", "emoji": "👔", "sheet": "男装", "desc": "男装 · 功能、版型与通勤场景表达"},
    "womenswear": {"name": "女装", "emoji": "👗", "sheet": "女装", "desc": "女装 · 上身效果、风格与穿搭种草"},
}

# 基于品类的「可执行创意方向」。只用于策略建议，不冒充实际画面标签。
CATEGORY_PLAYBOOK = {
    "文胸/乳贴/内裤": ("舒适感 / 支撑力 / 透气", "先给贴合或支撑结果，再用面料、弹力和细节证明，降低贴身穿着的不确定性。"),
    "袜子": ("吸汗透气 / 防滑耐磨 / 厚薄对比", "低客单决策快，功能对比和真实脚感展示能快速说明购买理由。"),
    "塑身衣/裤": ("塑形对比 / 收腹提臀 / 久穿舒适", "前后对比和局部细节可直接回应显瘦、勒痕和舒适度焦虑。"),
    "睡衣/家居服": ("亲肤面料 / 宽松版型 / 居家场景", "真实居家场景搭配触感和版型展示，容易形成舒适生活方式代入。"),
    "儿童内衣裤袜": ("亲肤安全 / 弹力 / 家长决策", "把面料安全和孩子活动舒适度可视化，符合家长的信任决策路径。"),
    "上衣": ("上身比例 / 显瘦版型 / 一衣多搭", "上身效果和通勤、约会等搭配场景直接降低用户对版型和搭配的判断成本。"),
    "裤子": ("腿型修饰 / 弹力 / 多场景搭配", "站立、走路、下蹲等动态展示能同时证明版型、舒适度与实穿性。"),
    "裙子": ("显瘦 / 垂坠 / 风格穿搭", "上身动态和不同身材参考更能放大风格与身材修饰价值。"),
    "套装/学生校服/工作制服": ("整套搭配 / 省心穿搭 / 场景适配", "成套结果一眼可见，适合直接回应通勤、活动或学生场景的省心需求。"),
    "速干衣裤": ("速干透气 / 户外实测 / 防晒", "运动和户外场景天然带入需求，实测镜头比参数口播更有说服力。"),
    "防晒衣/皮肤衣": ("防晒 / 透气 / 轻薄", "户外强光和面料透光、轻薄感展示，可将防晒需求转为直观证据。"),
    "羽绒服/棉服": ("保暖 / 轻量 / 蓬松", "季节场景加上蓬松、厚薄或保暖展示，能建立冬季高客单的信任。"),
    "衬衫": ("挺括版型 / 通勤 / 易打理", "上身通勤场景与抗皱、版型细节结合，能减少职场穿搭决策成本。"),
    "通用箱包": ("静音轮 / 抗摔 / 大容量", "差旅场景把拖行、收纳和耐用需求一次带入，演示镜头可解释高客单价值。"),
    "女包": ("上身比例 / 包型质感 / 容量", "颜值、质感和能装三类决策点同时呈现，更利于完成种草与转化。"),
    "书包/拉杆书包": ("护脊减负 / 分区收纳 / 开学", "家长决策明确，背负和收纳演示可直观回应减负、护脊和容量问题。"),
    "休闲鞋": ("软底缓震 / 增高 / 上脚效果", "上脚、弯折和走路镜头能同时证明脚感、增高和日常百搭。"),
    "时尚单鞋": ("显瘦显高 / 鞋型 / 穿搭", "腿部比例和动态走路比静态产品更能说明显瘦显高的结果。"),
    "凉鞋": ("不磨脚 / 透气 / 夏日穿搭", "脚部特写和行走动态直接回应夏季闷脚、磨脚和搭配焦虑。"),
}

GENERIC_PLAYBOOK = ("核心功能 / 使用场景 / 结果展示", "优先把类目的关键决策点做成可见结果，再用细节和使用场景补足信任。")


def num(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def clean_text(value: object) -> str:
    if value is None:
        return ""
    v = str(value).strip()
    return "" if v in {"空", "None", "nan", "-"} else v


def weighted(rows: list[dict], key: str) -> float:
    spend = sum(r["spend"] for r in rows)
    return sum(r["spend"] * r[key] for r in rows) / spend if spend else 0.0


def metric_dict(rows: list[dict]) -> dict:
    return {
        "materials": len(rows),
        "ctr": round(weighted(rows, "ctr"), 2),
        "cvr": round(weighted(rows, "cvr"), 2),
        "v3": round(weighted(rows, "v3"), 1),
    }


def category_rows(rows: list[dict], limit: int = 10) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        cat = r["category"] or "未标注类目"
        grouped[cat].append(r)
    total_spend = sum(r["spend"] for r in rows)
    out = []
    for cat, group in grouped.items():
        spend = sum(r["spend"] for r in group)
        m = metric_dict(group)
        focus, why = CATEGORY_PLAYBOOK.get(cat, GENERIC_PLAYBOOK)
        out.append({
            "name": cat,
            "materials": len(group),
            "share": round(spend / total_spend * 100, 1) if total_spend else 0.0,
            "ctr": m["ctr"],
            "cvr": m["cvr"],
            "v3": m["v3"],
            "focus": focus,
            "why": why,
        })
    return sorted(out, key=lambda x: x["share"], reverse=True)[:limit]


def best(categories: list[dict], key: str) -> dict | None:
    # 过滤单条、未标注类目，减少偶发值噪声。
    eligible = [x for x in categories if x["materials"] >= 3 and x["name"] != "未标注类目"]
    return max(eligible, key=lambda x: x[key]) if eligible else None


def narrative(industry: str, cats: list[dict]) -> dict:
    leader = next((x for x in cats if x["name"] != "未标注类目"), cats[0] if cats else None)
    ctr = best(cats, "ctr")
    v3 = best(cats, "v3")
    cvr = best(cats, "cvr")
    if not leader:
        return {"headline": "当前暂无可用素材数据", "text": "请补充含素材 URL 与指标的行业数据。", "direction": "—"}
    bits = [f"{leader['name']}是当前消耗占比最高的细分类目（{leader['share']}%）"]
    if ctr:
        bits.append(f"{ctr['name']}的 CTR 表现最好（{ctr['ctr']}%）")
    if v3:
        bits.append(f"{v3['name']}的 3 秒完播最高（{v3['v3']}%）")
    if cvr:
        bits.append(f"{cvr['name']}的浅层 CVR 最高（{cvr['cvr']}%）")
    return {
        "headline": f"{industry}赛道：优先用类目决策点组织创意表达",
        "text": "；".join(bits) + "。",
        "direction": f"下一轮可优先围绕「{leader['name']}」测试：{leader['focus']}。{leader['why']}",
    }


def read_sheet(wb, sheet: str, industry_id: str, industry_name: str) -> dict:
    ws = wb[sheet]
    rows: list[dict] = []
    # 女装 Sheet 存在多余格式列，固定读取前 8 个真实字段。
    for excel_row in ws.iter_rows(min_row=2, max_col=8, values_only=True):
        _, url, cat2, cat3, spend, ctr, cvr, v3 = excel_row
        if not isinstance(url, str) or not url.startswith("http"):
            continue
        category = clean_text(cat3) or clean_text(cat2)
        rows.append({
            "url": url,
            "id": hashlib.md5(url.encode()).hexdigest()[:10],
            "category": category,
            "category2": clean_text(cat2),
            "spend": num(spend),
            "ctr": num(ctr),
            "cvr": num(cvr),
            "v3": num(v3),
        })
    # 同一素材 URL 若有重复行，保留消耗最高的一行。
    unique: dict[str, dict] = {}
    for row in rows:
        if row["url"] not in unique or row["spend"] > unique[row["url"]]["spend"]:
            unique[row["url"]] = row
    rows = list(unique.values())
    rows.sort(key=lambda x: x["spend"], reverse=True)
    cats = category_rows(rows)
    return {
        "id": industry_id,
        "name": industry_name,
        "emoji": INDUSTRIES[industry_id]["emoji"],
        "desc": INDUSTRIES[industry_id]["desc"],
        "metrics": metric_dict(rows),
        "categories": cats,
        "insight": narrative(industry_name, cats),
        "top_materials": [{k: r[k] for k in ["id", "url", "category", "ctr", "cvr", "v3"]} for r in rows[:12]],
        "data_note": "数据来自《服饰大盘》；按素材 URL 去重后，以日均消耗加权聚合。未标注类目不参与类目结论。",
    }


def bag_shoes_data() -> dict:
    p = json.loads(BAG_HISTORY.read_text(encoding="utf-8"))
    cats = []
    videos = []
    total_cost = 0.0
    for tab in p["tabs"]:
        for item in tab.get("top_thirds", []):
            total_cost += num(item.get("cost_wan"))
            focus, why = CATEGORY_PLAYBOOK.get(item["name"], GENERIC_PLAYBOOK)
            cats.append({
                "name": item["name"], "materials": item.get("materials", 0),
                "cost_wan": num(item.get("cost_wan")), "ctr": item.get("ctr", 0), "cvr": item.get("cvr", 0),
                "v3": item.get("v3", 0), "focus": focus, "why": why,
            })
        videos += tab.get("top_videos", [])
    for x in cats:
        x["share"] = round(x.pop("cost_wan") / total_cost * 100, 1) if total_cost else 0
    cats.sort(key=lambda x: x["share"], reverse=True)
    cats = cats[:10]
    metrics = p["overall"]
    return {
        "id": "bag-shoes", "name": "箱包鞋靴", "emoji": "👜", "desc": INDUSTRIES["bag-shoes"]["desc"],
        "metrics": {"materials": metrics["materials"], "ctr": metrics["ctr"], "cvr": metrics["cvr"], "v3": metrics["v3"]},
        "categories": cats,
        "insight": narrative("箱包鞋靴", cats),
        "top_materials": [{"id": v.get("md5", ""), "url": v["url"], "category": v.get("third", ""), "ctr": v.get("ctr", 0), "cvr": v.get("cvr", 0), "v3": v.get("v3", 0)} for v in videos[:12]],
        "data_note": "箱包鞋靴来自已上线的 7 月 20 日深度分析归档；可进入原站查看标签树、逐帧拆解与创意标签。",
        "deep_link": "https://chenxiaomei19960125-glitch.github.io/bag-shoes-creative-report/",
    }


def build_data() -> dict:
    wb = load_workbook(XLSX, read_only=True, data_only=True)
    industries = {"bag-shoes": bag_shoes_data()}
    for key in ["underwear", "menswear", "womenswear"]:
        meta = INDUSTRIES[key]
        industries[key] = read_sheet(wb, meta["sheet"], key, meta["name"])
    return {"title": "服饰四大赛道创意洞察", "industries": industries, "order": list(INDUSTRIES)}


HTML = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>服饰四大赛道创意洞察</title>
<style>
:root{--blue:#0052d9;--blue2:#0d7df2;--ink:#172b4d;--text:#33425c;--muted:#71809a;--bg:#f4f7fb;--card:#fff;--line:#e2eaf5;--green:#00a870;--gold:#d88200}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",Arial,sans-serif}.wrap{max-width:1440px;margin:auto;padding:28px 36px 56px}.hero{padding:38px 42px;border-radius:24px;background:linear-gradient(135deg,#003ea6,#0052d9 55%,#1590f4);color:#fff;box-shadow:0 18px 42px rgba(0,82,217,.22);position:relative;overflow:hidden}.hero:after{content:"";position:absolute;right:-80px;top:-130px;width:420px;height:420px;border-radius:50%;background:rgba(255,255,255,.12)}.eyebrow{display:inline-block;padding:5px 10px;border:1px solid rgba(255,255,255,.42);border-radius:999px;background:rgba(255,255,255,.13);font-size:12px;font-weight:600}.hero h1{margin:16px 0 10px;font-size:32px;letter-spacing:.2px}.hero p{position:relative;z-index:1;max-width:800px;margin:0;color:rgba(255,255,255,.9);font-size:14px;line-height:1.8}.method{position:relative;z-index:1;display:flex;flex-wrap:wrap;gap:8px;margin-top:20px}.method span{padding:6px 10px;border-radius:8px;background:rgba(255,255,255,.12);font-size:12px}.industry-nav{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:22px 0}.industry{cursor:pointer;text-align:left;border:1px solid var(--line);background:#fff;padding:18px;border-radius:16px;transition:.2s;box-shadow:0 3px 12px rgba(0,82,217,.04)}.industry:hover{transform:translateY(-2px);border-color:#8ab8ff}.industry.active{background:linear-gradient(135deg,#0052d9,#0d7df2);border-color:#0052d9;color:#fff;box-shadow:0 10px 22px rgba(0,82,217,.22)}.industry b{display:block;font-size:17px}.industry span{display:block;margin-top:6px;font-size:12px;line-height:1.5;color:var(--muted)}.industry.active span{color:rgba(255,255,255,.88)}.section{margin-top:20px;padding:26px;background:var(--card);border:1px solid var(--line);border-radius:20px;box-shadow:0 5px 18px rgba(0,82,217,.04)}.section-head{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;margin-bottom:18px}.section h2{margin:0;font-size:21px}.section-head p{margin:5px 0 0;color:var(--muted);font-size:13px}.deep-link{white-space:nowrap;text-decoration:none;background:#eaf2ff;color:var(--blue);padding:8px 12px;border-radius:8px;font-size:12px;font-weight:600}.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.kpi{padding:18px;border-radius:14px;background:#f7faff;border:1px solid #e4eefb}.kpi b{display:block;color:var(--blue);font-size:26px}.kpi span{display:block;margin-top:5px;color:var(--muted);font-size:12px}.insight{display:grid;grid-template-columns:1fr 1fr;gap:16px}.insight-main{padding:20px;border:1px solid #bfdbff;border-radius:14px;background:linear-gradient(135deg,#eff6ff,#f9fcff)}.insight-main .label{color:var(--blue);font-size:12px;font-weight:700}.insight-main h3{margin:8px 0;color:#123d83;font-size:18px}.insight-main p{margin:0;color:#425a7d;font-size:13px;line-height:1.75}.direction{padding:20px;border-left:4px solid var(--green);border-radius:10px;background:#f4fbf8}.direction b{color:#00865a}.direction p{margin:8px 0 0;color:#405869;font-size:13px;line-height:1.75}.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:12px}table{width:100%;border-collapse:collapse;min-width:1000px;font-size:13px}th{padding:12px;text-align:left;background:#edf4ff;color:#1d4f9d;white-space:nowrap;border-bottom:1px solid #dce8f7}td{padding:12px;color:var(--text);vertical-align:top;line-height:1.6;border-bottom:1px solid #edf2f8}tr:last-child td{border-bottom:0}td.name{font-weight:700;color:var(--ink)}td.hi{font-weight:700;color:var(--blue)}td.why{min-width:260px;color:#50637d}.tag{display:inline-block;padding:3px 7px;margin:0 4px 4px 0;border:1px solid #d6e4fa;border-radius:6px;background:#f0f6ff;color:#2e68bd;font-size:11px}.material-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.material{overflow:hidden;border:1px solid var(--line);border-radius:14px;background:#fff}.material video{display:block;width:100%;height:238px;background:#101828;object-fit:contain}.material-body{padding:13px}.material-title{font-weight:700;color:var(--ink);font-size:14px}.material-metrics{display:flex;gap:10px;margin-top:8px;font-size:12px;color:var(--muted)}.material-metrics b{color:var(--blue)}.note{margin-top:12px;color:var(--muted);font-size:12px;line-height:1.65}.empty{padding:28px;text-align:center;color:var(--muted);border:1px dashed #cbd9ea;border-radius:12px}.footer{text-align:center;color:#91a0b6;margin-top:30px;font-size:12px}@media(max-width:1000px){.industry-nav{grid-template-columns:repeat(2,1fr)}.material-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:700px){.wrap{padding:16px}.hero{padding:28px 24px}.hero h1{font-size:25px}.industry-nav,.kpis,.insight,.material-grid{grid-template-columns:1fr}.section{padding:18px}.section-head{display:block}.deep-link{display:inline-block;margin-top:10px}}
</style></head><body><main class="wrap"><header class="hero"><div class="eyebrow">AI 创意洞察 · 服饰行业专项</div><h1>服饰四大赛道创意分析</h1><p>覆盖箱包鞋靴、内衣、男装、女装四个独立入口：从行业大盘、细分类目到 Top 素材，识别高效品类表现并沉淀可验证的创意策略方向。</p><div class="method"><span>行业独立入口</span><span>消耗加权指标</span><span>类目效果对比</span><span>Top 素材可回看</span><span>策略方向沉淀</span></div></header><nav class="industry-nav" id="nav"></nav><div id="app"></div><footer class="footer">数据来源：箱包鞋靴深度分析归档 & 《服饰大盘》 · 指标按日均消耗加权聚合</footer></main><script>const DATA=__DATA__;
const fmt=n=>Number(n).toFixed(1); const fmtPct=n=>Number(n).toFixed(2)+'%';
function industryId(){const id=new URLSearchParams(location.search).get('industry');return DATA.industries[id]?id:'bag-shoes'}
function nav(){const current=industryId();document.getElementById('nav').innerHTML=DATA.order.map(id=>{const x=DATA.industries[id];return `<button class="industry ${id===current?'active':''}" onclick="go('${id}')"><b>${x.emoji} ${x.name}</b><span>${x.desc}</span></button>`}).join('')}
function go(id){history.pushState({},'',location.pathname+'?industry='+id);render();window.scrollTo({top:0,behavior:'smooth'})}
function tags(text){return String(text||'').split(' / ').map(t=>`<span class="tag">${t}</span>`).join('')}
function materialCard(x,i){return `<article class="material"><video controls muted preload="metadata" src="${x.url}"></video><div class="material-body"><div class="material-title">#${i+1} ${x.category||'未标注类目'}</div><div class="material-metrics"><span>CTR <b>${fmtPct(x.ctr)}</b></span><span>3s <b>${fmt(x.v3)}%</b></span><span>CVR <b>${fmtPct(x.cvr)}</b></span></div></div></article>`}
function render(){const x=DATA.industries[industryId()];nav();const catRows=x.categories.map((c,i)=>`<tr><td>${i+1}</td><td class="name">${c.name}</td><td>${c.materials}</td><td class="hi">${fmt(c.share)}%</td><td class="hi">${fmtPct(c.ctr)}</td><td>${fmt(c.v3)}%</td><td>${fmtPct(c.cvr)}</td><td>${tags(c.focus)}</td><td class="why">${c.why}</td></tr>`).join('');document.getElementById('app').innerHTML=`
<section class="section"><div class="section-head"><div><h2>${x.emoji} ${x.name}行业大盘</h2><p>${x.desc}</p></div>${x.deep_link?`<a class="deep-link" target="_blank" href="${x.deep_link}">进入箱包鞋靴深度站 ↗</a>`:''}</div><div class="kpis"><div class="kpi"><b>${x.metrics.materials}</b><span>有效去重素材</span></div><div class="kpi"><b>${fmtPct(x.metrics.ctr)}</b><span>消耗加权 CTR</span></div><div class="kpi"><b>${fmt(x.metrics.v3)}%</b><span>消耗加权 3秒完播</span></div><div class="kpi"><b>${fmtPct(x.metrics.cvr)}</b><span>消耗加权 浅层CVR</span></div></div></section>
<section class="section"><div class="section-head"><div><h2>📌 本期类目洞察与素材方向</h2><p>结论来自细分类目指标表现；策略方向依据品类决策需求生成，不将未视觉核验的内容冒充为实际素材标签。</p></div></div><div class="insight"><div class="insight-main"><div class="label">行业结论</div><h3>${x.insight.headline}</h3><p>${x.insight.text}</p></div><div class="direction"><b>下一轮素材方向</b><p>${x.insight.direction}</p></div></div></section>
<section class="section"><div class="section-head"><div><h2>📊 细分类目效果与主流打法</h2><p>按消耗占比排序，空类目不纳入结论。</p></div></div><div class="scroll"><table><thead><tr><th>#</th><th>细分类目</th><th>素材数</th><th>消耗占比</th><th>CTR</th><th>3秒完播</th><th>浅层CVR</th><th>建议关注的创意表达</th><th>为什么值得测试</th></tr></thead><tbody>${catRows}</tbody></table></div></section>
<section class="section"><div class="section-head"><div><h2>🎬 Top 素材回看</h2><p>按日均消耗排序；可直接播放视频核对类目与策略方向。视觉标签、逐帧拆解将在后续视觉识别标注完成后补充。</p></div></div><div class="material-grid">${x.top_materials.map(materialCard).join('')||'<div class="empty">当前暂无可播放的素材</div>'}</div><div class="note">${x.data_note}</div></section>`}
window.addEventListener('popstate',render);render();</script></body></html>'''


def main() -> None:
    if not XLSX.exists():
        raise FileNotFoundError(f"未找到数据文件：{XLSX}")
    if not BAG_HISTORY.exists():
        raise FileNotFoundError(f"未找到箱包鞋靴归档：{BAG_HISTORY}")
    data = build_data()
    OUT.mkdir(parents=True, exist_ok=True)
    DATA_OUT.mkdir(parents=True, exist_ok=True)
    (DATA_OUT / "apparel_snapshot.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "index.html").write_text(HTML.replace("__DATA__", json.dumps(data, ensure_ascii=False)), encoding="utf-8")
    print("[✓] 已生成服饰四大赛道创意分析站")
    for key in data["order"]:
        x = data["industries"][key]
        print(f"  {x['name']}: {x['metrics']['materials']} 条素材 / {len(x['categories'])} 个细分类目")
    print(f"[✓] 页面：{OUT / 'index.html'}")


if __name__ == "__main__":
    main()
