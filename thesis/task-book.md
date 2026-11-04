<!--
  本文件是《本科毕业设计（论文）任务书》的可编辑 Markdown 镜像，与 LaTeX 版逐段对应。
  由 scripts/tex2md.py 从 latex/chapters/taskbook_body.tex 生成；
  封面信息取自 latex/chapters/metadata.tex。
  改稿约定见 AGENTS.md 第 7 节：先改本文件，再同步 tex；tex 改动后重新运行本脚本。
  校验：python scripts/tex2md.py --check
-->

# 本科毕业设计（论文）任务书

## 封面信息

> 封面字段来自 `latex/chapters/metadata.tex`；改封面信息请改该文件，不要只改本镜像。

| 项目 | 内容 |
| --- | --- |
| 课题名称 | 面向代码智能体的开发任务上下文追踪与代码变更溯源系统设计与实现 |
| 副标题 | （无） |
| 学院 | 计算机科学与技术学院 |
| 专业 | 计算机科学与技术 |
| 学生姓名 | 待填写 |
| 学号 | 待填写 |
| 起讫时间 | 自 2026 年 10 月 26 日至 2027 年 5 月 31 日，共 32 周 |
| 指导教师签名 | （手写） |
| 教学院长签名 | （手写） |

## 一、课题背景

代码智能体（code agent）已逐渐应用于日常开发：开发者以自然语言描述任务，由智能体完成代码分析、文件修改、工具调用、测试执行与问题排查。但对话、代码差异、工具调用与测试结果通常分散在不同界面。由此产生三方面问题：一是缺少任务视角，多轮修改、多任务并行与中断重启后难以掌握当前进展；二是修改原因难以回溯，代码因何而改、依据哪次测试验证，需依靠人工查找与回忆；三是中断后上下文丢失，重新开始需重读长对话与大量差异。

本课题面向单个开发者，研究开发任务、对话、代码变更、工具调用与测试结果的关联与组织方法，设计并实现支持任务上下文追踪与变更溯源的原型系统，帮助开发者围绕任务、文件或代码片段查看证据链，并在中断后恢复上下文。

## 二、应完成的主要内容

本课题要求建立开发任务、对话、工具调用、文件变更、测试运行等实体的信息模型，设计统一的事件表示、可扩展的事件模式与存储结构；同时接入至少一种真实代码智能体的事件源，结合 Git 与测试输出采集开发过程数据，研究将异构记录关联到开发任务的方法。

在此基础上，以变更块为粒度生成“变更卡片”，记录触发来源、实施过程、修改前后快照、验证依据与后续演化，支持“代码—原因—证据”的双向查询；实现任务中心、任务时间线与变更证据侧栏三个视图，任务中断后生成任务快照，支持由快照跳转到证据；同时探索利用大语言模型生成任务摘要、整理开发进展（输出须绑定原始证据，证据不足时弃答），并在典型编程任务上与基线方法对比，评估其在代码理解、修改原因分析、问题定位与任务衔接方面的作用。

## 三、基本要求及应完成的成果形式

本课题要求学生完成以下工作：

1. 调研代码智能体、开发过程追踪与变更溯源的研究与产品现状；
2. 设计开发任务、对话、工具调用、文件变更、测试运行等实体的信息模型；
3. 实现任务上下文追踪与变更溯源原型系统，接入真实事件源；
4. 在典型编程任务上开展实验，与基线方法对比并形成可复现数据；
5. 撰写毕业设计论文，说明需求分析、系统设计、实现与评估过程。

<!-- pagebreak -->

成果形式：可运行的原型系统一套（含源代码、部署与使用说明）；毕业设计（论文）一份；系统设计、测试与评估报告，以及实验数据；演示视频与答辩幻灯片。

## 四、进度安排

表 4-1 进度安排

| 序号 | 设计（论文）各阶段名称 | 时间安排（教学周） |
| --- | --- | --- |
| 1 | 文献研究与产品调研 | 1—8 |
| 2 | 关键方法设计与实现 | 9—14 |
| 3 | 系统设计与实现 | 15—20 |
| 4 | 系统验证与测试 | 21—22 |
| 5 | 毕业设计论文撰写 | 23—28 |
| 6 | 论文审阅与修改 | 29—32 |

第 9 周进行开题；时间安排以教学周计，具体以学院通知为准。

## 五、主要参考文献

[1] JIMENEZ C E, YANG J, WETTIG A, et al. SWE-bench: can language models resolve real-world GitHub issues?[C]//Proceedings of the 12th International Conference on Learning Representations (ICLR 2024). 2024. arXiv: 2310.06770.

[2] YANG J, JIMENEZ C E, WETTIG A, et al. SWE-agent: agent-computer interfaces enable automated software engineering[C]//Advances in Neural Information Processing Systems 37 (NeurIPS 2024). 2024. arXiv: 2405.15793.

[3] WANG X, LI B, SONG Y, et al. OpenHands: an open platform for AI software developers as generalist agents[C]//Proceedings of the 13th International Conference on Learning Representations (ICLR 2025). 2025. arXiv: 2407.16741.

[4] WANG X, CHEN Y, YUAN L, et al. Executable code actions elicit better LLM agents[C]//Proceedings of the 41st International Conference on Machine Learning (ICML 2024). 2024. arXiv: 2402.01030.

[5] HONG S, ZHUGE M, CHEN J, et al. MetaGPT: meta programming for a multi-agent collaborative framework[C]//Proceedings of the 12th International Conference on Learning Representations (ICLR 2024). 2024. arXiv: 2308.00352.

[6] QIAN C, LIU W, LIU H, et al. ChatDev: communicative agents for software development[C]//Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics. 2024: 15174-15186. DOI: 10.18653/v1/2024.acl-long.810.

[7] KAGDI H, COLLARD M L, MALETIC J I. A survey and taxonomy of approaches for mining software repositories in the context of software evolution[J]. Journal of Software Maintenance and Evolution: Research and Practice, 2007, 19(2): 77-131. DOI: 10.1002/smr.344.

[8] ROBBES R, LANZA M. A change-based approach to software evolution[J]. Electronic Notes in Theoretical Computer Science, 2007, 166: 93-109. DOI: 10.1016/j.entcs.2006.06.015.

[9] FALLERI J R, MORANDAT F, BLANC X, et al. Fine-grained and accurate source code differencing[C]//Proceedings of the 29th ACM/IEEE International Conference on Automated Software Engineering (ASE 2014). 2014: 313-324. DOI: 10.1145/2642937.2642982.

[10] GRUND F, CHOWDHURY S A, BRADLEY N C, et al. CodeShovel: constructing method-level source code histories[C]//Proceedings of the 43rd International Conference on Software Engineering (ICSE 2021). 2021: 1510-1522. DOI: 10.1109/ICSE43902.2021.00135.

[11] KO A J, MYERS B A. Designing the Whyline: a debugging interface for asking questions about program behavior[C]//Proceedings of the SIGCHI Conference on Human Factors in Computing Systems (CHI 2004). 2004: 151-158. DOI: 10.1145/985692.985712.

[12] CHENEY J, CHITICARIU L, TAN W C. Provenance in databases: why, how, and where[J]. Foundations and Trends in Databases, 2009, 1(4): 379-474. DOI: 10.1561/1900000006.

[13] PIMENTEL J F, MURTA L, BRAGANHOLO V, et al. noWorkflow: a tool for collecting, analyzing, and managing provenance from Python scripts[J]. Proceedings of the VLDB Endowment, 2017, 10(12): 1841-1844. DOI: 10.14778/3137765.3137789.

[14] PARNIN C, RUGABER S. Resumption strategies for interrupted programming tasks[J]. Software Quality Journal, 2011, 19(1): 5-34. DOI: 10.1007/s11219-010-9104-9.

[15] OPENTELEMETRY. Generative AI semantic conventions[EB/OL]. (2026-10-27). https://opentelemetry.io/docs/specs/semconv/gen-ai/.

[16] LANGFUSE. Observability overview[EB/OL]. (2026-10-27). https://langfuse.com/docs/observability/overview.

[17] 张犬俊, 谢杨, 房春荣, 等. 检索增强生成在软件工程中的应用综述[J]. 软件学报, 2026, 37(3): 1316-1339. DOI: 10.13328/j.cnki.jos.007567.

[18] 汪莹, 字千成, 彭鑫, 等. 基于大语言模型的故障复现测试用例生成方法[J]. 软件学报, 2026, 37(4): 1690-1714. DOI: 10.13328/j.cnki.jos.007474.

## 六、其他要求

未尽事宜按学院有关规定执行；课题重大调整须经指导教师同意并记录在案。

**指导教师签名：**________________　　　　年　　月　　日

<!--
  说明：官方任务书表格的“审核意见”栏（指导教师意见 / 教研室意见 / 学院意见）
  由学院另行签署，LaTeX 版按模板未排入正文；如需补填，见
  latex/chapters/taskbook_body.tex 末尾注释。
-->
