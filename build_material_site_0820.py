#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""素材8.20：四Tab服饰素材分析站。所有单条案例仅展示/解读前15秒。"""
import json, html, shutil
from pathlib import Path
from collections import defaultdict, Counter
from tag_tree_0820 import TAG_TREE

BASE = Path(__file__).resolve().parent
DOCS = BASE / 'docs'
DATA = BASE / 'data'
FRAMES = BASE / 'assets' / 'frames0820'
raw = json.loads((DATA / 'material_0820.json').read_text(encoding='utf-8'))
manual = json.loads((DATA / 'manual_tags_0820.json').read_text(encoding='utf-8'))

DIMENSIONS = [
    ('struct', '制作类型', '内容形式'), ('season', '适用季节/节点', '商品属性'), ('function', '功能属性', '商品属性'), ('material', '材质属性', '商品属性'),
    ('test', '功能实测', '卖点表达'), ('pain', '场景痛点', '卖点表达'), ('trust', '信任背书类型', '卖点表达'), ('price', '价格/促销表达', '卖点表达'), ('compete', '竞品对比', '卖点表达'),
    ('emotion', '情绪钩子类型', '情绪与营销'), ('scene_use', '题材/使用场景', '情绪与营销'), ('festival', '节日/节点营销', '情绪与营销'), ('style', '穿搭风格类型', '情绪与营销'),
    ('shoot', '拍摄场景类型', '画面客观要素'), ('role', '出镜角色类型', '画面客观要素')]

def esc(x): return html.escape(str(x or '—'))
def n(x):
    try: return float(x)
    except: return 0.0

def fallback(item):
    """未进62条前15秒人工审阅清单的素材，仅用于三类大盘聚合；不伪造单条前15秒解读。"""
    s=(item.get('pname') or '').lower()
    d={'season':'四季通用','function':'其他','material':'未识别（信息不足）','struct':'真人口播','test':'无实测（口播为主）','pain':'其他','trust':'无背书','price':'无明显价格促销','compete':'无对比','emotion':'无明确钩子','scene_use':'日常通勤穿搭','festival':'无节日营销','style':'基础款','shoot':'家居室内（客厅）','role':'素人模特（女）','cat':'服饰其他','pn':item.get('pname','未命名产品')}
    if any(k in s for k in ['t恤','上衣','裙','连衣','衬衫','背心','防晒衣']):
        d.update({'cat':'女装','season':'夏季','function':'显瘦/透气','material':'纯棉','struct':'AI数字人口播','pain':'显瘦/显肉','style':'休闲日常','shoot':'绿幕影棚','role':'素人模特（女）'})
    elif any(k in s for k in ['文胸','内衣','内裤','睡衣','睡裙','塑身']):
        d.update({'cat':'内衣','function':'提拉聚拢/透气','material':'蕾丝','pain':'胖姐妹/身材焦虑','emotion':'身材焦虑自信种草','scene_use':'居家生活','shoot':'家居室内（卧室）'})
    elif any(k in s for k in ['男','polo','西裤','裤']):
        d.update({'cat':'男装','function':'透气/不起球','material':'纯棉','role':'素人模特（男）','style':'商务/职场通勤'})
    elif any(k in s for k in ['包','箱','书包']):
        d.update({'cat':'箱包','function':'大容量/收纳','material':'皮革','struct':'沉浸式产品展示','role':'无人出镜（纯产品/手部特写）','shoot':'家居室内（桌面）'})
    elif any(k in s for k in ['项链','耳环','首饰','珠宝']):
        d.update({'cat':'珠宝','function':'装饰/百搭','material':'银/合金','scene_use':'礼赠/婚庆','style':'轻奢高级'})
    return d

def enrich(items):
    out=[]
    for x in items:
        y=dict(x); tags=dict(fallback(y)); tags.update(manual.get(y['id'],{})); y['tags']=tags; out.append(y)
    return out

items=enrich(raw['items']); by_id={x['id']:x for x in items}
good=[by_id[x['id']] for x in raw['good']]; bad=[by_id[x['id']] for x in raw['bad']]; rising=[by_id[x['id']] for x in raw['rising']]
demo=[by_id[x['id']] for x in raw['demo30']]

# 黄金公式只保留已逐帧人工复核、且不是普通图片轮播/图文的真实视频素材。
# 剧情钩子但未在前15秒展示服饰产品的素材同样不纳入，避免用泛剧情充数。
GOLDEN_EXCLUDE_IDS = {'cc830a3642', 'aa745ae4c3'}
def golden_score(x):
    return n(x['ctr']) * .65 + n(x['dur']) / 10 * .20 + n(x['v3']) / 100 * .15

golden=[x for x in items if x['id'] in manual
        and x['tags'].get('struct') not in {'AI数字人口播', '图文'}
        and x['id'] not in GOLDEN_EXCLUDE_IDS]
golden.sort(key=golden_score, reverse=True)

# 用户指定的优秀防晒口罩素材：置于黄金公式第一名，按其真实前15秒画面复盘。
FEATURED_URL = 'https://adsmind.gdtimg.com/ads_svp_video__0bc3vmdauaag5aajojxcgjurzkyebkvqmcsa.f0.mp4?dis_k=f759b48db7f57016d920457fd7967c81&dis_t=1776590198&m=88032107e08097f69c48887fda2735b2&sha256=ac2261a9fd457ff3614f448db22bf54c5d7029e71c86786d1be3b2c96b3f1599'
featured = {
    'id': '4da64df243', 'url': FEATURED_URL, 'pname': 'UPF200+ 冰丝防晒口罩',
    'tags': {
        'formula_override': ['下周开始紫外线飙升危机钩子', 'UPF200+物理防晒实测', '反复水洗不变形卖点'],
        'open': '0-3s：女生拿起冰丝面罩，字幕直给「下周开始紫外线飙升」，以紫外线危机抢占注意力。',
        'mid': '3-9s：真人戴上面罩，展示 UV 检测卡并打出「UPF200+」；随后贴脸展示凉感、透气与不闷。',
        'end': '9-15s：水中浸洗面罩并展示洗后形态，字幕强调「不掉防晒力 / 不会变形褪色」；最后切户外通勤穿搭。',
        'end_frame': 5,
        'audience_override': '户外通勤女性 / 敏感肌怕晒人群 / 25-45岁每天开车、骑行或步行出门的人群',
        'cat': '防晒装备 / 冰丝防晒口罩'
    }
}
golden.insert(0, featured)

# ==== 用户指定的 AI 短剧素材（不在8.20表内，已单独下载并逐帧复核前15秒画面）====
AI_DRAMA_URL = 'https://adsmind.gdtimg.com/ads_svp_video__0b536qa72aabiuaf2vlbhrvbv5ae7x2ad7ka.f0.mp4'
ai_drama = {
    'id': '4b96fcfd3e', 'url': AI_DRAMA_URL, 'pname': 'AI短剧 · 家庭情感冲突（服饰剧情引流）',
    'tags': {
        'formula_override': ['悬念反转情绪钩子（撞见老公车上有人）', 'AI生成多人剧情制作类型', '母婴亲子出镜 × 车内座驾冲突场景'],
        'open': '0-3s：AI生成画面，孕妈牵着女儿走在街边，字幕直给「回家路上竟看到老公和别的女人在车上…」，用婚姻危机悬念抢占注意力。',
        'mid': '3-9s：切到车内，西装男与黑色蕾丝裙女子亲密同框，冲突升级；随后孕妈侧脸特写喊「小宝」，格纹衬衫＋白吊带＋阔腿裤仅作剧情自然穿着。',
        'end': '9-15s：女儿喊「不行」并伸手拉住车门，字幕「爸爸的副驾只有妈妈能坐」「坏阿姨」，用孩子视角完成情绪反转收尾。注：前15秒无任何服饰卖点展示或功能实测，属纯剧情引流打法。',
        'open_frame': 1, 'mid_frame': 2, 'end_frame': 6,
        'audience_override': '已婚已育女性 / 25-45岁 / 关注婚姻信任与家庭情感话题、易被强冲突剧情吸引的人群',
        'cat': 'AI短剧 / 女装（剧情引流）', 'struct': 'AI生成多人剧情（AI短剧）'
    }
}

def _pop_golden(mid):
    for i, x in enumerate(golden):
        if x['id'] == mid:
            return golden.pop(i)
    return None

_polo = _pop_golden('2ba75c286e')   # 原第2位 POLO衫，按要求后移
_shoe = _pop_golden('68533446e9')   # 原第28位 厚底运动鞋，按要求提到第4位
golden.insert(1, ai_drama)          # 第2位：AI短剧素材
if _shoe: golden.insert(3, _shoe)   # 第4位
if _polo: golden.insert(11, _polo)  # 后移至第12位

def tree_html():
    res=[]
    for main,desc,core,children in TAG_TREE:
        rows=''.join(f'<tr><td class="sub">{esc(n)}</td><td><i>{esc(p)}</i></td><td>{esc(vals)}</td><td>{esc(rule)}</td><td>{esc(explain)}</td></tr>' for n,p,vals,rule,explain in children)
        res.append(f'<article class="tree"><aside class="tree-main {"core" if core else ""}"><b>{esc(main)}</b><span>{esc(desc)}</span></aside><div class="scroll"><table><thead><tr><th>二级标签</th><th>优先级</th><th>Value枚举值（各赛道可自行扩改）</th><th>判断依据/画面特征（核心Key）</th><th>二级标签分类说明</th></tr></thead><tbody>{rows}</tbody></table></div></article>')
    return ''.join(res)

# ============ Tab3：统一样本池 → 15个二级标签 → 按CTR分三类输出Top3枚举值 ============
# 关键修正：高CTR与低CTR必须在"同一个样本池、同一套枚举值排名"上取两端，
# 否则（旧逻辑分别在 good / bad 两个子池里各自取Top3）同一枚举值会同时出现在高低两栏。
POOL_TARGET = 500      # 目标样本量：500条去重视频样本
MIN_SAMPLES = 3        # 单个枚举值最少样本数，低于此不参与排名（避免个别素材噪音）

# 按消耗降序取前 POOL_TARGET 条去重素材作为打标样本池（不足则全量，不虚构补足）
POOL = sorted(items, key=lambda x: n(x['spend']), reverse=True)[:POOL_TARGET]
POOL_N = len(POOL)
POOL_MANUAL = sum(1 for x in POOL if x['id'] in manual)   # 其中人工逐帧复核条数

def tag_stats(field):
    """在统一样本池上，按该二级标签的枚举值聚合 CTR 与 CTR 趋势。"""
    g=defaultdict(list)
    for x in POOL:
        v=x['tags'].get(field)
        if v and v not in ('—',''): g[v].append(x)
    rows=[]
    for tag,xs in g.items():
        if len(xs) < MIN_SAMPLES: continue      # 样本量不足不参与排名
        multi=[x for x in xs if n(x.get('days'))>=2]   # 趋势仅用多天素材计算
        rows.append({'tag':tag,'count':len(xs),
                     'ctr':sum(n(x['ctr']) for x in xs)/len(xs),
                     'v3':sum(n(x['v3']) for x in xs)/len(xs),
                     'dur':sum(n(x['dur']) for x in xs)/len(xs),
                     'cvr':sum(n(x['cvr']) for x in xs)/len(xs),
                     'spend':sum(n(x['spend']) for x in xs),
                     'slope':(sum(n(x['slope']) for x in multi)/len(multi)) if multi else None,
                     'slope_n':len(multi)})
    return rows

_CACHE={}
def stats_of(field):
    if field not in _CACHE: _CACHE[field]=tag_stats(field)
    return _CACHE[field]

def top3_high(field):
    rows=sorted(stats_of(field), key=lambda r:r['ctr'], reverse=True)
    return rows[:3]

def top3_low(field):
    high={r['tag'] for r in top3_high(field)}
    # 显式排除已进入高CTR板块的枚举值，保证两个板块绝不重叠
    rows=[r for r in sorted(stats_of(field), key=lambda r:r['ctr']) if r['tag'] not in high]
    return rows[:3]

def top3_rising(field):
    rows=[r for r in stats_of(field) if r['slope'] is not None and r['slope']>0]
    rows.sort(key=lambda r:r['slope'], reverse=True)
    return rows[:3]

KINDS={'high':('ctr 高','ctr'),'low':('ctr 低','ctr'),'rising':('ctr 上升趋势','slope')}

# 已成功抽帧的素材（只有这些能给出真实画面证据，不做任何示意图/占位图）
FRAME_IDS={p.name for p in FRAMES.iterdir() if p.is_dir() and any(p.glob('*.jpg'))} if FRAMES.exists() else set()

def rep_material(field, tag, kind):
    """为某枚举值挑一条"有真实关键帧"的代表素材，作为可核对证据。"""
    xs=[x for x in POOL if x['tags'].get(field)==tag and x['id'] in FRAME_IDS]
    if not xs: return None
    if kind=='rising': xs.sort(key=lambda x: n(x['slope']), reverse=True)
    elif kind=='low':  xs.sort(key=lambda x: n(x['ctr']))
    else:              xs.sort(key=lambda x: n(x['ctr']), reverse=True)
    return xs[0]

def _thumb(x):
    if not x:
        return '<span class="noshot">该枚举值样本未抽帧<br>暂无画面证据</span>'
    d=FRAMES/x['id']; idx=None
    for i in (3,1,2,4,5,6):
        if (d/f'{i}.jpg').exists(): idx=i; break
    if idx is None:
        return '<span class="noshot">暂无画面证据</span>'
    pn=x['tags'].get('pn') or x.get('pname') or ''
    return (f'<a class="shot" href="{esc(x["url"])}" target="_blank" '
            f'title="点击打开原视频核对：{esc(pn)}（CTR {n(x["ctr"]):.2f}%）">'
            f'<img src="assets/frames0820/{x["id"]}/{idx}.jpg" loading="lazy" onerror="this.remove()">'
            f'<span class="cap">{esc(pn)[:12]}<br>CTR {n(x["ctr"]):.2f}%</span></a>')

def _kind_cell(field, kind):
    pick={'high':top3_high,'low':top3_low,'rising':top3_rising}[kind]
    rows=pick(field)
    # 过滤掉没有真实画面证据的枚举值（如"其他"/"未识别"等占位值），不显示
    rows=[r for r in rows if rep_material(field,r['tag'],kind) is not None]
    if not rows: return '<span class="na">有效枚举值不足</span>'
    out=[]
    for i,r in enumerate(rows,1):
        metric=(f'CTR趋势 +{r["slope"]:.2f}pp · 现CTR {r["ctr"]:.2f}%' if kind=='rising'
                else f'CTR {r["ctr"]:.2f}%')
        out.append(f'<div class="item"><div class="txt"><b>TOP{i}</b>'
                   f'<span class="tg">{esc(r["tag"])}</span>'
                   f'<i>{metric}</i></div>{_thumb(rep_material(field,r["tag"],kind))}</div>')
    return ''.join(out)

def combo_table():
    """三类合并为一张表：一级分类 | 二级标签 | ctr高 | ctr低 | ctr上升趋势。"""
    order=[]
    for field,name,section in DIMENSIONS:
        if not order or order[-1][0]!=section: order.append((section,[]))
        order[-1][1].append((field,name))
    rows=[]
    for section,dims in order:
        for i,(field,name) in enumerate(dims):
            tds=''
            if i==0: tds+=f'<td class="sect" rowspan="{len(dims)}">{esc(section)}</td>'
            tds+=f'<td class="dim">{esc(name)}</td>'
            for kind in ('high','low','rising'):
                tds+=f'<td class="kcell {kind}">{_kind_cell(field,kind)}</td>'
            tds+=f'<td class="act"><button class="detail" data-dim="{field}" data-kind="all">查看完整表现</button></td>'
            rows.append(f'<tr>{tds}</tr>')
    return ('<div class="scroll"><table class="combo"><thead><tr>'
            '<th>一级分类</th><th>排序 / 维度</th><th class="h">ctr 高</th>'
            '<th class="l">ctr 低</th><th class="r">ctr 上升趋势</th><th>明细</th>'
            f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')

def all_dim_data():
    """每个二级标签在统一样本池上的完整枚举值排名，供弹窗展示。"""
    o={}
    for field,name,sec in DIMENSIONS:
        rows=[]
        for r in sorted(stats_of(field), key=lambda r:r['ctr'], reverse=True):
            rows.append({'tag':r['tag'],'count':r['count'],
                         'ctr':round(r['ctr'],2),'v3':round(r['v3'],2),
                         'dur':round(r['dur'],2),'cvr':round(r['cvr'],2),
                         'spend':round(r['spend'],2),
                         'slope':(round(r['slope'],2) if r['slope'] is not None else None)})
        o[field]={'name':name,'rows':rows}
    return o

def sample_table():
    rows=[]
    fields=[('season','适用季节/节点'),('function','功能属性'),('material','材质属性'),('struct','制作类型'),('test','功能实测'),('pain','场景痛点'),('trust','信任背书类型'),('price','价格/促销表达'),('compete','竞品对比'),('emotion','情绪钩子类型'),('scene_use','题材/使用场景'),('festival','节日/节点营销'),('style','穿搭风格类型'),('shoot','拍摄场景类型'),('role','出镜角色类型')]
    for i,x in enumerate(demo,1):
        t=x['tags']; frame=f'assets/frames0820/{x["id"]}/1.jpg'
        imgs=''.join(f'<img src="assets/frames0820/{x["id"]}/{j}.jpg" onerror="this.remove()">' for j in (1,3,6))
        cells=''.join(f'<td>{esc(t.get(k))}</td>' for k,_ in fields)
        rows.append(f'<tr><td>{i}</td><td class="product">{esc(t.get("pn",x["pname"]))}</td>{cells}<td class="shot">{imgs}</td><td><a href="{esc(x["url"])}" target="_blank">视频</a></td></tr>')
    heads=''.join(f'<th>{name}</th>' for _,name in fields)
    return f'<div class="scroll"><table class="sample"><thead><tr><th>#</th><th>产品名称</th>{heads}<th>前15秒关键帧<br>0s / 6s / 15s</th><th>素材url</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>'

PAIN_COPY = {
    '户外暴晒晒黑焦虑': '分节晒黑痛点场景',
    '大肚腩/胖大腿': '产后小肚腩/大腿赘肉痛点',
    '胖姐妹/身材焦虑': '大杯/微胖身材焦虑钩子',
    '显瘦/显肉': '上身显胖/遮胯显肉痛点',
    '粗手臂/遮副乳': '粗手臂/副乳外露痛点',
    '粗手臂/穿搭尴尬痛点': '粗手臂叠穿显臃肿痛点',
    '大肚腩/勒腰': '久坐大肚腩/腰头勒肉痛点',
    '勒腰/不透气': '夏季勒腰闷热痛点',
    '不透气': '夏季闷热出汗痛点',
    '磨脚': '久走磨脚痛点',
    '容量不足': '通勤随身物装不下痛点',
    '显脸大/穿搭尴尬痛点': '发型单调/显脸大痛点',
    '家人平安/健康祈愿': '送礼寓意/祝福需求钩子',
}
TEST_COPY = {
    'UPF数值贴纸/紫外线灯测试': 'UPF防晒物理实测演示',
    '弹力拉伸实测': '高弹回弹实测演示',
    '尺码贴合实测': '贴合包裹上身实测演示',
    '材质透光影展示': '面料透光垂感实拍展示',
    '承重拉扯实测': '容量分层承重实拍展示',
    '防水防泼实测': '防泼水耐脏实测演示',
    '反复水洗/耐用实测': '可反复水洗耐用实测',
    '透气透汗实测': '冰丝透气排汗实测演示',
    '防滑底实测': '上脚防滑厚底实拍展示',
}
SCENE_COPY = {
    '骑行/运动户外': '开车骑行多场景防晒',
    '运动户外': '通勤走路轻运动多场景',
    '日常通勤穿搭': '上班通勤/接送孩子多场景',
    '居家生活': '居家久坐/睡眠多场景',
    '学习/求学场景': '开学上学/课本收纳场景',
    '礼赠/婚庆': '七夕/纪念日送礼场景',
    '旅行出行': '海边度假/旅行拍照场景',
    '工厂溯源': '工厂现货/源头直发场景',
}

def formula_tags(t):
    """黄金公式：最多3个创意标签，标签可来自15个二级标签中的任意维度。
    优先取人工逐帧复核（基于真实前15秒画面/字幕）写下的公式，避免模板套死与画面不符。"""
    if t.get('formula_override'):
        return [p for p in t['formula_override'] if p][:3]
    # 人工复核公式（真实画面依据），按 ' + ' 拆分，最多3个
    if t.get('formula'):
        parts=[p.strip() for p in str(t['formula']).replace('＋','+').split('+') if p.strip()]
        if parts:
            return parts[:3]
    # 仅当完全没有人工公式时才走保守兜底：只用该素材已有的真实标签，不臆造场景
    fallback_tags=[]
    for key in ('emotion','pain','test','function','struct','trust','price','compete',
                'material','style','scene_use','shoot','role'):
        v=t.get(key)
        if v and v not in ('—','','其他','无背书','无对比','无明确钩子','无节日营销',
                           '无明显价格促销','无实测（口播为主）','未识别（信息不足）'):
            fallback_tags.append(str(v))
        if len(fallback_tags)>=3: break
    return fallback_tags[:3] if fallback_tags else ['前15秒画面信息不足，未生成公式']

def audience_copy(t):
    """目标人群必须同时包含：性别/年龄 + 真实生活场景 + 具体需求。"""
    if t.get('audience_override'):
        return t['audience_override']
    cat=t.get('cat',''); pain=t.get('pain',''); use=t.get('scene_use','')
    if '防晒衣' in cat:
        return '夏季户外通勤女性 / 开车骑行族 / 30-50岁怕晒、想要轻薄防晒的女性'
    if '冲锋衣' in cat:
        return '周末轻户外/自驾女性 / 25-45岁 / 需要防风保暖、拍照不臃肿的人群'
    if 'POLO' in cat:
        return '夏季商务通勤/周末聚会男性 / 35-55岁 / 怕闷热、希望穿得得体不显老'
    if '西裤' in cat:
        return '春秋商务通勤男性 / 35-60岁 / 久坐怕勒腰、想显腿直且易打理的人群'
    if '长袖T恤' in cat:
        return '换季日常通勤男性 / 40-65岁 / 想显精神、需要多色基础打底的人群'
    if '男士内裤' in cat:
        return '久坐通勤/夏季易出汗男性 / 30-50岁 / 大肚腩、怕勒腰闷热的人群'
    if '文胸' in cat or '内衣' in cat:
        detail = '产后/久坐有小肚腩' if ('大肚腩' in pain or '塑身' in cat) else '大杯/微胖身材'
        return f'居家与通勤女性 / 28-50岁 / {detail}、在意勒肉/外扩/闷热问题的人群'
    if '睡衣' in cat or '睡裙' in cat:
        return '夏季居家女性 / 20-40岁 / 睡觉怕闷热、想要宽松舒适和自带胸垫的人群'
    if 'T恤' in cat or '上衣' in cat or '连衣裙' in cat or '背心' in cat:
        detail = '微胖/小肚腩、需要遮胯显瘦' if ('显瘦' in pain or '显肉' in pain or '粗手臂' in pain) else '需要快速完成日常穿搭'
        return f'上班通勤/接送孩子女性 / 25-50岁 / {detail}的人群'
    if '女包' in cat:
        return '上班通勤/接送孩子女性 / 28-50岁 / 手机、充电宝、钥匙等随身物较多的人群'
    if '双肩包' in cat:
        return '开学通勤学生与家长 / 18-45岁 / 需要分层收纳、久背减负的人群'
    if '运动鞋' in cat:
        return '日常走路/轻运动女性 / 20-35岁 / 想增高、怕磨脚且需要百搭的人群'
    if '发绳' in cat or '耳环' in cat:
        return '上班约会女性 / 18-35岁 / 想快速整理发型或修饰脸型、提升精致感的人群'
    if '珠宝' in cat:
        return '七夕/纪念日送礼男性及自购女性 / 25-45岁 / 看重寓意、包装和仪式感的人群'
    return f'{use}人群 / 25-45岁 / 有「{pain if pain not in {"其他","—"} else t.get("function","核心功能")}」明确需求的人群'

def frame_case(t, fr):
    phases=[('开头 0-3s', t.get('open','—'), t.get('open_frame', 1)), ('中间 3-9s', t.get('mid','—'), t.get('mid_frame', 3)), ('结尾 9-15s', t.get('end','—'), t.get('end_frame', 6))]
    return ''.join(f'<div class="phase"><b>{esc(title)}</b><p>{esc(desc)}</p><img src="{fr}/{idx}.jpg" onerror="this.remove()"></div>' for title,desc,idx in phases)

def golden_table():
    rows=[]
    for i,x in enumerate(golden,1):
        t=x['tags']; fr=f'assets/frames0820/{x["id"]}'
        labels=formula_tags(t)
        formula=''.join(f'<span class="formula-tag t{k+1}">{esc(label)}</span>' + ('<b class="formula-plus">+</b>' if k < len(labels)-1 else '') for k,label in enumerate(labels))
        rows.append(f'<tr><td class="rank">{i}</td><td class="goldf">{formula}</td><td class="cases">{frame_case(t,fr)}</td><td class="audience">{esc(audience_copy(t))}</td><td>{esc(t.get("cat","—"))}</td><td><a href="{esc(x["url"])}" target="_blank">视频</a></td></tr>')
    return f'<div class="scroll"><table class="golden"><thead><tr><th>排名</th><th>黄金公式<br><small>严格只有3个创意标签</small></th><th>案例：前15秒关键帧与内容说明</th><th>目标人群</th><th>适合品类</th><th>素材url</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>'

SECTORS = [
    ('大盘创意数据', '服饰行业整体创意数据看板（内网 BI，需登录访问）', '📊', 'bi',
     'https://adata.woa.com/bi/artifact/a853f982-58e8-4c76-9039-46aa8aa619da/%E6%9C%8D%E9%A5%B0%E5%88%9B%E6%84%8F%E6%95%B0%E6%8D%AE%E7%9C%8B%E6%9D%BF_v3.html'),
    ('箱包鞋靴', '箱包 / 鞋靴分 Tab 创意分析，含 Top 素材关键帧与 Learning', '👜', '',
     'https://chenxiaomei19960125-glitch.github.io/bag-shoes-creative-report/'),
    ('配饰', '墨镜 / 太阳镜等配饰品类创意分析看板', '🕶️', '',
     'https://lihaiyou80-ux.github.io/jewelry-creative-report/cat_%E5%A2%A8%E9%95%9C-%E5%A4%AA%E9%98%B3%E9%95%9C.html'),
    ('内衣', '文胸品类创意分析看板 v4', '👙', '',
     'https://johnsywang.github.io/johnsywang/wenxiong-creative-v4/'),
    ('男装', '男装品类创意视频分析看板', '👔', '',
     'https://menclothingvideo.netlify.app/'),
]

def sector_cards():
    cards=[]
    for name,desc,icon,flag,url in SECTORS:
        badge='<span class="badge">内网</span>' if flag=='bi' else ''
        cards.append(f'<a class="scard {flag}" href="{esc(url)}" target="_blank" rel="noopener">'
                     f'<div class="sicon">{icon}</div>'
                     f'<div class="sbody"><b>{esc(name)}{badge}</b><p>{esc(desc)}</p></div>'
                     f'<div class="sgo">进入看板 →</div></a>')
    return f'<div class="sgrid">{"".join(cards)}</div>'

stat=raw['stat']
STYLE='''<style>
:root{--blue:#1668dc;--ink:#172b4d;--muted:#65758c;--line:#d9e5f3;--bg:#f4f7fb;--soft:#f5f9ff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",Arial,sans-serif}.wrap{max-width:1540px;margin:auto;padding:26px 28px 60px}.hero{padding:32px 36px;color:#fff;border-radius:22px;background:linear-gradient(135deg,#003c9c,#0052d9 58%,#1797f5)}.hero h1{margin:8px 0;font-size:30px}.hero p{margin:0;line-height:1.7;color:#e8f2ff}.tabs{display:flex;gap:9px;margin:20px 0}.tab{border:1px solid var(--line);background:#fff;color:#51647f;border-radius:11px;padding:13px 18px;font-size:14px;font-weight:700;cursor:pointer}.tab.active{background:var(--blue);color:#fff;border-color:var(--blue)}.view{display:none}.view.active{display:block}.section{margin-top:16px;padding:22px;background:#fff;border:1px solid var(--line);border-radius:17px;box-shadow:0 4px 16px rgba(0,82,217,.04)}h2{margin:0 0 9px;font-size:20px}p{line-height:1.7}.hint,.rule{padding:13px 16px;border-left:4px solid var(--blue);background:#eef5ff;color:#48617e;font-size:13px;line-height:1.75;border-radius:7px}.tree{display:grid;grid-template-columns:210px minmax(0,1fr);border:1px solid var(--line);border-radius:13px;overflow:hidden;margin-top:13px}.tree-main{padding:17px;background:#edf4ff}.tree-main.core{background:linear-gradient(160deg,#0045bd,#006fe6);color:#fff}.tree-main b{display:block;font-size:17px}.tree-main span{display:block;margin-top:6px;font-size:12px;line-height:1.65}.scroll{overflow:auto}.tree table,.sample,.golden,.perf{border-collapse:collapse;width:100%;min-width:1050px;font-size:12px}.tree th,.sample th,.golden th,.perf th{background:#edf4ff;color:#164c9c;text-align:left;padding:9px;border:1px solid #d9e5f3;white-space:nowrap}.tree td,.sample td,.golden td,.perf td{padding:9px;border:1px solid #e2ebf5;vertical-align:top;line-height:1.6;color:#40546f}.tree .sub{font-weight:700;color:#0052d9;white-space:nowrap}.tree i{font-style:normal;font-weight:700;color:#0052d9;background:#e8f1ff;padding:2px 5px;border-radius:4px}.sample{min-width:2600px}.sample .product{min-width:190px;font-weight:700;color:#0052d9}.sample td{max-width:145px}.sample .shot,.frames{min-width:300px}.sample img,.frames img{width:90px;height:140px;object-fit:cover;border-radius:5px;margin-right:4px;background:#eef2f7}.golden{min-width:1450px}.golden th{background:#1463df;color:#fff;text-align:center}.golden th small{font-weight:500;color:#dbeaff}.golden td{font-size:13px}.golden .rank{font-weight:800;text-align:center;color:#0052d9;font-size:16px}.goldf{min-width:270px;font-weight:700;vertical-align:middle!important}.formula-tag{display:inline-block;padding:8px 9px;margin:5px 2px;border-radius:7px;line-height:1.45}.formula-plus{display:inline-block;padding:0 3px;color:#0052d9;font-size:17px;vertical-align:middle}.formula-tag.t1{background:#e3f5ec;color:#137c4d}.formula-tag.t2{background:#e8f1ff;color:#0052d9}.formula-tag.t3{background:#fff3d7;color:#a55d00}.cases{min-width:560px;padding:0!important}.phase{display:inline-block;width:33.333%;min-height:250px;vertical-align:top;padding:9px;border-right:1px solid #dfe8f5;background:#fff}.phase:last-child{border-right:0}.phase b{display:block;color:#1c477f;font-size:12px}.phase p{height:52px;margin:5px 0 8px;color:#566a85;font-size:11px;line-height:1.45;overflow:hidden}.phase img{display:block;width:100%;height:170px;object-fit:cover;border-radius:4px;background:#edf2f7}.golden .audience{min-width:175px;font-weight:700;color:#334f72}.dash{display:grid;grid-template-columns:repeat(3,1fr);gap:13px}.panel{border:1px solid var(--line);border-radius:14px;overflow:hidden}.panel h3{margin:0;padding:14px 15px;background:#f0f6ff;color:#0045bd;font-size:15px}.panel .mini{padding:12px;color:#64738a;font-size:12px}.perf{min-width:980px;font-size:13px}.dash.single{grid-template-columns:1fr}.dash.single .perf{min-width:100%}.dash.single .perf th:first-child,.dash.single .perf td:first-child{width:150px;font-weight:700;color:#0045bd}.dash.single .perf th:last-child,.dash.single .perf td:last-child{width:120px;text-align:center}.dash.single .perf td{padding:11px 12px;white-space:normal}.dash.single .perf td b{color:#0052d9}.panel.high h3{background:#e8f7ee;color:#0b7a41}.panel.low h3{background:#fdeceb;color:#b42318}.panel.rise h3{background:#fff4e0;color:#a55d00}.rank .dim{font-weight:700;color:#0045bd;white-space:nowrap}.rank td{vertical-align:top}.tagv{display:block;font-size:13px;line-height:1.5;color:#17233d}.mv{display:block;margin-top:4px;font-size:12px;font-weight:700;color:#0052d9}.mv.up{color:#0b7a41}.mn{display:block;margin-top:2px;font-size:11px;color:#8a95a8;font-weight:400}.panel.high .tagv{color:#0b7a41}.panel.low .tagv{color:#b42318}.panel.rise .tagv{color:#a55d00}.panel.low .mv{color:#b42318}.na{color:#aab;font-size:12px}
.mini .ch{color:#0b7a41}.mini .cl{color:#b42318}.mini .cr{color:#a55d00}
.combo{border-collapse:collapse;width:100%;min-width:1180px;font-size:12px}
.combo th{background:#edf4ff;color:#164c9c;text-align:left;padding:10px 9px;border:1px solid #d9e5f3;white-space:nowrap}
.combo th.h{background:#e8f7ee;color:#0b7a41}.combo th.l{background:#fdeceb;color:#b42318}.combo th.r{background:#fff4e0;color:#a55d00}
.combo td{padding:8px 9px;border:1px solid #e2ebf5;vertical-align:top}
.combo .sect{background:#f4f8ff;color:#0045bd;font-weight:800;font-size:13px;width:86px;vertical-align:middle;text-align:center}
.combo .dim{font-weight:700;color:#17233d;width:104px;background:#fafcff}
.combo .kcell{width:auto;min-width:250px}
.combo .act{width:96px;text-align:center;vertical-align:middle}
.combo .item{display:flex;gap:8px;align-items:flex-start;padding:6px 0;border-bottom:1px dashed #e6edf6}
.combo .item:last-child{border-bottom:0}
.combo .item .txt{flex:1;min-width:0}
.combo .item .txt b{display:inline-block;background:#eef4ff;color:#0052d9;border-radius:4px;padding:1px 5px;font-size:10px;margin-right:4px}
.combo .item .tg{font-weight:700;font-size:12.5px;line-height:1.45;color:#17233d}
.combo .item .txt i{display:block;margin-top:3px;font-style:normal;font-size:11px;font-weight:700;color:#0052d9}
.combo .high .tg{color:#0b7a41}.combo .low .tg{color:#b42318}.combo .rising .tg{color:#a55d00}
.combo .high .txt i{color:#0b7a41}.combo .low .txt i{color:#b42318}.combo .rising .txt i{color:#a55d00}
.shot{flex:none;width:56px;text-decoration:none;display:block}
.shot img{display:block;width:56px;height:84px;object-fit:cover;border-radius:5px;background:#eef2f7;border:1px solid #dde6f2}
.shot .cap{display:block;margin-top:3px;font-size:9px;line-height:1.3;color:#7d8ba0;text-align:center}
.shot:hover img{border-color:#0052d9;box-shadow:0 2px 8px rgba(0,82,217,.25)}
.noshot{flex:none;width:56px;font-size:9px;line-height:1.3;color:#b3bccb;text-align:center;border:1px dashed #dde6f2;border-radius:5px;padding:6px 2px}
.sgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:14px;margin-top:14px}
.scard{display:flex;align-items:center;gap:14px;padding:18px;border:1px solid var(--line);border-radius:14px;background:#fff;text-decoration:none;color:inherit;transition:.18s}
.scard:hover{border-color:#0052d9;box-shadow:0 8px 22px rgba(0,82,217,.14);transform:translateY(-2px)}
.scard.bi{background:linear-gradient(135deg,#f2f7ff,#fff);border-color:#b9d4ff}
.sicon{flex:none;width:52px;height:52px;border-radius:13px;background:#eef4ff;display:grid;place-items:center;font-size:26px}
.sbody{flex:1;min-width:0}
.sbody b{display:block;font-size:16px;color:#17233d}
.sbody p{margin:4px 0 6px;font-size:12px;color:#65758c;line-height:1.55}
.surl{display:block;font-size:10px;color:#9aa7ba;word-break:break-all;line-height:1.4}
.badge{display:inline-block;margin-left:7px;padding:1px 7px;border-radius:9px;background:#fff3d7;color:#a55d00;font-size:10px;vertical-align:middle}
.sgo{flex:none;color:#0052d9;font-size:12px;font-weight:700;white-space:nowrap}.section-row td{background:#f4f8ff!important;color:#0045bd!important;font-weight:700!important}.detail{color:#0052d9;background:#fff;border:1px solid #b9d4ff;border-radius:6px;padding:4px 8px;font-size:11px;cursor:pointer}.modal{display:none;position:fixed;inset:0;background:rgba(12,28,55,.45);z-index:10;padding:8vh 8vw}.modal.open{display:block}.dialog{max-height:84vh;overflow:auto;background:#fff;border-radius:16px;padding:20px}.close{float:right;border:0;background:#eaf2ff;color:#0052d9;padding:6px 10px;border-radius:6px;cursor:pointer}.legend{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.legend span{padding:5px 9px;background:#f0f6ff;color:#0052d9;border-radius:999px;font-size:12px}.footer{text-align:center;color:#8190a8;font-size:12px;margin-top:28px}@media(max-width:900px){.wrap{padding:16px}.tabs{overflow:auto}.tree{grid-template-columns:1fr}.dash{grid-template-columns:1fr}.hero{padding:24px}.hero h1{font-size:25px}}
</style>'''
DIMJSON=json.dumps(all_dim_data(),ensure_ascii=False)
PAGE=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>服饰素材创意打标分析 · 8.20</title>{STYLE}</head><body><main class="wrap"><header class="hero"><div>服饰创意洞察 · 素材8.20</div><h1>服饰素材创意打标分析</h1><p>标签树、行业素材打标实操、创意元素表现与素材起量黄金公式。所有单条素材仅按前15秒画面和可见字幕打标。</p></header><nav class="tabs"><button class="tab active" data-v="tree">1. 服饰素材标签树结构</button><button class="tab" data-v="demo">2. 行业素材打标实操</button><button class="tab" data-v="performance">3. 创意元素表现</button><button class="tab" data-v="golden">4. 素材起量黄金公式</button><button class="tab" data-v="sector">5. 服饰分行业看板汇总</button></nav><div id="tree" class="view active"><section class="section"><h2>服饰素材标签树结构</h2><div class="hint">中心层面先搭建服饰通用 5×15 标签框架，统一维度与评判口径；各赛道复用基础框架，补充赛道专属枚举值（鞋靴专属材质、内衣专属卖点等），实现分赛道差异化落地。</div>{tree_html()}</section></div><div id="demo" class="view"><section class="section"><h2>行业素材打标实操</h2>{sample_table()}</section></div><div id="performance" class="view"><section class="section"><h2>创意元素表现</h2><div class="rule">仅识别前15秒画面，若需更精准结论建议扩充人工复核量。</div><div class="dash single"><article class="panel"><h3>创意标签 CTR 三类表现（合并视图）</h3><div class="mini">同一张表对比：<b class="ch">ctr 高</b> / <b class="cl">ctr 低</b> / <b class="cr">ctr 上升趋势</b>。每个枚举值右侧的截图为该枚举值下真实素材的前15秒关键帧，<b>点击截图可直接打开原视频核对</b>；未抽帧的枚举值如实标注「暂无画面证据」，不放示意图。</div>{combo_table()}</article></div></section></div><div id="golden" class="view"><section class="section"><h2>素材起量黄金公式</h2><p>1、素材前 15 秒，是用户决策的黄金窗口，同时也是批量素材分析性价比最高的单元，完全可以支撑跑量归因和标签提炼。<br>2、每条公式<b>最多 3 个创意标签</b>，标签可来自 <b>15 个二级标签中的任意维度</b>，<b>按该素材前15秒真实画面与字幕判断</b>，并与右侧开头/中间/结尾关键帧一一对应。目标人群明确到年龄、性别、场景和诉求。</p>{golden_table()}</section></div><div id="sector" class="view"><section class="section"><h2>服饰分行业看板汇总</h2><div class="hint">各行业创意看板入口，点击卡片在新标签页打开对应看板原始链接。<b>大盘创意数据</b>为公司内网 BI 看板，需在内网/已登录环境下访问。</div>{sector_cards()}</section></div><footer class="footer">素材8.20 · 前15秒创意分析 · 数据来源：用户提供表格</footer></main><div id="modal" class="modal"><div class="dialog"><button id="close" class="close">关闭</button><h2 id="mtitle">标签明细</h2><div id="mbody"></div></div></div><script>const DATA={DIMJSON};const kinds={{high:'ctr 高',low:'ctr 低',rising:'ctr 上升趋势',all:'全部枚举值'}};document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{{document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x===b));document.querySelectorAll('.view').forEach(x=>x.classList.toggle('active',x.id===b.dataset.v))}});document.querySelectorAll('.detail').forEach(b=>b.onclick=()=>{{let d=DATA[b.dataset.dim]||{{name:'',rows:[]}};document.getElementById('mtitle').textContent=kinds[b.dataset.kind]+' · '+d.name+' · 全部枚举值表现（按CTR降序）';document.getElementById('mbody').innerHTML='<div class="scroll"><table class="perf"><thead><tr><th>枚举值</th><th>CTR</th><th>CTR趋势</th><th>平均播放时长</th><th>3秒完播率</th><th>CVR</th></tr></thead><tbody>'+d.rows.map(r=>`<tr><td>${{r.tag}}</td><td><b>${{r.ctr}}%</b></td><td>${{r.slope===null?'—':(r.slope>0?'+':'')+r.slope+'pp'}}</td><td>${{r.dur}}s</td><td>${{r.v3}}%</td><td>${{r.cvr}}%</td></tr>`).join('')+'</tbody></table></div>';document.getElementById('modal').classList.add('open')}});document.getElementById('close').onclick=()=>document.getElementById('modal').classList.remove('open');</script></body></html>'''
DOCS.mkdir(exist_ok=True)
(DOCS/'index.html').write_text(PAGE,encoding='utf-8')
# 静态 frames 同步到 GitHub Pages 发布目录
out_frames=DOCS/'assets'/'frames0820'
if FRAMES.exists():
    out_frames.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(FRAMES,out_frames,dirs_exist_ok=True)
print('built', DOCS/'index.html', '| demo',len(demo),'golden',len(golden),'rising',len(rising))
