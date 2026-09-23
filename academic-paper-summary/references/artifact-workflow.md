# 复用脚本与逐篇目录

生成文档优先调用skill自带的 `scripts/paper_artifacts.py`，不要在每次任务中重写字体、标题、编号、裁图和DOCX插图脚本。Agent负责阅读与判断，脚本负责重复的文件和版面操作。仅遇到该工具确实不能处理的特殊情况才编写必要补充代码，保存在该论文的`draft/`，不能散落工作区；可通用的改进应在用户授权维护skill时再回收进工具。

## 每篇一次初始化

以下`<工具>`表示skill目录下`/scripts/paper_artifacts.py`的绝对路径，`<论文目录>`使用init实际返回路径；路径中有空格时加引号。

```text
python "<工具>" init --pdf "<原论文.pdf>" --output-root "<工作区>/outputs"
```

每次init都产生包含时间、论文名和随机短标记的新目录，不覆盖历史目录：

```text
outputs/日期时间_论文名_短标记/
  manifest.json          本文源文件与工作区信息
  source/paper.pdf        原论文副本，保持不变
  source/pages.json       每页尺寸、旋转与提取文字
  source/figure_mentions.json  候选图/子图引用与页码上下文（非自动判定）
  source/text.txt         分页文本辅助阅读
  assets/                题名截图、结论图、每张裁图的来源坐标记录
  draft/report.json      Agent填写的事实、正文、图注与图片路径
  review/                页面预览、验证日志、版面检查
  memory/                源文件身份、问题/证据记录、交接索引与最终检查
  final/summary-001.docx  最终文档；再次构建自动递增文件名
```

一篇PDF对应一个目录；多篇分别初始化。默认每篇一个成稿，除非用户明确要求合集。合集是额外输出，不把各论文图片、中间文件混入同一目录。交付只链接final中的成稿，图片和中间文件留在各自子目录，不一股脑列给用户。

## 先查看页面，再确定裁图

```text
python "<工具>" pages --workspace "<论文目录>" --pages 1 3
python "<工具>" crop --workspace "<论文目录>" --page 1 --rect 30 30 560 230 --label identity
```

页码从1开始，rect是PDF显示页面上的x0、y0、x1、y1，单位pt，左上角为原点。先结合`source/pages.json`尺寸和实际页面预览确定区域；命令中的坐标只是演示，不能套到论文。原图旋转、布局不同均须实际检查裁片。脚本默认240dpi截图，并保存源页码和裁剪坐标。

题名截图来自SCI原文的英文期刊栏、英文题目、作者及完整单位地址区，不翻译、不重排；与中文总结题目同时存在。结论图只截图像主体，裁除图外Fig. X及英文原图注，保留所有必要轴、单位、图例和子图标记。

crop同时在`review/crops/`生成带红色裁剪框的整页预览与JSON检查记录，标记待复核，报告截断PDF文字、疑似英文图注及疑似旁栏正文。这些只是几何和文字启发式告警，扫描页、嵌在图片里的文字、曲线或图框被截断可能没有告警；不能把无告警当作合格。工具不自动收紧裁框。

Agent必须实际打开整页预览与最终裁片对照检查四边、全部子图和图内文字；有错误重新crop，不能靠改名为clean/final宣称修好。检查通过后记录具体发现及每项告警的处理理由：

```text
python "<工具>" review-crop --workspace "<论文目录>" --image "assets/figure2-001.png" --note "填写实际观察：哪些边界、标签与子图完整，图外图注和旁栏正文是否排除；如有误报说明原因"
```

这是Agent自己的视觉复核记录，不要求用户审批。不能未经看图批量填写通用“通过”记录。程序校验图片、来源坐标及源PDF的哈希，未复核或依赖改变时阻止build。旧裁片坐标记录没有source_sha256时，从本目录源PDF重新crop并复核，不给旧图直接补写通过哈希。它不能证明Agent确实看过图，视觉责任仍由Agent承担。

已有旧裁图可先运行`inspect-crop --workspace "<论文目录>" --image "assets/figure2-001.png"`生成上下文及告警，再查看并review-crop。该命令需要裁图同名JSON中的source、page、rect来源信息；缺少来源的旧图应从原PDF重新crop，不能编造坐标。重新inspect-crop会重置复核状态。

## 内容数据格式

发现错误裁片时，先登记拒用（本目录生效），再重裁：

```text
python "<工具>" reject-crop --workspace "<论文目录>" --image "assets/figure2-001.png" --reason "填写实际缺陷，例如左侧纵轴文字和底部标签被截断"
```

同样的图片字节即使改名、重新inspect-crop或review-crop也会被拒绝。正确的新裁片仍须实际查看后复核。ink_at_crop_edge提示裁片边界有深色内容，可发现嵌入位图的文字截断，也可能只是图片背景或完整边框；须对照原页判断，不自动裁白边或宣称通过。

按[quality-gates.md](quality-gates.md)保存简短证据表和实际问题的关闭记录；题名截图必须带完整单位地址。新建目录不会自动继承其他任务的拒用记录，不能跨任务盲用旧素材。

init生成空的`draft/report.json`。将精读确认后的中文内容填入以下结构；所有示意文字都应替换，不能把这个结构当成真实总结。

```json
{
  "title_zh": "中文总结题目（必填，可编辑文字）",
  "identity_images": ["assets/identity-001.png"],
  "background": ["背景第一段", "背景第二段"],
  "methods": [
    {
      "heading": "材料设计与制备",
      "paragraphs": ["简短方法正文"],
      "figures": [{"number": 1, "source_figure": "所选原文图号", "image": "assets/method-001.png", "caption": "所选图片的实际内容及与方法的关系"}]
    }
  ],
  "conclusions": [
    {
      "heading": "具体结果型标题，不写编号",
      "paragraphs": ["围绕阶段性发现展开比较和有依据的解释，按论述需要引用图片"],
      "figures": [
        {"number": 2, "source_figure": "原文对应图号，仅内部使用", "image": "assets/figure2-001.png", "caption": "图像内容。（a）单独说明；（b）单独说明；（c）单独说明。"}
      ]
    }
  ],
  "innovations": ["贡献一", "贡献二", "贡献三"],
  "citation": "用下方当前论文元数据生成的完整引用条目",
  "citation_metadata": {
    "original_title": "从当前PDF核实的完整原文题名，不是中文总结题目",
    "authors": ["按原文顺序核实的作者"],
    "journal": "当前论文的期刊",
    "year": "核实后的四位出版年份",
    "doi": "有已核实DOI才填写，否则省略此字段"
  }
}
```

`heading`和创新点不带序号；方法、结论由脚本各自从1编号。`caption`不带“图2”前缀，number必须是总结实际出现的连续编号，方法图与结论图共用序列。build校验number后按出现顺序生成图号，编号错误会报错，不静默改动正文；source_figure仅记录原文图号。正文中的图X及图X(a)必须同步使用总结编号，调整图序后逐项复核。只有原文完全没有图时才允许方法节不配图，此时须填写顶层methods_figure_absence_reason，说明全文核查确无图片；此字段不进入成稿。caption中子图顺序由Agent核对，程序不能代替读图。图片路径相对于论文目录，不能引用其他论文目录。

第五节仅引用当前被总结论文。上面的citation和citation_metadata都是字段示意，须全部替换为当前原文信息；不能照抄示例或旧稿。旧report.json缺少citation_metadata时，须回到本目录source/paper.pdf提取并核对，不能只复制旧citation来填充。build检查题名、年份及已填写DOI的一致性；作者、期刊、卷期与页码等仍须逐项核对源文。

## 构建与复核

build另将本版本的总结图号、source_figure和图片路径保存至review/summary-XXX-figure-map.json供复核；该映射不写入成稿，也不替代Agent核对正文图号。

同时生成review/summary-XXX-build.json，将该DOCX绑定到源PDF、report.json、图片和裁图坐标。交付前memory check --artifact核对这些哈希，防止检查新正文却交付旧Word。旧版没有构建记录的文档须用当前脚本重建并复核；禁止手填构建记录。正常修订修改JSON后重新build。直接在Word修改会使记录失效，应把修改回写到输入或生成逻辑后重建；特殊补充脚本或合集暂不支持这套自动绑定，须明确记录该限制并独立核验实际输出，不能宣称自动交付检查通过。

```text
python "<工具>" build --workspace "<论文目录>"
python "<skill目录>/scripts/validate_summary.py" "<论文目录>/final/summary-001.docx" --expected-papers 1
```

正文数据由Agent生成，用户无需手工填写JSON。Word生成器固定最新字体字号、无项目符号、无自动多级编号及中文题目在前/英文截图在后的顺序。裁图工具提供部分可疑文字告警和复核门槛，但不能自动判定图片完整，也不保证分页完美。通过现有Word或LibreOffice等工具导出PDF到同一`final/`，再用下列命令生成逐页预览：

```text
python "<工具>" pages --workspace "<论文目录>" --pdf "final/summary-001.pdf"
```

观察渲染后需要换页时，可在对应方法/结论小节增加`"page_break_before": true`，脚本将插入显式分页符；不要给所有段落套keep-with-next。修改JSON后重新build得到新版本，保留旧稿。图片不能读清时重新crop，更新路径后再build。最终选择通过内容、结构和视觉检查的版本交付。

没有目标论文时不得为了演示工具生成真实论文总结。工具测试只能使用明确的合成材料和临时目录。

## 保持质量的耗时优化

- 优先复用init已生成的全文、分页文本和figure_mentions候选索引，不为每节重写提取脚本或重提全文。旧任务没有索引时直接检索source/text.txt即可，不要求迁移旧数据或重建目录。
- pages已按PDF内容哈希、分辨率与渲染器版本复用当前论文目录内的页面预览；重复页不再渲染，新增页补齐，PDF或DPI变化用新缓存，缓存图片损坏则重建。缓存不代表已经看过图。
- 先完整阅读、分类汇总并复读研究主线，再确定正文提纲与配图关系；图序稳定后裁图和编号，减少返工。先低分辨率预览定位，最终裁片仍按原质量要求生成。
- 保留逐图内容复核、引用身份核对及成稿逐页检查；修改裁片仍须重新复核。现有工具足够时不另写脚本。特殊PDF无法正确提取时，沿用原来的渲染/OCR和人工核验路径，不能为节省时间跳读、降低分辨率或猜测。
- 这些优化减少重复操作，不承诺固定耗时降幅；若缓存或快捷路径不可靠，使用原流程，质量优先。

## 提取质量与复核边界

使用source/pages.json和source/text.txt前，先检查文本是否与页面信息量相符。大量仅含符号、单个图号的行或整段空缺，意味着提取可能失败，应查看相应PDF页面并按需OCR。图引用索引基于同一文本，提取失败时索引也不完整；缺少检索命中不能证明原文没有解释。

裁片复核和内容证据核对不能由“有reviewed记录”替代。自然留白不触发重新生成；仅在内容、可读性或图文关系存在实际问题时调整，以减少无意义返工。

新论文init自动创建memory；旧论文可运行paper_memory.py init。开始/交接/完成前使用[memory-workflow.md](memory-workflow.md)。reject-crop会自动记录问题；修订后仍需实际核验再resolve。memory索引与既有源文本、图号映射、页面缓存配合使用，不重复保存整个输出。
