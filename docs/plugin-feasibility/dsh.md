# DSH 插件形态可行性取证（DeepSeek Harness）

> 对象：本机 DSH Desktop，`@deepseek-ai/dsh-desktop-runtime` **0.2.1-rc.3**，实现在 `D:\DSH\resources\app.asar`（下文 asar 路径省略前缀，写作 `/dsh/...`）。
> 方式：只读解析 asar 与检查 `~/.dsh` 真实安装实例；**未安装插件、未写代码、未运行验证**。无法证实者标「未证实」。

## 一、结论

**评级：B（有条件可行）——能力上界最高，契约稳定性与可复现性扣分。**

1. **能力上界是三种形态中最高的。** DSH 本身就是智能体宿主，Host 插件在 Node 进程内直接读事件溯源会话日志：`tool/call` 带完整 `arguments`、`tool/result` 带完整结果，`ctx.workspaceChanges.diff()` 直接返回带 3 行上下文的 hunk。六类采集对象中「对话、工具调用、文件变更（hunk）」可一等获取。
2. **但这不是公开稳定 API。** 版本停在 RC（npm `next` 已 0.2.1-rc.4），事件名、服务名、Slot 名只以包内 README、`.d.ts` 和内嵌声明存在；指南要求「以已安装的 Harness 为准」，客户端包明言「They change without notice」；hunk 只活在 Host 进程内存。
3. **与开题报告口径冲突最大。** 形态由「Web 三视图 + 可选 IDE 插件」变为「宿主内插件」，需改四(四)、六(二)、六(三)、表 7-1、图 6-2、九共 6 处；「只接 DSH」满足任务书「至少一种」，但不满足开题报告「两种来源」。

## 二、插件体系取证

**两类插件，同一套 cordis 组合树。** Host 插件是普通 cordis 插件：`index.js` 导出 `export function apply(ctx, config)`（可带 `inject`、`Config`）或以 service class 作默认导出，跑在 Node 进程内；Client UI 插件是浏览器 bundle，注册 `window.__ModuleLoader__.load({ id, factory(require) })` 懒工厂，React 由宿主模块表提供（`.../references/ui-plugin.md` L3、L9–13；同目录 `templates/decoration/client.js`）。

**manifest 即 package.json 的 `dsh` 字段**，无独立 manifest 文件：`dsh.manifestVersion: 1`、`dsh.bundle.patch`、`dsh.client { platform, immediately, inject, external }`、`icon`；`engines.dsh` 只是声明式兼容范围，**安装器与 loader 并不校验**（`dsh-package-manifest/README.md` L46–53、L93）。

**加载路径（本机实证）。** `~/.dsh/profiles/desktop/` 是 pnpm workspace：`cordis.yml` 是空根 `[]`，树由「`package.json` 的 `dsh.profile.bundles` 各层 → `cordis.patch.yml` → `--patch`」合成；loader 条目为 `{ id, name, config, group, disabled, inject }`，`name` 交 Node 解析（`cordis-plugin-loader/README.md` L26–34）。插件包自带 `cordis.patch.yml` 的 `- insert:` 行完成挂载。

**第三方实例已存在。** `dsh-zotero@0.13.1` 装在 `~/.dsh/profiles/desktop/node_modules/dsh-zotero`，同时出现在 profile `package.json` 的 `dependencies` 与 `dsh.profile.bundles`；其 `cordis.patch.yml` insert 两行（`zotero`、`zotero/scholarly`），`lib/client.js` 404 KB，`dsh.client.inject` 列 11 个客户端包。

**最小结构（判断「能不能写一个插件」的直接依据）：**

| 文件 | Host-only | 带 UI |
| --- | --- | --- |
| `package.json` | 必需（`type: module`、`exports`、`dsh.bundle.patch`） | 追加 `./client` 与 `dsh.client` |
| `cordis.patch.yml` | 必需（`- insert: [{id,name,config}]`） | 同左 |
| `index.js` | 必需（`apply()` 可空） | 同左 |
| `client.js` | 不需要 | 必需，且须预构建成单文件 |
| `locale/*.json`、`icon` | 建议（管理器显示元数据） | 同左 |
| 构建产物 | **不需要**，纯 JS 即可 | 需要，缺 `lib/client.js` 会激活失败 |
Host-only bundle「无需依赖、安装脚本或构建工具」（`host-plugin.md` L5–18）；Client bundle 由 Host 经 `/plugins` 提供、浏览器懒加载（`dsh-client-modules/README.md`「Build requirements」）。

## 三、逐项分析

### 3.1 形态与运行环境

见第二节：Host 插件持业务能力（工具、存储、事件订阅），Client 插件只渲染；生命周期由 cordis 上下文管理（`practices.md` L8）。**Host 侧零构建可跑，Client 侧需构建链。**

### 3.2 事件可见性（最关键）

DSH 会话是**事件溯源日志**：「模型可见即已记录」，插件正式接口是 `session.append()` 与 `session/event` 流（`dsh-session/README.md`「追加」小节）。完整词汇由 `KNOWN_SESSION_EVENT_TYPES` 给出（`dsh-session/lib/types/known-event-types.js` L21–84，共 60 类），载荷形状见内嵌 `SessionEventMap` 声明（`dsh-agent-preset-registry/lib/typert.host.js`）。

| 采集对象 | 判定 | 依据 |
| --- | --- | --- |
| 对话消息 | **能** | `user/message`、`assistant/message`（含 stream 与 usage）、`system/message`、`developer/message`、`turn/*`、`step/*`、`session/title` |
| 工具调用及参数 | **能（完整）** | `tool/call: { turn, step, callId, name, arguments: string }`；`tool/result: { turn, step, message, error?, meta? }`；另有 `tools/pre-execute`、`execute`、`post-execute`、`tools/result` 四事件（`dsh-tools/README.md` L89、L109） |
| 文件变更（含 hunk） | **能（Host）/ 部分（持久化）** | `workspace/changes` 事件只带 `{ turn }`；内容走服务：`workspaceChanges.summary(sessionId, seq)` 给每文件行数，`.diff(sessionId, seq, index, signal)` 给「3 行上下文 hunk」，另有 `binary`/`oversized`/`coarse` 标记（`dsh-workspace-changes/README.md` L12、L48）。**但摘要与 diff 只活在该 Session 的 Host 进程内，重启后历史 turn 无卡片无 diff（L86）** |
| 终端命令 | **部分** | 无独立终端事件；命令在 `tool/call` 的 `arguments` 里（`dsh-tool-bash`、`dsh-tool-pwsh`）。交互式终端侧栏（`dsh-api-terminal-controller`）是否落事件**未证实** |
| 测试运行结果 | **部分** | 无 TestRun/TestCaseResult 一等实体；只能从 `tool/call`（如 `pnpm test`）+ `tool/result` 文本自行解析归类 |
| git 状态 | **部分** | 无 git 状态服务或事件；`dsh-workspace-changes` 内部用 git 快照（`rev-parse`/`write-tree`/`diff-tree --numstat`）算 turn 级变更，只暴露摘要；`git status` 需自己调 shell 再取其 `tool/call` 记录 |
| 「开发任务」聚合 | **不能（需自建）** | 聚合单位是 Session → Turn → Step，无 Task 实体；可借锚点 `goal/change`、`todo/write`、`team/task`，但语义不同 |

**客户端插件也能拿全事件**：Client 通过 `session/page`、`session/follow` 收到 `{ type: 'event', event: SessionWireEvent }`，且「Tool arguments, result content, failures … pass through unchanged」（`dsh-api-session-controller/README.md` L30、L54）。故「本质优势」的边界不在「服务端 vs 客户端」，而在：**Host 插件能拿到服务层派生能力（hunk、存储、fs），Client 插件只能拿到事件流本身。**

### 3.3 UI 承载力

技术栈 **React**（`templates/decoration/client.js` 从宿主模块表 `require('react')`；具体版本未在包内直接证实，`dsh-zotero` 以 React 18 开发）。扩展点齐全且有面向第三方包的公开注册表：

- 布局：根 slot 组合三栏；全局面板占 root 作用域的 `main` 键控 slot，`ctx.layout.selectPanel(id)` 切换；另有 `shell.bottom`、`shell.overlay`、`shell.leading` 与右侧 `rightbar` 轨道（`dsh-client-ui-layout/README.md` L30–34、L59）。
- 右侧栏（最适合「证据侧栏」）：**Tab 类型注册表** `ctx.sidebarRightTabs.register({ id, kind, patterns, priority, canOpen, title, guide, keepMounted })` + 内容 slot `sidebar.right.pane.tab`，文档明示「a type from another package」走同一公开路径（`dsh-client-ui-sidebar-right/README.md` L78–88、L93）。
- 会话内行：`ctx.uiConversation.events.register()` + `conversation.chat.node`（`practices.md` L37）；通用：`ctx.slots.inject(ownerKey, () => ctx.slots.register({ name, id, order }, Component))`。

**三视图可落位**：任务时间线 → `main` 全局面板；证据侧栏 → `rightbar` 的一个 tab 类型；恢复视图 → 第二个全局面板或 `shell.bottom`。**结论：能，无需 iframe 或自绘壳。** 但明文禁止 `require('@deepseek-ai/dsh-client-ui-primitives')` 等宿主包，要求复制标记与样式、只用 `--dsw-alias-*` token（`practices.md` L33–35）。

### 3.4 存储

- Host 插件在 Node 进程内可写文件系统（组合里已有 `dsh-fs`/`dsh-fs-local`）；另有正式存储服务：`ctx.storage` + `dsh-storage-json`（root = `dshHomePath('storages')`，即 `~/.dsh/storages`）+ `ctx.storageDomain`（`defineDomain` 声明 zod schema 的 KV 域，同步读、持久写、发 `domain/changed`）。见 `dsh-storage/README.md`、`dsh-storage-domain/README.md`；root 见 `dsh-session-projection-cache/README.md` L38。
- **SQLite 可用且宿主自己就在用**：`dsh-session-query-sqlite` 用 **`node:sqlite`** 做 FTS5 索引，`path` 可配任意库、缺失自动建（`dsh-session-query-sqlite/README.md` L45–46、L67）。引擎要求 `node ^22.19 || >=24`；Node 22 下 `node:sqlite` 仍带 experimental 警告（L67），第三方插件是否被鼓励直接用**未证实**。
- `~/.dsh/storages` 实测：`cost-meter/`、`session_projcache/sessions/*.json`、`workspace.json`——即 storage-json 的按域目录，新域会得到自己的子目录。
- 会话日志落在 `~/.dsh/sessions/<workspace>/<sessionId>/session.v4.jsonl.zstd`（zstd 压缩 JSONL，格式 v4，有 v0→v4 迁移链）。

### 3.5 开发与分发

- **开发与打包**：无脚手架命令，但有随包模板与 5 篇 references，写法是手写 `package.json` + `cordis.patch.yml` + `index.js`(+`client.js`)；按 npm 包发布，`files` 须含 patch、locale、icon 与全部运行时文件，Client 侧须构建成单文件。
- **安装**：`plugin_manager` 的 `install_bundle`（Web 侧栏 Plugins 页或 agent 工具，需 `danger-full-access` 或逐次审批），底层在 profile 跑 `pnpm add`；来源支持 registry、git、tarball 与**本地目录（`link:`/`file:`）**（`dsh-plugin-manager/README.md` L31、L48、L50、L100）。
- **签名/联网**：未发现插件签名校验；默认路径要经 registry 查询与 `pnpm add`，**离线安装只能靠本地目录 + 零第三方依赖**，且要求 checkout 已 `pnpm install` 与 `pnpm run build`（L50）。
- **配置页从哪来**：插件导出 `Config`（Schemastery schema），Host 侧 `Config.listConfigs` 暴露已装插件 schema，管理界面据此渲染；`dsh-zotero` 的 `dsh.client.inject` 同时注入 `dsh-client-ui-plugin-manager` 与 `dsh-client-ui-settings`，说明其配置页是「插件自带 Config + 宿主管理器渲染」（`host-plugin.md` L64；其 `package.json`）。第三方市场包 `dshmarket@1.70.2` 已装在 profile，状态与日志在 `~/.dsh/profiles/desktop/.dsh-market/`。

### 3.6 稳定性与生态

- **RC 阶段**：0.2.1-rc.3；npm `next=0.2.1-rc.4`、`alpha=0.2.2-alpha.2`，迭代密集；包内另有大量 `dsh-experimental-*`。
- **文档在包内**：asar 内 1268 个 `.md`，每包带 `README.md` + `README.zh.md`，交叉引用生成式 `config-catalog`/`tool-catalog`/`persistence-catalog`（顶层 docs 未打进 asar，**未证实可获取**）；插件开发指南以 agent skill 随包分发（`.../skills/cordis-plugin-development/SKILL.md`）。
- **公开文档站：未检索到**。`web_fetch` 对 GitHub 仓库与 raw README 均失败（本机网络受限），但 npm registry 可达：`@deepseek-ai/dsh-session` 元数据 200，`homepage`/`repository` 指向 `https://github.com/deepseek-ai/deepseek-harness`，MIT，`access: public`（访问 2026-10-28）。即**有公开源码仓与公开 npm 包，但未检索到专门的插件开发文档站**。
- **API 是否 experimental**：核心 Session/Tools/Storage API 未见 experimental 标注，但指南要求「每个 Service 方法、Event 名都用 `cordis_inspect_query` 现场确认，已安装的 Harness 才是权威」（`practices.md` L3），客户端包「change without notice」（L35）。实质是「内部契约 + 现场自省」。

### 3.7 离线演示可行性

- 插件运行不需联网：Host 插件在进程内，Client bundle 由本地 `/plugins` 提供，已装插件冷启动即可用。
- 智能体本身需要模型：`~/.dsh/.credentials.yaml`、`~/.dsh/llm-deepseek/` 与 profile 里 `dsh-llm-pi-ai` 的 `baseURL: https://agi.tongji.edu.cn/v1`、`apiKeyEnv: TONGJI_API_KEY` 说明走外部 API，**无网无法现场让智能体改代码**。
- 可行方案：回放已落盘的 `session.v4.jsonl.zstd` 或提前录好一次完整任务；但 hunk 只在 Host 内存，**回放历史会话拿不到 diff**，须在演示前把 diff 另存进 SQLite。
- 离线安装前提同 3.5：本地目录 + 零第三方依赖。

### 3.8 与开题报告契合度

需改 6 处：**四(四)** 由「Web 形态三个核心视图、IDE 插件可选」改为「宿主插件形态：Host 采集 + Client 三视图」；**六(二)** 采集来源由 Claude Code + OpenHands 改为 DSH；**六(三)** 由日志导入/git 集成改为事件总线订阅 + 会话日志 + `workspaceChanges`；**表 7-1** 载体改为 DSH 插件；**图 6-2** 重画为「宿主进程内 Host 插件 + Client 插件」；**九** 若只接 DSH，「多来源接入」须弱化为「可扩展事件模式 + 单来源深接」。

**改动量**：四(四) 与六(二)(三) 各约 1 页重写，表 7-1 与图 6-2 重做，九 一段改写；约 1500–2500 字 + 1 图 1 表，半天到一天。**承诺评估**：任务书「至少接入一种真实代码智能体」——只接 DSH **满足**；开题报告「两种来源」——只接 DSH **不满足**，须显式降级。

## 四、关键证据清单

| 结论 | 依据 | asar 内路径 / 外部 | 位置 |
| --- | --- | --- | --- |
| 版本与 cordis 底座 | `0.2.1-rc.3`；依赖 `cordis 4.0.5` + `cordis-plugin-{group,include,loader,timer}` | `/dsh/package.json` | `version`、`dependencies` |
| Host 插件导出形式 | `apply(ctx, config)` 或 service class；资源用 `ctx.effect`/`ctx.on` | `.../references/host-plugin.md` | L57–64 |
| manifest 字段 | `manifestVersion`/`bundle.patch`/`client`；`engines.dsh` 不校验 | `dsh-package-manifest/README.md` | L46–53、L93 |
| loader 条目 | `{id,name,config,group,disabled,inject}`，`name` 交 Node 解析 | `cordis-plugin-loader/README.md` | L26–34 |
| Client 插件格式 | `__ModuleLoader__.load({id, factory(require)})`，React 来自模块表 | `.../templates/decoration/client.js`、`ui-plugin.md` | L3、L9–13 |
| Client 须构建 | 缺 `lib/client.js` 激活失败 | `dsh-client-modules/README.md` | 「Build requirements」 |
| 事件词汇（60 类） | `turn/*`、`step/*`、`*/message`、`tool/call`、`tool/result`、`workspace/changes` | `dsh-session/lib/types/known-event-types.js` | L21–84 |
| 事件载荷 | `tool/call.arguments: string`；`tool/result.message/error/meta` | `dsh-agent-preset-registry/lib/typert.host.js` | `SessionEventMap` |
| 工具流水线事件 | `tools/pre-execute`/`execute`/`post-execute`/`result` | `dsh-tools/README.md` | L89、L109 |
| hunk 与不持久 | `.diff()` 返回 3 行上下文 hunk；仅存活于该 Session 的 Host 进程 | `dsh-workspace-changes/README.md` | L12、L48、L86 |
| Client 也拿全事件 | `session/page`/`session/follow`；tool 参数与结果原样透传 | `dsh-api-session-controller/README.md` | L30、L54 |
| 三视图落位 | `main`/`shell.bottom`/`shell.overlay` + `ctx.layout.selectPanel` | `dsh-client-ui-layout/README.md` | L30–34、L59 |
| 右侧栏 Tab 注册表 | `ctx.sidebarRightTabs.register(...)` + `sidebar.right.pane.tab` | `dsh-client-ui-sidebar-right/README.md` | L78–88、L93 |
| 安装与本地目录 | `install_bundle` → pnpm；支持 registry/git/tarball/本地 `link:` | `dsh-plugin-manager/README.md` | L31、L48、L50、L100 |
| 第三方实例 | `dsh-zotero@0.13.1` 含 `dsh` 字段与 `cordis.patch.yml` | `~/.dsh/profiles/desktop/node_modules/dsh-zotero/package.json` | `dsh`、`engines` |
| 插件安装位置 | profile 为 pnpm workspace，bundles 逐层合成 | `~/.dsh/profiles/desktop/{package.json,cordis.yml,cordis.patch.yml}` | 全文 |
| 会话落盘格式 | `session.v4.jsonl.zstd`（magic `28 b5 2f fd`） | `~/.dsh/sessions/--…--/session-…/session.v4.jsonl.zstd` | 文件头 |

## 五、风险与不可行点

1. **RC + 非公开契约（最高风险）。** 两三周内从 rc.1 到 rc.4；事件名、服务方法、Slot 名无版本化契约。事件模型须放在自建适配层，正文只写课题自定的统一模型。
2. **hunk 不可持久。** 摘要与 diff 只活在该 Session 的 Host 进程内，「重启再讲」时证据侧栏会是空的，必须插件自己落库。
3. **测试与 git 无一等实体。** 测试结果要从终端输出文本解析，git 状态要自己调 shell；「变更↔测试」证据链只能靠启发式规则，需相对开题报告降级说明。
4. **UI 成本高。** 禁 import 宿主 UI 原语，要复制样式与行为、只用主题 token。
5. **单来源风险。** 丢掉「多来源接入」创新点，与开题报告「两种来源」冲突；DSH 相对小众，可能被质疑「换一个智能体就失效」。
6. **可复现性。** 离线安装依赖「本地目录 + 零依赖」；智能体要模型 API；会话日志是 zstd + 版本化格式，外部直读不稳妥。
7. **未证实项**：交互式终端命令是否落事件；第三方插件调 `node:sqlite` 是否被鼓励；`docs/*-catalog.md` 是否可得。

## 六、若选此形态的实施要点

| 模块 | 职责 | 依赖的 DSH 能力 |
| --- | --- | --- |
| M1 事件采集 | 订阅 `session/event`，60 类事件归一化为自建事件表 | `ctx.sessions` |
| M2 变更采集 | `tool/result` 后取 `workspaceChanges.summary/diff` 落库；解析 write/edit 的 `tool/call.arguments` 兜底 | `ctx.workspaceChanges` |
| M3 任务归并 | Session/Turn → 开发任务；用 `todo/write`、`goal/change`、首条 `user/message` 定边界 | 事件（+ LLM 可选） |
| M4 存储 | SQLite（`node:sqlite`）建 Task/Turn/Message/ToolCall/FileChange(Hunk)/TestRun 表，或用 `storageDomain` 起步 | `node:sqlite` |
| M5 查询 API | 时间线、证据链、恢复三接口 | 自建 |
| M6 Client 三视图 | `main` 面板、`rightbar` tab、第二面板 | `ctx.slots`、`sidebarRightTabs`、`ctx.layout` |
| M7 适配层 | 隔离 DSH 专有名字，便于换版本/换来源 | — |

**工作量粗估（单人，含学习成本）**：M1+M2+M4 约 2–3 周；M3 约 1 周；M5 约 1 周；M6 约 2–3 周（受「不能 import 宿主原语」影响最大）；M7 与联调 1 周；合计 **7–9 周**，与开题 2026.12–2027.02 窗口基本吻合，但**没有余量做第二来源**。

**建议**：若选 DSH，定位为「深接的唯一来源」，另加一个轻量 CLI 日志导入适配器（约半天）补足「两种来源」承诺。
