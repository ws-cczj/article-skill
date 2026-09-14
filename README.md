# 论文精读总结 Skill

安装后只需提供待总结的完整论文PDF，并说“总结这篇文献”。Agent读取skill内置的老师要求与写作规范，生成中文图文总结。默认DOCX；多个目标PDF默认形成同一文档内的独立总结单元。

核心要求：正式学术题目；按实际研究工作归类的简洁方法；明确陈述变化、差异或机制的主要结论；原图与具体证据解释相对应。没有目标原论文时不生成新总结，只要求修改skill时不擅自试写。

使用示例：

> 使用 $academic-paper-summary，总结这篇论文，生成Word文档。

老师附件和成功总结仅用于创建阶段提炼规范，不是安装后的运行依赖。整个 `academic-paper-summary` 文件夹包含所需规则与校验脚本；无需重新提供范例、老师附件或创建对话。示例事实不得进入目标论文总结。

## 文件

- `academic-paper-summary/SKILL.md`：任务边界与执行流程。
- `references/example-writing-patterns.md`：标题、方法、结论的正反例及模仿规则。
- 其他 references：来源、老师要求、报告结构、图片和交付检查。
- `scripts/validate_summary.py`：结构、层级、图片存在性及条目检查。
- `scripts/test_validate_summary.py`：使用临时自建材料运行的回归测试，不生成论文总结。

## 验证

从仓库根目录执行：

```text
python academic-paper-summary/scripts/test_validate_summary.py
python academic-paper-summary/scripts/validate_summary.py summary.docx --expected-papers 1
```

DOCX检查需要python-docx。默认主要结论至少5幅图、创新点3条。原文可用图不足时可按已核实数量指定`--min-figures`，多篇不同数量可用`--min-figures-per-paper 3,5`。机械通过不代表事实、图文对应和写作质量通过，仍须原文核查与逐页视觉检查。

用户附件、论文和提取图片仅留在当次输出目录，不随skill公开分发。
