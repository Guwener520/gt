# -*- coding: utf-8 -*-
"""Draw the three proposal figures with Pillow (no matplotlib in the bundled runtime).

Layout rules that keep the figures readable when placed at 14 cm in the docx:
  * canvas width 2000 px  ->  a 40 px glyph prints at about 8 pt
  * minimum glyph size used here is 30 px (about 6 pt) for secondary annotations
  * no outer frame is drawn; the docx builder must not add one either
"""
import math
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "thesis" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

REG = r"C:\Windows\Fonts\msyh.ttc"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"

INK = (31, 41, 55)
SUB = (71, 85, 105)
BLUE_F = (219, 234, 254)
BLUE_E = (37, 99, 163)
GRAY_F = (241, 245, 249)
GRAY_E = (120, 134, 152)
WARM_F = (254, 243, 199)
WARM_E = (176, 82, 8)
BAND = (248, 250, 252)
BAND_E = (203, 213, 225)
GRID = (226, 232, 240)

W = 2000


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size)


def text_at(d, cx, cy, s, f, fill=INK):
    bb = d.textbbox((0, 0), s, font=f)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]), s, font=f, fill=fill)


def text_left(d, x, cy, s, f, fill=INK):
    bb = d.textbbox((0, 0), s, font=f)
    d.text((x, cy - (bb[3] - bb[1]) / 2 - bb[1]), s, font=f, fill=fill)


def text_right(d, x, cy, s, f, fill=INK):
    bb = d.textbbox((0, 0), s, font=f)
    d.text((x - (bb[2] - bb[0]) - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]), s, font=f, fill=fill)


def rbox(d, x, y, w, h, fill, edge, radius=16, width=3):
    d.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill, outline=edge, width=width)


def arrow(d, p1, p2, color=BLUE_E, width=3, head=15, dashed=False):
    x1, y1 = p1
    x2, y2 = p2
    dist = math.hypot(x2 - x1, y2 - y1)
    if dist == 0:
        return
    ux, uy = (x2 - x1) / dist, (y2 - y1) / dist
    if dashed:
        seg, gap, t = 14, 10, 0.0
        while t < dist - head:
            a = (x1 + ux * t, y1 + uy * t)
            e = min(t + seg, dist - head)
            d.line([a, (x1 + ux * e, y1 + uy * e)], fill=color, width=width)
            t += seg + gap
    else:
        d.line([(x1, y1), (x2 - ux * head * 0.6, y2 - uy * head * 0.6)], fill=color, width=width)
    ang = math.atan2(y2 - y1, x2 - x1)
    left = (x2 - head * math.cos(ang - 0.45), y2 - head * math.sin(ang - 0.45))
    right = (x2 - head * math.cos(ang + 0.45), y2 - head * math.sin(ang + 0.45))
    d.polygon([(x2, y2), left, right], fill=color)


def polyline(d, pts, color=WARM_E, width=2, dashed=False):
    for a, b in zip(pts, pts[1:]):
        arrow(d, a, b, color=color, width=width, dashed=dashed)


# --------------------------------------------------------------------------- fig 1
def fig_route():
    H = 1040
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    f_t, f_d, f_tag = font(42, True), font(31), font(28, True)

    # numbering: 步骤一…六 (the calendar schedule elsewhere uses 阶段一…十二, so the
    # two series must not share a name); the right-hand tag maps to 研究内容 (1)…(6)
    steps = [
        ("步骤一　需求与调研", "文献综述、竞品分析、需求清单、可行性 Spike 报告", "准备"),
        ("步骤二　模型设计", "实体关系模型、可扩展事件模式、表结构", "内容(1)"),
        ("步骤三　采集实现", "会话 / 文件与 Git / 测试报告采集，六步归一化", "内容(2)"),
        ("步骤四　关联与溯源", "关联算法、变更卡片、证据链与多跳查询", "内容(3)(4)"),
        ("步骤五　界面与续接", "任务时间线、证据侧栏、任务快照与恢复视图", "内容(5)"),
        ("步骤六　评估验证", "离线消融、受试者实验、错误分析，结果回流", "内容(6)"),
    ]
    bx, bw, bh = 110, 1400, 124
    ys = [30 + i * 166 for i in range(6)]
    cx = bx + bw / 2

    for i, (title, detail, tag) in enumerate(steps):
        y = ys[i]
        fill, edge = (BLUE_F, BLUE_E) if i < 5 else (WARM_F, WARM_E)
        rbox(d, bx, y, bw, bh, fill, edge)
        text_left(d, bx + 34, y + 44, title, f_t)
        text_left(d, bx + 34, y + 92, detail, f_d, SUB)
        text_right(d, bx + bw - 26, y + bh / 2, tag, f_tag, edge)
        if i < 5:
            arrow(d, (cx, y + bh + 4), (cx, ys[i + 1] - 6), head=16)

    # feedback loop: step 6 -> step 2
    fx = 1690
    polyline(d, [(bx + bw + 4, ys[5] + bh / 2), (fx, ys[5] + bh / 2),
                 (fx, ys[1] + bh / 2), (bx + bw + 4, ys[1] + bh / 2)], dashed=True, width=2)
    for j, line in enumerate(["评估结果", "回流修正", "模型与算法"]):
        text_left(d, fx + 26, ys[1] + bh / 2 + 150 + j * 44, line, font(30), WARM_E)

    im.save(OUT / "fig1-route.png", dpi=(300, 300))


# --------------------------------------------------------------------------- fig 2
def fig_arch():
    H = 1080
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    f_band, f_item, f_note = font(38, True), font(31), font(27)
    # the analysis row carries four boxes, so its widest label (实体链接与位置映射, 9 glyphs)
    # needs a 29 px face to keep a visible side padding inside a ~281 px box
    band_fs = {"分析与关联层": 29}

    bands = [
        ("交互层", ["任务时间线", "变更证据侧栏", "恢复视图"], 50, BLUE_F, BLUE_E),
        ("分析与关联层", ["归一化与边界判定", "实体链接与位置映射", "证据链构建", "摘要与证据校验"],
         295, BLUE_F, BLUE_E),
        ("模型与存储层", ["SQLite 实体表", "FTS5 全文索引", "变更卡片与快照"], 540, BLUE_F, BLUE_E),
        ("接入层", ["会话事件\nhooks / stream-json", "文件系统与 Git", "测试报告与命令输出"],
         785, GRAY_F, GRAY_E),
    ]
    band_h, label_w = 190, 240
    left, right = 40, 1470

    for name, items, y, fill, edge in bands:
        d.rounded_rectangle([left, y, right, y + band_h], radius=18, fill=BAND, outline=BAND_E, width=3)
        text_at(d, left + label_w / 2, y + band_h / 2, name, f_band, (40, 52, 70))
        area_x0 = left + label_w + 8
        area_x1 = right - 16
        gap = 14
        n = len(items)
        iw = (area_x1 - area_x0 - gap * (n - 1)) / n
        f_body = font(band_fs[name]) if name in band_fs else f_item
        for i, it in enumerate(items):
            x = area_x0 + i * (iw + gap)
            rbox(d, x, y + 30, iw, band_h - 60, fill, edge, radius=12, width=2)
            lines = it.split("\n")
            base = y + band_h / 2 - (len(lines) - 1) * 20
            for k, line in enumerate(lines):
                text_at(d, x + iw / 2, base + k * 40, line, f_body if len(lines) == 1 else f_note)

    # upward data-flow arrows with the data form on each gap
    gaps = [
        (785, 730, "原始事件"),
        (540, 485, "统一事件与实体表"),
        (295, 240, "证据链与任务快照"),
    ]
    for y_from, y_to, note in gaps:
        for x in (641, 1101):
            arrow(d, (x, y_from - 6), (x, y_to + 6), head=15)
        text_at(d, 871, (y_from + y_to) / 2, note, f_note, SUB)

    # LLM side service
    lx0, lx1, ly0, ly1 = 1600, 1970, 150, 610
    rbox(d, lx0, ly0, lx1 - lx0, ly1 - ly0, WARM_F, WARM_E, radius=18, width=3)
    text_at(d, (lx0 + lx1) / 2, ly0 + 46, "大语言模型服务", font(32, True))
    for i, t in enumerate(["任务摘要生成", "修改意图归纳", "缺失关联补全", "输出证据绑定"]):
        text_at(d, (lx0 + lx1) / 2, ly0 + 112 + i * 62, t, f_note, SUB)

    mid = (right + lx0) / 2
    arrow(d, (right + 4, 460), (lx0 - 6, 460), color=WARM_E, width=3)
    text_at(d, mid, 432, "调用", font(26), WARM_E)
    arrow(d, (lx0 - 6, 150), (right + 4, 150), color=WARM_E, width=3)
    text_at(d, mid, 122, "结论", font(26), WARM_E)
    arrow(d, (lx0 - 6, 380), (right + 4, 380), color=WARM_E, width=2, dashed=True)
    text_at(d, mid, 352, "证据 id", font(26), WARM_E)
    text_at(d, (lx0 + lx1) / 2, ly1 + 34, "校验失败则弃答", f_note, WARM_E)

    im.save(OUT / "fig2-arch.png", dpi=(300, 300))


# --------------------------------------------------------------------------- fig 3
def fig_gantt():
    H = 940
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    f_lbl, f_tick, f_ms = font(34), font(30), font(28)

    stages = [
        ("一　调研与 spike", date(2026, 11, 2), date(2026, 11, 15)),
        ("二　开题", date(2026, 11, 16), date(2026, 11, 30)),
        ("三　模型设计", date(2026, 12, 1), date(2026, 12, 20)),
        ("四　采集与边界", date(2026, 12, 21), date(2027, 1, 10)),
        ("五　中期检查", date(2027, 1, 11), date(2027, 1, 20)),
        ("六　关联与溯源", date(2027, 1, 21), date(2027, 2, 20)),
        ("七　界面与续接", date(2027, 2, 21), date(2027, 3, 15)),
        ("八　数据与标注", date(2027, 3, 16), date(2027, 3, 31)),
        ("九　实验与分析", date(2027, 4, 1), date(2027, 4, 20)),
        ("十　论文初稿", date(2027, 4, 21), date(2027, 5, 10)),
        ("十一　修改送审", date(2027, 5, 11), date(2027, 5, 25)),
        ("十二　答辩", date(2027, 5, 26), date(2027, 5, 31)),
    ]
    d0, d1 = date(2026, 10, 26), date(2027, 6, 6)
    total = (d1 - d0).days
    x0, x1 = 450, 1940
    top, row_h = 140, 58

    def xpos(dt):
        return x0 + (dt - d0).days / total * (x1 - x0)

    axis_bottom = top + row_h * len(stages)

    # month grid
    m = date(2026, 11, 1)
    while m <= d1:
        x = xpos(m)
        d.line([(x, top - 8), (x, axis_bottom)], fill=GRID, width=2)
        text_at(d, x, axis_bottom + 30, f"{m.year}-{m.month:02d}", f_tick, (71, 85, 105))
        m = date(m.year + (1 if m.month == 12 else 0), 1 if m.month == 12 else m.month + 1, 1)

    # bars first, labels afterwards so nothing can occlude the text
    for i, (_, s, e) in enumerate(stages):
        y = top + i * row_h
        bx0, bx1 = xpos(s), xpos(e)
        d.rounded_rectangle([bx0, y + 10, max(bx1, bx0 + 8), y + row_h - 10],
                            radius=9, fill=BLUE_F, outline=BLUE_E, width=2)

    for i, (name, _, _) in enumerate(stages):
        y = top + i * row_h
        text_right(d, x0 - 22, y + row_h / 2, name, f_lbl, INK)

    # milestones as diamonds on the axis, labels above the plot
    for dt, txt in [(date(2026, 11, 30), "11-30 开题"),
                    (date(2027, 1, 20), "01-20 中期"),
                    (date(2027, 5, 25), "05-25 送审")]:
        x = xpos(dt)
        d.line([(x, top - 4), (x, axis_bottom)], fill=WARM_E, width=2)
        cy = top - 46
        r = 11
        d.polygon([(x, cy - r), (x + r, cy), (x, cy + r), (x - r, cy)], fill=WARM_E)
        text_at(d, x, cy - 34, txt, f_ms, WARM_E)

    d.line([(x0, axis_bottom), (x1, axis_bottom)], fill=(148, 163, 184), width=2)
    im.save(OUT / "fig3-gantt.png", dpi=(300, 300))


if __name__ == "__main__":
    fig_route()
    fig_arch()
    fig_gantt()
    for f in sorted(OUT.glob("*.png")):
        im = Image.open(f)
        print(f.name, im.size, f.stat().st_size, "bytes")
