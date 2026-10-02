import unittest
from review_claims import calculate, hints, seed, validate


class ClaimTests(unittest.TestCase):
    def test_ratio_and_increase_are_different(self):
        self.assertAlmostEqual(calculate(dict(operation='ratio', baseline=40, value=100,
                                             stated=2.5, decimals=1)), 2.5)
        self.assertAlmostEqual(calculate(dict(operation='increase_percent', baseline=40,
                                             value=100, stated=150)), 150)
        with self.assertRaises(ValueError):
            calculate(dict(operation='percent_of', baseline=80, value=60, stated=76))

    def test_finite_inputs_and_rounding(self):
        self.assertAlmostEqual(calculate(dict(operation='decrease_percent', baseline=3,
                                             value=2, stated=33.3, decimals=1)), 100/3)
        for baseline in [0, float('nan'), float('inf')]:
            with self.assertRaises(ValueError):
                calculate(dict(operation='ratio', baseline=baseline, value=1, stated=1))

    def test_generic_language_hints(self):
        self.assertTrue(hints('倾斜角降至1.25%'))
        self.assertTrue(hints('强度提高约3.2倍'))
        self.assertFalse(hints('角度为1.25°，相对降幅为20%'))

    def test_missing_current_quote_and_contribution_fail(self):
        data = {'title_zh': '合成标题', 'innovations': ['新方法']}
        review = seed(data)
        for row in review['claims']:
            row.update(status='verified', source='p1', evidence='合成证据', judgment='核验解释')
        with self.assertRaisesRegex(ValueError, 'innovation prior_work'):
            validate(data, review)
        review['claims'][1].update(prior_work='基线', increment='增量', value='意义')
        validate(data, review)
        review['claims'].pop(0)
        with self.assertRaisesRegex(ValueError, 'Missing draft'):
            validate(data, review)

    def test_calculation_must_reference_actual_text(self):
        data = {'title_zh': '数值为75%'}
        review = seed(data)
        row = review['claims'][0]
        row.update(status='verified', source='p1', evidence='合成证据', judgment='核对比例',
                   numeric_check={'kind': 'calculated', 'basis': '比例来自两项测量值'},
                   calculations=[dict(operation='percent_of', baseline=80, value=60,
                                      stated=75, basis='p1，同单位试验值/基线')])
        validate(data, review)
        row['calculations'][0]['stated'] = 76
        with self.assertRaises(ValueError):
            validate(data, review)

    def test_whole_section_review_cannot_be_replaced_by_fact_rows(self):
        data = {'title_zh': '合成标题', 'conclusions': [
            {'heading': '合成发现', 'paragraphs': ['合成比较及其解释']}]}
        review = seed(data)
        for row in review['claims']:
            row.update(status='verified', source='p1', evidence='合成事实', judgment='合成判断')
        with self.assertRaisesRegex(ValueError, 'Unresolved whole-section'):
            validate(data, review)
        review['sections'][0].update(status='verified', question='回答什么', takeaway='得到什么认识',
                                    evidence_use='比较怎样支持认识', coherence_review='解释如何衔接')
        validate(data, review)
        data['conclusions'][0]['paragraphs'][0] = '另一版没有数值的正文'
        with self.assertRaisesRegex(ValueError, 'Whole-section review differs'):
            validate(data, review)


if __name__ == '__main__':
    unittest.main()
