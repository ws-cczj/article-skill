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

优先使用Agent已有的文档环境。需要新建时，在仓库根目录执行：

Windows PowerShell：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\academic-paper-summary\requirements.txt
.\.venv\Scripts\python.exe .\academic-paper-summary\scripts\check_environment.py --smoke
```

macOS / Linux：

```sh
python3 -m venv .venv
./.venv/bin/python -m pip install -r ./academic-paper-summary/requirements.txt
./.venv/bin/python ./academic-paper-summary/scripts/check_environment.py --smoke
```

已安装用户可将命令中的Skill路径替换为实际安装路径，并让Agent使用配置好的Python解释器。检查退出码：`0`表示依赖可用且检测到字体/渲染器，`1`表示必需环境失败，`2`表示字体或渲染器尚未确认。检测通过不等于实际Word排版通过。详细配置和恢复方法见 [环境说明](academic-paper-summary/references/environment-setup.md)。

## 使用

附上目标论文PDF并发送：

> 使用 $academic-paper-summary，总结这篇论文，生成Word文档。

多篇论文：

> 使用 $academic-paper-summary，分别总结这些论文，每篇单独生成Word文档。

默认逐篇创建独立目录和成稿。只有明确要求合集时，才额外汇编。用户不需要填写JSON、提供裁图坐标或编写Python脚本。

首次实际使用时，Agent提示：

> 欢迎使用捶捶自己开发的article-skill。

首次状态按本机用户保存于 `$CODEX_HOME/skill-state/article-skill/welcomed`（默认 `~/.codex/skill-state/article-skill/welcomed`）；开发、测试Skill不消耗此状态。无法持久保存时只保证当前对话不重复提示。

## 文档内容与规范

每篇包含可编辑的中文学术题目、原论文英文题名信息区截图，以及以下五节：

1. **研究背景**：通常2–3段。
2. **研究方法**：制备过程集中介绍，其他实验、表征、模拟和数据处理集中介绍；确有材料或试样设计才使用“材料设计与制备”。**至少配一张图，仅原文完全没有图时可省略**。没有专门的方法图不构成省略理由，可选择其他原文图片并据实说明其与研究对象或测试的关系。
3. **主要结论**：约5项，通常4–6项；标题陈述具体结果，按证据关系组织。原文图源充足时，主要结论至少5幅不同原文图，方法图另计；原文不足时按实际可用数量处理，不凑图。
4. **创新点**：3点，每点通常2–3句，说明具体贡献和有依据的区别、意义。
5. **引用格式**：引用当前被总结论文自身，重新核实作者、原文题名、期刊、年份、卷期页码和DOI，不能照搬模板或其他论文的引用。

题目提炼核心研究问题，避免堆叠材料、构型和测试项目。允许页面自然留白，不为填满页面扩写或反复调整。原文提取缺失须回看页面；图文证据、倍数与未失效数据须另行核对。

正文直接陈述过程和结果，避免“作者在……”“本文提出……”等转述口吻。方法与结论的小项分别从1开始，不使用2.1、3.1。

### 图文规则

- 按总结中的出现顺序从图1连续编号，方法与结论共用序列，题名截图不编号；原文图号仅存内部映射。
- 综合原图注、正文中的Fig. 1a/1b等引用和布局识别真实子图，再按原标签顺序介绍。区域、测点和①②不自动当作独立子图；未解释的信息不凭空推断。
- 裁片保留子图、坐标、单位、图例、比例尺，去除图外原始英文图注和无关正文。
- 每张裁片对照整页预览复核。自动告警仅辅助判断，扫描图或图内文字可能漏检。

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
    check_environment.py      环境检查
    paper_artifacts.py        提取、预览、裁图、复核记录与Word构建
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
  final/      summary-001.docx及后续版本
```

Agent复用预置脚本，不为每篇重写整套生成代码。相同PDF和分辨率的页面预览可缓存复用；文件改变或缓存损坏会重新生成。候选图引用索引辅助定位，不替代精读。裁图复核与最终逐页检查始终保留。命令和数据结构见 [工具工作流](academic-paper-summary/references/artifact-workflow.md)。

## 检查与维护

在已配置依赖的仓库根目录执行（`python`须指向该环境）：

```sh
python -m unittest discover -s academic-paper-summary/scripts -p "test_*.py"
python academic-paper-summary/scripts/check_environment.py --smoke
python academic-paper-summary/scripts/validate_summary.py path/to/summary.docx --expected-papers 1
```

原文确实少图时，可按核实数量使用 `--min-figures N`。结构检查不证明事实、子图解释、引用身份或版面正确。构建工具检查图号连续性、方法配图、引用题名/年份/已填DOI一致性及裁片复核状态；Agent仍需核对原文并查看最终文档。

扫描件、复杂版面和缺失文字层可能需要额外OCR或人工核查。没有成功渲染成稿时，不应声称视觉验收通过。

## 发布范围与许可

源码发布包含 `academic-paper-summary/`、本README、`.gitignore`和[LICENSE](LICENSE)，采用Apache-2.0许可证。原论文、老师附件、他人总结、提取文本、截图、输出文档和字体不属于应随Skill发布的素材。

`.gitignore`忽略输出、临时目录、虚拟环境与本地打包文件；**已经被Git跟踪的文件不会因新增忽略规则而自动退出版本控制**。上传前检查 `git status` 和 `git ls-files`，确认没有夹带本地论文或生成材料。更新源码后不要继续分发旧的本地ZIP。
