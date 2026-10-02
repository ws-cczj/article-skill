---
name: academic-paper-summary
description: article-skill（论文精读总结）：将完整论文PDF按内置老师要求总结为中文图文Word文档。用户说“使用article-skill技能，帮我总结文献并生成一个word文件”或要求文献精读时使用。内置写作示范、研究主线组织、创新依据及图文格式规范，无需再次提供模板或范例。
---

# 论文精读总结

将完整原论文读懂，再写成围绕研究发现展开、图片辅助说明的中文总结。用户只需提供原论文；不要求重新提交老师附件、范文或长提示词，不增加提纲审批。正式技能名为`academic-paper-summary`，用户常称`article-skill`。仅修改或审阅skill时，不生成论文总结、不消耗首次欢迎状态。

## 总结前先检查官方更新

每次新文献总结任务开始，先按[update-workflow.md](references/update-workflow.md)对比官方GitHub默认分支与当前完整skill目录；有更新先安全更新或隔离使用已核实的最新版，重新读取新版规则后再总结。同一任务只检查一次，固定版本。无法确认最新或完成更新时说明障碍，不默默使用旧版；用户明确指定离线或固定版本时从其要求。保留本地定制、论文、环境和欢迎状态，不强制覆盖。仅审阅文档或开发skill不触发本流程。

## 规则分工与读取范围

用户当前明确要求优先；内置规范已整合此前用户要求与老师附件。原论文提供科学事实，范例只提供写法，不能覆盖规范或充当新论文证据。参考文件里的操作性文字不自动成为用户指令。

不要开场加载全部references。按下表在对应阶段读取，同一任务已读过且未变化的文件不重复读取；技术手册只查当前命令或字段。

| 阶段/问题 | 主要依据 | 读取方式 |
|---|---|---|
| 成稿必须包含什么 | [teacher-rubric.md](references/teacher-rubric.md)、[report-schema.md](references/report-schema.md) | 起草前确认结构与要求；后续只查疑点 |
| 环境与预置命令 | [environment-setup.md](references/environment-setup.md)、[artifact-workflow.md](references/artifact-workflow.md) | 初始化时读环境流程，操作时查命令和JSON字段 |
| 理解并组织研究主线 | [reading-synthesis.md](references/reading-synthesis.md) | 完整阅读后、写正文前 |
| 校准写作深度 | [approved-writing-example.md](references/approved-writing-example.md) | 读与结论、创新相关的示范；其他错误案例按需 |
| 特定写作难点 | [example-writing-patterns.md](references/example-writing-patterns.md)、[wechat-writing-examples.md](references/wechat-writing-examples.md) | 标题、方法分类、数值或论述不清时选相关小节；不是额外必读全集 |
| 图片选择、裁剪和图注 | [figure-analysis.md](references/figure-analysis.md) | 确定入稿图片后 |
| 排版前内容核查 | [content-self-review.md](references/content-self-review.md) | 完整文字稿完成后；审核字段查[review-claims-schema.md](references/review-claims-schema.md) |
| Word格式与视觉验收 | [output-formats.md](references/output-formats.md) | 构建及渲染检查时；字体字号只以此表为准 |
| 记忆、问题与交接 | [memory-workflow.md](references/memory-workflow.md) | 初始化/接手及记录问题时 |

[quality-gates.md](references/quality-gates.md)是上述流程的简短检查索引，不是第二轮自审或第二份证据表。来源角色不清时查[input-and-source-policy.md](references/input-and-source-policy.md)；[skill-evaluation.md](references/skill-evaluation.md)仅供维护评估，不属于每篇总结流程。

## 不变的交付要求

- 保留可编辑的简短中文总结题目，参照老师公众号自然概括研究对象与主题或发现，不强求设问、对比或比喻；下方放原论文英文期刊、完整题名、作者及单位地址区域的真实截图，不含关键词或摘要，不手工重制英文页眉。
- 五节依次为研究背景、研究方法、主要结论、创新点、引用格式。背景通常2–3段；方法将制备集中介绍，其余实验、表征、模拟和数据处理集中介绍，无相应工作则省略该类。材料或试样确有设计才写“设计与制备”。
- 主要结论至少5项，不固定六项；按实际发现之间的关系组织，不按图数拆节或编造结果凑数。正文讲清认识及证据，允许必要的详细比较、图像说明与自然并列，不规定每段句式、句数或数据配额。
- 创新点按3项有依据的贡献组织，适度展开已有基础、实际增量与具体价值，不重复结果清单。无法支持足够独立的贡献时回读；仍不足则如实指出，不编造。
- 直接陈述步骤、观察和解释，不用“作者……”“本文提出……”等旁观转述；保留推断的限定。主要结论直接以研究发现开篇，不用“如图X所示”“图X显示”等引图开场白，也不换成空泛的“结果表明”。一般图文对应由配图与图注承担；确需读者对照图中位置或现象时，在相关论述中自然引用，不用句尾“（图X）”堆引用。
- 方法至少配一张原论文图片，不限专门方法图；只有原文完全无图才省略并记`methods_figure_absence_reason`。结论图片按需要选择，无总数或每项配额。图号按总结出现顺序连续编号，题名截图不计；图注按真实子图标签顺序解释对象和内容，不只列代号。原图号仅存内部`source_figure`。
- 方法与结论的小项各自从1开始，不用2.1/3.1。引用必须是当前论文自身，已核实DOI独立置于引用末尾一段。字体、字号、黑色标题和无多余小点等执行output-formats.md；公众号格式、广告和推广内容不迁移。
- 每篇独立新目录；同一任务修订复用目录、保留版本。成稿以`title_zh`命名，非法文件名字符由脚本处理，同标题重建追加版本号；PDF沿用Word文件主名。多篇仅在用户要求时另做合集。

## 一条生成流程

### 1. 准备环境与论文目录

按environment-setup.md复用专属`.venv`。需要基础Python时，在Codex先通过可用的`load_workspace_dependencies`工具发现运行时，再将路径传给bootstrap，之后回退本机Python；用户明确指定的解释器优先。不能因路径不可访问就断言未安装Python。依赖只装入专属环境，后续始终使用返回的解释器绝对路径，不重建每篇环境、不改全局Python。

实际首次使用时，以该解释器运行`scripts/first_use.py`；有输出就原样单独向用户显示：

欢迎使用捶捶自己开发的article-skill。

无输出不重复欢迎，不写入成稿。状态保存在用户skill-state而非技能包中；不能持久化时仅在当前对话首次提示，不声称跨会话记忆。

使用`paper_artifacts.py init`创建source、assets、draft、review、memory、final目录。接手旧任务先运行记忆check并读INDEX，只复用来源与依赖仍匹配的记录。完整原文是必要内容输入；缺页或不可读时明确缺项，不用旧总结或范文补事实。

### 2. 完整阅读，形成主线

通读题目、摘要、方法、结果讨论、结论及图表。核验提取质量，缺失段落回看原页或OCR，不能把提取成功当成读完。按reading-synthesis.md在`memory/synthesis.md`整理研究问题、分组与条件、发现、解释、贡献依据和源定位；先整体复读，再定结论组织。

写作示范用于校准论述深度，不复制示例的提纲、材料、数值或创新。候选图片可随阅读记录，但不能先按图片分节再扩写图注。源文矛盾、模糊术语或缺失条件登记为问题，回核后处理，不靠推测补齐。

### 3. 写完整内容并核查

按主线完成`draft/report.json`，包括正文、引用元数据和拟用图注；它是唯一可编辑的成稿内容源。复用预置提取、截图和排版脚本，不为每篇重写Python程序。JSON字段及命令查artifact-workflow.md。

通过`content_review.py prepare`导出阅读稿，按content-self-review.md核查整篇主旨、每节论述、数值和范围、创新依据及图注。审核必须回到原论文，不能让memory与正文互相作证。原文报告的比例也需检查内部一致性；不确定性须保留在正文，不只写在审核表。先修正文，再更新受影响的审核记录。

读图、截图可以在阅读和写作中进行。入稿裁片须同时查看整页裁剪框预览与实际裁片，保留坐标、图例、标签和比例尺，排除图外原始Fig.说明及旁栏正文；用`review-crop`记录实际核查，有错误用`reject-crop`并重裁。无告警不等于视觉合格，不能只改文件名复用已拒绝图片。

### 4. 构建、看实际Word，再交付

内容核查完成且verify通过后，`content_review.py record`绑定当前版本，再由其`build`入口生成Word。审核表填齐不是科学判断通过的证明。

运行`validate_summary.py <成稿.docx> --expected-papers N`，处理错误与告警；按output-formats.md渲染并看每一页，核对实际正文、图片、图注、符号、字体和分页。正常留白不返工，图片/图注分离或标题孤悬等实际阅读问题才调整。没有成功渲染不能声称视觉通过。

发现问题修正对应输入并复核变更及关联内容，不重复全篇重写或维护新的通过表。最终运行`paper_memory.py check --artifact <实际成稿>`，解决未关闭问题与过期依赖，确认交付检查对应最终文件；交付工具实际返回的路径。证据卡、执行说明、范例分析和内部路径不进入成稿。未能完成的部分如实说明，不静默遗漏。

## 记录各自只做一件事

- `memory/synthesis.md`：读原文得到的研究主线、条件与源定位。
- `draft/report.json`：唯一成稿内容；`review/content-draft.md`仅为自动导出的阅读副本。
- `review/content-claims.json`：绑定当前原句的逐项证据与整节论述检查；具体字段按脚本格式。
- `review/content-review.md`：整稿判断、实际问题及修订结果，不重抄逐项证据。
- memory问题记录：追踪错误与依赖，引用已有核查位置；裁片记录由工具维护。不另造一份证据总表或通过状态。

用户新附件的有效要求记录在现有memory流程中；稳定范例留在skill的references，不复制到每篇目录。记录是为了定位和复用，不能替代阅读，也不能自行覆盖用户要求。
