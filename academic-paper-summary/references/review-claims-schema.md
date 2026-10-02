# 稿件原句审核数据

prepare导出阅读稿并首次生成review/content-claims.json。再次prepare保留已填数据，另生成content-claims-candidate.json供比较；合并变化的行、删除不存在的行，保留不受影响的核验结果，不批量改verified。path是report.json字段路径，数组从0计数，quote必须与该字段全文一致。

自动选中题目、方法正文、每项创新及含数字或部分强判断的结论字段。Agent按需添加其他背景、结论或图注字段。每行可含多句，须核查完整字段，不能只核对其中一个数字。

同一文件的sections数组承担整节叙述自审，与claims事实核对分工不同。每条结论对应一项，index从0开始；heading及paragraphs由prepare从实际稿件复制，必须保持一致。实际复读后填写question（回答的问题）、takeaway（核心认识）、evidence_use（必要证据如何支撑认识）、coherence_review（对当前各段作用及重组结果的具体判断），再将status由pending改为verified。不新建另一套审核文件，不要求每节套同一句式。旧任务缺少sections时从再次prepare产生的候选文件合并，不能仅凭事实审核状态直接放行。正文改动后重新复核受影响整节及相邻逻辑。

- source：当前论文可定位的页码、图表或段落。
- evidence：源文实际事实或短摘录，写清样品、条件及物理量定义；图像证据可写具体观察。
- judgment：原句与证据的关系、范围、推断强度及修订结果，不只写“通过”。
- status：pending待查；verified实际核实；qualified必要限定已写入正文。未核实的肯定断言不能用qualified放行。
- 创新行另填prior_work、increment、value，分别说明已有工作、实际增量和具体意义。
- 含数字及倍/%的行填numeric_check：kind为reported/calculated/mixed，basis解释原始量与派生量。calculated/mixed须填calculations；不能将衍生比例改为reported来逃避复算。

合成运算例（不是论文事实）：

```json
{
  "path": "conclusions.0.paragraphs.0",
  "quote": "处理组强度为100 MPa，对照组为40 MPa，前者达到后者的2.5倍。",
  "status": "verified",
  "source": "实际源页及表格位置",
  "evidence": "按实际源文填写同工况、同单位的两组数值",
  "judgment": "比较条件一致；这里是最终比值，不是增加2.5倍",
  "numeric_check": {"kind": "calculated", "basis": "两组强度比值"},
  "calculations": [{
    "operation": "ratio", "baseline": 40, "value": 100,
    "stated": 2.5, "decimals": 1,
    "basis": "实际源页；baseline为对照组，value为处理组，均为MPa"
  }]
}
```

operation支持ratio（value/baseline）、percent_of（比值×100）、increase_percent（增幅）、decrease_percent（降幅）。stated须出现在quote中，decimals为保留小数位数，按半个末位容差检查；不任意放宽精度。程序不使用eval、不猜分母、不自动改写测量值。不同单位、近零基准、不确定度或统计量另行按实际方法核验，不硬套简单比值。

```text
python "<skill>/scripts/content_review.py" prepare --workspace "<论文目录>"
# 实际审读、修订、填写审核数据；需要时再次prepare并合并变化
python "<skill>/scripts/content_review.py" verify --workspace "<论文目录>"
python "<skill>/scripts/content_review.py" record --workspace "<论文目录>"
python "<skill>/scripts/content_review.py" build --workspace "<论文目录>"
```

旧任务仅有Markdown笔记不能直接沿用放行：prepare生成逐项候选，复用已核实源定位，补齐实际原句审核再record。不必新建论文目录、重提全文或重裁未变化的合格图片，历史Word保持不变。
