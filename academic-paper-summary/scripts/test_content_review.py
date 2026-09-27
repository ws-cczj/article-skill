import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from content_review import prepare, record, check, reviewed_build
from paper_artifacts import save_json


class ContentReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ('draft', 'source', 'review'):
            (self.root / folder).mkdir()
        (self.root / 'source/paper.pdf').write_bytes(b'synthetic source')
        self.data = {'title_zh': '合成测试', 'background': ['背景'],
                     'methods': [], 'conclusions': [{'heading': '结果', 'paragraphs': ['正文'],
                       'figures': [{'number': 1, 'caption': '实际图注'}]}],
                     'innovations': ['贡献'], 'citation': '合成引用'}
        save_json(self.root / 'draft/report.json', self.data)
        self.notes = 'review/content-review.md'
        (self.root / self.notes).write_text('合成测试的复核记录', encoding='utf-8')

    def approve(self):
        prepare(self.root)
        record(self.root, self.notes)

    def test_export_includes_prose_and_captions(self):
        text = prepare(self.root).read_text(encoding='utf-8')
        for value in ['正文', '图1 实际图注', '贡献', '合成引用']:
            self.assertIn(value, text)

    def test_build_without_review_never_calls_builder(self):
        with patch('paper_artifacts.build') as builder:
            with self.assertRaises(OSError):
                reviewed_build(self.root)
            builder.assert_not_called()

    def test_matching_review_calls_existing_builder(self):
        self.approve()
        with patch('paper_artifacts.build', return_value='output') as builder:
            self.assertEqual(reviewed_build(self.root), 'output')
            builder.assert_called_once_with(self.root, 'draft/report.json')

    def test_changed_dependencies_block_build(self):
        for name in ('draft/report.json', 'source/paper.pdf', self.notes, 'review/content-draft.md'):
            with self.subTest(name=name):
                self.approve()
                path = self.root / name
                original = path.read_bytes()
                path.write_bytes(original + b' ')
                with patch('paper_artifacts.build') as builder:
                    with self.assertRaises(ValueError):
                        reviewed_build(self.root)
                    builder.assert_not_called()
                path.write_bytes(original)

    def test_change_after_prepare_requires_fresh_review(self):
        prepare(self.root)
        self.data['title_zh'] = '不同的标题'
        save_json(self.root / 'draft/report.json', self.data)
        with self.assertRaises(ValueError):
            record(self.root, self.notes)

    def test_reprepare_clears_approval_and_empty_notes_rejected(self):
        self.approve()
        prepare(self.root)
        with self.assertRaises(OSError):
            check(self.root)
        (self.root / self.notes).write_text(' ', encoding='utf-8')
        with self.assertRaises(ValueError):
            record(self.root, self.notes)


if __name__ == '__main__':
    unittest.main()
