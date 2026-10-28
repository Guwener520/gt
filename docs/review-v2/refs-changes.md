# 参考文献著录统一说明（GB/T 7714-2015 顺序编码制）

- **对象**：`thesis/proposal.md` 第十二节「主要参考文献」全部 **44 条**（原 L293—L336）
- **产物**：`docs/review-v2/refs-fixed.md`（44 条新文本，编号与顺序与原文件完全一致，未重排、未增删、未改编号）
- **依据**：① `docs/review-v2/04-形式与语言.md`「文献著录问题」节（逐条核查表 + D05/D23）；② GB/T 7714-2015；③ 本次任务给定的统一体例
- **约束声明**：**未修改** `thesis/proposal.md` 本体，未触碰 `deliverables/`、`scripts/`、`thesis/figures/`

---

## 一、总览

| 项 | 数量 | 说明 |
| --- | --- | --- |
| 文献总数 | 44 | 编号 [1]—[44]，顺序与原文件逐条一致（脚本核验） |
| **改动条目** | **27** | [1][3][4][5][6][14][15][17][18][21][22][23][24][25][26][28][29][30][33][34][36][37][38][39][40][42][44] |
| 未改动条目 | 17 | 其中 15 条原本合规，2 条缺项（[9][41]）按"不补"原则原样保留 |
| 类型分布（未变） | `[C]` 21、`[EB/OL]` 12、`[J]` 10、`[M]//` 1 | 与评审统计一致，无类型误标（[41] 见第五节） |
| 按问题类型计（一条可计多类） | 格式类 **25 条/25 处**；著录错误类 **3 条/3 处** | 二者重叠 1 条（[17]），净改动 27 条 |

**格式类 25 条**＝19 条删会议录名括注（[1][3][4][5][6][14][15][17][18][21][22][23][24][25][26][28][29][30][34]）＋6 条团体责任者大小写（[36][37][38][39][40][44]）。
**著录错误类 3 条**＝[17] 会议录名缺"Proceedings of the"、[33] 会议录名序数词/年份位置错、[42] 出版者名错（Taylor and Francis → Taylor & Francis）。

---

## 二、本次实际执行的统一体例

| # | 规则 | 依据 |
| --- | --- | --- |
| R1 | 期刊：`作者. 题名[J]. 刊名, 年, 卷(期): 起止页. DOI: 10.xxxx/yyyy.` | GB/T 7714-2015 第 8 章连续出版物析出文献 |
| R2 | 会议：`作者. 题名[C]//会议录名. 年: 起止页. DOI: xxx.`；**出版地、出版者一律省略**，并在文献表首行声明 | 本次统一体例（GB/T 7714-2015 对会议文献本要求"出版地: 出版者"，此处为消除"21 条 [C] 全缺出版地"的不一致而整类省略，属须在文首声明的体例约定） |
| R3 | 会议录名后括注的会议缩写与年份（如 `(ICLR 2024)`、`(CHI 2010)`）一律删除 | 会议录名著录正式名称；年份已在"出版年"位置著录，括注年份与之重复（评审 04 已列 5 处重复，本表按同一规则处理全部 19 条，避免"有的有、有的无"） |
| R4 | 团体责任者按原名著录，不作全大写：`Anthropic.` `Cursor.` `Cline.` `Langfuse.` `OpenTelemetry.` `Tree-sitter.` | GB/T 7714-2015 责任者著录；评审 04 第 D23 条（个人著者"姓全大写"与团体著者全大写视觉混淆） |
| R5 | 作者：≤3 人全列；>3 人列前 3 人后加 `et al.`（英文）/`等`（中文）；英文姓全大写、名缩写不加点 | GB/T 7714-2015 §4.1；44 条全部符合，无需改动 |
| R6 | 文献类型标识紧贴题名，`[J]. ` `[C]//` `[EB/OL]. ` 后接续著录项；每条以半角 `.` 收尾；页码用半角连字符 | GB/T 7714-2015 §4.4、§8 |
| R7 | 电子资源：`责任者. 题名[EB/OL]. (发布日期)[引用日期]. URL.`；引用日期统一 `[2026-10-27]` | GB/T 7714-2015 §8.8；`AGENTS.md` 5.3 |
| R8 | DOI 写作 `DOI: 10.xxxx/yyyy.`（冒号后**一个空格**） | 依本次"具体统一为"条 `DOI: 10.xxxx/yyyy.`，并与原稿、评审基线"DOI 统一 `DOI: 10.xxxx`"（已核 ✅）保持一致。若学院模板要求冒号后不留空格，可对全文做一次替换 `DOI: ` → `DOI:`，不影响其他著录项 |

---

## 三、逐条改动（27 条）

> "原写法/新写法"只截取**被改动的片段**（`…` 表示省略的未变部分），便于核对；完整新文本见 `refs-fixed.md`。

| 编号 | 原写法 | 新写法 | 依据条款 |
| --- | --- | --- | --- |
| [1] | `…Learning Representations (ICLR 2024). 2024. arXiv: 2310.06770.` | `…Learning Representations. 2024. arXiv: 2310.06770.` | R3；GB/T 7714-2015 §8.4 会议录名著录正式名称 |
| [3] | `…Neural Information Processing Systems 37 (NeurIPS 2024). 2024.` | `…Neural Information Processing Systems 37. 2024.` | R3 |
| [4] | `…Learning Representations (ICLR 2025). 2025.` | `…Learning Representations. 2025.` | R3 |
| [5] | `…Machine Learning (ICML 2024). 2024.` | `…Machine Learning. 2024.` | R3 |
| [6] | `…Learning Representations (ICLR 2024). 2024.` | `…Learning Representations. 2024.` | R3 |
| [14] | `…Computing Systems (CHI 2024). 2024: 1-16.` | `…Computing Systems. 2024: 1-16.` | R3 |
| [15] | `…Communications Security (CCS 2023). 2023: 2785-2799.` | `…Communications Security. 2023: 2785-2799.` | R3 |
| [17] | `[C]//CHI Conference on Human Factors in Computing Systems Extended Abstracts (CHI EA 2022). 2022: 1-7.` | `[C]//Proceedings of the CHI Conference on Human Factors in Computing Systems Extended Abstracts. 2022: 1-7.` | **著录错误**：会议录名缺"Proceedings of the"（其余 20 条 `[C]` 均有），GB/T 7714-2015 §8.4；另删括注（R3，格式） |
| [18] | `…Software Repositories (MSR 2005). 2005: 1-5.` | `…Software Repositories. 2005: 1-5.` | R3 |
| [21] | `…Automated Software Engineering (ASE 2014). 2014: 313-324.` | `…Automated Software Engineering. 2014: 313-324.` | R3 |
| [22] | `…Software Engineering (ICSE 2021). 2021: 1510-1522.` | `…Software Engineering. 2021: 1510-1522.` | R3 |
| [23] | `…Foundations of Software Engineering (FSE 2006). 2006: 1-11.` | `…Foundations of Software Engineering. 2006: 1-11.` | R3 |
| [24] | `…Intelligent User Interfaces (IUI 2005). 2005: 75-82.` | `…Intelligent User Interfaces. 2005: 75-82.` | R3 |
| [25] | `…Automated Software Engineering (ASE 2015). 2015: 864-869.` | `…Automated Software Engineering. 2015: 864-869.` | R3 |
| [26] | `…Software Engineering (ICSE 2010). 2010: 125-134.` | `…Software Engineering. 2010: 125-134.` | R3 |
| [28] | `…Computing Systems (CHI 2010). 2010: 93-102.` | `…Computing Systems. 2010: 93-102.` | R3 |
| [29] | `…Collaborative Research (CASCON 2007). 2007: 229-243.` | `…Collaborative Research. 2007: 229-243.` | R3 |
| [30] | `…Program Comprehension (ICPC 2007). 2007: 155-166.` | `…Program Comprehension. 2007: 155-166.` | R3 |
| [33] | `[C]//Proceedings of the 2025 IEEE 21st International Conference on e-Science. 2025.` | `[C]//Proceedings of the 21st IEEE International Conference on e-Science. 2025.` | **著录错误**：序数词/主办方/年份位置与全篇 20 条 `[C]` 体例不一致，且年份与出版年重复；GB/T 7714-2015 §8.4 + §4.1 一致性原则。**页码未补**（见第五节） |
| [34] | `…Computing Systems (CHI 2004). 2004: 151-158.` | `…Computing Systems. 2004: 151-158.` | R3 |
| [36] | `ANTHROPIC. Claude Code documentation: overview[EB/OL].` | `Anthropic. Claude Code documentation: overview[EB/OL].` | R4；GB/T 7714-2015 责任者著录；评审 04 D23 |
| [37] | `CURSOR. Cursor documentation[EB/OL].` | `Cursor. Cursor documentation[EB/OL].` | R4 |
| [38] | `CLINE. Cline: AI coding, open source and open choice[EB/OL].` | `Cline. Cline: AI coding, open source and open choice[EB/OL].` | R4 |
| [39] | `LANGFUSE. Observability overview[EB/OL].` | `Langfuse. Observability overview[EB/OL].` | R4 |
| [40] | `OPENTELEMETRY. Generative AI semantic conventions[EB/OL].` | `OpenTelemetry. Generative AI semantic conventions[EB/OL].` | R4 |
| [42] | `London: Taylor and Francis, 1996: 189-194.` | `London: Taylor & Francis, 1996: 189-194.` | **著录错误**：出版者正式名称为 Taylor & Francis，GB/T 7714-2015 §4.2 出版者按正式名称著录 |
| [44] | `TREE-SITTER. Tree-sitter documentation[EB/OL].` | `Tree-sitter. Tree-sitter documentation[EB/OL].` | R4；按 GitHub 组织名 "Tree-sitter" 著录，**未**添加"项目组"等原文没有的限定语 |

---

## 四、未改动条目（17 条）及原因

| 编号 | 状态 | 说明 |
| --- | --- | --- |
| [2] [8] [10] [13] [32] [43] | 已合规，未改 | `[EB/OL]`：责任者. 题名[EB/OL]. (发布日期)[引用日期]. URL. 六项齐备，与 R7 一致 |
| [7] [16] [19] [20] [27] [31] [35] | 已合规，未改 | `[J]`：刊名, 年, 卷(期): 起止页. DOI. 结构完整（[20] 该刊无期号，`166: 93-109` 保留）。[7] 评审原以"缺出版地/出版者"记缺陷，本次按 R2 整类省略并在文首声明，故不再构成缺陷 |
| [11] [12] | **原样保留，逐字未动** | 两条中文文献的作者（3 人 + 等）、刊名、年、卷(期)、起止页、DOI 全部保留；`，`/`：`/`．` 已为半角 `, ` `: ` `.`，与 R1/R5/R6 一致，无需改动 |
| [9] | 缺项，未补 | 期刊条目缺起止页/文章号：保留 `2024, 33(8).` 原样，**未臆造页码**（第五节） |
| [41] | 缺项，未改类型 | 类型标识存疑（Advances in Psychology 第 52 卷系丛书卷，宜作 `[M]//` 析出），但补正须补书名、编者、出版地、出版者，均属原文没有的信息，按"不补"原则暂留 `[J]`（第五节给出建议文本，供作者核实后采用） |

---

## 五、缺项未补清单（一律未补，供作者核实）

| 编号 | 缺项 | 本次处理 |
| --- | --- | --- |
| [1] [3] [4] [5] [6] [33] | 会议论文集起止页 | 只著录出版年，arXiv 号置于条目末尾；**未补页码**（未查得原论文集页码，不臆造） |
| [9] | 期号后的起止页/文章号 | 保留 `2024, 33(8).`；标注"**缺项，未补**"（须查 ACM DL 原页） |
| [17] | 页码 `1-7` 疑为文章号 | 原样保留，标注"页码待核实，未补" |
| [33] | 会议论文集起止页 | 同 [1]，未补 |
| [36] [37] [38] [39] [40] [44] | 更新/发布日期 | 省略 `(发布日期)`，仅保留 `[2026-10-27]`；标注"**缺项，未补**"。注：与 [2][8][10][13][32][43] 的 `(日期)[引用日期]` 体例不完全一致，若须完全一致，只能由作者核实各文档的更新日期后补入 |
| [41] | 析出文献的书名、编者、出版地、出版者 | 未补，故类型标识仍为 `[J]`。**建议文本（待作者核实后采用，勿直接采信）**：`HART S G, STAVELAND L E. Development of NASA-TLX (Task Load Index): results of empirical and theoretical research[M]//HANCOCK P A, MESHKATI N. Human Mental Workload. Amsterdam: North-Holland, 1988: 139-183.`——书名、编者、出版地、出版者均取自评审 04 文件 [41] 条建议，其自身已标"待核实" |

---

## 六、与评审意见 `04-形式与语言.md` 的四点差异（需 Lead 决策）

| # | 评审建议 | 本次做法 | 理由 |
| --- | --- | --- | --- |
| 1 | 21 条 `[C]` 补"出版地: 出版者"（如 `New York: ACM`、`Piscataway: IEEE`） | **整类省略**，并在文献表首行声明 | 任务给定体例："会议文献统一写作 `[C]//会议名. 年: 页码.`（省略出版地与出版者，并在文首声明）"。省略可一次性消除 21 条的不一致，且不必逐条判定 ACM/IEEE/PMLR 的出版地 |
| 2 | 6 条带 arXiv 号的 `[C]` 改著录为 `[EB/OL]` + arXiv URL | **保留 `[C]//`**，arXiv 号置于条目末尾 | 任务给定体例："会议论文若同时有 arXiv，保留会议信息、arXiv 号放末尾"。**遗留风险**：这 6 条仍无页码，评审 D05 的"类型标识与实际依据不符"只解决了一半；若 Lead 采纳评审方案，整条改 `[EB/OL]` 即可 |
| 3 | [41] 改 `[M]//` 并补书名、编者、出版者 | **暂留 `[J]`**，建议文本见第五节 | 补正须补原文没有的信息，与"不得补原文没有的信息"直接冲突；留待作者核实 |
| 4 | [36]—[40][44] 补发布日期 | **省略**（缺项未补） | 无法核实各文档更新日期，不得编造；文首说明只声明了会议与引用日期两项 |

---

## 七、文首说明与插入方式

`refs-fixed.md` 第 1 行为（原样插入「十二、主要参考文献」标题之后、`[1]` 之前）：

```
（说明：会议文献按 GB/T 7714-2015 著录，出版地与出版者从略；网络资源引用日期统一为 2026-10-27。）
```

插入时建议：该行用与文献表相同的字号（五号）、左对齐、不设悬挂缩进，`[1]`—`[44]` 保持悬挂缩进 0.85 cm 不变。

---

## 八、机器核验结果

| 检查项 | 结果 |
| --- | --- |
| 条目数 | 44（与原文一致） |
| 编号序列 | `1,2,…,44` 严格连续、无重号、无跳号、顺序与原文逐条对应 |
| 每条前缀 | 全部匹配 `^\[\d+\] ` |
| 每条收尾 | 全部以半角 `.` 结束 |
| 非 ASCII 破折号/弯引号 | 0 处（页码全为半角 `-`） |
| 连续空格、标点前空格 | 0 处 |
| DOI 写法 | 25 条含 DOI，统一 `DOI: 10.xxxx/…`（冒号后一个空格，见 R8） |
| 类型标识紧贴题名 | 0 处 `题名 [J]` 式空格 |
| 类型分布 | `[C]` 21、`[EB/OL]` 12、`[J]` 10、`[M]//` 1（与原文一致，未改类型） |
| 改动条目数 | 27（逐字比对，大小写敏感） |

---

*整理：文献著录统一任务｜2026-10-28*
