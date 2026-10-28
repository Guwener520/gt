# -*- coding: utf-8 -*-
"""Measure every label against its container to catch overflow without seeing the image."""
from PIL import ImageFont

REG = r"C:\Windows\Fonts\msyh.ttc"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
def f(sz, b=False): return ImageFont.truetype(BOLD if b else REG, sz)
def w(s, fo): 
    bb = fo.getbbox(s); return bb[2]-bb[0]

problems = []

# fig1: boxes 480 wide
t, s = f(40, True), f(30)
for line in ["阶段一　需求与调研","阶段二　模型设计","阶段三　采集实现","阶段四　关联与溯源","阶段五　界面与续接","阶段六　评估验证"]:
    ww = w(line, t)
    if ww > 440: problems.append(f"fig1 title {line!r} {ww}px > 440")
for line in ["会话 / 文件 / Git / 测试","变更卡片与证据链","证据侧栏 · 恢复视图","最小闭环打通","事件模式与表结构"]:
    ww = w(line, s)
    if ww > 440: problems.append(f"fig1 sub {line!r} {ww}px > 440")

# fig2: item boxes
area_x0, area_x1, gap = 300, 1340, 18
for n, items in [(5, ["任务中心","任务时间线","文件/片段","证据侧栏","恢复视图"]),
                 (5, ["实体链接","位置映射","证据链构建","摘要与意图","证据校验"]),
                 (4, ["统一事件表","实体关系表","变更卡片","任务快照"]),
                 (4, ["会话日志","文件系统 / Git","测试报告","命令输出"])]:
    iw = (area_x1 - area_x0 - gap*(n-1)) / n
    for it in items:
        ww = w(it, f(30))
        if ww > iw - 16: problems.append(f"fig2 item {it!r} {ww}px > {iw-16:.0f}")
    print(f"fig2 n={n} box={iw:.1f}px")

for lb in ["交互层","分析与关联层","模型与存储层","接入层"]:
    ww = w(lb, f(34, True))
    if ww > 230: problems.append(f"fig2 band {lb!r} {ww}px > 230")

# fig2 LLM box width 350
for it in ["任务摘要生成","修改意图归纳","缺失关联补全","输出证据绑定"]:
    ww = w(it, f(27))
    if ww > 330: problems.append(f"fig2 llm {it!r} {ww}px > 330")

# fig3 labels in 380px column
for lb in ["一　需求与调研","二　开题报告","三　模型设计","四　采集与关联","五　中期检查","六　溯源与界面","七　续接与 LLM","八　实验与评估","九　论文初稿","十　定稿送审","十一　答辩"]:
    ww = w(lb, f(28))
    if ww > 360: problems.append(f"fig3 label {lb!r} {ww}px > 360")

print("PROBLEMS:", len(problems))
for p in problems: print(" -", p)
