# Report schema

Use this schema once for every target paper. When several PDFs are supplied, repeat the complete schema without merging the blocks.

## Document level

Optional collection title: a field topic or “文献调研”. It may appear once at the beginning of a compilation and is not a substitute for paper-level sections.

## Paper block

### Paper heading

Use a formal Chinese academic title identifying the research object and topic. Follow the title examples in [example-writing-patterns.md](example-writing-patterns.md); avoid conversational instructions or promotional hooks. Keep the original paper title directly below or in the same title block. Include authors and venue only when helpful for identification.

### 一、研究背景

Paragraph 1: broader research or application problem.

Paragraph 2: limitations or unresolved gap in existing work.

Paragraph 3: what this paper studies and why its design addresses the gap.

### 二、研究方法

Group actual work into conceptual categories; use the decision table in [example-writing-patterns.md](example-writing-patterns.md). Default to “材料制备” when preparation exists; use “材料设计与制备” with explicit material or specimen design and preparation/machining. Specimen geometry, dimensions, configuration and loading-related design count as design; routine grouping alone does not establish design work. Omit preparation when absent. Name experimental, characterization and numerical categories only when the paper contains those activities. Use direct method–information statements (e.g. “采用XX方法，获得XX”) instead of narrating what the authors did. Put specific techniques in connected body paragraphs explaining their objects, measured information and purpose; do not turn instrument names into peer headings. Keep useful methodological explanations while removing generic padding.

Insert a workflow/apparatus figure here only when it helps explain the method and the teacher requires images.

### 三、主要结论

Order findings by their actual evidentiary relationships: observed changes, complementary evidence, supported explanation, and consequences or conditions where present. Preserve parallel findings and avoid invented causality. One finding may combine several figures. Each subsection contains:

1. a heading stating a concrete observed change, comparison, relationship or supported mechanism, not a generic method assessment;
2. an evidence paragraph with the key trend/value and conditions;
3. the associated figure/table and caption when required; explain every labeled panel in original (a), (b), (c) order in both text and caption before synthesizing the finding;
4. a limitation or scope statement where needed.

This section is where key figure analysis belongs. Do not create a detached figure-analysis chapter by default.

### 四、创新点

List three concrete contributions. Use bullets, numbered points, or short paragraphs; make the boundaries between points obvious.

### 五、引用格式

Give one exact citation for this paper only. Never place another paper's citation in this block.

## Multi-paper compilation order

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
