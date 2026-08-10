#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为内衣、男装、女装 Top 素材下载视频并抽取 6 张关键帧。

关键帧保存为：assets/frames/<sector>/<material_id>/1.jpg ... 6.jpg
供深度页的逐帧拆解展示和人工视觉标签校验使用。
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from urllib.request import urlopen

import imageio_ffmpeg

BASE = Path(__file__).resolve().parent
SNAPSHOT = BASE / "data" / "sector_snapshot.json"
CACHE = BASE / "assets" / "videos"
OUT = BASE / "assets" / "frames"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
RATIOS = [0.02, 0.20, 0.40, 0.60, 0.80, 0.95]


def download(url: str, path: Path) -> bool:
    if path.exists() and path.stat().st_size > 0:
        return True
    temp = path.with_suffix('.part')
    try:
        with urlopen(url, timeout=50) as src, open(temp, 'wb') as dst:
            while chunk := src.read(1024 * 1024):
                dst.write(chunk)
        temp.replace(path)
        return path.stat().st_size > 0
    except Exception as exc:
        print(f"[download fail] {url[:60]}: {exc}")
        temp.unlink(missing_ok=True)
        return False


def duration(path: Path) -> float:
    try:
        text = subprocess.run([FFMPEG, '-i', str(path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=25).stderr.decode(errors='ignore')
        m = re.search(r'Duration:\s*(\d+):(\d+):(\d+\.?\d*)', text)
        return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 30.0
    except Exception:
        return 30.0


def extract(video: Path, sec: float, target: Path) -> bool:
    if target.exists() and target.stat().st_size > 0:
        return True
    try:
        subprocess.run([FFMPEG, '-y', '-ss', f'{sec:.2f}', '-i', str(video), '-frames:v', '1', '-vf', 'scale=360:-2', '-q:v', '4', str(target)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=35)
        return target.exists() and target.stat().st_size > 0
    except Exception:
        return False


def main(limit=12):
    data = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    for sector, payload in data.items():
        videos = payload['top'][:limit]
        print(f'=== {sector}: {len(videos)} 条 ===', flush=True)
        for index, item in enumerate(videos, 1):
            video = CACHE / f"{item['id']}.mp4"
            frame_dir = OUT / sector / item['id']
            frame_dir.mkdir(parents=True, exist_ok=True)
            print(f'[{index}/{len(videos)}] {item["id"]} {item["category"]}', flush=True)
            if not download(item['url'], video):
                continue
            dur = duration(video)
            for i, ratio in enumerate(RATIOS, 1):
                extract(video, max(0, min(dur - .1, dur * ratio)), frame_dir / f'{i}.jpg')


if __name__ == '__main__':
    import sys
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 12)
