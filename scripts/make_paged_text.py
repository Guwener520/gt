"""把 refs/pdfs 抽取出的纯文本转为带页标记的版本，便于精读时精确标注「原文 p.N」。

用法：
    python scripts/make_paged_text.py

输入：.work/papers/txt/<slug>.txt   （由 pdftotext -layout -enc UTF-8 生成，用 \f 分页）
输出：.work/papers/paged/<slug>.paged.txt   （每页前插入 === [PAGE N] ===）
"""

from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / ".work" / "papers" / "txt"
DST = ROOT / ".work" / "papers" / "paged"


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    for src in sorted(SRC.glob("*.txt")):
        raw = src.read_text(encoding="utf-8", errors="replace")
        pages = raw.split("\f")
        if pages and pages[-1].strip() == "":
            pages = pages[:-1]
        out: list[str] = []
        for i, page in enumerate(pages, start=1):
            body = re.sub(r"\n{3,}", "\n\n", page).strip("\n")
            out.append(f"\n===== [PAGE {i}] =====\n{body}\n")
        dst = DST / f"{src.stem}.paged.txt"
        dst.write_text("".join(out), encoding="utf-8")
        print(f"{src.stem}: {len(pages)} pages -> {dst.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
