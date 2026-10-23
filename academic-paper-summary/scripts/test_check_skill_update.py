import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import check_skill_update as update


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.skill = self.root / 'academic-paper-summary'
        (self.skill / 'scripts').mkdir(parents=True)
        (self.skill / 'SKILL.md').write_bytes(b'test\n')
        (self.skill / 'scripts/paper_artifacts.py').write_bytes(b'init\n')
        self.tree = {'tree': [dict(path=update.PREFIX + n, type='blob',
                                  sha=update.blob_hash((self.skill/n).read_bytes()))
                              for n in ('SKILL.md', 'scripts/paper_artifacts.py')]}

    def test_zip_install_matches_manifest_with_windows_line_endings(self):
        (self.skill/'SKILL.md').write_bytes(b'test\r\n')
        with patch.object(update, 'remote_head', return_value=('main', 'abc')), \
             patch.object(update, 'api', return_value=self.tree) as api:
            self.assertEqual(update.check(self.skill)['status'], 'content_equal')
            self.assertEqual(api.call_count, 1)

    def test_missing_file_and_extra_rule_are_detected(self):
        (self.skill/'SKILL.md').write_text('changed')
        (self.skill/'old-rule.md').write_text('old')
        changed, extra = update.compare_tree(self.skill, self.tree)
        self.assertEqual(changed, ['SKILL.md'])
        self.assertEqual(extra, ['old-rule.md'])

    def test_incomplete_manifest_is_not_current(self):
        with self.assertRaises(ValueError):
            update.compare_tree(self.skill, {'truncated': True})


if __name__ == '__main__':
    unittest.main()
