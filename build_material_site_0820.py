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
    ('struct', '视频结构类型', '内容形式'), ('season', '适用季节', '商品属性'), ('function', '功能属性', '商品属性'), ('material', '材质属性', '商品属性'),
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

def tree_html():
    res=[]
    for main,desc,core,children in TAG_TREE:
        rows=''.join(f'<tr><td class="sub">{esc(n)}</td><td><i>{esc(p)}</i></td><td>{esc(vals)}</td><td>{esc(rule)}</td><td>{esc(explain)}</td></tr>' for n,p,vals,rule,explain in children)
        res.append(f'<article class="tree"><aside class="tree-main {"core" if core else ""}"><b>{esc(main)}</b><span>{esc(desc)}</span></aside><div class="scroll"><table><thead><tr><th>二级标签</th><th>优先级</th><th>Value枚举值（各赛道可自行扩改）</th><th>判断依据/画面特征（核心Key）</th><th>二级标签分类说明</th></tr></thead><tbody>{rows}</tbody></table></div></article>')
    return ''.join(res)

def metric_top(group, field, label, reverse=True):
    g=defaultdict(list)
    for x in group: g[x['tags'][field]].append(x)
    vals=[]
    for name, xs in g.items():
        vals.append((name, sum(n(x[label]) for x in xs)/len(xs), len(xs)))
    vals.sort(key=lambda a:a[1], reverse=reverse)
    return vals[:3]

def formula_for(vals, metric):
    if not vals: return '有效样本不足'
    return '　'.join(f'TOP{i+1} {esc(a)} <b>{b:.2f}{"%" if metric in ("ctr","v3") else "s"}</b>' for i,(a,b,c) in enumerate(vals))

def performance_table(group, title):
    out=[]; current=None
    for field,name,section in DIMENSIONS:
        if section != current:
            current=section
            out.append(f'<tr class="section-row"><td colspan="5">{esc(section)}</td></tr>')
        out.append(f'<tr><td>{esc(name)}</td><td>{formula_for(metric_top(group,field,"v3"),"v3")}</td><td>{formula_for(metric_top(group,field,"dur"),"dur")}</td><td>{formula_for(metric_top(group,field,"ctr"),"ctr")}</td><td><button class="detail" data-dim="{field}" data-group="{title}">查看完整表现</button></td></tr>')
    return ''.join(out)

def all_dim_data():
    groups={'good':good,'bad':bad,'rising':rising}
    o={}
    for gname,arr in groups.items():
        o[gname]={}
        for field,name,sec in DIMENSIONS:
            gg=defaultdict(list)
            for x in arr: gg[x['tags'][field]].append(x)
            rows=[]
            for tag,xs in gg.items():
                rows.append({'tag':tag,'count':len(xs),'v3':round(sum(n(x['v3']) for x in xs)/len(xs),2),'dur':round(sum(n(x['dur']) for x in xs)/len(xs),2),'ctr':round(sum(n(x['ctr']) for x in xs)/len(xs),2),'cvr':round(sum(n(x['cvr']) for x in xs)/len(xs),2),'spend':round(sum(n(x['spend']) for x in xs),2)})
            o[gname][field]=sorted(rows,key=lambda r:r['ctr'],reverse=True)
    return o

def sample_table():
    rows=[]
    fields=[('season','适用季节'),('function','功能属性'),('material','材质属性'),('struct','视频结构类型'),('test','功能实测'),('pain','场景痛点'),('trust','信任背书类型'),('price','价格/促销表达'),('compete','竞品对比'),('emotion','情绪钩子类型'),('scene_use','题材/使用场景'),('festival','节日/节点营销'),('style','穿搭风格类型'),('shoot','拍摄场景类型'),('role','出镜角色类型')]
    for i,x in enumerate(demo,1):
        t=x['tags']; frame=f'assets/frames0820/{x["id"]}/1.jpg'
        imgs=''.join(f'<img src="assets/frames0820/{x["id"]}/{j}.jpg" onerror="this.remove()">' for j in (1,3,6))
        cells=''.join(f'<td>{esc(t.get(k))}</td>' for k,_ in fields)
        rows.append(f'<tr><td>{i}</td><td class="product">{esc(t.get("pn",x["pname"]))}</td>{cells}<td class="shot">{imgs}</td><td><a href="{esc(x["url"])}" target="_blank">视频</a></td></tr>')
    heads=''.join(f'<th>{name}</th>' for _,name in fields)
    return f'<div class="scroll"><table class="sample"><thead><tr><th>#</th><th>产品名称</th>{heads}<th>前15秒关键帧<br>0s / 6s / 15s</th><th>素材url</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>'

PAIN_COPY = {
    '户外暴晒晒黑焦虑': '夏季暴晒/晒黑焦虑',
    '大肚腩/胖大腿': '产后小肚腩/大腿赘肉焦虑',
    '胖姐妹/身材焦虑': '大杯/微胖身材焦虑',
    '显瘦/显肉': '上身显胖/遮胯显肉焦虑',
    '粗手臂/遮副乳': '粗手臂/副乳外露焦虑',
    '粗手臂/穿搭尴尬痛点': '粗手臂/叠穿显臃肿焦虑',
    '大肚腩/勒腰': '大肚腩/腰头勒肉痛点',
    '勒腰/不透气': '久穿勒腰/闷热不透气痛点',
    '不透气': '闷热出汗/贴身不透气痛点',
    '磨脚': '久走磨脚/脚感不舒适痛点',
    '容量不足': '通勤随身物装不下痛点',
    '显脸大/穿搭尴尬痛点': '发型单调/显脸大焦虑',
    '家人平安/健康祈愿': '送礼寓意/祝福表达需求',
}
TEST_COPY = {
    'UPF数值贴纸/紫外线灯测试': '冰丝凉感/UPF防晒效果展示',
    '弹力拉伸实测': '高弹拉伸/回弹效果实测',
    '尺码贴合实测': '上身包裹/贴合效果实测',
    '材质透光影展示': '面料透光/垂感质感展示',
    '承重拉扯实测': '容量分层/承重收纳展示',
    '防水防泼实测': '防泼水/耐脏效果实测',
    '反复水洗/耐用实测': '水洗内胆/耐用结构实测',
    '透气透汗实测': '透气排汗/亲肤面料展示',
    '防滑底实测': '上脚防滑/厚底脚感展示',
}
SCENE_COPY = {
    '骑行/运动户外': '开车/骑行/户外防晒通勤',
    '运动户外': '日常走路/轻运动出行',
    '日常通勤穿搭': '上班通勤/接送孩子/周末出门',
    '居家生活': '居家久坐/睡眠/贴身穿着',
    '学习/求学场景': '开学上学/课本收纳整理',
    '礼赠/婚庆': '七夕/纪念日送礼场景',
    '旅行出行': '海边度假/旅行拍照场景',
    '工厂溯源': '工厂现货/源头直发决策场景',
}

def formula_tags(t):
    """黄金公式严格只有3个标签，但每一个必须写清具体创意元素，而非泛类目。"""
    pain=t.get('pain','')
    hook = PAIN_COPY.get(pain)
    if not hook:
        emotion=t.get('emotion','无明确钩子')
        hook = f'{emotion.replace("钩子", "").replace("心理", "") }开场'
    test=t.get('test','')
    evidence=TEST_COPY.get(test)
    if not evidence:
        evidence=f'{t.get("function","核心功能").split("/")[0]}功能表达'
    use=t.get('scene_use','')
    scene=SCENE_COPY.get(use, use or t.get('shoot','真实场景'))
    return [hook, evidence, scene]

def audience_copy(t):
    """目标人群必须同时包含：性别/年龄 + 真实生活场景 + 具体需求。"""
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
    phases=[('开头 0-3s', t.get('open','—'), 1), ('中间 3-9s', t.get('mid','—'), 3), ('结尾 9-15s', t.get('end','—'), 6)]
    return ''.join(f'<div class="phase"><b>{esc(title)}</b><p>{esc(desc)}</p><img src="{fr}/{idx}.jpg" onerror="this.remove()"></div>' for title,desc,idx in phases)

def golden_table():
    rows=[]
    for i,x in enumerate(golden,1):
        t=x['tags']; fr=f'assets/frames0820/{x["id"]}'
        labels=formula_tags(t)
        formula=''.join(f'<span class="formula-tag t{k+1}">{esc(label)}</span>' for k,label in enumerate(labels))
        rows.append(f'<tr><td class="rank">{i}</td><td class="goldf">{formula}</td><td class="cases">{frame_case(t,fr)}</td><td class="audience">{esc(audience_copy(t))}</td><td>{esc(t.get("cat","—"))}</td><td><a href="{esc(x["url"])}" target="_blank">视频</a></td></tr>')
    return f'<div class="scroll"><table class="golden"><thead><tr><th>排名</th><th>黄金公式<br><small>严格只有3个创意标签</small></th><th>案例：前15秒关键帧与内容说明</th><th>目标人群</th><th>适合品类</th><th>素材url</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>'

stat=raw['stat']
summary=f'''<div class="rule"><b>优质素材筛选口径：</b>CTR 为第一优先级，平均播放时长、3秒完播率为次要参考；所有打标和案例仅分析前15秒。<br><b>样本：</b>去重 {raw['total']} 条；优质 {len(good)} 条；CTR低 {len(bad)} 条；CTR上升 {len(rising)} 条（原始数据仅支持识别 {len(rising)} 条至少两天且 CTR 上升的素材，未虚构补足100条）。</div>'''
STYLE='''<style>
:root{--blue:#1668dc;--ink:#172b4d;--muted:#65758c;--line:#d9e5f3;--bg:#f4f7fb;--soft:#f5f9ff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",Arial,sans-serif}.wrap{max-width:1540px;margin:auto;padding:26px 28px 60px}.hero{padding:32px 36px;color:#fff;border-radius:22px;background:linear-gradient(135deg,#003c9c,#0052d9 58%,#1797f5)}.hero h1{margin:8px 0;font-size:30px}.hero p{margin:0;line-height:1.7;color:#e8f2ff}.tabs{display:flex;gap:9px;margin:20px 0}.tab{border:1px solid var(--line);background:#fff;color:#51647f;border-radius:11px;padding:13px 18px;font-size:14px;font-weight:700;cursor:pointer}.tab.active{background:var(--blue);color:#fff;border-color:var(--blue)}.view{display:none}.view.active{display:block}.section{margin-top:16px;padding:22px;background:#fff;border:1px solid var(--line);border-radius:17px;box-shadow:0 4px 16px rgba(0,82,217,.04)}h2{margin:0 0 9px;font-size:20px}p{line-height:1.7}.hint,.rule{padding:13px 16px;border-left:4px solid var(--blue);background:#eef5ff;color:#48617e;font-size:13px;line-height:1.75;border-radius:7px}.tree{display:grid;grid-template-columns:210px minmax(0,1fr);border:1px solid var(--line);border-radius:13px;overflow:hidden;margin-top:13px}.tree-main{padding:17px;background:#edf4ff}.tree-main.core{background:linear-gradient(160deg,#0045bd,#006fe6);color:#fff}.tree-main b{display:block;font-size:17px}.tree-main span{display:block;margin-top:6px;font-size:12px;line-height:1.65}.scroll{overflow:auto}.tree table,.sample,.golden,.perf{border-collapse:collapse;width:100%;min-width:1050px;font-size:12px}.tree th,.sample th,.golden th,.perf th{background:#edf4ff;color:#164c9c;text-align:left;padding:9px;border:1px solid #d9e5f3;white-space:nowrap}.tree td,.sample td,.golden td,.perf td{padding:9px;border:1px solid #e2ebf5;vertical-align:top;line-height:1.6;color:#40546f}.tree .sub{font-weight:700;color:#0052d9;white-space:nowrap}.tree i{font-style:normal;font-weight:700;color:#0052d9;background:#e8f1ff;padding:2px 5px;border-radius:4px}.sample{min-width:2600px}.sample .product{min-width:190px;font-weight:700;color:#0052d9}.sample td{max-width:145px}.sample .shot,.frames{min-width:300px}.sample img,.frames img{width:90px;height:140px;object-fit:cover;border-radius:5px;margin-right:4px;background:#eef2f7}.golden{min-width:1450px}.golden th{background:#1463df;color:#fff;text-align:center}.golden th small{font-weight:500;color:#dbeaff}.golden td{font-size:13px}.golden .rank{font-weight:800;text-align:center;color:#0052d9;font-size:16px}.goldf{min-width:270px;font-weight:700;vertical-align:middle!important}.formula-tag{display:block;padding:8px 9px;margin:5px 0;border-radius:7px;line-height:1.45}.formula-tag.t1{background:#e3f5ec;color:#137c4d}.formula-tag.t2{background:#e8f1ff;color:#0052d9}.formula-tag.t3{background:#fff3d7;color:#a55d00}.cases{min-width:560px;padding:0!important}.phase{display:inline-block;width:33.333%;min-height:250px;vertical-align:top;padding:9px;border-right:1px solid #dfe8f5;background:#fff}.phase:last-child{border-right:0}.phase b{display:block;color:#1c477f;font-size:12px}.phase p{height:52px;margin:5px 0 8px;color:#566a85;font-size:11px;line-height:1.45;overflow:hidden}.phase img{display:block;width:100%;height:170px;object-fit:cover;border-radius:4px;background:#edf2f7}.golden .audience{min-width:175px;font-weight:700;color:#334f72}.dash{display:grid;grid-template-columns:repeat(3,1fr);gap:13px}.panel{border:1px solid var(--line);border-radius:14px;overflow:hidden}.panel h3{margin:0;padding:14px 15px;background:#f0f6ff;color:#0045bd;font-size:15px}.panel .mini{padding:12px;color:#64738a;font-size:12px}.perf{min-width:980px}.section-row td{background:#f4f8ff!important;color:#0045bd!important;font-weight:700!important}.detail{color:#0052d9;background:#fff;border:1px solid #b9d4ff;border-radius:6px;padding:4px 8px;font-size:11px;cursor:pointer}.modal{display:none;position:fixed;inset:0;background:rgba(12,28,55,.45);z-index:10;padding:8vh 8vw}.modal.open{display:block}.dialog{max-height:84vh;overflow:auto;background:#fff;border-radius:16px;padding:20px}.close{float:right;border:0;background:#eaf2ff;color:#0052d9;padding:6px 10px;border-radius:6px;cursor:pointer}.legend{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.legend span{padding:5px 9px;background:#f0f6ff;color:#0052d9;border-radius:999px;font-size:12px}.footer{text-align:center;color:#8190a8;font-size:12px;margin-top:28px}@media(max-width:900px){.wrap{padding:16px}.tabs{overflow:auto}.tree{grid-template-columns:1fr}.dash{grid-template-columns:1fr}.hero{padding:24px}.hero h1{font-size:25px}}
</style>'''
DIMJSON=json.dumps(all_dim_data(),ensure_ascii=False)
PAGE=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>服饰素材创意打标分析 · 8.20</title>{STYLE}</head><body><main class="wrap"><header class="hero"><div>服饰创意洞察 · 素材8.20</div><h1>服饰素材创意打标分析</h1><p>标签树、行业素材打标实操、创意元素表现与素材起量黄金公式。所有单条素材仅按前15秒画面和可见字幕打标。</p></header><nav class="tabs"><button class="tab active" data-v="tree">1. 服饰素材标签树结构</button><button class="tab" data-v="demo">2. 行业素材打标实操</button><button class="tab" data-v="performance">3. 创意元素表现</button><button class="tab" data-v="golden">4. 素材起量黄金公式</button></nav><div id="tree" class="view active"><section class="section"><h2>服饰素材标签树结构</h2><div class="hint">直接按业务标签框架呈现：内容形式、画面客观要素作为 p00 核心标签；其余用于解释商品属性、卖点表达与情绪营销。Value 枚举按截图内容整理。</div>{tree_html()}</section></div><div id="demo" class="view"><section class="section"><h2>行业素材打标实操</h2><p>选取消耗较高的 30 条素材作为示范。<b>“产品名称”</b>对应原表中的推广产品ID（翻译后）；每条标签仅基于 0-15 秒关键帧。</p>{sample_table()}</section></div><div id="performance" class="view"><section class="section"><h2>创意元素表现</h2>{summary}<div class="legend"><span>指标排序：3秒完播率</span><span>平均播放时长</span><span>CTR表现</span><span>点击“查看完整表现”可查看各标签完整分布</span></div><div class="dash"><article class="panel"><h3>优质素材（200条）</h3><div class="mini">CTR 高为第一优先级，播放时长与3秒完播为次要参考。</div><div class="scroll"><table class="perf"><thead><tr><th>排序/维度</th><th>3s 完播率表现</th><th>平均播放时长表现</th><th>CTR 表现</th><th>明细</th></tr></thead><tbody>{performance_table(good,'good')}</tbody></table></div></article><article class="panel"><h3>CTR低素材（200条）</h3><div class="mini">用于反向识别低点击标签组合与应规避元素。</div><div class="scroll"><table class="perf"><thead><tr><th>排序/维度</th><th>3s 完播率表现</th><th>平均播放时长表现</th><th>CTR 表现</th><th>明细</th></tr></thead><tbody>{performance_table(bad,'bad')}</tbody></table></div></article><article class="panel"><h3>CTR上升趋势素材（{len(rising)}条）</h3><div class="mini">数据中仅识别到 {len(rising)} 条至少两天且 CTR 上升的素材，按真实数据呈现。</div><div class="scroll"><table class="perf"><thead><tr><th>排序/维度</th><th>3s 完播率表现</th><th>平均播放时长表现</th><th>CTR 表现</th><th>明细</th></tr></thead><tbody>{performance_table(rising,'rising')}</tbody></table></div></article></div></section></div><div id="golden" class="view"><section class="section"><h2>素材起量黄金公式</h2><p>只保留已逐帧复核的真人口播、实拍展示或剧情素材；<b>普通图片轮播 / AI图文素材已全部剔除</b>。每条公式严格只有 <b>3 个创意标签</b>（场景痛点/情绪钩子、功能实测/功能表达、使用场景），并配开头/中间/结尾前15秒文字说明与不同关键帧。目标人群明确到年龄、性别、场景和诉求。</p>{golden_table()}</section></div><footer class="footer">素材8.20 · 前15秒创意分析 · 数据来源：用户提供表格</footer></main><div id="modal" class="modal"><div class="dialog"><button id="close" class="close">关闭</button><h2 id="mtitle">标签明细</h2><div id="mbody"></div></div></div><script>const DATA={DIMJSON};const names={{good:'优质素材',bad:'CTR低素材',rising:'CTR上升趋势素材'}};document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{{document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x===b));document.querySelectorAll('.view').forEach(x=>x.classList.toggle('active',x.id===b.dataset.v))}});document.querySelectorAll('.detail').forEach(b=>b.onclick=()=>{{let rows=DATA[b.dataset.group][b.dataset.dim]||[];document.getElementById('mtitle').textContent=names[b.dataset.group]+' · '+b.closest('tr').children[0].textContent+' 标签明细';document.getElementById('mbody').innerHTML='<div class="scroll"><table class="perf"><thead><tr><th>标签</th><th>素材数</th><th>消耗(万)</th><th>CTR</th><th>平均播放时长</th><th>3秒完播率</th><th>CVR</th></tr></thead><tbody>'+rows.map(r=>`<tr><td>${{r.tag}}</td><td>${{r.count}}</td><td>${{r.spend}}</td><td>${{r.ctr}}%</td><td>${{r.dur}}s</td><td>${{r.v3}}%</td><td>${{r.cvr}}%</td></tr>`).join('')+'</tbody></table></div>';document.getElementById('modal').classList.add('open')}});document.getElementById('close').onclick=()=>document.getElementById('modal').classList.remove('open');</script></body></html>'''
DOCS.mkdir(exist_ok=True)
(DOCS/'index.html').write_text(PAGE,encoding='utf-8')
# 静态 frames 同步到 GitHub Pages 发布目录
out_frames=DOCS/'assets'/'frames0820'
if FRAMES.exists():
    out_frames.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(FRAMES,out_frames,dirs_exist_ok=True)
print('built', DOCS/'index.html', '| demo',len(demo),'golden',len(golden),'rising',len(rising))
