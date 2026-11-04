"""校验 docs/paper-notes/ 下的 9 篇精读 HTML 是否满足写作规范。

用法：
    python scripts/check_paper_notes.py            # 校验已存在的文件
    python scripts/check_paper_notes.py --strict   # 缺文件也算失败

检查项：
  1. 文件齐全（--strict）
  2. 共享 CSS 块与 _template.html 逐字节一致
  3. 十个 section（id=s1..s10）齐全且顺序正确
  4. 无残留占位符（{{…}} / 此处放 / 组件示例注释）
  5. 无外部资源（http(s):// 出现在 src/href/link 中）
  6. 至少 1 个内联 SVG + 1 个数据表
  7. 至少 3 处页码引用
  8. 汉字数在区间内（A/B 簇 2000–3500，C 簇 2000–7500，见规范第二节例外说明）
  9. data-cluster 取值正确
 10. 翻页链接指向的文件存在
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "docs" / "paper-notes"
TEMPLATE = DIR / "_template.html"

PAPERS = [
    ("01-swe-bench.html", "b", "SWE-bench"),
    ("02-swe-agent.html", "b", "SWE-agent"),
    ("03-openhands.html", "b", "OpenHands"),
    ("04-codeact.html", "a", "CodeAct"),
    ("05-metagpt.html", "a", "MetaGPT"),
    ("06-chatdev.html", "a", "ChatDev"),
    ("07-noworkflow.html", "c", "noWorkflow"),
    ("08-msr-survey.html", "c", "MSR Survey"),
    ("09-resumption.html", "c", "Resumption"),
]

CJK = re.compile(r"[\u4e00-\u9fff]")
STYLE_BLOCK = re.compile(r"<style>(.*?)</style>", re.S)
PLACEHOLDER = [
    re.compile(r"\{\{.*?\}\}"),
    re.compile(r"此处放"),
    re.compile(r"组件示例：写完"),
    re.compile(r"\{\{图说明\}\}"),
]
EXTERNAL = re.compile(
    r"""(?:src|href|data-src)\s*=\s*["'](?:https?:)?//""", re.I
)


def cjk_count(html: str) -> int:
    body = re.sub(r"<style.*?</style>", "", html, flags=re.S)
    body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
    body = re.sub(r"<svg.*?</svg>", "", body, flags=re.S)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    body = re.sub(r"<[^>]+>", "", body)
    return len(CJK.findall(body))


def check_one(name: str, cluster: str, label: str, tpl_css: str) -> list[str]:
    errs: list[str] = []
    path = DIR / name
    if not path.exists():
        return [f"{name}: 文件不存在"]
    html = path.read_text(encoding="utf-8", errors="replace")

    # 1. CSS 一致性
    m = STYLE_BLOCK.search(html)
    if not m:
        errs.append("缺少 <style> 块")
    elif m.group(1).strip() != tpl_css.strip():
        errs.append("共享 CSS 块与模板不一致（请整块从 _template.html 复制）")

    # 2. 章节
    ids = re.findall(r'<section id="s(\d+)"', html)
    expect = [str(i) for i in range(1, 11)]
    if ids != expect:
        errs.append(f"section 顺序/数量不对：得到 {ids}，应为 s1..s10")

    # 3. 占位符
    for pat in PLACEHOLDER:
        hits = pat.findall(html)
        if hits:
            errs.append(f"残留占位符 {len(hits)} 处：{hits[:3]}")

    # 4. 外部资源
    ext = EXTERNAL.findall(html)
    if ext:
        errs.append(f"存在外部资源引用 {len(ext)} 处")

    # 5. 组件
    if html.count("<svg") < 1:
        errs.append("没有内联 SVG 示意图")
    if "<table" not in html:
        errs.append("没有数据表")

    # 6. 页码引用
    refs = re.findall(r"p\.\s?(\d{1,3})", html)
    if len(refs) < 3:
        errs.append(f"页码引用只有 {len(refs)} 处（至少 3 处）")
    for r in refs:
        n = int(r)
        if n < 1 or n > 130:
            errs.append(f"页码 {n} 不合理")

    # 7. 字数。A/B 簇按 2000–3500；C 簇（溯源与人因）是本课题的理论根基，
    #    三篇分别对应"溯源断裂/信息分散/上下文丢失"，需要更充分的原文证据与论证，
    #    故上限放宽到 7500（见 _writing-guide.md 第二节的字数例外说明）。
    n = cjk_count(html)
    lo, hi = (2000, 3500) if cluster != "c" else (2000, 7500)
    if n < lo - 200:
        errs.append(f"正文汉字仅 {n}，偏少（下限 {lo - 200}，目标 {lo}–{hi}）")
    elif n > hi:
        errs.append(f"正文汉字 {n}，偏多（目标 {lo}–{hi}）")

    # 8. cluster
    cm = re.search(r'<body data-cluster="([abc])"', html)
    if not cm:
        errs.append("body 缺少 data-cluster")
    elif cm.group(1) != cluster:
        errs.append(f"data-cluster 应为 {cluster}，实际 {cm.group(1)}")

    # 9. 翻页链接存在性
    for href in re.findall(r'<a href="([^"#]+\.html)"', html):
        if href == "index.html":
            continue
        if not (DIR / href).exists():
            errs.append(f"翻页链接指向不存在的文件：{href}")

    return errs


def main() -> int:
    if not TEMPLATE.exists():
        print(f"缺少模板：{TEMPLATE}")
        return 2
    tpl_css = STYLE_BLOCK.search(TEMPLATE.read_text(encoding="utf-8")).group(1)
    strict = "--strict" in sys.argv

    total_err = 0
    missing = 0
    print(f"{'文件':24s} {'汉字':>6s}  状态")
    print("-" * 74)
    for name, cluster, label in PAPERS:
        if not (DIR / name).exists():
            missing += 1
            print(f"{name:24s} {'-':>6s}  ○ 未生成")
            if strict:
                total_err += 1
            continue
        errs = check_one(name, cluster, label, tpl_css)
        n = cjk_count((DIR / name).read_text(encoding="utf-8", errors="replace"))
        print(f"{name:24s} {n:6d}  {'✓ 通过' if not errs else '✗ ' + str(len(errs)) + ' 项问题'}")
        for e in errs:
            print(f"    · {e}")
        total_err += len(errs)

    print("-" * 74)
    if missing:
        print(f"未生成 {missing} 篇" + ("（--strict 计为失败）" if strict else ""))
    print("全部通过 ✓" if total_err == 0 else f"共 {total_err} 项问题 ✗")
    return 0 if total_err == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
