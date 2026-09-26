# article-skill｜论文精读总结

捶捶开发的中文论文精读 Skill。安装并配置运行环境后，向 Agent 提供完整论文 PDF，即可按内置规范生成包含原文图片的 Word 总结。

仓库名为 **article-skill**，实际安装的 Skill 名称为 **academic-paper-summary**。老师要求、写作规则和格式规范已包含在 Skill 中，无需再次提供老师附件、成功范例或创建时的聊天记录。

## 安装

### 通过 Codex 安装

在支持技能安装的 Codex 中发送：

> 请使用 skill-installer，从 GitHub 仓库 ws-cczj/article-skill 安装 academic-paper-summary 目录中的 skill。

应安装仓库中的 `academic-paper-summary/` 子目录，而不是把整个仓库当作 Skill。安装完成后，在下一轮对话确认该技能可用；Python 依赖仍需按下文配置。

### 手动安装

下载或克隆本仓库，将完整的 `academic-paper-summary` 文件夹放入 Codex 的技能目录：

- 设置了 `CODEX_HOME`：`$CODEX_HOME/skills/academic-paper-summary/`
- 默认位置：`~/.codex/skills/academic-paper-summary/`

安装后应能找到 `academic-paper-summary/SKILL.md`，并保留同级的 `references/`、`scripts/`、`agents/` 和 `requirements.txt`。更新已有安装时先备份本地定制内容，再同步完整 Skill 文件夹。

其他 Agent 可按自身技能加载机制使用；本仓库未逐一验证所有客户端，不能保证仅复制文件就能自动识别。

## 环境准备

需要具备文件读写、Python 执行、PDF与图片阅读能力的 Agent。Skill不包含模型、Office或字体，也不是独立的一键论文理解程序。

- Python **3.10及以上**。
- Python依赖：`python-docx`、`PyMuPDF`、`Pillow`，版本范围见 [requirements.txt](academic-paper-summary/requirements.txt)。
- DOCX排版复核：Microsoft Word、LibreOffice或Agent可用的等效渲染工具。
- 字体：**宋体、楷体、Times New Roman**。字体不随仓库分发，缺字体时不能保证显示效果一致。

默认使用**用户专属.venv**隔离Python依赖。本地或Codex提供的Python 3.10+用于创建环境；后续统一调用虚拟环境中的解释器。

Windows PowerShell（仓库根目录）：

```powershell
powershell -NoProfile -File ./academic-paper-summary/scripts/bootstrap.ps1
```

macOS/Linux：

```sh
sh ./academic-paper-summary/scripts/bootstrap.sh
```

入口脚本本身不依赖Python。Agent按“可用的专属`.venv` → Codex提供的Python → 用户本机Python”选择。在Codex中先通过`load_workspace_dependencies`发现运行时路径，传入Windows的`-RuntimePython`或macOS/Linux的`--runtime-python`，再验证是否可执行、版本和venv/ensurepip是否可用；工具不可用时才直接检查本机环境。用户无需手动寻找Codex缓存路径。

找不到路径不能直接认定未安装Python：须区分路径不可见、权限/沙箱限制、版本不兼容、缺模块和安装依赖失败。默认`.venv`目录不可写时，可指定当前工作区可写位置；不自动改全局权限。只有没有任何兼容、可访问的基础Python时，才给出[Python官方安装入口](https://www.python.org/downloads/)或系统包管理器方案。安装后重跑同一入口继续。

仅检查解释器、不创建环境时使用`-CheckOnly`或`--check-only`。这不代表依赖、字体和Word渲染已通过检查。Windows若阻止脚本执行，按本机策略处理，不自动更改全局执行策略。

已安装用户使用实际skill目录下的同一脚本。环境默认位于`$CODEX_HOME/skill-state/article-skill/.venv`，未设置时为`~/.codex/skill-state/article-skill/.venv`；独立于skill安装目录，更新skill和多篇生成可复用。需要仓库内环境时Windows入口加`-VenvPath "<仓库路径>/.venv"`，其他入口加`--venv "<仓库路径>/.venv"`。脚本返回后续应使用的绝对Python路径，无需手动激活。

首次配置需要安装requirements.txt中的依赖；依赖未改变且导入正常时直接复用、不重复安装。`--repair`可重查依赖，失败不向全局Python安装包。不要将本机`.venv`提交或打进ZIP，其他用户在自己电脑创建；依赖隔离不能替代Office与字体安装，也不保证不同机器依赖版本完全一致。

使用返回的Python运行`scripts/check_environment.py --smoke`可复查环境：`0`表示依赖可用且检测到字体/渲染器，`1`表示必需环境失败，`2`表示字体或渲染器尚未确认。检查通过不等于Word实际排版通过。详细配置见[环境说明](academic-paper-summary/references/environment-setup.md)。

## 使用

附上目标论文PDF并发送：

> 使用article-skill技能，帮我总结文献并生成一个word文件。

技能描述已包含`article-skill`常用名称。需要在客户端明确选择技能时，使用正式调用名：

> 使用 $academic-paper-summary，总结这篇论文，生成Word文档。

多篇论文：

> 使用 $academic-paper-summary，分别总结这些论文，每篇单独生成Word文档。

默认逐篇创建独立目录和成稿。只有明确要求合集时，才额外汇编。用户不需要填写JSON、提供裁图坐标或编写Python脚本。

### 如何保持写作质量

已内置[用户认可的写作示范与注解](academic-paper-summary/references/approved-writing-example.md)，包含研究主线、完整结论段落、三项贡献定位及正文/图注分工。Agent在写第一版正文前读取，用当前论文重新建立证据和提纲；不套用示例的材料、数值或五项结论。生成后分别复读正文逻辑、创新依据和子图说明，再检查实际Word。

每篇的`memory/synthesis.md`保存研究主线、来源定位和贡献依据。用户另附指导文件时，原件/提取文本放`source/reference/`，本次有效要求与冲突处理放`memory/requirements.md`；通用规范保留在skill中，不要求每次重新提供附件。原始论文和用户附件不随仓库分发。

更新时须同步完整技能目录，包括新增references，不能只替换SKILL.md。不同模型的阅读与写作能力仍有差异；本次认可稿验证了示范写法，不代表所有模型或客户端已通过相同测试。结构检查通过也不等于科学事实与论述质量达标。

首次实际使用时，Agent提示：

> 欢迎使用捶捶自己开发的article-skill。

首次状态按本机用户保存于 `$CODEX_HOME/skill-state/article-skill/welcomed`（默认 `~/.codex/skill-state/article-skill/welcomed`）；开发、测试Skill不消耗此状态。无法持久保存时只保证当前对话不重复提示。

## 文档内容与规范

每篇包含可编辑的中文学术题目、原论文英文题名、作者及单位地址区截图，以及以下五节：

1. **研究背景**：通常2–3段。
2. **研究方法**：制备过程集中介绍，其他实验、表征、模拟和数据处理集中介绍；确有材料或试样设计才使用“材料设计与制备”。**至少配一张图，仅原文完全没有图时可省略**。没有专门的方法图不构成省略理由，可选择其他原文图片并据实说明其与研究对象或测试的关系。
3. **主要结论**：至少5项，不固定为六项；标题与正文共同概括阶段性发现，先给发现再展开比较、图证和解释，不把正文写成逐图报读清单。按文献实际研究流程组织，每项可详细展开条件、比较和解释；图片服务于结论，选择足以说明关键发现的图即可，不设每项或总图数配额。
4. **创新点**：3点，每点通常2–3句，说明具体贡献和有依据的区别、意义。
5. **引用格式**：引用当前被总结论文自身，重新核实作者、原文题名、期刊、年份、卷期页码和DOI，不能照搬模板或其他论文的引用。

题目面向公众号读者，简短并突出有依据的发现、对比或权衡，避免平铺的长标题和夸张宣传。允许页面自然留白，不为填满页面扩写或反复调整。原文提取缺失须回看页面；图文证据、倍数与未失效数据须另行核对。

正文直接陈述过程和结果，避免“作者在……”“本文提出……”等转述口吻。方法与结论的小项分别从1开始，不使用2.1、3.1。

### 图文规则

- 题名截图保留完整作者单位地址，排除Keywords/关键词和摘要，尽量排除无关收稿日期。
- 正文按需自然写“如图X所示”等，不用句尾“（图X）”式引用；无必要时不强行添加图号。

- 按总结中的出现顺序从图1连续编号，方法与结论共用序列，题名截图不编号；原文图号仅存内部映射。
- 综合原图注、正文中的Fig. 1a/1b等引用和布局识别真实子图，再按原标签顺序介绍。区域、测点和①②不自动当作独立子图；未解释的信息不凭空推断。
- 裁片保留子图、坐标、单位、图例、比例尺，去除图外原始英文图注和无关正文。
- 每张裁片对照整页预览复核，并检查四边；工具会提示边缘深色内容，但可能误报或漏报。发现错误后登记拒用，同一论文目录内相同图片字节不能改名重新使用。

### Word格式

| 元素 | 中文字体与字号 | 西文 | 字重 |
|---|---|---|---|
| 中文题目 | 宋体四号，14pt | Times New Roman，同字号 | 加粗 |
| 五节标题 | 宋体小二，18pt | Times New Roman，同字号 | 加粗 |
| 小标题 | 宋体小四，12pt | Times New Roman，同字号 | 加粗 |
| 正文 | 楷体小四，12pt | Times New Roman，12pt | 常规 |
| 图片介绍 | 楷体，11pt | Times New Roman，11pt | 加粗 |
| 引用条目 | Times New Roman，小四12pt | 同左 | 常规 |

完整规范以 [SKILL.md](academic-paper-summary/SKILL.md) 和 [格式说明](academic-paper-summary/references/output-formats.md) 为准。

## 文件组织与预置工具

```text
academic-paper-summary/
  SKILL.md
  agents/openai.yaml
  requirements.txt
  references/                 写作、来源、图片、格式和环境规范
  scripts/
    first_use.py              首次使用提示
    bootstrap.ps1 / bootstrap.sh  无需Python的发现与启动入口
    setup_environment.py      创建或复用用户专属.venv
    check_environment.py      环境检查
    paper_artifacts.py        提取、预览、裁图、复核记录与Word构建
    paper_memory.py           每篇问题记忆、证据索引与交付前检查
    validate_summary.py       成稿结构检查
    test_*.py                 合成材料回归测试
```

每篇论文生成独立的新目录：

```text
outputs/日期时间_论文名_标记/
  source/     原论文副本、分页文本、图引用候选索引
  assets/     裁片及来源坐标
  draft/      内容数据
  review/     页面预览、裁图检查、图号映射
  memory/     本篇问题、证据、可重建索引与检查记录
  final/      summary-001.docx及后续版本
```

Agent复用预置脚本，不为每篇重写整套生成代码。相同PDF和分辨率的页面预览可缓存复用；文件改变或缓存损坏会重新生成。候选图引用索引辅助定位，不替代精读。裁图复核与最终逐页检查始终保留。命令和数据结构见 [工具工作流](academic-paper-summary/references/artifact-workflow.md)。

## 检查与维护

### Windows一键提交并推送

双击仓库根目录的`push.bat`。脚本从自身位置定位项目，显示改动，执行`git add --all`，有改动时以当前时间生成提交说明，然后将当前分支推送到`origin`同名分支；没有新改动时仍可推送已有本地提交。它会提交全部未被忽略的改动（包括删除和已暂存内容），运行前请确认这些改动均准备提交。

需要已安装Git并具备远端写入权限。窗口完成后停留显示结果；分支游离、合并/变基未完成、提交失败或推送被拒绝时停止，不自动拉取合并、不强推、不回退本地提交。没有推送成功时修复提示的问题后重试。

默认遵循Git现有网络配置；如需代理，可设置用户环境变量`ARTICLE_SKILL_GIT_PROXY`后重新打开窗口，或单次运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ./scripts/push.ps1 -Message "更新论文总结规范" -Proxy "http://127.0.0.1:7890"
```

代理地址仅为示例，按本机实际填写；脚本不固定代理端口，也不修改全局Git配置。BAT中的执行策略参数仅作用于本次PowerShell进程。

### 验证

在已配置依赖的仓库根目录执行（`python`须指向该环境）：

```sh
python -m unittest discover -s academic-paper-summary/scripts -p "test_*.py"
python academic-paper-summary/scripts/check_environment.py --smoke
python academic-paper-summary/scripts/validate_summary.py path/to/summary.docx --expected-papers 1
```

默认检查至少5项结论，不设结论图数下限；仅用户另外明确要求图数时使用 `--min-figures N`。结构检查不证明事实、子图解释、引用身份或版面正确。构建工具检查图号连续性、方法配图、引用题名/年份/已填DOI一致性及裁片复核状态；Agent仍需核对原文并查看最终文档。

扫描件、复杂版面和缺失文字层可能需要额外OCR或人工核查。没有成功渲染成稿时，不应声称视觉验收通过。

## 发布范围与许可

源码仓库包含 `academic-paper-summary/`、维护脚本`push.bat`与`scripts/`、本README、`.gitignore`和[LICENSE](LICENSE)，采用Apache-2.0许可证。安装Skill仍只需`academic-paper-summary/`目录。原论文、老师附件、他人总结、提取文本、截图、输出文档和字体不属于应随Skill发布的素材。

`.gitignore`忽略输出、临时目录、虚拟环境与本地打包文件；**已经被Git跟踪的文件不会因新增忽略规则而自动退出版本控制**。上传前检查 `git status` 和 `git ls-files`，确认没有夹带本地论文或生成材料。更新源码后不要继续分发旧的本地ZIP。

生成执行检查见 [五个检查点](academic-paper-summary/references/quality-gates.md)：提取质量、标题与单位地址、具体陈述的证据、裁片拒用与实际成稿复核、问题关闭。程序不能代替真实阅读与看图。

## 每篇论文记忆

新任务自动建立memory目录，其他Agent可先运行记忆check、阅读INDEX.md后继续工作。问题有open/resolved状态，证据和定位有recorded/verified状态；源文件、正文或图片等依赖变化会使相关记录过期。仅核实且未过期的内容可复用。记忆不跨论文自动传播，也不覆盖当前用户要求。

交付前运行paper_memory.py check并通过--artifact指定实际成稿；未关闭问题和过期记录会阻止检查通过，草稿仍可构建。构建记录将Word绑定到实际使用的源PDF、正文、图片及裁图坐标；修改输入后须重建，不能用旧Word通过新内容的检查。旧版裁片缺源文件哈希时须重新裁取并复核，旧Word缺构建记录时须重建，不能直接补写“通过”。此检查不证明内容或图片本身正确。完整命令、字段、旧任务补建及协作规则见[记忆工作流](academic-paper-summary/references/memory-workflow.md)。

写作顺序：完整阅读→分类汇总→整体复读研究主线→组织正文→按需配图→成稿整体回读与事实核验。图注解释图片，正文按论述需要引用；不要求每图每子图都在正文点名。
