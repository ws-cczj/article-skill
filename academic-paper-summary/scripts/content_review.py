"""Export prose for agent review and bind that review to the inputs before build.

This verifies provenance, not scientific correctness. The agent performs the review.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

from paper_artifacts import inside, digest, read_json, save_json, citation_paragraphs
from review_claims import seed, validate

CLAIMS = 'review/content-claims.json'


def snapshot(root, content):
    return {name: digest(inside(root, name))
            for name in (content, 'source/paper.pdf')}


def prose(data):
    lines = ['# ' + data['title_zh'], '']
    for heading, key in [('研究背景', 'background'), ('研究方法', 'methods'),
                         ('主要结论', 'conclusions'), ('创新点', 'innovations')]:
        lines += ['## ' + heading, '']
        for n, item in enumerate(data.get(key, []), 1):
            if isinstance(item, str):
                lines += [item, '']
            else:
                lines += [f'### {n}. {item["heading"]}', '']
                for paragraph in item.get('paragraphs', []):
                    lines += [paragraph, '']
                for figure in item.get('figures', []):
                    lines += [f'图{figure["number"]} {figure["caption"]}', '']
    lines += ['## 引用格式', '', '\n\n'.join(citation_paragraphs(data.get('citation', ''))), '']
    return '\n'.join(lines)


def prepare(root, content='draft/report.json'):
    review = root / 'review'
    review.mkdir(exist_ok=True)
    text = prose(read_json(inside(root, content)))
    (review / 'content-draft.md').write_text(text, encoding='utf-8')
    # Preserve edited evidence. A new candidate file makes changed quotes explicit.
    target = root / CLAIMS
    save_json(review / 'content-claims-candidate.json' if target.exists() else target,
              seed(read_json(inside(root, content))))
    inputs = snapshot(root, content)
    inputs['review/content-draft.md'] = digest(review / 'content-draft.md')
    save_json(review / 'content-prepared.json', {'inputs': inputs})
    # Preparing a new reading copy is not approval of that copy.
    (review / 'content-approved.json').unlink(missing_ok=True)
    return review / 'content-draft.md'


def record(root, notes, content='draft/report.json'):
    prepared = read_json(root / 'review/content-prepared.json')['inputs']
    expected = snapshot(root, content)
    expected['review/content-draft.md'] = digest(root / 'review/content-draft.md')
    if prepared != expected:
        raise ValueError('Inputs changed since prepare; regenerate and review the reading copy')
    if (root / 'review/content-draft.md').read_text(encoding='utf-8') != prose(read_json(inside(root, content))):
        raise ValueError('Reading copy differs from report.json; edit report.json and prepare again')
    note_path = inside(root, notes)
    if note_path == root / 'review/content-draft.md':
        raise ValueError('Review notes must be separate from the reading copy')
    if not note_path.read_text(encoding='utf-8').strip():
        raise ValueError('Actual review notes are required')
    validate(read_json(inside(root, content)), read_json(root / CLAIMS))
    expected[notes] = digest(note_path)
    expected[CLAIMS] = digest(root / CLAIMS)
    receipt = {'inputs': expected, 'notes': notes,
               'scope': 'Agent-declared content review; not automated fact verification'}
    save_json(root / 'review/content-approved.json', receipt)
    return receipt


def check(root, content='draft/report.json'):
    receipt = read_json(root / 'review/content-approved.json')
    expected = snapshot(root, content)
    for name in ('review/content-draft.md', receipt['notes'], CLAIMS):
        expected[name] = digest(inside(root, name))
    if receipt['inputs'] != expected:
        raise ValueError('Content review is stale; review changed content and record again')
    validate(read_json(inside(root, content)), read_json(root / CLAIMS))
    return receipt


def reviewed_build(root, content='draft/report.json'):
    check(root, content)
    from paper_artifacts import build
    return build(root, content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'verify', 'record', 'check', 'build'])
    parser.add_argument('--workspace', required=True)
    parser.add_argument('--content', default='draft/report.json')
    parser.add_argument('--notes', default='review/content-review.md')
    args = parser.parse_args()
    root = Path(args.workspace).resolve()
    try:
        if args.action == 'prepare':
            print(prepare(root, args.content))
        elif args.action == 'verify':
            results = validate(read_json(inside(root, args.content)), read_json(root / CLAIMS))
            print(f'Draft quotes and review fields match; {len(results)} calculations checked. '
                  'Source truth and scientific interpretation still require agent review.')
        elif args.action == 'record':
            record(root, args.notes, args.content)
            print('Review recorded for current inputs; scientific judgment remains the agent responsibility.')
        elif args.action == 'check':
            check(root, args.content)
            print('Content review matches current inputs.')
        else:
            print(reviewed_build(root, args.content))
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
