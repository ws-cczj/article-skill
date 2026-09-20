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
  source/text.txt         分页文本辅助阅读
  assets/                题名截图、结论图、每张裁图的来源坐标记录
  draft/report.json      Agent填写的事实、正文、图注与图片路径
  review/                页面预览、验证日志、版面检查
  final/summary-001.docx  最终文档；再次构建自动递增文件名
```

一篇PDF对应一个目录；多篇分别初始化。默认每篇一个成稿，除非用户明确要求合集。合集是额外输出，不把各论文图片、中间文件混入同一目录。交付只链接final中的成稿，图片和中间文件留在各自子目录，不一股脑列给用户。

## 先查看页面，再确定裁图

```text
python "<工具>" pages --workspace "<论文目录>" --pages 1 3
python "<工具>" crop --workspace "<论文目录>" --page 1 --rect 30 30 560 230 --label identity
```

页码从1开始，rect是PDF显示页面上的x0、y0、x1、y1，单位pt，左上角为原点。先结合`source/pages.json`尺寸和实际页面预览确定区域；命令中的坐标只是演示，不能套到论文。原图旋转、布局不同均须实际检查裁片。脚本默认240dpi截图，并保存源页码和裁剪坐标。

题名截图来自SCI原文的英文期刊栏、英文题目和作者区，不翻译、不重排；与中文总结题目同时存在。结论图只截图像主体，裁除图外Fig. X及英文原图注，保留所有必要轴、单位、图例和子图标记。

crop同时在`review/crops/`生成带红色裁剪框的整页预览与JSON检查记录，标记待复核，报告截断PDF文字、疑似英文图注及疑似旁栏正文。这些只是几何和文字启发式告警，扫描页、嵌在图片里的文字、曲线或图框被截断可能没有告警；不能把无告警当作合格。工具不自动收紧裁框。

Agent必须实际打开整页预览与最终裁片对照检查四边、全部子图和图内文字；有错误重新crop，不能靠改名为clean/final宣称修好。检查通过后记录具体发现及每项告警的处理理由：

```text
python "<工具>" review-crop --workspace "<论文目录>" --image "assets/figure2-001.png" --note "填写实际观察：哪些边界、标签与子图完整，图外图注和旁栏正文是否排除；如有误报说明原因"
```

这是Agent自己的视觉复核记录，不要求用户审批。不能未经看图批量填写通用“通过”记录。程序校验记录和图片/来源坐标的哈希，未复核或图片、来源坐标改变时阻止build。它不能证明Agent确实看过图，视觉责任仍由Agent承担。

已有旧裁图可先运行`inspect-crop --workspace "<论文目录>" --image "assets/figure2-001.png"`生成上下文及告警，再查看并review-crop。该命令需要裁图同名JSON中的source、page、rect来源信息；缺少来源的旧图应从原PDF重新crop，不能编造坐标。重新inspect-crop会重置复核状态。

## 内容数据格式

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
      "figures": []
    }
  ],
  "conclusions": [
    {
      "heading": "具体结果型标题，不写编号",
      "paragraphs": ["按(a)、(b)、(c)逐项说明的结果正文"],
      "figures": [
        {"number": 2, "image": "assets/figure2-001.png", "caption": "图像内容。（a）单独说明；（b）单独说明；（c）单独说明。"}
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

`heading`和创新点不带序号；方法、结论由脚本各自从1编号。`caption`不带“图2”前缀，脚本根据number加入中文图号。caption中子图顺序由Agent核对，程序不能代替读图。图片路径相对于论文目录，不能引用其他论文目录。

第五节仅引用当前被总结论文。上面的citation和citation_metadata都是字段示意，须全部替换为当前原文信息；不能照抄示例或旧稿。旧report.json缺少citation_metadata时，须回到本目录source/paper.pdf提取并核对，不能只复制旧citation来填充。build检查题名、年份及已填写DOI的一致性；作者、期刊、卷期与页码等仍须逐项核对源文。

## 构建与复核

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
