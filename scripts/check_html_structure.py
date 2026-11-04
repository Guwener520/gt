"""HTML 结构体检：标签闭合、外部资源、汉字数、SVG/表格数量。

用法：python scripts/check_html_structure.py [文件...]
不给参数时检查 docs/paper-notes/ 下所有 html。
"""

from __future__ import annotations

import html.parser
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "docs" / "paper-notes"

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
    # SVG 自闭合元素
    "path", "circle", "rect", "line", "stop", "use", "polygon", "polyline",
    "ellipse", "marker",
}


class P(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.err: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.err.append(f"多余闭合 </{tag}>")
            return
        if self.stack[-1] == tag:
            self.stack.pop()
        else:
            # 容忍中间被误判的自闭合
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.err.append(f"未闭合 <{self.stack.pop()}>（在 </{tag}> 之前）")
                if self.stack:
                    self.stack.pop()
            else:
                self.err.append(f"闭合不匹配：期望 </{self.stack[-1]}>，得到 </{tag}>")


def cjk(html: str) -> int:
    body = re.sub(r"<style.*?</style>", "", html, flags=re.S)
    body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
    body = re.sub(r"<svg.*?</svg>", "", body, flags=re.S)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    body = re.sub(r"<[^>]+>", "", body)
    return len(re.findall(r"[\u4e00-\u9fff]", body))


def check(path: Path) -> int:
    src = path.read_text(encoding="utf-8", errors="replace")
    p = P()
    p.feed(src)
    problems = list(p.err)
    if p.stack:
        problems.append(f"未闭合标签：{p.stack[:6]}")

    ext = re.findall(r'(?:src|href|data-src)\s*=\s*["\'](?:https?:)?//', src, re.I)
    if ext:
        problems.append(f"外部资源引用 {len(ext)} 处")

    svgs = len(re.findall(r"<svg", src))
    tables = len(re.findall(r"<table", src))
    n = cjk(src)

    status = "✓" if not problems else "✗"
    print(f"{status} {path.name:26s} 汉字={n:5d} svg={svgs} table={tables}")
    for pr in problems:
        print(f"    · {pr}")
    return len(problems)


def main() -> int:
    if len(sys.argv) > 1:
        files = [Path(a) for a in sys.argv[1:]]
    else:
        files = sorted(DIR.glob("*.html"))
    total = 0
    for f in files:
        total += check(f)
    print("-" * 60)
    print("结构全部通过 ✓" if total == 0 else f"共 {total} 项结构问题 ✗")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
