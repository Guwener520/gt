#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把 latex/ 下的行政表格正文转成可编辑的 Markdown 镜像，并校验二者是否同步。

每份 LaTeX 文档对应一份 Markdown 镜像（约定见 AGENTS.md 第 7 节）：

    latex/chapters/taskbook_body.tex  <->  thesis/task-book.md
    latex/chapters/proposal_body.tex  <->  thesis/proposal.md

用法（在工作区根目录）：

    python scripts/tex2md.py              # 从 tex 重新生成两份 md
    python scripts/tex2md.py --check      # 只校验 md 与 tex 是否一致（不一致退出码 1）
    python scripts/tex2md.py proposal     # 只处理开题报告
    python scripts/tex2md.py taskbook --check

约定：
* 本脚本由作者决定何时运行；智能体（AI 助手）调用前须先征得作者同意，
  包括 --check 校验（见 AGENTS.md 第 7 节）。
* tex 是排版权威；md 是逐段对应的可编辑镜像。改稿时先改 md，再同步 tex；
  tex 有改动后重新运行本脚本生成 md。提交前用 --check 确认两者一致。
* 封面信息取自 latex/chapters/metadata.tex，不在正文 tex 中，故单独生成“封面信息”表。
* 新增 LaTeX 文档时，在下面 DOCS 表登记 tex/md 路径与标题即可。
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LATEX = ROOT / "latex"
THESIS = ROOT / "thesis"

DOCS = {
    "taskbook": {
        "tex": LATEX / "chapters" / "taskbook_body.tex",
        "md": THESIS / "task-book.md",
        "title": "本科毕业设计（论文）任务书",
    },
    "proposal": {
        "tex": LATEX / "chapters" / "proposal_body.tex",
        "md": THESIS / "proposal.md",
        "title": "本科毕业设计（论文）开题报告",
    },
}

HEADER_TEXT = "毕业设计（论文）"


# --------------------------------------------------------------------------- #
# 通用工具
# --------------------------------------------------------------------------- #
def strip_comments(lines: list[str]) -> list[str]:
    """删除未转义的 % 行内注释（保留 \\%）。"""
    out = []
    for raw in lines:
        line = raw.rstrip("\n")
        m = re.search(r"(?<!\\)%", line)
        if m:
            line = line[: m.start()]
        out.append(line.rstrip())
    return out


def find_end(lines: list[str], start: int, env: str) -> int:
    needle = f"\\end{{{env}}}"
    for j in range(start, len(lines)):
        if needle in lines[j]:
            return j
    raise ValueError(f"找不到 {needle}（起始行 {start + 1}）")


def read_metadata() -> dict:
    text = (LATEX / "chapters" / "metadata.tex").read_text(encoding="utf-8")

    def one(pattern: str) -> str:
        m = re.search(pattern, text, re.S)
        return m.group(1).strip() if m else ""

    meta = {
        "school": one(r"\\school\{([^}]*)\}"),
        "major": one(r"\\major\{([^}]*)\}"),
        "title": one(r"\\thesistitle\{([^}]*)\}"),
        "title_eng": one(r"\\thesistitleeng\{([^}]*)\}"),
        "advisor": one(r"\\thesisadvisor\{([^}]*)\}"),
    }
    m = re.search(r"\\student\{([^}]*)\}\{([^}]*)\}", text)
    meta["student_name"] = m.group(1).strip() if m else ""
    meta["student_id"] = m.group(2).strip() if m else ""
    m = re.search(
        r"\\taskbookperiod\{(\d+)\}\{(\d+)\}\{(\d+)\}\{(\d+)\}\{(\d+)\}\{(\d+)\}",
        text,
    )
    if m:
        nums = [int(x) for x in m.groups()]
        start = date(nums[0], nums[1], nums[2])
        end = date(nums[3], nums[4], nums[5])
        meta["period_start"] = f"{start.year} 年 {start.month} 月 {start.day} 日"
        meta["period_end"] = f"{end.year} 年 {end.month} 月 {end.day} 日"
        meta["period_weeks"] = str(math.ceil(((end - start).days + 1) / 7))
    else:
        meta["period_start"] = meta["period_end"] = ""
        meta["period_weeks"] = ""
    return meta


def inline(text: str, labels: dict[str, str] | None = None) -> str:
    """把一行 LaTeX 行内命令转成 Markdown 行内文本。"""
    if labels:
        text = re.sub(r"\\ref\{([^}]*)\}", lambda m: labels.get(m.group(1), "??"), text)
    # 控制词后的空格只是 TeX 分隔符，不应进入 Markdown（否则“（论文） 的”多一个空格）
    text = re.sub(r"\\tjheadertext\s*", HEADER_TEXT, text)
    text = re.sub(r"\\textbf\{(.*?)\}", r"**\1**", text)
    text = re.sub(r"\\mbox\{(.*?)\}", r"\1", text)
    text = re.sub(r"\\allowbreak\s*", "", text)
    text = text.replace("~", " ")
    text = text.replace("\\&", "&").replace("\\%", "%").replace("\\_", "_")
    text = re.sub(r"\\quad", "  ", text)
    text = re.sub(r"\\[,;:]", " ", text)
    text = re.sub(r"\\vspace\*?\{[^}]*\}", "", text)
    text = re.sub(r"\\vfill\b", "", text)
    text = re.sub(r"\\(?:pagebreak|newpage)\*?(?:\[[^\]]*\])?", "", text)
    text = re.sub(r"\\hspace\{[^}]*\}", "", text)
    text = text.replace("\\par", "")
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text


# --------------------------------------------------------------------------- #
# 编号预扫描：先建立 label -> "2-1" 映射，正文里的 \ref 才能解析
# --------------------------------------------------------------------------- #
def scan_labels(lines: list[str]) -> dict[str, str]:
    labels: dict[str, str] = {}
    sec: int | None = None
    tab = fig = 0
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        m = re.match(r"\\tjformsection\{.*?\}(?:\\tjformsecnum\{(\d+)\})?\s*$", s)
        if m:
            if m.group(1):
                sec = int(m.group(1))
                tab = fig = 0
            i += 1
            continue
        if s.startswith("\\begin{table}") or s.startswith("\\begin{longtable}"):
            env = "longtable" if s.startswith("\\begin{longtable}") else "table"
            j = find_end(lines, i, env)
            lab = re.search(r"\\label\{([^}]*)\}", "\n".join(lines[i : j + 1]))
            tab += 1
            if lab:
                labels[lab.group(1)] = f"{sec}-{tab}" if sec is not None else str(tab)
            i = j + 1
            continue
        if s.startswith("\\begin{figure}"):
            j = find_end(lines, i, "figure")
            lab = re.search(r"\\label\{([^}]*)\}", "\n".join(lines[i : j + 1]))
            fig += 1
            if lab:
                labels[lab.group(1)] = f"{sec}-{fig}" if sec is not None else str(fig)
            i = j + 1
            continue
        i += 1
    return labels


# --------------------------------------------------------------------------- #
# 块级渲染
# --------------------------------------------------------------------------- #
def render_table(block: list[str], labels: dict[str, str], num: str) -> list[str]:
    text = "\n".join(block)
    cap = re.search(r"\\caption\{(.*?)\}", text)
    caption = inline(cap.group(1)) if cap else ""
    label = re.search(r"\\label\{([^}]*)\}", text)
    if label:
        labels[label.group(1)] = num

    rows: list[list[str]] = []
    for ln in block:
        t = ln.strip()
        if "&" not in t:
            continue
        if t.startswith(("\\caption", "\\label")):
            continue
        t = re.sub(r"\\\\\s*$", "", t).strip()
        cells = [inline(c.strip()) for c in re.split(r"(?<!\\)&", t)]
        rows.append(cells)

    # longtable 的表头会在 \endfirsthead 后重复一次，去掉重复行
    if len(rows) >= 2 and rows[0] == rows[1]:
        rows = [rows[0]] + rows[2:]

    out = [f"表 {num} {caption}".rstrip(), ""]
    if rows:
        width = len(rows[0])
        out.append("| " + " | ".join(rows[0]) + " |")
        out.append("| " + " | ".join(["---"] * width) + " |")
        for r in rows[1:]:
            if len(r) < width:
                r = r + [""] * (width - len(r))
            out.append("| " + " | ".join(r[:width]) + " |")
    out.append("")
    return out


def render_figure(block: list[str], labels: dict[str, str], num: str) -> list[str]:
    text = "\n".join(block)
    cap = re.search(r"\\caption\{(.*?)\}", text)
    caption = inline(cap.group(1)) if cap else ""
    label = re.search(r"\\label\{([^}]*)\}", text)
    if label:
        labels[label.group(1)] = num
    img = re.search(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", text)
    path = img.group(1) if img else ""
    alt = f"图 {num} {caption}".rstrip()
    return [f"![{alt}]({path})", ""]


def render_refs(block: list[str]) -> list[str]:
    out = []
    idx = 0
    for ln in block:
        t = ln.strip()
        m = re.match(r"\\item\s*(.*)$", t)
        if not m:
            continue
        idx += 1
        out.append(f"[{idx}] {inline(m.group(1))}")
        out.append("")
    return out


def render_reviewbox(block: list[str]) -> list[str]:
    label = hint = sig = ""
    for ln in block:
        t = ln.strip()
        m = re.search(r"\\tjformlabel\{([^}]*)\}", t)
        if m:
            label = inline(m.group(1))
        m = re.search(r"\\tjformhint\{(.*?)\}", t)
        if m:
            hint = inline(m.group(1))
        m = re.search(r"\\tjformsignature(?:\[[^\]]*\])?\{([^}]*)\}\{[^}]*\}", t)
        if m:
            sig = inline(m.group(1))
    out = []
    body = f"**{label}**{hint}" if label else hint
    out.append(f"> {body}" if body else ">")
    out.append(">")
    if sig:
        out.append(f"> {sig}：________________　　　　年　　月　　日")
    out.append("")
    return out


# --------------------------------------------------------------------------- #
# 正文转换主循环
# --------------------------------------------------------------------------- #
def convert(lines: list[str], labels: dict[str, str]) -> list[str]:
    md: list[str] = []
    sec: int | None = None
    tab = fig = 0
    seen_subsection = False
    lists: list[list] = []  # [[kind, counter], ...]
    i = 0
    n = len(lines)

    while i < n:
        s = lines[i].strip()

        if not s:
            md.append("")
            i += 1
            continue

        # ---- 导言区辅助块 ----
        if s.startswith("\\makeatletter"):
            while i < n and "\\makeatother" not in lines[i]:
                i += 1
            i += 1
            continue
        if s in ("\\iftjproposalabstract", "\\fi", "\\begingroup", "\\endgroup", "\\small"):
            i += 1
            continue
        if s.startswith("\\setlength{") or s.startswith("\\renewcommand{\\theH"):
            i += 1
            continue
        if s.startswith("{\\zihao") or s == "}":
            i += 1
            continue
        if s == "\\vfill":
            i += 1
            continue
        if s.startswith("\\clearpage") or s.startswith("\\newpage"):
            md.append("<!-- pagebreak -->")
            md.append("")
            i += 1
            continue

        # ---- 一级/二级/三级标题 ----
        m = re.match(r"\\tjformsection\{(.*?)\}(?:\\tjformsecnum\{(\d+)\})?\s*$", s)
        if m:
            title = inline(m.group(1))
            if m.group(2):
                sec = int(m.group(2))
                tab = fig = 0
            seen_subsection = False
            md.extend([f"## {title}", ""])
            i += 1
            continue
        m = re.match(r"\\tjformsubsection\{(.*?)\}\s*$", s)
        if m:
            seen_subsection = True
            md.extend([f"### {inline(m.group(1))}", ""])
            i += 1
            continue
        m = re.match(r"\\tjformsubsub\{(.*?)\}\s*$", s)
        if m:
            level = "####" if seen_subsection else "###"
            md.extend([f"{level} {inline(m.group(1))}", ""])
            i += 1
            continue

        # ---- 表格 / 图 ----
        if s.startswith("\\begin{table}"):
            j = find_end(lines, i, "table")
            tab += 1
            num = f"{sec}-{tab}" if sec is not None else str(tab)
            md.extend(render_table(lines[i : j + 1], labels, num))
            i = j + 1
            continue
        if s.startswith("\\begin{longtable}"):
            j = find_end(lines, i, "longtable")
            tab += 1
            num = f"{sec}-{tab}" if sec is not None else str(tab)
            md.extend(render_table(lines[i : j + 1], labels, num))
            i = j + 1
            continue
        if s.startswith("\\begin{figure}"):
            j = find_end(lines, i, "figure")
            fig += 1
            num = f"{sec}-{fig}" if sec is not None else str(fig)
            md.extend(render_figure(lines[i : j + 1], labels, num))
            i = j + 1
            continue

        # ---- 参考文献 / 审核框 ----
        if s.startswith("\\begin{tjreflist}"):
            j = find_end(lines, i, "tjreflist")
            md.extend(render_refs(lines[i : j + 1]))
            i = j + 1
            continue
        if s.startswith("\\begin{tjreviewbox}"):
            j = find_end(lines, i, "tjreviewbox")
            md.extend(render_reviewbox(lines[i : j + 1]))
            i = j + 1
            continue

        # ---- 列表 ----
        if s.startswith("\\begin{enumerate}"):
            m = re.match(r"\\begin\{enumerate\}(?:\[(.*?)\])?\s*$", s)
            label = m.group(1) if m else ""
            if "（\\arabic*）" in label:
                style = "fullwidth-paren"
            elif "(\\arabic*)" in label:
                style = "halfwidth-paren"
            else:
                style = "dot"
            lists.append(["enumerate", 0, style])
            i += 1
            continue
        if s.startswith("\\end{enumerate}") or s.startswith("\\end{itemize}"):
            if lists:
                lists.pop()
            i += 1
            continue
        if s.startswith("\\begin{itemize}"):
            lists.append(["itemize", 0, ""])
            i += 1
            continue
        if s.startswith("\\item"):
            rest = re.sub(r"^\\item\s*", "", s)
            if lists:
                kind, count, style = lists[-1]
                count += 1
                lists[-1][1] = count
                if kind == "enumerate":
                    if style == "fullwidth-paren":
                        prefix = f"（{count}）"
                    elif style == "halfwidth-paren":
                        prefix = f"({count})"
                    else:
                        prefix = f"{count}. "
                else:
                    prefix = "- "
            else:
                prefix = "- "
            md.append(prefix + inline(rest, labels))
            i += 1
            continue

        # ---- 独立签字行 ----
        m = re.search(
            r"\\tjformsignature(?:\[[^\]]*\])?\{([^}]*)\}\{[^}]*\}", s
        )
        if m and not lists:
            md.extend(
                [
                    f"**{inline(m.group(1))}：**________________　　　　年　　月　　日",
                    "",
                ]
            )
            i += 1
            continue

        # ---- 普通段落 ----
        text = inline(s, labels)
        if text:
            md.append(text)
            md.append("")
        i += 1

    return md


# --------------------------------------------------------------------------- #
# 封面与文档头
# --------------------------------------------------------------------------- #
def cover_markdown(name: str, meta: dict) -> list[str]:
    out = [
        "## 封面信息",
        "",
        "> 封面字段来自 `latex/chapters/metadata.tex`；改封面信息请改该文件，"
        "不要只改本镜像。",
        "",
        "| 项目 | 内容 |",
        "| --- | --- |",
    ]
    if name == "taskbook":
        rows = [
            ("课题名称", meta["title"]),
            ("副标题", "（无）"),
            ("学院", meta["school"]),
            ("专业", meta["major"]),
            ("学生姓名", meta["student_name"]),
            ("学号", meta["student_id"]),
            (
                "起讫时间",
                f"自 {meta['period_start']}至 {meta['period_end']}，共 {meta['period_weeks']} 周",
            ),
            ("指导教师签名", "（手写）"),
            ("教学院长签名", "（手写）"),
        ]
    else:
        rows = [
            ("课题名称", meta["title"]),
            ("副标题", "（无）"),
            ("学院", meta["school"]),
            ("专业", meta["major"]),
            ("学生姓名", meta["student_name"]),
            ("学号", meta["student_id"]),
            ("日期", "年　月　日（封面留空，手写）"),
        ]
    for k, v in rows:
        out.append(f"| {k} | {v} |")
    out.append("")
    return out


def header_markdown(name: str, cfg: dict) -> list[str]:
    tex_name = cfg["tex"].name
    return [
        "<!--",
        f"  本文件是《{cfg['title']}》的可编辑 Markdown 镜像，与 LaTeX 版逐段对应。",
        f"  由 scripts/tex2md.py 从 latex/chapters/{tex_name} 生成；",
        "  封面信息取自 latex/chapters/metadata.tex。",
        "  改稿约定见 AGENTS.md 第 7 节：先改本文件，再同步 tex；tex 改动后重新运行本脚本。",
        "  校验：python scripts/tex2md.py --check",
        "-->",
        "",
    ]


def build_markdown(name: str) -> str:
    cfg = DOCS[name]
    meta = read_metadata()
    lines = strip_comments(cfg["tex"].read_text(encoding="utf-8").splitlines())
    labels = scan_labels(lines)
    body = convert(lines, labels)
    out = header_markdown(name, cfg) + [f"# {cfg['title']}", ""]
    out += cover_markdown(name, meta)
    out += body
    if name == "taskbook":
        out += [
            "<!--",
            "  说明：官方任务书表格的“审核意见”栏（指导教师意见 / 教研室意见 / 学院意见）",
            "  由学院另行签署，LaTeX 版按模板未排入正文；如需补填，见",
            "  latex/chapters/taskbook_body.tex 末尾注释。",
            "-->",
            "",
        ]
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text


# --------------------------------------------------------------------------- #
# 校验与入口
# --------------------------------------------------------------------------- #
def check(name: str) -> bool:
    cfg = DOCS[name]
    want = build_markdown(name)
    have = cfg["md"].read_text(encoding="utf-8") if cfg["md"].exists() else ""
    if want == have:
        print(f"[OK] {cfg['md'].relative_to(ROOT)} 与 {cfg['tex'].name} 同步")
        return True
    print(f"[DIFF] {cfg['md'].relative_to(ROOT)} 与 {cfg['tex'].name} 不一致：")
    want_lines = want.splitlines()
    have_lines = have.splitlines()
    for idx in range(max(len(want_lines), len(have_lines))):
        a = want_lines[idx] if idx < len(want_lines) else "<文件结束>"
        b = have_lines[idx] if idx < len(have_lines) else "<文件结束>"
        if a != b:
            print(f"  首个差异在第 {idx + 1} 行：")
            print(f"    tex 生成: {a[:160]}")
            print(f"    现有 md : {b[:160]}")
            break
    print("  处理：先按改稿方向同步 tex 或 md，再运行 python scripts/tex2md.py")
    return False


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="LaTeX 正文 <-> Markdown 镜像生成与校验")
    parser.add_argument("names", nargs="*", choices=sorted(DOCS), help="只处理指定文档")
    parser.add_argument("--check", action="store_true", help="只校验，不写文件")
    args = parser.parse_args(argv)

    names = args.names or list(DOCS)
    if args.check:
        ok = all(check(name) for name in names)
        return 0 if ok else 1

    for name in names:
        cfg = DOCS[name]
        text = build_markdown(name)
        cfg["md"].parent.mkdir(parents=True, exist_ok=True)
        with open(cfg["md"], "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"[OK] {cfg['tex'].relative_to(ROOT)} -> {cfg['md'].relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
