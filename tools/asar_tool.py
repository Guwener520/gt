#!/usr/bin/env python
"""只读 asar 工具：列出 / 提取 / 全文检索 DSH 打包内容。

用途：DSH 以 app.asar 形式分发（D:\\DSH\\resources\\app.asar），插件 API 的
真实形态只能从包内 TypeScript 定义与源码确认。本工具不写回 asar。

用法：
    python tools/asar_tool.py list   [--grep PATTERN] [--limit N]
    python tools/asar_tool.py cat    <asar内路径> [--max-bytes N]
    python tools/asar_tool.py extract <asar内路径前缀> --out DIR
    python tools/asar_tool.py search <正则> [--ext .ts,.js,.md] [--limit N]

示例：
    python tools/asar_tool.py list --grep "/dsh/.*plugin"
    python tools/asar_tool.py cat /dsh/package.json
    python tools/asar_tool.py search "export interface .*Plugin" --ext .ts
"""

import argparse
import json
import os
import re
import struct
import sys

DEFAULT_ASAR = r"D:\DSH\resources\app.asar"


def open_asar(path):
    f = open(path, "rb")
    f.seek(8)
    struct.unpack("<I", f.read(4))[0]  # pickle payload size
    json_len = struct.unpack("<I", f.read(4))[0]
    header = json.loads(f.read(json_len).decode("utf-8"))
    # 数据区起点 = 8 + pickle_size(4) + 4 + json_len，按 Chromium Pickle 对齐到 4 字节
    base = 8 + 4 + 4 + json_len
    base = (base + 3) & ~3
    return f, header, base


def walk(node, prefix="", out=None):
    if out is None:
        out = []
    for name, v in node.get("files", {}).items():
        p = prefix + "/" + name
        if "files" in v:
            walk(v, p, out)
        else:
            out.append((p, v.get("size", 0), v.get("offset", 0), v.get("unpacked", False)))
    return out


def read_entry(f, base, entry):
    path, size, offset, unpacked = entry
    if unpacked:
        raise SystemExit(f"{path} 标记为 unpacked，请直接读 app.asar.unpacked 目录")
    f.seek(base + int(offset))
    return f.read(size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "cat", "extract", "search"])
    ap.add_argument("target", nargs="?", default="")
    ap.add_argument("--asar", default=DEFAULT_ASAR)
    ap.add_argument("--grep", default="")
    ap.add_argument("--ext", default="")
    ap.add_argument("--limit", type=int, default=80)
    ap.add_argument("--max-bytes", type=int, default=200000)
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    f, header, base = open_asar(a.asar)
    entries = walk(header)
    by_path = {e[0]: e for e in entries}

    if a.cmd == "list":
        pat = re.compile(a.grep) if a.grep else None
        rows = [e for e in entries if (not pat or pat.search(e[0]))]
        for p, size, _, unpacked in rows[: a.limit]:
            print(f"{size:>10}  {'U' if unpacked else ' '}  {p}")
        print(f"# matched {len(rows)} / total {len(entries)}", file=sys.stderr)

    elif a.cmd == "cat":
        e = by_path.get(a.target) or by_path.get("/" + a.target.lstrip("/"))
        if not e:
            print(f"not found: {a.target}", file=sys.stderr)
            sys.exit(2)
        data = read_entry(f, base, e)
        sys.stdout.write(data[: a.max_bytes].decode("utf-8", "replace"))

    elif a.cmd == "extract":
        if not a.out:
            sys.exit("extract 需要 --out DIR")
        pre = a.target.rstrip("/")
        rows = [e for e in entries if e[0].startswith(pre)]
        for e in rows:
            dest = os.path.join(a.out, e[0].lstrip("/").replace("/", os.sep))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            try:
                with open(dest, "wb") as w:
                    w.write(read_entry(f, base, e))
            except SystemExit as ex:
                print(f"skip {e[0]}: {ex}", file=sys.stderr)
        print(f"extracted {len(rows)} files under {pre} -> {a.out}")

    elif a.cmd == "search":
        pat = re.compile(a.target)
        exts = tuple(x.strip() for x in a.ext.split(",") if x.strip()) if a.ext else None
        hits = 0
        for e in entries:
            if exts and not e[0].endswith(exts):
                continue
            if e[1] > 2_000_000:
                continue
            try:
                text = read_entry(f, base, e).decode("utf-8", "replace")
            except SystemExit:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if pat.search(line):
                    print(f"{e[0]}:{i}: {line.strip()[:240]}")
                    hits += 1
                    if hits >= a.limit:
                        print(f"# stopped at limit {a.limit}", file=sys.stderr)
                        return
        print(f"# {hits} hits", file=sys.stderr)


if __name__ == "__main__":
    main()
