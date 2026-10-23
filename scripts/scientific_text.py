"""Render explicit scientific notation as native Word superscript/subscript runs.

Never infer exponents or chemical formulas from ordinary digits such as 104,
CO2, T700 or specimen IDs. Authors must resolve their meaning from the paper.
"""
import re

SUPER = dict(zip('⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ', '0123456789+-=()ni'))
SUB = dict(zip('₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎', '0123456789+-=()'))
TOKEN = re.compile(
    r'(?<=\d)\^(?:\{(?P<braced>[+\-−]?\d+)\}|(?P<bare>[+\-−]?\d+)(?![0-9A-Za-z_.]))'
    + '|(?P<super>[' + ''.join(SUPER) + ']+)'
    + '|(?P<sub>[' + ''.join(SUB) + ']+)'
)


def scientific_runs(text):
    """Yield (visible text, vertical alignment), retaining unmarked text."""
    end = 0
    for match in TOKEN.finditer(text):
        if match.start() > end:
            yield text[end:match.start()], None
        if match.group('super'):
            yield ''.join(SUPER[c] for c in match.group()), 'superscript'
        elif match.group('sub'):
            yield ''.join(SUB[c] for c in match.group()), 'subscript'
        else:
            yield match.group('braced') or match.group('bare'), 'superscript'
        end = match.end()
    if end < len(text):
        yield text[end:], None


def add_scientific_text(paragraph, text):
    for value, alignment in scientific_runs(text):
        run = paragraph.add_run(value)
        if alignment:
            setattr(run.font, alignment, True)
