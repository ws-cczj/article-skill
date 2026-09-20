# Report schema

Write every section in a direct, content-focused voice: state procedures, observations and relationships without “作者……”, “本文提出……” or “该研究表明……”. Preserve uncertainty and source-supported scope. Captions describe the image directly, without “原文 Fig. X：” source prefixes. Each labeled panel needs its own explanation in original order.

Use this schema once for every target paper. When several PDFs are supplied, use separate newly created per-paper workspaces and reports. Only compile them if explicitly requested.

## Document level

Optional collection title: a field topic or “文献调研”. It may appear once at the beginning of a compilation and is not a substitute for paper-level sections.

## Paper block

### Paper heading

Use a formal Chinese academic title identifying the research object and topic. Follow the title examples in [example-writing-patterns.md](example-writing-patterns.md); avoid conversational instructions or promotional hooks. The editable Chinese summary title is mandatory. Place a real English crop of the SCI paper’s first-page journal/title/author area beneath it, following figure-analysis.md. Do not typeset separate “原题目/作者/期刊” introduction lines. Retain the full bibliographic citation at the end.

### 一、研究背景

Paragraph 1: broader research or application problem.

Paragraph 2: limitations or unresolved gap in existing work.

Paragraph 3: what this paper studies and why its design addresses the gap.

### 二、研究方法

Default to two groups: keep ALL material/specimen preparation, processing and fabrication together; keep the other experiments, characterization, simulations and data processing together, using short internal paragraphs. Omit an absent group. Do not split preparation across peer subsections or give each technique a heading. Group actual work into conceptual categories; use the decision table in [example-writing-patterns.md](example-writing-patterns.md). Default to “材料制备” when preparation exists; use “材料设计与制备” with explicit material or specimen design and preparation/machining. Specimen geometry, dimensions, configuration and loading-related design count as design; routine grouping alone does not establish design work. Omit preparation when absent. Name experimental, characterization and numerical categories only when the paper contains those activities. Use direct method–information statements (e.g. “采用XX方法，获得XX”) instead of narrating what the authors did. Put specific techniques in connected body paragraphs explaining their objects, measured information and purpose; do not turn instrument names into peer headings. Keep useful methodological explanations while removing generic padding.

Number method subsections 1, 2, 3 independently, never 2.1, 2.2. Keep each category to a concise paragraph where practical, covering actual work and essential conditions without tutorial detail.

Insert a workflow/apparatus figure here only when it helps explain the method and the teacher requires images.

### 三、主要结论

Aim for about five evidence-based findings (usually 4–6). Merge complementary evidence for the same finding; do not confuse finding count with figure count, invent findings, or suppress independent key results.

Restart result subsection numbering at 1, 2, 3, never 3.1, 3.2.

Order findings by their actual evidentiary relationships: observed changes, complementary evidence, supported explanation, and consequences or conditions where present. Preserve parallel findings and avoid invented causality. One finding may combine several figures. Each subsection contains:

1. a heading stating a concrete observed change, comparison, relationship or supported mechanism, not a generic method assessment;
2. an evidence paragraph with the key trend/value and conditions;
3. the associated figure/table and caption when required; explain every labeled panel in original (a), (b), (c) order in both text and caption before synthesizing the finding;
4. a limitation or scope statement where needed.

This section is where key figure analysis belongs. Do not create a detached figure-analysis chapter by default.

### 四、创新点

List three concrete contributions. Expand each into a compact paragraph, usually 2–3 sentences stating the contribution, a supported distinction, and its specific significance where evidenced. Avoid slogans, speculative novelty, padding, and merely repeating result numbers. Use numbered points or short paragraphs, not bullet dots; make the boundaries between points obvious.

### 五、引用格式

Give one exact citation for this paper only. Never place another paper's citation in this block.

“引用格式”指当前被总结论文自身的引用条目，不是固定范例，也不是该论文末尾参考文献列表中的条目。只模仿格式，不能复用范例中的作者、题名、期刊、年份或DOI。每次从当前PDF首页和出版信息提取原文作者（保持顺序）、完整原文题名、期刊、出版年份、卷（期）、页码或文章号、DOI，核对后填写。SCI英文论文保留英文书目信息，不能用自行拟定的中文总结题目替代原文题名。

默认排列为“作者. 原文题名[J]. 期刊, 年, 卷(期): 页码或文章号. DOI.”；该句只是字段顺序，不可原样放进成稿。用户或老师明确指定其他引用样式时从其要求，引用对象始终不变。不得把收稿日期、版权日期直接当出版年份。未核实的卷期页码或DOI不得编造；必要时通过该论文DOI对应的出版商页面核实，仍无法确认则省略未核实字段并在交付说明中指出。

在report.json中填写citation_metadata，包含original_title、authors数组、journal、year（字符串），以及已核实的doi（有则填）。citation写最终完整条目。build会拒绝缺少元数据、题名或年份不匹配、遗漏已核实DOI的引用。该检查只能验证两者一致，不能替代与源PDF核对作者、期刊、卷期、页码及论文身份；不能为绕过检查而让元数据迎合错误引用。独立结构检查器validate_summary.py仅检查引用存在和年份，不证明引用对象正确。

## Explicitly requested multi-paper compilation order

```text
Document title (optional)
Paper 1 heading
  一、研究背景
  二、研究方法
  三、主要结论
  四、创新点
  五、引用格式
Paper 2 heading
  一、研究背景
  二、研究方法
  三、主要结论
  四、创新点
  五、引用格式
...
```

No paper may borrow a section, figure, or citation from a neighboring block.

For DOCX, apply the mandatory Chinese/Latin fonts, sizes and bold settings in [output-formats.md](output-formats.md). Semantic chapter level and Word style ID are mapped there; do not confuse the paper title with the first-level chapter headings.
