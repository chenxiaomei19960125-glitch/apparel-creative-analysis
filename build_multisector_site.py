#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""服饰创意分析站：总站标签树 + 三个行业深度页。

- 总站仅呈现行业整体标签树和四个赛道入口。
- 箱包鞋靴入口直达既有深度站，内容保持原样。
- 内衣、男装、女装分别生成与箱包鞋靴一致的三 Tab 页面：
  标签树 / 标签分析和结论 / 素材内容逐帧剖析。
"""
from __future__ import annotations

import hashlib
import html
import json
import shutil
from collections import defaultdict
from pathlib import Path

from openpyxl import load_workbook

BASE = Path(__file__).resolve().parent
XLSX = Path('/Users/chenxiaomei/Desktop/服饰大盘.xlsx')
DOCS = BASE / 'docs'
DATA_DIR = BASE / 'data'
FRAME_ROOT = BASE / 'assets' / 'frames'

SECTORS = {
    'underwear': {'name': '内衣', 'emoji': '🩲', 'sheet': '内衣', 'desc': '舒适、支撑与贴身功能表达'},
    'menswear': {'name': '男装', 'emoji': '👔', 'sheet': '男装', 'desc': '功能、版型与通勤场景表达'},
    'womenswear': {'name': '女装', 'emoji': '👗', 'sheet': '女装', 'desc': '上身效果、风格与穿搭种草'},
}

# 分行业/类目创意标签基线。实际关键帧视觉覆盖优先写在 manual_visual_tags.json。
CATEGORY_TAGS = {
    '文胸/乳贴/内裤': {'struct':'真人口播','role':'单人女','scene':'居家室内','sell':'功能实测','function':'舒适贴合','emotion':'身材焦虑自信种草','people':'女性贴身需求','pain':'勒痕/空杯/闷热'},
    '袜子': {'struct':'沉浸式产品展示','role':'无人出镜','scene':'居家室内','sell':'功能实测','function':'吸汗透气','emotion':'促销紧迫感','people':'日常通勤','pain':'闷脚/滑落/磨脚'},
    '塑身衣/裤': {'struct':'真人口播','role':'单人女','scene':'居家室内','sell':'场景痛点','function':'收腹提臀','emotion':'身材焦虑自信种草','people':'女性塑形','pain':'显胖/勒肉/卷边'},
    '睡衣/家居服': {'struct':'真人口播','role':'单人女','scene':'居家室内','sell':'颜值种草','function':'亲肤舒适','emotion':'舒适治愈','people':'居家女性','pain':'闷热/扎肤/版型松垮'},
    '儿童内衣裤袜': {'struct':'真人口播','role':'单人女','scene':'居家室内','sell':'信任背书','function':'亲肤安全','emotion':'家长关怀','people':'儿童家长','pain':'敏感肌/勒痕/不耐穿'},
    '上衣': {'struct':'真人口播','role':'单人女','scene':'居家室内','sell':'颜值种草','function':'显瘦修饰','emotion':'身材焦虑自信种草','people':'通勤女性','pain':'显胖/不好搭/版型不合身'},
    '裤子': {'struct':'真人口播','role':'单人女','scene':'居家室内','sell':'功能实测','function':'显腿长','emotion':'身材焦虑自信种草','people':'日常通勤','pain':'卡裆/显腿粗/不舒服'},
    '裙子': {'struct':'真人口播','role':'单人女','scene':'户外街景','sell':'颜值种草','function':'显瘦显高','emotion':'美女吸睛','people':'约会穿搭','pain':'显胖/透/不好搭'},
    '套装/学生校服/工作制服': {'struct':'真人口播','role':'单人女','scene':'居家室内','sell':'场景痛点','function':'省心搭配','emotion':'省心决策','people':'通勤/学生','pain':'搭配困难/不正式'},
    '速干衣裤': {'struct':'真人口播','role':'单人男','scene':'户外街景','sell':'功能实测','function':'速干透气','emotion':'运动挑战','people':'运动户外','pain':'闷汗/黏身/不耐磨'},
    '防晒衣/皮肤衣': {'struct':'真人口播','role':'单人女','scene':'户外街景','sell':'功能实测','function':'防晒透气','emotion':'夏日出行','people':'户外女性','pain':'晒黑/闷热/不显瘦'},
    '羽绒服/棉服': {'struct':'真人口播','role':'单人女','scene':'户外街景','sell':'功能实测','function':'保暖轻量','emotion':'冬季保暖','people':'冬季通勤','pain':'臃肿/不保暖/钻绒'},
    '衬衫': {'struct':'真人口播','role':'单人女','scene':'居家室内','sell':'颜值种草','function':'挺括显瘦','emotion':'通勤自信','people':'职场通勤','pain':'易皱/显胖/不好搭'},
}
DEFAULT_TAGS = {'struct':'真人口播','role':'单人女','scene':'居家室内','sell':'功能实测','function':'核心卖点展示','emotion':'结果导向','people':'目标消费人群','pain':'常见决策顾虑'}

TREE = [
    ('内容形式','核心：先定义素材的视频创意体裁。', True, [('视频结构类型','p00','真人口播 / 多人剧情 / 沉浸式产品展示 / 直播切片 / AI数字人口播','单人真人讲解或种草=真人口播；两人及以上互动=多人剧情；无人/手部/纯产品=沉浸式。')]),
    ('画面客观要素','核心：基于真实画面识别角色和拍摄地点。', True, [('拍摄场景类型','p00','居家室内 / 纯色棚拍 / 酒店大堂 / 户外街景 / 工厂车间 / 机场 / 商场门店 / 学校展会','按画面物理拍摄地直接识别。'),('出镜角色类型','p00','单人女 / 单人男 / 多人对话 / 无人出镜 / 明星','按画面人物数量、性别与关系判断；纯产品或仅手部归无人出镜。')]),
    ('商品属性','季节、功能与材质构成商品本身的可解释决策点。', False, [('适用季节','p0','春夏秋冬 / 四季通用 / 开学季 / 暑假出游季 / 换季','商品厚薄、画面环境、字幕或口播季节词。'),('功能属性','p0','防滑 / 防水 / 透气 / 显瘦显高 / 增高 / 大容量 / 收纳分层 / 耐磨 / 缓震 / 护脊','字幕/口播功能词和实测画面共同确认。'),('材质属性','p0','真皮 / PU / 帆布 / 棉 / EVA / 五金 / 尼龙防泼水','画面特写与字幕材质词；无清晰依据不强标。')]),
    ('卖点表达','识别素材如何切入需求、建立信任并推动转化。', False, [('功能实测','p0','弹力 / 防水 / 透气 / 耐磨 / 承重 / 收纳 / 防滑 / 减震','测试动作 + 测试字幕或口播。'),('场景痛点','p0','磨脚 / 显胖 / 闷热 / 容量不足 / 收纳乱 / 轮子卡顿','痛点文字、前后对比或场景冲突。'),('信任背书 / 价格促销 / 竞品对比','p0','工艺 / 工厂 / 检测 / 达人 / 限时折扣 / 工厂直销 / 平替','背书字幕、价格浮层或明确对比话术。')]),
    ('情绪与营销','通过情绪、使用场景与风格建立观看动机。', False, [('情绪钩子类型','p0','身材焦虑 / 大牌平替 / 促销紧迫感 / 美女吸睛 / 亲情关怀 / 猎奇实验','开头3秒标题、口播话术、画面情绪。'),('题材 / 使用场景','p0','通勤 / 旅行 / 运动 / 居家 / 礼赠 / 中老年关怀','场景背景 + 口播用途综合判定。'),('穿搭风格 / 节日节点','p0','通勤简约 / 休闲日常 / 轻奢高级 / 少女法系 / 运动风 / 开学季 / 618 / 双11','整体视觉调性、节点字幕和促销话术。')]),
]


def num(v):
    try: return float(v)
    except (TypeError, ValueError): return 0.0


def clean(v):
    v = '' if v is None else str(v).strip()
    return '' if v in {'空','None','nan','-'} else v


def md5(url): return hashlib.md5(url.encode()).hexdigest()[:10]


def load_overrides():
    p = DATA_DIR / 'manual_visual_tags.json'
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}


def load_sector(sheet, sector):
    wb = load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb[sheet]
    overrides = load_overrides().get(sector, {})
    rows = {}
    for r in ws.iter_rows(min_row=2, max_col=8, values_only=True):
        _, url, cat2, cat3, spend, ctr, cvr, v3 = r
        if not isinstance(url, str) or not url.startswith('http'): continue
        row = {'id':md5(url),'url':url,'cat2':clean(cat2),'category':clean(cat3) or clean(cat2),'spend':num(spend),'ctr':num(ctr),'cvr':num(cvr),'v3':num(v3)}
        if url not in rows or row['spend'] > rows[url]['spend']: rows[url] = row
    out = list(rows.values())
    for r in out:
        tags = dict(CATEGORY_TAGS.get(r['category'], DEFAULT_TAGS))
        tags.update(overrides.get(r['id'], {}))
        r['tags'] = tags
    return sorted(out, key=lambda x:x['spend'], reverse=True)


def wavg(rows, key):
    total = sum(x['spend'] for x in rows)
    return sum(x['spend']*x[key] for x in rows)/total if total else 0


def aggregate(rows, tag):
    total = sum(r['spend'] for r in rows)
    groups = defaultdict(list)
    for r in rows: groups[r['tags'][tag]].append(r)
    result=[]
    for name, rs in groups.items():
        cost=sum(x['spend'] for x in rs)
        result.append({'name':name,'count':len(rs),'share':round(cost/total*100,1) if total else 0,'ctr':round(wavg(rs,'ctr'),2),'cvr':round(wavg(rs,'cvr'),2),'v3':round(wavg(rs,'v3'),1)})
    # 结构类型固定补齐五类
    if tag == 'struct':
        for name in ['真人口播','多人剧情','沉浸式产品展示','直播切片','AI数字人口播']:
            if name not in groups: result.append({'name':name,'count':0,'share':None,'ctr':None,'cvr':None,'v3':None})
    return sorted(result,key=lambda x:(x['count']==0,-(x['share'] or 0)))


def categories(rows):
    d=defaultdict(list)
    for r in rows:
        if r['category']: d[r['category']].append(r)
    total=sum(r['spend'] for r in rows)
    out=[]
    for name,rs in d.items():
        cost=sum(r['spend'] for r in rs)
        out.append({'name':name,'count':len(rs),'share':round(cost/total*100,1),'ctr':round(wavg(rs,'ctr'),2),'cvr':round(wavg(rs,'cvr'),2),'v3':round(wavg(rs,'v3'),1)})
    return sorted(out,key=lambda x:-x['share'])[:10]


def sector_payload(key):
    meta=SECTORS[key]; rows=load_sector(meta['sheet'],key)
    total=sum(r['spend'] for r in rows)
    by={x:aggregate(rows,x) for x in ['struct','role','scene','sell','function','emotion']}
    cats=categories(rows)
    active=lambda xs:[x for x in xs if x['count']]
    def leader(xs): return active(xs)[0] if active(xs) else {'name':'—','share':0}
    def best(xs,field): return max(active(xs),key=lambda x:x[field]) if active(xs) else {'name':'—',field:0}
    bs=best(by['struct'],'ctr'); bv=best(by['struct'],'v3')
    narrative=(f"{meta['name']}赛道消耗主要集中在「{leader(cats)['name'] if cats else '—'}」；创意结构以「{leader(by['struct'])['name']}」为主。"
               f"CTR 最优为「{bs['name']}」（{bs['ctr']}%），3秒完播最优为「{bv['name']}」（{bv['v3']}%）。")
    return {'id':key,'name':meta['name'],'emoji':meta['emoji'],'desc':meta['desc'],'metrics':{'materials':len(rows),'ctr':round(wavg(rows,'ctr'),2),'cvr':round(wavg(rows,'cvr'),2),'v3':round(wavg(rows,'v3'),1)},'analysis':by,'categories':cats,'top':rows[:12],'narrative':narrative,'note':'标签先以品类创意基线生成；Top素材的可见画面标签会由 manual_visual_tags.json 的关键帧人工核验覆盖。'}


def esc(v): return html.escape(str(v))


def tree_html():
    parts=[]
    for title,desc,core,children in TREE:
        cards=''.join(f'<div class="child"><b>{esc(n)}</b><em>{p}</em><span><strong>标签值：</strong>{esc(vals)}</span><span><strong>判断：</strong>{esc(rule)}</span></div>' for n,p,vals,rule in children)
        parts.append(f'<article class="tree"><div class="tree-main {"core" if core else ""}"><strong>{esc(title)}</strong><span>{esc(desc)}</span></div><div class="tree-child">{cards}</div></article>')
    return ''.join(parts)


def home_html():
    entries = '<a class="entry bag" href="https://chenxiaomei19960125-glitch.github.io/bag-shoes-creative-report/"><div class="emoji">👜</div><b>箱包鞋靴</b><span>进入既有深度站：标签树、标签分析与结论、素材逐帧剖析均保持原样。</span></a>'
    for key,m in SECTORS.items():
        entries += f'<a class="entry" href="{key}/"><div class="emoji">{m["emoji"]}</div><b>{m["name"]}</b><span>{m["desc"]}；进入独立深度分析页。</span></a>'
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>服饰行业创意分析</title>{STYLE}</head><body><main class="wrap"><header class="hero"><div class="eyebrow">AI 创意洞察 · 服饰行业专项</div><h1>服饰行业创意分析</h1><p>总站仅提供服饰行业整体标签树和四个赛道入口；各赛道进入后使用独立的「标签树结构 / 标签分析和结论 / 素材内容逐帧剖析」页面。</p></header><section class="section"><h2>进入赛道分析</h2><p>箱包鞋靴保留已上线的原站内容；内衣、男装和女装分别进入独立分析站。</p><div class="entry-grid">{entries}</div></section><section class="section"><h2>服饰行业整体标签树结构</h2><p>内容形式、画面客观要素为最优先的创意标签；其余标签用于补足商品决策、卖点表达和情绪营销解释。</p><div class="tree-wrap">{tree_html()}</div></section><footer class="footer">服饰创意 XAI · 统一标签语言、效果归因与素材复用</footer></main></body></html>'''

STYLE = r'''<style>
:root{--blue:#0052d9;--ink:#172b4d;--text:#33425c;--muted:#71809a;--bg:#f4f7fb;--card:#fff;--line:#e2eaf5}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",Arial,sans-serif}.wrap{max-width:1440px;margin:auto;padding:28px 36px 56px}.hero{padding:42px;border-radius:24px;background:linear-gradient(135deg,#003ea6,#0052d9 55%,#1590f4);color:#fff;box-shadow:0 18px 42px rgba(0,82,217,.22);position:relative;overflow:hidden}.hero:after{content:"";position:absolute;right:-80px;top:-130px;width:420px;height:420px;border-radius:50%;background:rgba(255,255,255,.12)}.eyebrow{position:relative;z-index:1;display:inline-block;padding:5px 10px;border:1px solid rgba(255,255,255,.42);border-radius:999px;background:rgba(255,255,255,.13);font-size:12px;font-weight:600}.hero h1{position:relative;z-index:1;margin:16px 0 10px;font-size:34px}.hero p{position:relative;z-index:1;max-width:850px;margin:0;color:rgba(255,255,255,.9);font-size:14px;line-height:1.8}.section{margin-top:20px;padding:28px;background:var(--card);border:1px solid var(--line);border-radius:20px;box-shadow:0 5px 18px rgba(0,82,217,.04)}.section h2{margin:0;font-size:22px}.section>p{color:var(--muted);font-size:13px;line-height:1.75}.entry-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:18px}.entry{display:block;text-decoration:none;color:var(--ink);padding:22px;border:1px solid var(--line);border-radius:16px;background:#fff;transition:.2s;box-shadow:0 3px 12px rgba(0,82,217,.04)}.entry:hover{transform:translateY(-3px);border-color:#76aaff;box-shadow:0 12px 25px rgba(0,82,217,.14)}.entry.bag{background:linear-gradient(135deg,#0052d9,#0d7df2);border-color:#0052d9;color:#fff}.entry .emoji{font-size:28px}.entry b{display:block;margin:11px 0 5px;font-size:18px}.entry span{font-size:12px;line-height:1.55;color:var(--muted)}.entry.bag span{color:rgba(255,255,255,.88)}.tree-wrap{display:flex;flex-direction:column;gap:14px;margin-top:18px}.tree{display:grid;grid-template-columns:220px minmax(0,1fr);border:1px solid var(--line);border-radius:15px;overflow:hidden;background:#fff}.tree-main{padding:20px;background:linear-gradient(160deg,#eaf2ff,#dceaff);border-right:1px solid #cfe0fb}.tree-main strong{display:block;color:#003c9f;font-size:19px}.tree-main span{display:block;margin-top:6px;color:#4e617d;font-size:12px;line-height:1.65}.tree-main.core{background:linear-gradient(160deg,#0045bd,#006fe6)}.tree-main.core strong{color:#fff}.tree-main.core span{color:rgba(255,255,255,.87)}.tree-child{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;padding:14px}.child{padding:13px;border:1px solid #e2eaf5;border-radius:10px;background:#fbfdff}.child b{display:block;color:#0052d9;font-size:14px}.child span{display:block;margin-top:6px;color:#65748c;font-size:12px;line-height:1.6}.child strong{color:#33425c}.child em{display:inline-block;margin-top:8px;padding:2px 7px;border-radius:5px;background:#e9f1ff;color:#0052d9;font-size:11px;font-style:normal;font-weight:700}.footer{text-align:center;color:#91a0b6;margin-top:30px;font-size:12px}@media(max-width:1000px){.entry-grid{grid-template-columns:repeat(2,1fr)}.tree{grid-template-columns:1fr}.tree-main{border-right:0;border-bottom:1px solid #cfe0fb}.tree-child{grid-template-columns:repeat(2,1fr)}}@media(max-width:700px){.wrap{padding:16px}.hero{padding:28px 24px}.hero h1{font-size:26px}.entry-grid,.tree-child{grid-template-columns:1fr}.section{padding:19px}}
</style>'''

SECTOR_STYLE = r'''<style>
:root{--blue:#0052d9;--ink:#172b4d;--text:#33425c;--muted:#71809a;--bg:#f4f7fb;--card:#fff;--line:#e2eaf5;--green:#00a870}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",Arial,sans-serif}.wrap{max-width:1440px;margin:auto;padding:24px 36px 56px}.back{display:inline-block;color:#46617e;text-decoration:none;font-size:13px;margin-bottom:14px}.hero{padding:30px 34px;border-radius:21px;background:linear-gradient(135deg,#003ea6,#0052d9 60%,#1590f4);color:white}.hero h1{margin:8px 0;font-size:28px}.hero p{margin:0;color:rgba(255,255,255,.9);font-size:13px}.tabs{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:20px 0}.tab{border:1px solid var(--line);background:#fff;border-radius:13px;padding:15px;cursor:pointer;color:#60708a;font-weight:700;font-size:15px}.tab.active{background:#0052d9;color:white;border-color:#0052d9}.view{display:none}.view.active{display:block}.section{padding:24px;background:#fff;border:1px solid var(--line);border-radius:18px;box-shadow:0 4px 16px rgba(0,82,217,.04);margin-top:14px}.section h2{margin:0;font-size:20px}.section>p{color:var(--muted);font-size:13px;line-height:1.7}.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:16px}.kpi{padding:17px;border:1px solid #e0ebfa;border-radius:12px;background:#f7faff}.kpi b{display:block;color:#0052d9;font-size:25px}.kpi span{display:block;margin-top:5px;color:var(--muted);font-size:12px}.insight{margin-top:16px;padding:18px;border-left:4px solid #0052d9;background:#f4f8ff;border-radius:10px;color:#3e587b;font-size:13px;line-height:1.8}.dim-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-top:16px}.dim{border:1px solid #e0ebfa;border-radius:14px;padding:17px}.dim.core{background:linear-gradient(145deg,#e6f0ff,#d6e8ff);border-color:#85b5ff}.dim h3{margin:0 0 10px;color:#0045bd;font-size:16px}.scroll{overflow-x:auto}.table{width:100%;min-width:620px;border-collapse:collapse;font-size:12px}.table th{background:#edf4ff;color:#164c9c;text-align:left;padding:9px;border-bottom:1px solid #dce8f7}.table td{padding:9px;color:#40546f;border-bottom:1px solid #edf2f8}.table .name{font-weight:700;color:#1f3e73}.table .hi{font-weight:700;color:#0052d9}.tree-wrap{display:flex;flex-direction:column;gap:13px}.tree{display:grid;grid-template-columns:205px minmax(0,1fr);border:1px solid var(--line);border-radius:14px;overflow:hidden}.tree-main{padding:18px;background:#e7f0ff}.tree-main.core{background:linear-gradient(160deg,#0045bd,#006fe6);color:#fff}.tree-main b{font-size:17px}.tree-main span{display:block;margin-top:5px;font-size:12px;line-height:1.6}.tree-child{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;padding:12px}.child{border:1px solid #e2eaf5;border-radius:8px;padding:11px;font-size:12px;color:#5d6d84;line-height:1.6}.child b{display:block;color:#0052d9}.video-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:16px}.video-card{border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#fff}.video-card video{width:100%;height:235px;background:#0d1828;object-fit:contain;display:block}.video-body{padding:14px}.video-head{font-weight:700}.meta{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}.chip{font-size:11px;border:1px solid #cfe0fa;color:#0052d9;background:#eff5ff;padding:3px 7px;border-radius:6px}.creative{margin-top:8px;padding:11px;background:#f7faff;border-radius:8px}.creative b{font-size:12px;color:#34517a}.creative span{display:inline-block;margin:5px 4px 0 0;padding:3px 7px;border:1px solid #d6e4fa;border-radius:5px;color:#2e68bd;font-size:11px}.frames{display:flex;gap:5px;overflow-x:auto;margin-top:11px;padding-bottom:2px}.frames img{width:70px;height:112px;object-fit:cover;border:1px solid #d9e5f5;border-radius:6px;background:#edf3fb}.note{margin-top:12px;color:#71809a;font-size:12px;line-height:1.6}@media(max-width:900px){.kpis,.dim-grid,.video-grid{grid-template-columns:1fr}.tree{grid-template-columns:1fr}.tree-child{grid-template-columns:1fr}.wrap{padding:16px}} 
</style>'''


def sector_html(payload):
    tree = tree_html()
    dim_names={'struct':'视频结构类型','role':'出镜角色类型','scene':'拍摄场景类型','sell':'卖点表达','function':'产品功效','emotion':'情绪钩子'}
    dims=[]
    for key,title in dim_names.items():
        rows=''.join(f'<tr><td class="name">{esc(x["name"])}</td><td>{"—" if x["share"] is None else str(x["share"])+"%"}</td><td class="hi">{"—" if x["ctr"] is None else str(x["ctr"])+"%"}</td><td>{"—" if x["v3"] is None else str(x["v3"])+"%"}</td><td>{"—" if x["cvr"] is None else str(x["cvr"])+"%"}</td></tr>' for x in payload['analysis'][key])
        dims.append(f'<article class="dim {"core" if key in {"struct","role","scene"} else ""}"><h3>{title}</h3><div class="scroll"><table class="table"><thead><tr><th>标签</th><th>消耗占比</th><th>CTR</th><th>3秒完播</th><th>CVR</th></tr></thead><tbody>{rows}</tbody></table></div></article>')
    cats=''.join(f'<tr><td>{i+1}</td><td class="name">{esc(x["name"])}</td><td>{x["count"]}</td><td class="hi">{x["share"]}%</td><td class="hi">{x["ctr"]}%</td><td>{x["v3"]}%</td><td>{x["cvr"]}%</td></tr>' for i,x in enumerate(payload['categories']))
    videos=[]
    for i,x in enumerate(payload['top']):
        t=x['tags']; frame_dir=f'../assets/frames/{payload["id"]}/{x["id"]}'
        frames=''.join(f'<img loading="lazy" src="{frame_dir}/{n}.jpg" onerror="this.style.display=\'none\'" alt="关键帧{n}">' for n in range(1,7))
        videos.append(f'''<article class="video-card"><video controls muted preload="metadata" src="{esc(x['url'])}"></video><div class="video-body"><div class="video-head">#{i+1} {esc(x['category'] or '未标注类目')}</div><div class="meta"><span class="chip">CTR {x['ctr']:.2f}%</span><span class="chip">3s {x['v3']:.1f}%</span><span class="chip">CVR {x['cvr']:.2f}%</span></div><div class="creative"><b>创意标签</b><br><span>视频结构：{esc(t['struct'])}</span><span>出镜角色：{esc(t['role'])}</span><span>拍摄场景：{esc(t['scene'])}</span><span>卖点表达：{esc(t['sell'])}</span><span>产品功效：{esc(t['function'])}</span><span>情绪钩子：{esc(t['emotion'])}</span><span>场景人群：{esc(t['people'])}</span><span>用户痛点：{esc(t['pain'])}</span></div><div class="frames">{frames}</div></div></article>''')
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{payload['name']}创意分析</title>{SECTOR_STYLE}</head><body><main class="wrap"><a class="back" href="../">← 返回服饰行业总站</a><header class="hero"><div>AI 创意洞察 · {payload['name']}赛道</div><h1>{payload['emoji']} {payload['name']}创意分析</h1><p>{payload['desc']} · 结构化标签、效果分析、Top素材创意标签与回看。</p></header><div class="tabs"><button class="tab active" data-tab="tree">🌳 素材标签树结构</button><button class="tab" data-tab="analysis">🏷 标签分析和结论</button><button class="tab" data-tab="materials">🎬 素材内容 · 逐帧剖析</button></div><div class="view active" id="tree"><section class="section"><h2>素材标签树结构</h2><p>与箱包鞋靴使用同一套服饰创意标签语言，内容形式与画面客观要素优先。</p><div class="tree-wrap">{tree}</div></section></div><div class="view" id="analysis"><section class="section"><h2>大盘标签分析 · 一分钟看懂本期</h2><div class="kpis"><div class="kpi"><b>{payload['metrics']['materials']}</b><span>有效去重素材</span></div><div class="kpi"><b>{payload['metrics']['ctr']}%</b><span>消耗加权 CTR</span></div><div class="kpi"><b>{payload['metrics']['v3']}%</b><span>消耗加权 3秒完播</span></div><div class="kpi"><b>{payload['metrics']['cvr']}%</b><span>消耗加权 浅层CVR</span></div></div><div class="insight">{esc(payload['narrative'])}</div></section><section class="section"><h2>核心标签与效果</h2><p>视频结构、出镜角色、拍摄场景为核心标签，使用更深的蓝色卡片强调。</p><div class="dim-grid">{''.join(dims)}</div></section><section class="section"><h2>细分类目效果</h2><div class="scroll"><table class="table"><thead><tr><th>#</th><th>细分类目</th><th>素材数</th><th>消耗占比</th><th>CTR</th><th>3秒完播</th><th>CVR</th></tr></thead><tbody>{cats}</tbody></table></div></section></div><div class="view" id="materials"><section class="section"><h2>Top 素材内容与创意标签</h2><p>每条素材的标签均采用行业类目创意基线；标为关键帧人工核验的素材会覆盖基线标签。后续可持续补充逐帧画面和人工校正。</p><div class="video-grid">{''.join(videos)}</div><div class="note">{esc(payload['note'])}</div></section></div></main><script>document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{{document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x===b));document.querySelectorAll('.view').forEach(x=>x.classList.toggle('active',x.id===b.dataset.tab))}})</script></body></html>'''


def main():
    if not XLSX.exists(): raise FileNotFoundError(XLSX)
    DOCS.mkdir(parents=True, exist_ok=True); DATA_DIR.mkdir(parents=True, exist_ok=True)
    # 首页不加载行业数据；行业页各自独立构建。
    (DOCS/'index.html').write_text(home_html(), encoding='utf-8')
    all_data={}
    for key,meta in SECTORS.items():
        payload=sector_payload(key); all_data[key]=payload
        target=DOCS/key; target.mkdir(parents=True, exist_ok=True)
        (target/'index.html').write_text(sector_html(payload),encoding='utf-8')
    (DATA_DIR/'sector_snapshot.json').write_text(json.dumps(all_data,ensure_ascii=False,indent=2),encoding='utf-8')
    # 同步已抽取关键帧到 Pages 静态目录；未完成的帧会在下一次构建自动补入。
    source_frames = FRAME_ROOT
    target_frames = DOCS / 'assets' / 'frames'
    if source_frames.exists():
        target_frames.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_frames, target_frames, dirs_exist_ok=True)
    print('[✓] 总站：行业入口 + 服饰整体标签树')
    for key,x in all_data.items(): print(f"[✓] {x['name']}深度页：{x['metrics']['materials']} 条素材")

if __name__ == '__main__': main()
