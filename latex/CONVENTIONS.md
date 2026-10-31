# latex/ 正文改写约定（两份行政表格共用）

本文件是 `chapters/proposal_body.tex` 与 `chapters/taskbook_body.tex` 的写作规范。
两份文件各由一人负责，互不重叠；本约定必须严格遵守，否则两份文档版式会不一致。

## 0. 事实前提

- 模板：TongjiThesis v1.5.1，`style/` **一律不改**。类已加载 float / booktabs / tabularx /
  longtable / caption / subcaption / enumitem[inline] / newunicodechar / underscore。
- 编译环境：TeX Live 2026，XeLaTeX + latexmk，`fontset=windows`（宋体/黑体）。
- 内容源稿（**唯一内容来源，不得增删论点、不得改写数据**）：
  - 开题报告：`../thesis/proposal.md`（v3 定稿，13 节 + 摘要 + 44 篇文献）
  - 任务书：`../thesis/task-book.md`（8 节 + 18 篇文献）
- Word 版成品（用于核对文字）：`../deliverables/毕业设计开题报告-v3-20261028.pdf`、
  `../deliverables/毕业设计任务书-v1-20261027.pdf`

## 1. 可用排版命令（不要手写字号/字族）

| 命令 | 用途 | 视觉 |
| --- | --- | --- |
| `\tjformsection{一、……}` | 一级小节（官方表格的“一、二、三、四/五、六”） | 四号黑体，缩进 2 字符 |
| `\tjformsubsection{1．……}` | 二级小节（官方表格的“1．2．3．”，全角句点“．”） | 小四黑体 |
| `\tjformsubsub{（一）……}` | 三级小节（原稿的“（一）（二）”，本课题新增） | 小四宋体加粗 |
| `\tjformsecnum{n}` | 图表编号接管，紧跟在一级小节标题之后单独一行 | 无输出 |
| `\begin{tjreviewbox} … \end{tjreviewbox}` | 审核意见方框 | 带框 |
| `\tjformlabel{指导教师意见：}` | 审核框内的字段标签 | 小四黑体 |
| `\tjformsignature[字号]{标签}{下划线宽度}` | 右对齐签字行 | 黑体 |
| `\tjformhint{…}` / `\tjformnote{…}` | **仅供审核框内的模板原文提示语**，正文一律不用 | 灰色 |

正文中“（1）（2）”这类条目引导句用行内加粗：`\textbf{（1）开发任务过程的信息模型与统一事件表示。}` + 正文。

## 2. 图表

- 编号由 `\tjformsecnum{n}` 接管：图/表编号形如 `图 2-1`、`表 2-3`（n = 所在小节号）。
  **每个一级小节标题后必须调用一次**（摘要节除外），否则编号会串到上一节。
- 正文交叉引用一律 `\ref`：写“如图~\ref{fig:route} 所示”“见表~\ref{tab:metrics}”，
  **不要**写“如图 6-1”（原稿编号已失效），也**不要**用 `\cref`（会出英文名）。
- 表题在上、图题在下，由 `\caption` 在 `table`/`figure` 环境内自动处理。
- 短表：`\begin{table}[H]\centering\begin{tabularx}{\linewidth}{...}` + `\toprule/\midrule/\bottomrule`，
  表内字号由类自动设为五号。
- 长表（可能跨页，如评价指标表、风险表、进度表）：`longtable`，在 `\endhead` 首行写
  `\tjlongtablecont{列数}` 生成“续表”行；列宽用 `p{...}` 固定，必要时 `\small`。
- 图：`\begin{figure}[htbp]\centering\includegraphics[width=\linewidth]{figures/fig1-route.png}`，
  caption 在 figure 内、图之下。三张图已就位：fig1-route.png、fig2-arch.png、fig3-gantt.png。

## 3. 参考文献（直录，不用 .bib）

- 两份行政表格的参考文献**照录源稿定稿文本**，不建 .bib、不用 `\cite`。
  理由：源稿 44/18 条已逐条核验（DOI、卷期、页码），直录可确保与已审定的 Word 版完全一致，
  并避免转录误差；模板对该栏的要求只是“悬挂缩进 0.74cm、与正文参考文献格式一致”，
  由 `tj-extras.tex` 提供的 `tjreflist` 环境满足。
- 写法：

  `\begin{tjreflist}`
  `\item JIMENEZ C E, YANG J, WETTIG A, et al. SWE-bench: can language models resolve real-world GitHub issues?[C]//Proceedings of the 12th International Conference on Learning Representations. 2024. arXiv: 2310.06770.`
  `\end{tjreflist}`

  每条一个 `\item`，条目文本照抄源稿（含 `[C]//`、`[J]`、`[EB/OL]`、`(2021-07-07)[2026-10-27]` 等标记），
  不删不改，不要手工加 `[1]` 序号（环境自动编号）。
- 顺序必须与源稿完全一致（源稿按首次引用编号），序号自动生成为 [1]…[n]。
- 正文引用保持源稿的 `[n]`、`[n,m]`、`[n-m]` 字面写法，不要改成 `\cite`、不要加空格。
- 源稿文献表前的“（说明：会议文献按 GB/T 7714-2015 著录……）”一句保留在列表之前（原稿即如此）。
- 不得新增、删减、改写任何文献条目。

## 4. 字符与标点

- 中文标点用全角；引号用“”，破折号用——，间隔号用·（原稿即如此，照抄）。
- `→ ≥ ≤ − κ Δ ⁶` 等符号**按原稿直书**，已在 `chapters/tj-extras.tex` 中映射为数学符号，
  不要手写 `$\rightarrow$`。
- 下划线直书（`metric_coverage.py`、`.gitattributes` 等），已加载 underscore 宏包，**不要**写成 `\_`。
- 百分比、单位、英文缩写照原稿；不要引入新的术语译名。

## 5. 禁止事项

1. 不改 `style/`、不改 `chapters/metadata.tex`、不改入口 `.tex`、不改 `tj-extras.tex`（Lead 负责）。
2. 不增删论点、不改数字、不新造文献。
3. 不用 `\tjformnote`/`\tjformhint` 包裹正文（会变灰），审核框内的模板提示语除外。
4. 不写 `\chapter`/`\section`（会打乱表格版式与编号）。
5. 不在正文里出现“请在此处填写……”“（此项成稿删除）”等模板占位语。

## 6. 自检（提交前必须做）

```powershell
cd latex
latexmk -xelatex -interaction=nonstopmode -file-line-error -halt-on-error proposal.tex   # 或 taskbook.tex
Select-String -Path proposal.log -Pattern 'Missing character|Undefined control sequence|LaTeX Warning: Reference|Overfull \\hbox' | Select-Object -First 20
pdfinfo proposal.pdf | Select-String '^Pages:'
```

要求：编译 0 error；无 Missing character；无未定义引用；Overfull hbox 超过 10pt 的必须处理。
