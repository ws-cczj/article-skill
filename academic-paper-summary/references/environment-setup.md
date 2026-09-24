# 环境准备与恢复

运行环境需要能执行脚本、读取PDF/图片、写入DOCX并检查渲染结果的Agent。Skill提供工作规范与辅助检查，不自带模型、Office软件、字体或一键生成论文的程序。用户内容输入仍只有原论文；依赖属于环境准备，不是额外文献输入。

## 每次开始任务时

先按下节运行不依赖Python的bootstrap入口，再由setup_environment.py取得专属.venv的Python路径，再使用该Python运行 `<skill目录>/scripts/check_environment.py --json`，环境首次配置后或依赖变更后可加 `--smoke`。后续检查、欢迎语和生成操作均使用该解释器的绝对路径并加引号；PowerShell以`& "<Python绝对路径>" "<脚本路径>"`调用，不能又切回裸python或py -3。

- 退出码0：依赖可导入，渲染器和字体名称已检测到；不代表已完成实际渲染。
- 退出码1：Python版本或依赖导入/读写测试失败，检查输出中的具体项目。
- 退出码2：依赖可用，但渲染工具或字体未确认，需要配置或人工验证。未检测到不一定未安装，尤其是macOS字体及Agent自带工具。

预检查不安装软件、不修改字体、不打开用户文档、不消耗欢迎语状态。`--smoke`只在自动清理的临时目录创建无论文内容的测试文件。它验证PDF文本提取、页面栅格化和DOCX插图读写，不验证DOCX到PDF导出。

## Python依赖：专属.venv优先

默认使用本机用户专属虚拟环境。解释器选择顺序固定为：

1. 当前任务指定的专属`.venv`存在且能执行时复用，不因Codex更新就重建。
2. 需要基础Python时，在Codex中先调用可用的`load_workspace_dependencies`工具（当前工具名可能为`mcp__codex_app__load_workspace_dependencies`），取得返回的Python绝对路径，并实际验证。工具不可用或没有返回Python时记录这一情况，不假定所有Codex宿主都有相同运行时。
3. 将发现的路径传入bootstrap的`-RuntimePython`或`--runtime-python`；入口按“已有.venv → 传入的Codex运行时 → 本机py/python3/python”逐个检查。Shell脚本不能自行调用Codex工具，Agent负责发现并传参。不得跳过Codex发现直接让用户安装Python。
4. 仅在这些路径都没有兼容且可访问的解释器时给安装指引。用户明确指定某解释器时用`-PythonPath`或`--python`，失败不静默切换。

Codex Python只作创建环境的基础运行时，不向它或系统Python安装skill依赖；创建后统一使用`.venv`返回的解释器路径。基础Python不支持venv/ensurepip时保留具体诊断，再尝试本机兼容Python，不能把“有Python”当成“能创建虚拟环境”。

Windows PowerShell首次配置：

```powershell
powershell -NoProfile -File "<skill目录>/scripts/bootstrap.ps1"
```

macOS/Linux：

```sh
sh "<skill目录>/scripts/bootstrap.sh"
```

入口按上述顺序检查Python版本和venv/ensurepip。`-CheckOnly`（PowerShell）或`--check-only`（sh）只做解释器检查，不安装、不建目录。缺Python时退出2并提供下一步，不开始生成；初始化失败退出非零，成功退出0，但Office/字体仍需独立检查。

在Codex中发现路径后，例如：

```powershell
powershell -NoProfile -File "<skill目录>/scripts/bootstrap.ps1" -RuntimePython "<工具返回的Python路径>"
```

macOS/Linux使用`sh "<skill目录>/scripts/bootstrap.sh" --runtime-python "<工具返回的Python路径>"`。不把工具返回的路径硬编码进skill或复制到其他设备。

### 区分环境失败原因

- 路径不存在或当前执行环境不可见：重新发现运行时，确认本机、远程或容器的路径归属；不能据此认定电脑没装Python。
- Permission denied、Access denied或沙箱限制：报告具体路径和错误，使用当前环境允许访问的运行时/目录；遵守宿主权限流程，不以安装Python代替访问问题。
- 解释器可启动，但版本过低或缺venv/ensurepip：报告版本或缺少模块，继续寻找兼容基础解释器。
- Python可用，但默认环境目录不可写：在当前可写工作区选择专属目录，传`-VenvPath`或`--venv`，后续持续复用并记录路径。不要求写入用户电脑上不可见的CODEX_HOME路径。
- pip下载、代理或依赖安装失败：报告安装阶段错误；不要删除环境或声称缺Python。恢复访问后重跑，已成功环境不重复安装。

启动脚本保留失败候选的诊断；“未找到可用解释器”只表示当前候选在当前执行环境不可用，不等于确认未安装。

完全没有兼容Python时，给用户明确安装指引：[Python官方下载](https://www.python.org/downloads/)（受支持的稳定版本且满足3.10+），或使用操作系统包管理器；Linux可能需要额外的venv/ensurepip组件。安装完成后重开终端，再运行同一入口。不要只抛出python命令不存在，也不自动下载安装不明运行时、更改PATH或全局执行策略。若用户已授权安装，按目标系统提供的正规安装方式完成再复查。

PowerShell脚本若受执行策略限制，依用户机器策略处理；不要默默改全局策略。自定义环境位置用PowerShell的`-VenvPath`或sh的`--venv`。首次初始化保持单写入者，同一环境不要并发安装依赖。

脚本默认在`$CODEX_HOME/skill-state/article-skill/.venv`创建环境，未设置CODEX_HOME时使用`~/.codex/skill-state/article-skill/.venv`。它位于skill安装目录外，更新skill不需重装依赖，也适用于只读安装目录。所有论文共用这一个专属环境，不在每篇输出目录重建。仅首次配置或requirements改变、导入失败、显式--repair时安装依赖；成功的重复调用复用环境、不联网安装。首次安装需能够访问pip配置的软件源；断网时不要假装成功或擅自改全局pip源。

最后输出JSON中的`python`是后续所有脚本使用的绝对解释器路径，无需activate。启动每次任务可重跑setup，再用返回的Python执行check_environment.py --json；检查字体和渲染器的责任仍保留。setup退出0只说明Python依赖可用，不保证Office/字体可用。

开发者希望使用仓库内`.venv`时加`--venv "<仓库目录>/.venv"`；已选自定义路径的任务必须持续使用同一路径。已有环境损坏时用`--repair`重查安装；环境本身缺Python或无法运行时选择新的空目录重建，不自动删除旧目录、不静默切回全局环境。若标准Python缺venv/ensurepip，换一个支持venv的Python，或依系统要求补齐该组件。

**不提交、不打包、不跨设备复制.venv。** 它包含本机路径和平台相关二进制；仓库只分发setup_environment.py与requirements.txt。依赖版本范围不是精确锁文件，不保证所有机器安装完全相同的版本；安装后执行冒烟测试。用户明确指定已有环境时可沿用，但先检查依赖并说明它不受专属环境隔离。

## DOCX渲染与字体

- Windows：可使用已安装的Microsoft Word，经PowerShell COM导出PDF；也可使用LibreOffice。预检查仅检测Word注册或LibreOffice可执行文件，不启动应用。实际导出需在生成后验证。
- macOS/Linux：推荐LibreOffice，确保`soffice`在PATH中，或使用其绝对路径。macOS常见路径为`/Applications/LibreOffice.app/Contents/MacOS/soffice`。
- Agent自带文档渲染工具也可以使用；预检查未发现时说明采用的替代工具，完成实际导出与检查后再确认可用。

LibreOffice导出示例（目标目录先创建，文件路径按实际替换）：

```sh
soffice --headless --convert-to pdf --outdir ./rendered ./summary.docx
```

确认PDF确实生成，再用PyMuPDF渲染页面并逐页检查。不可将原论文PDF的渲染误当成所生成Word的排版检查。若已有同名旧PDF，使用新的输出目录避免把旧文件当作本次导出结果。

所需字体是宋体（SimSun）、楷体（KaiTi）和Times New Roman；其他平台不保证预装。用户应安装自己有权使用的字体，不随skill分发字体文件。Word里填写字体名称不能证明渲染器拥有该字体；缺字体时不能悄悄替换并声称满足要求。预检查Windows字体注册表，其他平台优先用`fc-list`；无法确认时在实际渲染环境核查。

## 缺项处理

优先使用当前Agent已有的等效工具完成任务；依赖安装按当前环境权限执行。缺少Office或字体等需要用户配置的条件时，明确说缺哪项和解决方式，不泛泛索要更多材料。仍可完成原文阅读、证据整理和可完成的文档工作，但未完成渲染/字体核验时不能宣称最终格式合格。

扫描PDF按需要使用可用OCR工具；不要对所有用户强制安装OCR。OCR后的数字、公式及图注须回核原页面。图表无法辨认时索取更清晰的对应原文内容。
