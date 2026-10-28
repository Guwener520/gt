# VSCode 扩展形态可行性取证

> 取证日期 2026-10-28。方式：官方文档（code.visualstudio.com、code.claude.com）+ 本机 VS Code 1.130.0（Electron 42.6.0）扩展清单与打包源码。未安装、未运行、未编译任何原型。文档未明示者一律标「未证实」。

## 一、结论

| 维度 | 评级 | 一句话理由 |
| --- | --- | --- |
| (i) 纯扩展独立完成六类事件采集 | **C（不可行）** | 稳定 API 中不存在「观测其他扩展智能体对话/工具调用」的入口，`vscode.chat` 只能「参与」不能「旁观」。 |
| (ii) 扩展 + Agent Hooks 组合采集 | **B（有条件可行）** | VSCode 已内建 agent hooks（**Preview**）并支持 Copilot/Claude/Codex harness，可拿到 prompt 与 `tool_name`/`tool_input`/`tool_response`；但 manifest 无 `contributes.hooks`，需扩展写配置文件引导。 |
| (iii) 三视图 UI 承载力 | **A（充分）** | Webview 视图、面板、编辑器页签三处均可承载 React，消息通信与本地资源机制齐备。 |

三句话：①采集端不能靠扩展 API 观测，只能靠 hooks 或会话日志导入；②展示端恰是扩展最成熟的能力；③故「插件只做展示端」**仅在只用扩展 API 时成立**，扩展 + hooks 时不成立。

## 二、逐项分析

### 2.1 形态与运行环境

扩展宿主是独立进程：桌面版 local 宿主为 **Node.js 运行时**，另有 web/remote 宿主；扩展需 `main` 入口，宿主隔离扩展以保护启动性能与 UI（[Extension Host](https://code.visualstudio.com/api/advanced-topics/extension-host)）。采集端因此可用 Node 全能力（`fs`、`child_process`、SQLite 绑定），与工作区经 `workspace` 命名空间交互，`extensionKind` 决定本地/远端。语言为 TypeScript + 打包。结论：A。

### 2.2 事件可见性（核心判定）

**仅凭扩展 API，不能观测其他扩展（Copilot Chat / Cline / Claude Code）的对话与工具调用。** 依据：①Chat Participant 已 deprecated 且「not supported in the Copilot harness」，迁移文档明言不迁移「history, feedback events」——自始是「被调用」而非「观测」（[Chat participants](https://code.visualstudio.com/api/extension-guides/ai/chat)）；②Language Model API 是「自己发请求」，Language Model Tool 是「提供能力」（[AI extensibility](https://code.visualstudio.com/api/extension-guides/ai/ai-extensibility-overview)）；③唯一跨扩展通道 `getExtension(id)`→`activate()`→`exports` 须对方 activate 返回 API，范例 `getExtension('vscode.typescript-language-features').exports.getAPI(0)`（[Contribution Points](https://code.visualstudio.com/api/references/contribution-points#contributes.typescriptServerPlugins)）；Claude Code 与 ChatGPT 的 manifest 未声明扩展 API（未证实可调用）；④本机 chatgpt manifest 的 `contributes.chatSessions` 不在稳定贡献点列表中（未证实）。

**但** VSCode 2026 已内建 agent hooks（Preview），这是官方观测点；除工具事件外还有 `SessionStart`/`SessionEnd`/`Stop`/`SubagentStart`/`SubagentStop`/`PreCompact`，可用于切分「开发任务」边界。逐项判定：

| 事件类别 | 判定 | 依据（API / 字段） |
| --- | --- | --- |
| 对话消息 | **部分** | 用户提示词：Local `UserPromptSubmit.prompt`、Copilot `userPromptSubmitted`。助手消息无稳定事件，Local 仅给 `transcript_path`（文档注明「not a stable hook API」）；Claude 有 `MessageDisplay`（display-only），入参字段未完整读取（未证实）。兜底：Claude 会话 JSONL 导入（已证实）。 |
| 工具调用及参数 | **能** | `PreToolUse`：`tool_name`、`tool_input`、`tool_use_id`；`PostToolUse` 追加 `tool_response`；Copilot 对应 `preToolUse` 的 `toolName`/`toolArgs`（[Local hooks reference](https://code.visualstudio.com/docs/agents/reference/hooks-reference)）。 |
| 文件变更含 hunk | **部分** | hook 不含 hunk。须用 `workspace.onDidChangeTextDocument`、`onDidSaveTextDocument`、`createFileSystemWatcher` 记快照，再以 git diff 切 hunk；Claude 另有 `FileChanged`（只报文件名）。 |
| 终端命令 | **能（组合）** | hook：Bash/PowerShell 的 `tool_input.command`；编辑器侧 `window.onDidStartTerminalShellExecution`/`onDidEndTerminalShellExecution`（含退出码，需 shell integration，仅 bash/fish/pwsh/zsh/Git Bash）。 |
| 测试运行与结果 | **部分** | Test API 是「提供/发布」侧（`tests.createTestController`），不能旁观他人运行，但支持 publish-only controller 导入外部结果（[Testing API](https://code.visualstudio.com/api/extension-guides/testing)）。实采靠 `tool_response` + 退出码。 |
| git 状态 | **能** | `getExtension('vscode.git').exports.getAPI(1)`；本机 `extensions/git/dist/main.js` 可见 `repositories`、`getRepository(uri)`、`state`。无官方文档页（原 git API 页 404）→ 源码取证。 |

**四问**：A. 扩展能否自带 hook？**部分能**——贡献点列表无 `contributes.hooks`；hook 来源为 `~/.copilot/hooks/`、仓库 `.github/hooks/*.json`、内联 settings、agent plugin、agent frontmatter（[Configure agent hooks](https://code.visualstudio.com/docs/agent-customization/hooks)）；Claude 格式的 settings 文件需 `chat.useClaudeHooks` 打开。扩展可写这些文件并用 settings API 打开 `chat.useHooks`/`chat.hookFilesLocations` 实现零手工配置，但官方未把 VSIX 扩展列为 hook 来源（未证实）。B. 覆盖见上表；C. 与编辑器事件互补：是；D. 评级见第一节。

**Claude 扩展与 CLI 的关系（已证实）**：文档称「The extension and CLI share the same conversation history」，hooks「fire the same hook events wherever it runs: sessions in the terminal, IDE extensions, the Desktop app」（[vs-code](https://code.claude.com/docs/en/vs-code)、[hooks](https://code.claude.com/docs/en/hooks)）。本机印证：`~/.claude/projects/<项目>/<uuid>.jsonl` 含 user/assistant/tool_use/tool_result、`sessionId`、`cwd`、`gitBranch`。

### 2.3 UI 承载力

三处容器：`window.createWebviewPanel`（页签）、`WebviewView`+`registerWebviewViewProvider`（侧栏/面板）、custom editor；webview 是受控 iframe，「can render almost any HTML content」，靠 `postMessage`/`onDidReceiveMessage` 通信（[Webview API](https://code.visualstudio.com/api/extension-guides/webview)）。建议：时间线放页签或面板，证据侧栏放侧栏 WebviewView，恢复视图复用页签。React 可行。本地资源须经 `asWebviewUri` 转换、受 `localResourceRoots` 限制，模板需声明 CSP（`webview.cspSource`）。限制：webview 开销大，且不能改原生 UI。

### 2.4 存储

五条路（[Common Capabilities](https://code.visualstudio.com/api/extension-capabilities/common-capabilities)）：`globalState`/`workspaceState`（键值，不适合万级事件）、`globalStorageUri`/`storageUri`（本地目录，适合放 SQLite 文件）、`secrets`（加密凭据）。SQLite：`better-sqlite3` 为原生模块，须匹配宿主 ABI（本机 Code 1.130.0 / Electron 42.6.0），并按平台打包（`vsce package --target win32-x64`，官方「平台特定扩展」节）；原「Using Native Node Modules」页已 404，最新指引**未证实**。备选 `sql.js`（WASM，零 ABI，需自行落盘）。写入侧建议单事务批量插入 + `(task_id, ts)` 索引，1 万事件量级满足 P95<1s 属设计推断（未实测）。离线：全本地。

### 2.5 开发与分发成本

`yo code` 脚手架 → `vsce package` 生成 `.vsix` → `code --install-extension xxx.vsix` 或 Extensions 视图「Install from VSIX」；市场发布可选，需 publisher + PAT/Entra，文档未要求签名。`engines.vscode` 控制兼容（本机 1.130.0；Claude 扩展要求 ^1.94.0）。离线更新即手工换 vsix（[Publishing Extensions](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)）。成本：低。

### 2.6 稳定性与生态

| API | 状态 | 来源 |
| --- | --- | --- |
| `activationEvents` | 稳定（1.74 起多数贡献点隐式激活） | [Activation Events](https://code.visualstudio.com/api/references/activation-events) |
| `workspace.onDidChangeTextDocument`、`createFileSystemWatcher` | 稳定 | Testing API 示例使用 |
| `workspace.onDidSaveTextDocument` | 稳定 | 本机 claude `extension.js` 使用 |
| `window.onDidStart/onDidEndTerminalShellExecution` | 稳定 | 本机 claude `extension.js` 使用 |
| `tests.createTestController` | 稳定（1.59+） | Testing API |
| `extensions.getExtension(...).exports` | 稳定 | API 参考 `#extensions.getExtension` |
| Webview API | 稳定 | Webview API |
| `ExtensionContext.secrets/globalState/globalStorageUri` | 稳定 | Common Capabilities |
| `vsce package` | 稳定工具 | Publishing Extensions |
| Agent hooks | **Preview** | hooks 页首「in Preview」 |
| Chat Participant | **deprecated** | Chat participants 页 |
| `contributes.chatSessions` | 未文档化（未证实） | 本机 chatgpt manifest |

Proposed API 仅存于 Insiders 且不应发布（[Using Proposed API](https://code.visualstudio.com/api/advanced-topics/using-proposed-api)），本方案不依赖。生态：扩展社区最大，`yo code`/`vsce` 文档完整；宿主兼容由 `engines.vscode` 声明，需自行覆盖 1.94–1.130 的 API 差异。

### 2.7 离线演示可行性

能：`.vsix` 离线安装是文档路径；webview 走本地资源，扩展本身无需联网。hook 脚本需解释器：官方示例要求本机 Node，可改用 PowerShell/CMD。风险：hooks 为 Preview，跨版本可能变；答辩机若无 Copilot/Claude 会话则无事件源，必须备 `fixtures/` 回放。

### 2.8 与开题报告契合度

现文「界面限定为 Web 三视图，IDE 插件列为可选」。改此形态需动五处：四(四) 研究边界（约 250 字）、六(二)(三) 技术路线与架构（约 500 字，且**图 6-2 须重绘**：采集端由「Web 前端 + Node 服务」改为「扩展宿主 + hooks 桥 + webview」）、表 7-1 载体（1 行）、九 创新点（约 120 字）。合计约 900 字改写 + 1 图重绘 ≈ **1–1.5 人日**。契合度：与「必做：至少一种真实智能体事件接入」高度契合，把「可选」升为主载体反增创新点，但须写明「不做多 IDE 适配」。

## 三、关键证据清单

| 结论 | 依据 | 来源 |
| --- | --- | --- |
| 扩展不能观测他人对话/工具调用 | 弃用声明 + 无历史/事件导出 | https://code.visualstudio.com/api/extension-guides/ai/chat |
| 跨扩展只走 exports | `getExtension().exports.getAPI(0)` 范例 | https://code.visualstudio.com/api/references/contribution-points#contributes.typescriptServerPlugins |
| hooks 是官方观测点 | 事件字段表 + `transcript_path` 不稳定声明 | https://code.visualstudio.com/docs/agents/reference/hooks-reference |
| hooks 为 Preview、扩展无该贡献点 | 页首标注；贡献点列表无 `hooks` | https://code.visualstudio.com/docs/agent-customization/hooks ；https://code.visualstudio.com/api/references/contribution-points |
| Claude 扩展与 CLI 共享会话与 hooks | 原句见 2.2 | https://code.claude.com/docs/en/vs-code ；https://code.claude.com/docs/en/hooks |
| 会话 JSONL 结构 | tool_use/sessionId/cwd/gitBranch | 本机 `C:\Users\32511\.claude\projects` |
| git 与终端事件可用 | `getAPI(1).repositories`；Start/EndTerminalShellExecution | 本机 `D:\Microsoft VS Code\1b6a188127\resources\app\extensions\git\dist\main.js`；`…\.vscode\extensions\anthropic.claude-code-2.1.220-win32-x64\extension.js` |

## 四、风险与不可行点

1. **硬约束**：纯扩展无「旁观」API，助手消息正文拿不到（仅 transcript 文件，非稳定格式）。
2. hooks 为 Preview，字段/事件名可能变；Local harness 已标 Legacy 并迁移至 Copilot harness，有二次迁移成本。
3. hook 是可执行代码，受企业策略（`chat.useHooks`、`allowManagedHooksOnly`）与工作区信任约束，演示环境需预置。
4. 原生 SQLite 有 ABI/平台包问题：答辩机须锁定 win32-x64，换机即失效。
5. 只覆盖装了对应智能体扩展的会话；Cline 本机未装，其 hook 兼容性未证实。

## 五、若选此形态的实施要点

模块：①`hooks-bridge`（写 `.github/hooks`/`.claude/settings.json` + 读 stdin JSON 落库）；②`editor`（文档变更、保存、watcher、shell integration、git API）；③`importers`（Claude JSONL、fixtures 回放）；④`model`（Task/Turn/Message/ToolCall/FileChange/TestRun 统一事件）；⑤`store`（SQLite，`globalStorageUri` 下单文件 + 索引）；⑥`webview`（React 三视图 + postMessage 协议）；⑦`extension.ts`（激活、命令、状态栏）。

工作量粗估（单人）：采集桥 3 人日、编辑器事件 2、存储层 2、三视图 6、关联与溯源查询 4、导入器 2、打包与离线验证 1、联调 2 ≈ **22 人日**，比纯 Web 形态多 2–3 人日（hooks 桥 + vsix 平台包）。采集走双通道：hooks 为主、Claude JSONL 导入兜底，避免 Preview 变更导致答辩演示失败。
