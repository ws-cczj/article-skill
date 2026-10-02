"""Draft-bound review rows and explicit arithmetic; no inferred scientific facts."""
import math
import re


def fields(data):
    result = {'title_zh': data['title_zh']}
    for section in ('background', 'innovations'):
        for i, text in enumerate(data.get(section, [])):
            result[f'{section}.{i}'] = text
    for section in ('methods', 'conclusions'):
        for i, item in enumerate(data.get(section, [])):
            result[f'{section}.{i}.heading'] = item['heading']
            for j, text in enumerate(item.get('paragraphs', [])):
                result[f'{section}.{i}.paragraphs.{j}'] = text
            for j, figure in enumerate(item.get('figures', [])):
                result[f'{section}.{i}.figures.{j}.caption'] = figure['caption']
    return result


def hints(text):
    found = []
    if re.search(r'(?:提高|提升|增加|增长)\s*(?:了|约|近|至|到)*\s*\d+(?:\.\d+)?\s*倍', text):
        found.append('倍率：区分最终比值与增加量，明确比较基准')
    if re.search(r'(?:倾斜角|倾角|角度|θ)[^。；;，,°]{0,18}?(?:至|为|=)\s*\d+(?:\.\d+)?\s*[%％]', text):
        found.append('角度后出现百分号：核对是角度值还是相对变化率')
    if re.search(r'优先演化|损伤转移|阈值|最优.*窗口|证明|验证了', text):
        found.append('证据强度：区分观察、模拟、支持的解释和未验证推测')
    return found


def required(path, text):
    return (path == 'title_zh' or path.startswith('innovations.')
            or (path.startswith('methods.') and '.paragraphs.' in path)
            or (path.startswith('conclusions.') and
                (re.search(r'\d', text) or hints(text)))
            or bool(hints(text)))


def seed(data):
    return {'schema_version': 1, 'claims': [
        {'path': path, 'quote': text, 'hints': hints(text), 'status': 'pending',
         'source': '', 'evidence': '', 'judgment': '', 'calculations': []}
        for path, text in fields(data).items() if required(path, text)],
        'sections': [
            {'index': i, 'heading': item['heading'], 'paragraphs': list(item['paragraphs']),
             'status': 'pending', 'question': '', 'takeaway': '',
             'evidence_use': '', 'coherence_review': ''}
            for i, item in enumerate(data.get('conclusions', []))]}


def calculate(row):
    # Agent supplies quantities and their meanings from the source. Never eval expressions.
    baseline, value = float(row['baseline']), float(row['value'])
    stated = float(row['stated'])
    decimals = row.get('decimals', 0)
    if type(decimals) is not int or not 0 <= decimals <= 8:
        raise ValueError('decimals must be an integer from 0 to 8')
    if not all(math.isfinite(x) for x in (baseline, value, stated)) or baseline == 0:
        raise ValueError('Calculation requires finite quantities and nonzero baseline')
    operations = {'ratio': value / baseline, 'percent_of': value / baseline * 100,
                  'increase_percent': (value - baseline) / baseline * 100,
                  'decrease_percent': (baseline - value) / baseline * 100}
    if row['operation'] not in operations:
        raise ValueError('Unknown calculation operation')
    computed = operations[row['operation']]
    if abs(computed - stated) > 0.5 * 10 ** (-decimals) + 1e-9:
        raise ValueError(f'Arithmetic mismatch: stated {stated}, computed {computed:.10g}')
    return computed


def validate(data, review):
    if review.get('schema_version') != 1 or not isinstance(review.get('claims'), list):
        raise ValueError('Unsupported claims review schema')
    actual = fields(data)
    seen = set()
    results = []
    for claim in review['claims']:
        path = claim['path']
        if path in seen or path not in actual:
            raise ValueError(f'Duplicate or unknown draft path: {path}')
        seen.add(path)
        if claim['quote'] != actual[path]:
            raise ValueError(f'Review quote differs from actual draft: {path}')
        if claim.get('status') not in ('verified', 'qualified'):
            raise ValueError(f'Unresolved claim: {path}')
        for name in ('source', 'evidence', 'judgment'):
            if not isinstance(claim.get(name), str) or not claim[name].strip():
                raise ValueError(f'Missing {name}: {path}')
        if path.startswith('innovations.'):
            for name in ('prior_work', 'increment', 'value'):
                if not isinstance(claim.get(name), str) or not claim[name].strip():
                    raise ValueError(f'Missing innovation {name}: {path}')
        if not isinstance(claim.get('calculations', []), list):
            raise ValueError(f'calculations must be a list: {path}')
        if re.search(r'\d.*(?:倍|%|％)', claim['quote']):
            numeric = claim.get('numeric_check', {})
            if numeric.get('kind') not in ('reported', 'calculated', 'mixed') or not numeric.get('basis', '').strip():
                raise ValueError(f'Classify reported quantities versus derived ratios: {path}')
            if numeric['kind'] in ('calculated', 'mixed') and not claim.get('calculations'):
                raise ValueError(f'Derived ratio requires an explicit calculation: {path}')
        for calculation in claim.get('calculations', []):
            if not calculation.get('basis', '').strip():
                raise ValueError(f'Calculation quantity definitions and source required: {path}')
            token = str(calculation['stated'])
            if not re.search(r'(?<![\d.])' + re.escape(token) + r'(?![\d.])', claim['quote']):
                raise ValueError(f'Stated calculation value not present in draft: {path}')
            results.append({'path': path, 'computed': calculate(calculation)})
    missing = [path for path, text in actual.items() if required(path, text) and path not in seen]
    if missing:
        raise ValueError('Missing draft review rows: ' + ', '.join(missing))
    sections = review.get('sections', [])
    conclusions = data.get('conclusions', [])
    if not isinstance(sections, list) or len(sections) != len(conclusions):
        raise ValueError('Every conclusion requires a whole-section narrative review')
    indices = set()
    for section in sections:
        i = section.get('index')
        if type(i) is not int or i in indices or not 0 <= i < len(conclusions):
            raise ValueError('Invalid or duplicate conclusion review index')
        indices.add(i)
        actual_section = conclusions[i]
        if section.get('heading') != actual_section['heading'] or section.get('paragraphs') != actual_section['paragraphs']:
            raise ValueError(f'Whole-section review differs from actual draft: conclusions.{i}')
        if section.get('status') != 'verified':
            raise ValueError(f'Unresolved whole-section narrative review: conclusions.{i}')
        for key in ('question', 'takeaway', 'evidence_use', 'coherence_review'):
            if not isinstance(section.get(key), str) or not section[key].strip():
                raise ValueError(f'Missing whole-section {key}: conclusions.{i}')
    return results
