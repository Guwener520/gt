# -*- coding: utf-8 -*-
"""Draw the three proposal figures with Pillow (no matplotlib in the bundled runtime).

v3 (2026-11-03) redraw:
  fig1-route : four research modules (concept/model, acquisition/association, provenance/resumption,
               evaluation)
  fig2-model : eight-entity task-context graph with provenance relations (replaces the old
               four-layer software architecture figure)
  fig3-gantt : 32 teaching weeks, six phases, matching task-book v6

Layout rules that keep the figures readable when placed at ~15 cm:
  * canvas width 2000 px  ->  a 40 px glyph prints at about 8 pt
  * minimum glyph size used here is 26 px (about 5.5 pt) for secondary annotations
  * no outer frame is drawn; the LaTeX figure environment must not add one either
"""
import math
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
BLUE_F2 = (239, 246, 255)
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


def tag(d, cx, cy, s, f, fill=SUB):
    """Relation label on a white patch so the arrow behind it cannot cut the text."""
    bb = d.textbbox((0, 0), s, font=f)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    pad = 7
    d.rounded_rectangle([cx - w / 2 - pad, cy - h / 2 - pad,
                         cx + w / 2 + pad, cy + h / 2 + pad], radius=6, fill="white")
    text_at(d, cx, cy, s, f, fill)


# --------------------------------------------------------------------------- fig 1
def fig_route():
    H = 720
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    f_t, f_d = font(42, True), font(30)

    modules = [
        ("模块一　概念框架与信息模型", "任务、上下文与溯源界定；八实体关系；统一事件模式"),
        ("模块二　采集、关联与任务边界", "会话/工具/Git/测试接入；变更归一化；关联与边界判定"),
        ("模块三　变更溯源与任务续接", "变更卡片；双向查询；任务快照；证据绑定摘要"),
        ("模块四　评估方案", "离线指标；4—5 人试点；错误分析；结果反馈"),
    ]
    bx, bw, bh = 110, 1400, 126
    ys = [34 + i * 174 for i in range(4)]
    cx = bx + bw / 2

    for i, (title, detail) in enumerate(modules):
        y = ys[i]
        fill, edge = (BLUE_F, BLUE_E) if i < 3 else (WARM_F, WARM_E)
        rbox(d, bx, y, bw, bh, fill, edge)
        text_left(d, bx + 34, y + 46, title, f_t)
        text_left(d, bx + 34, y + 94, detail, f_d, SUB)
        if i < 3:
            arrow(d, (cx, y + bh + 4), (cx, ys[i + 1] - 6), head=16)

    # feedback loop: evaluation -> model & methods
    fx = 1690
    polyline(d, [(bx + bw + 4, ys[3] + bh / 2), (fx, ys[3] + bh / 2),
                 (fx, ys[0] + bh / 2), (bx + bw + 4, ys[0] + bh / 2)], dashed=True, width=2)
    for j, line in enumerate(["评估结果", "反馈修正", "模型与方法"]):
        text_left(d, fx + 26, ys[0] + bh / 2 + 120 + j * 44, line, font(30), WARM_E)

    im.save(OUT / "fig1-route.png", dpi=(300, 300))


# --------------------------------------------------------------------------- fig 2
def fig_model():
    H = 1080
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    f_title, f_sub, f_rel = font(36, True), font(26), font(27)
    f_note = font(27)

    boxes = {
        "task":      (700, 34, 600, 118, "开发任务（Task）", "目标、状态、起止时间", BLUE_F, BLUE_E),
        "check":     (1480, 34, 470, 118, "检查点（Checkpoint）", "阶段快照、恢复入口", WARM_F, WARM_E),
        "turn":      (80, 268, 380, 118, "对话轮次（Turn）", "用户与智能体的轮次", BLUE_F2, BLUE_E),
        "msg":       (580, 268, 380, 118, "消息（Message）", "请求、回复、引用", BLUE_F2, BLUE_E),
        "tool":      (1080, 268, 380, 118, "工具调用（ToolCall）", "命令、参数、结果", BLUE_F2, BLUE_E),
        "change":    (580, 498, 380, 118, "文件变更（hunk）", "内容哈希、路径、位置", BLUE_F, BLUE_E),
        "test":      (1080, 498, 380, 118, "测试运行（TestRun）", "命令、退出码、环境", BLUE_F2, BLUE_E),
        "case":      (1080, 728, 380, 118, "测试用例结果", "用例、状态、耗时", BLUE_F2, BLUE_E),
    }

    def box(key):
        x, y, w, h, title, sub, fill, edge = boxes[key]
        rbox(d, x, y, w, h, fill, edge)
        text_at(d, x + w / 2, y + 40, title, f_title)
        text_at(d, x + w / 2, y + 82, sub, f_sub, SUB)
        return x, y, w, h

    for key in boxes:
        box(key)

    # relations
    arrow(d, (1000, 152), (270, 268), head=15)
    tag(d, 635, 205, "包含", f_rel)

    arrow(d, (460, 327), (580, 327), head=13)
    tag(d, 520, 296, "包含", f_rel)

    arrow(d, (960, 327), (1080, 327), head=13)
    tag(d, 1020, 296, "触发", f_rel)

    arrow(d, (1270, 386), (960, 498), head=15)
    tag(d, 1115, 442, "产出", f_rel)

    arrow(d, (960, 557), (1080, 557), head=13)
    tag(d, 1020, 526, "验证", f_rel)

    arrow(d, (1270, 616), (1270, 728), head=15)
    tag(d, 1270, 672, "产出", f_rel)

    arrow(d, (1300, 93), (1480, 93), color=WARM_E, head=13, dashed=True)
    tag(d, 1390, 62, "快照", f_rel, WARM_E)

    # self loop: later evolution of the same hunk
    polyline(d, [(580, 498), (500, 498), (500, 616), (580, 616)], color=WARM_E, width=2, dashed=True)
    tag(d, 452, 557, "演化", f_rel, WARM_E)

    # legend
    ly = 930
    d.line([(150, ly), (250, ly)], fill=BLUE_E, width=3)
    d.polygon([(250, ly), (236, ly - 9), (236, ly + 9)], fill=BLUE_E)
    text_left(d, 270, ly, "包含 / 触发 / 产出 / 验证", f_note, SUB)
    d.line([(700, ly), (800, ly)], fill=WARM_E, width=2)
    d.polygon([(800, ly), (786, ly - 9), (786, ly + 9)], fill=WARM_E)
    text_left(d, 820, ly, "快照 / 演化（回退、重写）", f_note, SUB)
    text_left(d, 150, 995, "箭头方向表示证据来源到证据结果；所有实体以 task_id 归属开发任务，hunk 以内容哈希标识。", f_note, SUB)

    im.save(OUT / "fig2-model.png", dpi=(300, 300))


# --------------------------------------------------------------------------- fig 3
def fig_gantt():
    H = 840
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    f_lbl, f_tick, f_ms, f_note = font(32), font(28), font(28), font(27)

    phases = [
        ("1　文献研究与产品调研", 1, 8),
        ("2　关键方法设计与实现", 9, 14),
        ("3　系统设计与实现", 15, 20),
        ("4　系统验证与测试", 21, 22),
        ("5　毕业设计论文撰写", 23, 28),
        ("6　论文审阅与修改", 29, 32),
    ]
    x0, x1 = 430, 1940
    total = 32
    ww = (x1 - x0) / total
    top, row_h = 170, 80
    axis_bottom = top + row_h * len(phases)

    def xpos(week):
        """Left edge of a teaching week (1-based)."""
        return x0 + (week - 1) * ww

    # grid + week ticks
    for week in (1, 4, 8, 12, 16, 20, 24, 28, 32):
        x = xpos(week)
        d.line([(x, top - 10), (x, axis_bottom)], fill=GRID, width=2)
        text_at(d, x, axis_bottom + 30, f"第{week}周", f_tick, SUB)

    # bars
    for i, (_, start, end) in enumerate(phases):
        y = top + i * row_h
        bx0, bx1 = xpos(start) + 2, xpos(end) + ww - 2
        fill = BLUE_F if i % 2 == 0 else BLUE_F2
        d.rounded_rectangle([bx0, y + 12, max(bx1, bx0 + 8), y + row_h - 12],
                            radius=9, fill=fill, outline=BLUE_E, width=2)

    for i, (name, _, _) in enumerate(phases):
        y = top + i * row_h
        text_right(d, x0 - 24, y + row_h / 2, name, f_lbl, INK)

    # milestone: proposal defence in week 9
    mx = xpos(9)
    d.line([(mx, top - 8), (mx, axis_bottom)], fill=WARM_E, width=2)
    cy = top - 46
    r = 12
    d.polygon([(mx, cy - r), (mx + r, cy), (mx, cy + r), (mx - r, cy)], fill=WARM_E)
    text_at(d, mx, cy - 36, "第 9 周　开题答辩", f_ms, WARM_E)

    d.line([(x0, axis_bottom), (x1, axis_bottom)], fill=(148, 163, 184), width=2)
    text_left(d, x0, axis_bottom + 78, "教学周编号按学院日历；中期检查、答辩按学院统一安排，具体以学院通知为准。", f_note, SUB)

    im.save(OUT / "fig3-gantt.png", dpi=(300, 300))


if __name__ == "__main__":
    fig_route()
    fig_model()
    fig_gantt()
    for f in sorted(OUT.glob("*.png")):
        im = Image.open(f)
        print(f.name, im.size, f.stat().st_size, "bytes")
