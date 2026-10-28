# Trae 插件形态可行性取证报告

> 取证方式：仅查阅公开官方文档，未安装 Trae、未写代码、未运行验证。检索日期：2026-10-28。
> 入口：`docs.trae.cn`（官方中文文档站）、`www.trae.cn`（下载页）；`www.trae.ai` 为 JS 渲染、正文未取到。
> 说明：本会话搜索引擎不可用，**未取得社区实测帖旁证**；官方未写明处一律标注"未检索到官方说明"。

---

## 一、结论

**评级：C（作为"Trae 插件"形态不可行）。若降级为"Trae Hook 采集源 + 独立 Web 界面"，可评为 B。**

1. TRAE IDE 官方文档全量导航中**不存在"扩展开发 / 插件 SDK / 发布 / 开发者平台"任何条目**，2026-10-28 未检索到官方插件开发文档，故该形态**本身不存在**。
2. Trae 基于 VS Code 内核且支持安装 VS Code 扩展（含 `.vsix` 导入），故实质等价于**"VS Code 扩展 + 宿主兼容性风险"**，该风险被官方 FAQ 明文承认。
3. 唯一实质价值在**官方 Hook 机制**：六类事件、stdin 传 JSON、含 `tool_input`/`tool_response`，与 Claude Code Hook 同名同构，可复用既有采集方案。

---

## 二、核心判定：Trae 是否开放插件开发

### a) 是否基于 VS Code —— **是**

更新日志以"内核升级"记载：v0.3.5（2025-04-01）"升级 VS Code 内核至 1.98.2 版本"；v2.8.0（2025-10-14）"升级 VSCode 内核至 1.104"。官方未用"fork"字样，但"内核"表述已足证其为 VS Code 衍生宿主。来源：`https://docs.trae.cn/ide_changelog`（访问 2026-10-28）。

### b) 是否支持安装 VS Code 扩展 —— **是（有专门文档，两种装法）**

《扩展市场》首句："你可以从 TRAE 或 VS Code 的扩展市场安装扩展，或直接将本地的 .vsix 文件导入至 TRAE。"三条路径：Trae 扩展市场搜索安装；从 VS Code Marketplace 手工拼链接下载后拖入；"··· > 从 VSIX 安装"。来源：`https://docs.trae.cn/ide_manage-extensions`（访问 2026-10-28）。

### c) 是否有插件 SDK / 扩展 API / 开发者平台，能否发布 —— **否，未检索到**

文档全量导航共 12 个一级分区（入门、教程、AI 编程核心、Agent 窗口、SOLO、工具与扩展、开发环境、系统设置、会员、活动、排查、协议），其下 40 余篇文档**无一篇涉及"扩展开发""插件 SDK""发布""开发者平台"**；《扩展市场》全文只讲安装与导入。判定：**不存在面向第三方的插件开发与发布通道**（未检索到官方说明）。

两处易混概念均**不是**"Trae 插件开发"：

- **TRAE Plugin**（独立分区 `plugin_*`）：官方称其为"AI 编程助手……支持 VSCode、JetBrains 系列以及 Android Studio"，即**把 Trae 的 AI 能力装进别人的 IDE**，方向相反。来源：`https://docs.trae.cn/plugin_what-is-trae-plugin`（访问 2026-10-28）。
- **插件市场**（`/ide_marketplace`）：此处"插件"是"MCP Server + Skill"封装的 **AI 能力组件**，装后在输入框用 `/` 调用，属**消费侧**，无开发发布说明（v3.3.97 上线）。来源：`https://docs.trae.cn/ide_marketplace`、`https://docs.trae.cn/ide_changelog`（访问 2026-10-28）。

### d) 只支持"安装"不支持"开发发布" —— **结论成立：Trae 路线 = VS Code 扩展路线 + 宿主兼容风险**

《扩展市场》"常见问题"原文："若 VS Code 扩展市场中某个版本的扩展依赖了新版 VS Code 中的某些接口，则可能会导致该扩展与 TRAE 不兼容。"这是**官方书面承认的宿主兼容性风险**，并印证内核版本漂移。来源：`https://docs.trae.cn/ide_manage-extensions`（访问 2026-10-28）。

### e) MCP 与 Rules/Hook 能否替代插件 —— **MCP 不能；Hook 能替代"采集"，不能替代 UI**

MCP 被官方限定为"智能体作为 MCP 客户端……以使用它们提供的工具"——**只提供工具，不提供 UI，不订阅宿主事件**，无法承担三视图与事件采集；Rules 是提示词约束，更不可能。

**Hook 可以**：官方给出六类事件 `SessionStart`/`UserPromptSubmit`/`PreToolUse`/`PostToolUse`/`Stop`/`Notification`，在事件节点"运行自定义 Shell 命令"，并将"该事件的 JSON 上下文"经 stdin 传给处理程序。故 **Hook 可替代采集职责（优于扩展 API：拿到的是语义化工具调用），但不能替代 UI 承载**，三视图只能落在 Trae 之外的独立进程或扩展 webview 中。来源：`https://docs.trae.cn/ide_automate-actions-with-hooks`（访问 2026-10-28）。

---

## 三、逐项分析（8 问）

### 1. 形态与运行环境

现为"三端（桌面/网页/移动）+ 双形态（Agent 窗口/IDE 窗口）+ 双模式（IDE/SOLO）"。版本线 v0.1.0（2025-03-03）至 v3.4.4（2026-10-15），约 20 个月 100+ 次发布。Windows 支持：下载页列"Windows 10, 11（x64）"、macOS 12.0+。**需账号登录**：下载页"下载登录即送 2500 积分"，导航含"登录"；计费以积分为核心。来源：`https://docs.trae.cn/ide_what-is-trae-code`、`https://www.trae.cn/download`、`https://docs.trae.cn/ide_changelog`（访问 2026-10-28）。

### 2. 事件可见性

| 事件 | 判定 | 依据 |
| --- | --- | --- |
| 对话消息 | **部分** | `UserPromptSubmit.stdin.prompt` 得用户输入；`Stop.stdin.last_assistant_message` 只给**最终**输出，中间消息与推理无事件；"导出历史对话"（v3.3.41）属人工操作 |
| 工具调用及参数 | **能** | `PreToolUse`/`PostToolUse` 提供 `tool_use_id`、`tool_name`、`llm_tool_name`、`tool_input`；工具名有标准枚举（`Read`/`Write`/`Edit`/`RunCommand`/`Skill`/`mcp__<server>__<tool>` 等），`matcher` 可正则筛选 |
| 文件变更含 hunk | **部分** | 无独立 hunk 事件。`Edit` 的 `tool_input` 是"旧串→新串"查找替换，**非 unified diff**，须自行归一化（正合开题报告第 162 行六步归一化） |
| 终端命令 | **能（含输出）** | `RunCommand` 为标准工具名，命令与结果分在 `tool_input`/`tool_response`。限制：v3.3.24&3.3.25"命令不记录在终端的历史中"，**不能靠 shell history 兜底** |
| 测试运行结果 | **部分** | 无 TestRun 事件；测试经 `RunCommand` 执行，结果仅文本，须自行解析退出码 |
| git 状态 | **部分** | 无 git 类工具，只能经 `RunCommand` 执行 `git`，或扩展侧旁路采集 |
| 落盘与存储位置 | **部分/未证实** | 仅 Hook 配置路径公开（`%userprofile%/.trae-cn/hooks.json`、`.trae/hooks.json`），Hook 日志退出后清空。**会话库位置未检索到官方说明** |

来源：`https://docs.trae.cn/ide_hook-configuration-reference`、`https://docs.trae.cn/ide_automate-actions-with-hooks`、`https://docs.trae.cn/ide_changelog`（访问 2026-10-28）。

### 3. UI 承载力

webview **可用**：v0.3.0（2025-03-17）"修复了 Webview 插件 IPv4、IPv6 端口占用冲突的问题"；但 v3.3.42"部分依赖 Worker 能力的插件无法启动"说明兼容缺口仍在。**Trae 自有 UI 不可扩展**：未检索到面向第三方的对话面板扩展点或 API，三视图只能落 webview 侧栏或独立窗口，**无法嵌入对话流**——而"证据侧栏与对话并列"正是本课题的交互主张。来源：`https://docs.trae.cn/ide_changelog`、`https://docs.trae.cn/ide_manage-extensions`（访问 2026-10-28）。

### 4. 存储

扩展宿主随内核而来，理论为 Node.js，可装 SQLite 类包；但原生模块（如 `better-sqlite3`）需按宿主 Electron ABI 重编译，**未检索到官方关于宿主 ABI 的说明**，属未证实风险。更稳的落库位在 **Hook 侧**：Hook 是独立 Shell 进程（Windows 默认 PowerShell），可用任意语言直连 SQLite，绕开 ABI 问题。Trae 自身数据目录格式**未检索到官方说明**（官方仅承诺隐私模式下代码保存在本地）。

### 5. 开发与分发成本

**不需要绕过市场限制**：官方支持从 VS Code Marketplace 手工下载 `.vsix` 后拖入，或"··· > 从 VSIX 安装"，即 **sideload 是官方一等路径**（v0.5.10 起），自建分发无需审核。**官方 SDK 不存在**（见二·c），"走官方 SDK"分支不成立。净成本等于做一个 VS Code 扩展。来源：`https://docs.trae.cn/ide_manage-extensions`（访问 2026-10-28）。

### 6. 稳定性与生态

更新极密（100+ 次发布），宿主行为与内核版本持续漂移。插件生态规模**未检索到官方数字**（仅有"插件热榜"等榜单页，非规模统计）。文档完整度**高**：Hook 有完整 stdin/stdout 字段表、退出码语义与配置 schema。**闭源**（未检索到公开源码仓库），FAQ 已承认接口不兼容可能，**API 不可依赖**。

### 7. 离线演示可行性

**不可行（智能体链路）**。模型全为云端内置或 API Key 接入的远端模型（官方"AI 编程能力—模型"段），无本地模型；使用以积分计费、需登录账号。答辩机无网时**无法运行智能体，也就没有事件可采**。可缓解：用 `fixtures/` 回放已采集事件演示三视图，但"现场跑一个任务"不可实现。来源：`https://docs.trae.cn/ide_what-is-trae-code`、`https://www.trae.cn/download`（访问 2026-10-28）。

### 8. 与开题报告契合度

现表述为"界面限定为 Web 形态的三个核心视图……IDE 插件列为可选"（第 99 行），采集来源已定 Claude Code（钩子与 stream-json）与 OpenHands（事件文件离线解析）（第 174 行），工作量表已"不做 IDE 插件 −5 人日"（第 236 行）。改 Trae 需动 **4 处**：第 99 行范围边界改口径；第 174 行采集方案（**关键**——新增第三来源则实验规模与标注量需重算）；第 236 行撤回"−5 人日"，缺口再扩大；第 224 行"采集侧接口形态差异"段补一条。

**但采集方案不必重写**：Trae Hook 与 Claude Code Hook **同名同构**（同样六事件、同样读 `~/.claude/settings.json`、同样注入 `CLAUDE_PROJECT_DIR`、官方支持导入 Claude 配置），**适配器可复用**，只需加变体并记录字段差异。

**改动量：中等偏小。**落点是 Hook 而非插件；但**"Trae 插件"在论文中无法成立**，只能表述为"Trae 事件采集适配器"。来源：`thesis/proposal.md`（第 99、162、174、224、236 行）、`https://docs.trae.cn/ide_automate-actions-with-hooks`、`https://docs.trae.cn/ide_hook-configuration-reference`（访问 2026-10-28）。

---

## 四、关键证据清单

| 结论 | 依据（原文要点） | 来源 URL | 访问日期 |
| --- | --- | --- | --- |
| Trae 基于 VS Code 内核 | 日志："升级 VS Code 内核至 1.98.2 / 1.100.3 / 1.104" | https://docs.trae.cn/ide_changelog | 2026-10-28 |
| 支持安装 VS Code 扩展（含 sideload） | "可以从 TRAE 或 VS Code 的扩展市场安装扩展，或直接将本地的 .vsix 文件导入"；"··· > 从 VSIX 安装" | https://docs.trae.cn/ide_manage-extensions | 2026-10-28 |
| 官方承认宿主兼容风险 | "依赖了新版 VS Code 中的某些接口，则可能会导致该扩展与 TRAE 不兼容" | https://docs.trae.cn/ide_manage-extensions | 2026-10-28 |
| 无插件 SDK / 开发者平台 | 12 分区、40 余篇文档无相关条目；扩展市场文档无"发布"节 | https://docs.trae.cn/ide_what-is-trae-code ；https://docs.trae.cn/ide_manage-extensions | 2026-10-28 |
| "TRAE Plugin"≠插件开发 | "TraeCode Plugin……支持 VSCode、JetBrains、Android Studio"（方向相反） | https://docs.trae.cn/plugin_what-is-trae-plugin | 2026-10-28 |
| "插件市场"≠代码扩展 | 插件为"MCP Server + Skill"封装的 AI 能力组件；v3.3.97 上线 | https://docs.trae.cn/ide_marketplace ；https://docs.trae.cn/ide_changelog | 2026-10-28 |
| Hook 提供六类事件与 JSON 上下文 | "将该事件的 JSON 上下文传递给你的 Hook 处理程序"；v3.3.66 上线 | https://docs.trae.cn/ide_automate-actions-with-hooks ；https://docs.trae.cn/ide_changelog | 2026-10-28 |
| Hook 输入含工具名/参数/结果 | `tool_name`、`tool_input`、`tool_response`；枚举含 `Edit`/`RunCommand`/`mcp__*` | https://docs.trae.cn/ide_hook-configuration-reference | 2026-10-28 |
| Hook 与 Claude Code 同构可复用 | 读 `~/.claude/settings.json`、"导入 CLAUDE 中的 Hooks 配置"、注入 `CLAUDE_PROJECT_DIR` | https://docs.trae.cn/ide_hook-configuration-reference | 2026-10-28 |
| 终端历史不含 AI 命令；webview 曾有问题 | v3.3.24&3.3.25"命令不记录在终端的历史中"；v0.3.0 修 Webview 端口冲突、v3.3.42 修 Worker 类插件 | https://docs.trae.cn/ide_changelog | 2026-10-28 |

> 未取得项：社区实测帖旁证、插件生态规模、会话数据落盘格式、扩展宿主 ABI、国际站文档正文。

---

## 五、风险与不可行点

1. **形态不存在（决定性）**：无 SDK、无开发者平台、无发布通道；只能退化为"VS Code 扩展 + 宿主兼容风险"。
2. **宿主兼容风险已被官方承认**：内核版本漂移，依赖新接口的扩展可能不兼容。
3. **自有 UI 不可扩展**：三视图无法嵌入对话面板，"证据侧栏与对话并列"在 Trae 内无法实现。
4. **闭源 + 高频迭代**：内部行为不可依赖；会话格式不公开。
5. **测试与 git 无一等事件**：`TestRun`/`TestCaseResult` 只能从 `RunCommand` 文本解析，与开题报告信息模型有语义落差。
6. **必须登录联网**：答辩机无网时无法现场运行智能体，只能 `fixtures/` 回放。
7. **证据边界**：本机未安装 Trae，结论全来自文档，未做运行时验证。

**建议**：论文中不采用"Trae 插件"表述。若引入 Trae，正确表述是"Trae 事件采集适配器（基于官方 Hook）"，与 Claude Code 适配器共用管线；三视图仍置于 Web 形态，改动可压缩到三处。
