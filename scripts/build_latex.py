#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""构建 latex/ 下的两份行政表格 PDF，并归档到 deliverables/。

用法（在工作区根目录）：
    python scripts/build_latex.py            # 构建 taskbook + proposal
    python scripts/build_latex.py proposal   # 只构建其中一份
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LATEX_DIR = ROOT / "latex"
DELIVERABLES = ROOT / "deliverables"

# 入口文件 -> 归档文件名
TARGETS = {
    "taskbook": "毕业设计任务书-latex-v6-20261103.pdf",
    "proposal": "毕业设计开题报告-latex-v11-20261112.pdf",
}

LATEXMK_ARGS = [
    "-xelatex",
    "-interaction=nonstopmode",
    "-file-line-error",
    "-halt-on-error",
]


def build(name: str) -> bool:
    entry = f"{name}.tex"
    print(f"\n=== 构建 {entry} ===")
    proc = subprocess.run(
        ["latexmk", *LATEXMK_ARGS, entry],
        cwd=LATEX_DIR,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if proc.returncode != 0:
        print(proc.stdout[-4000:])
        print(f"[FAIL] {entry} 编译失败（退出码 {proc.returncode}）")
        return False

    log = (LATEX_DIR / f"{name}.log").read_text(encoding="utf-8", errors="replace")
    problems = [
        line
        for line in log.splitlines()
        if any(
            key in line
            for key in (
                "Missing character",
                "Undefined control sequence",
                "LaTeX Warning: Reference",
                "LaTeX Warning: Citation",
                "! LaTeX Error",
            )
        )
    ]
    if problems:
        print("[WARN] 日志中的问题行：")
        for line in problems[:20]:
            print("   ", line.strip())
    else:
        print("[OK] 日志无缺字、无未定义引用")

    pdf = LATEX_DIR / f"{name}.pdf"
    if not pdf.exists():
        print(f"[FAIL] 未生成 {pdf}")
        return False

    DELIVERABLES.mkdir(exist_ok=True)
    dst = DELIVERABLES / TARGETS[name]
    shutil.copy2(pdf, dst)
    print(f"[OK] {pdf.name} -> {dst.relative_to(ROOT)}")
    return True


def main(argv: list[str]) -> int:
    names = argv[1:] or list(TARGETS)
    unknown = [n for n in names if n not in TARGETS]
    if unknown:
        print(f"未知目标：{unknown}；可选：{list(TARGETS)}")
        return 2
    results = [build(name) for name in names]
    failed = [n for n, ok in zip(names, results) if not ok]
    if failed:
        print(f"\n失败：{failed}")
        return 1
    print("\n全部完成。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
