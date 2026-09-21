# 环境准备与恢复

运行环境需要能执行脚本、读取PDF/图片、写入DOCX并检查渲染结果的Agent。Skill提供工作规范与辅助检查，不自带模型、Office软件、字体或一键生成论文的程序。用户内容输入仍只有原论文；依赖属于环境准备，不是额外文献输入。

## 每次开始任务时

先使用可用Python运行 `<skill目录>/scripts/check_environment.py --json`，环境首次配置后或依赖变更后可加 `--smoke`。使用绝对路径并加引号，Windows可用`py -3`，macOS/Linux通常用`python3`；后续检查、欢迎语和生成操作尽量使用同一个解释器。

- 退出码0：依赖可导入，渲染器和字体名称已检测到；不代表已完成实际渲染。
- 退出码1：Python版本或依赖导入/读写测试失败，检查输出中的具体项目。
- 退出码2：依赖可用，但渲染工具或字体未确认，需要配置或人工验证。未检测到不一定未安装，尤其是macOS字体及Agent自带工具。

预检查不安装软件、不修改字体、不打开用户文档、不消耗欢迎语状态。`--smoke`只在自动清理的临时目录创建无论文内容的测试文件。它验证PDF文本提取、页面栅格化和DOCX插图读写，不验证DOCX到PDF导出。

## Python依赖

推荐Python 3.10及以上。优先使用Agent已有的可用文档运行环境；不要在已有环境能工作时重复创建环境。需要新建时推荐隔离虚拟环境，以下命令在仓库根目录执行：

Windows PowerShell：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\academic-paper-summary\requirements.txt
.\.venv\Scripts\python.exe .\academic-paper-summary\scripts\check_environment.py --smoke
```

macOS/Linux：

```sh
python3 -m venv .venv
./.venv/bin/python -m pip install -r ./academic-paper-summary/requirements.txt
./.venv/bin/python ./academic-paper-summary/scripts/check_environment.py --smoke
```

已经安装skill的用户将`academic-paper-summary`替换为实际skill绝对路径即可；虚拟环境可建在自己的工作目录，不要求能写入skill安装目录。依赖随包提供在`requirements.txt`：python-docx用于DOCX读写与结构检查，PyMuPDF用于PDF读取/提图/页面渲染，Pillow用于图片检查。版本范围不是锁定环境，安装后运行smoke确认组合可用。

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
