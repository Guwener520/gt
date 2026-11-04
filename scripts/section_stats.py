"""逐节统计精读页汉字数，用于判断超长页面该压哪一节。

用法：python scripts/section_stats.py 09-resumption.html [更多文件...]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "docs" / "paper-notes"
CJK = re.compile(r"[\u4e00-\u9fff]")


def cjk(html: str) -> int:
    html = re.sub(r"<style.*?</style>", "", html, flags=re.S)
    html = re.sub(r"<script.*?</script>", "", html, flags=re.S)
    html = re.sub(r"<svg.*?</svg>", "", html, flags=re.S)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    html = re.sub(r"<[^>]+>", "", html)
    return len(CJK.findall(html))


def main() -> None:
    names = sys.argv[1:] or ["09-resumption.html"]
    for name in names:
        path = DIR / name
        src = path.read_text(encoding="utf-8", errors="replace")
        print(f"\n=== {name}  总计 {cjk(src)} 汉字 ===")
        # 按 section 切
        parts = re.split(r'(<section id="s(\d+)"[^>]*>)', src)
        # parts: [前, 开标签, id, 内容, 开标签, id, 内容...]
        i = 1
        while i < len(parts) - 1:
            sid = parts[i + 1]
            chunk = parts[i + 2]
            h2 = re.search(r"<h2[^>]*>(.*?)</h2>", chunk, re.S)
            title = re.sub(r"<[^>]+>", "", h2.group(1)).strip() if h2 else "?"
            print(f"  s{sid:<3s} {cjk(chunk):5d}  {title}")
            i += 3
        # 页头
        head = src.split('<main class="wrap">')[0]
        print(f"  hero  {cjk(head):5d}  (页头 + 页脚)")


if __name__ == "__main__":
    main()
