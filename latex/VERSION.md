# TongjiThesis 模板版本记录

| 项 | 值 |
| --- | --- |
| 上游仓库 | https://github.com/TJ-CSCCG/TongjiThesis |
| 版本 | v1.5.1 |
| 提交 | 96185a724e8719a7cc506bf321c8060b188d8bca |
| 取用日期 | 2026-10-31 |
| 许可证 | LPPL-1.3c（见 LICENSE） |

## 目录说明

- `style/`：文档类与字体定义，**保持上游原样，不做任何修改**（升级只需整体替换本目录）。
- `chapters/`：正文。本课题改写的是 `proposal_body.tex`（开题报告）与 `taskbook_body.tex`（任务书）；
  `metadata.tex` 为封面信息（两份表格共用）；`tj-extras.tex` 为本课题新增的本地补充宏；
  其余 `00_abstract`/`01_guide`…`06_conclusion`/`ack`/`appendix` 为模板演示内容，待论文写作时替换。
- `figures/`：`tongji.pdf`/`tongji-header.pdf` 为模板徽标（三份表格封面与页眉必需）；
  `fig1-route.png`/`fig2-model.png`/`fig3-gantt.png` 由 `scripts/make_figures.py` 生成。
- `bib/note.bib`：模板示例文献库，仅 `main.tex`（论文正文）使用；两份行政表格的参考文献为直录列表，见下。

## 取用方式（可复现）

```powershell
git -c http.sslBackend=openssl clone --depth 1 --branch v1.5.1 https://github.com/TJ-CSCCG/TongjiThesis.git "$env:TEMP\tongjithesis-v1.5.1"
```

> 本机 `raw.githubusercontent.com` 与 curl/pwsh 的 TLS 通道不可用（`SEC_E_NO_CREDENTIALS`），
> 需以 `git -c http.sslBackend=openssl` 走 OpenSSL 后端访问 GitHub。

复制到本目录时排除：`.git`、`.github`、`scripts/`、`package.json`、`release-please*`、`_config.yml`、
`CLAUDE.md`、`CONTRIBUTING.md`、`SECURITY.md`、`CHANGELOG.md`、`README-EN.md`；
上游 `AGENTS.md` 另存为 `UPSTREAM-AGENTS.md`（模板架构与贡献约定，供查阅）。

## 本地改动清单（与上游的差异）

1. 入口 `proposal.tex`/`taskbook.tex`：类选项设为
   `degree=bachelor, field=science, biblatex=true, fontset=windows`，并在导言区
   `\input{chapters/tj-extras}`。
2. 新增 `chapters/tj-extras.tex`：特殊字符映射、下划线直书、图表编号接管、三级标题、
   参考文献列表环境 `tjreflist`、开题报告摘要开关。
3. 改写 `chapters/metadata.tex`（封面信息）与两个 body 文件（正文内容）。
4. 新增 `figures/fig1-route.png`、`fig2-model.png`、`fig3-gantt.png`（复制自 `thesis/figures/`）。
5. 删除上游 `figures/tongjithesis.png|svg`（1.9 MB 预览图，正文不使用）。
6. 页眉页脚按学院 Word 表格补齐：开题报告加页眉「本科毕业设计（论文）开题报告」+ 页脚页码，
   任务书只有页脚页码（`tjformhead`/`tjformplain` 两个 fancypagestyle）；封面页仍为空。
   同时把 `\footskip` 收窄到 15pt——类文件给表格设了 `bottom=1.0cm`，默认 30pt 的页脚会被
   推到纸张边缘之外、页码被裁掉。
7. 参考文献列表用五号 + 单倍行距（与 Word 定稿 10.5pt 一致），正文仍为小四。

## 参考文献为何是直录列表

两份行政表格的参考文献照录已逐条核验的定稿文本（`thesis/proposal.md`、`thesis/task-book.md`
是 body 的可编辑 Markdown 镜像，二者逐条一致），用 `tjreflist` 环境排版（悬挂缩进 0.74cm、
序号左对齐至页边距），**不建 .bib、不用 biblatex**：

- 模板对该栏的要求只是“悬挂缩进 0.74cm，与正文参考文献格式一致”，并未要求文献数据库；
- 直录可保证与已审定的 Word 版逐字一致，避免 44+18 条书目在转录中引入作者/卷期/页码误差
  （工作区规范：参考文献不得编造，须真实可查）；
- 若改用 biblatex(GB/T 7714-2025)，载体会由 `[J]` 变 `[J/OL]`、`[C]` 变 `[C/OL]`，
  会议论文的 `arXiv: xxxx.xxxxx` 注记会被丢弃，与已提交版本差异较大。

论文正文（`main.tex`）仍走 biblatex + `bib/note.bib`，写作时再建论文自己的文献库。

## 字体

默认 `fontset=windows`（系统宋体/黑体，与学院 Word 模板一致）。换机器若无 Windows 中文字体，
把入口文件的 `fontset=windows` 改为 `fontset=fandol`（随 TeX Live 分发）即可，其余不用改。

## 构建

```powershell
# 在 latex/ 目录下（latexmkrc 的 TEXINPUTS 相对于工作目录，必须在此目录执行）
latexmk -xelatex proposal.tex
latexmk -xelatex taskbook.tex
# 或在工作区根目录用脚本一次构建并归档到 deliverables/
python scripts/build_latex.py

# 生成 / 校验可编辑 Markdown 镜像（thesis/task-book.md、thesis/proposal.md）
python scripts/tex2md.py
python scripts/tex2md.py --check
```
