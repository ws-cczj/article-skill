"""Exercise a copied installation outside the developer repo and current cwd."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import fitz
from paper_artifacts import workspace


class PortableWorkspaceTests(unittest.TestCase):
    def test_copied_skill_initializes_all_folders_from_another_cwd(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            installed = root / 'installed skill'
            shutil.copytree(Path(__file__).resolve().parents[1], installed,
                            ignore=shutil.ignore_patterns('__pycache__', '.git'))
            task = root / 'user task'
            task.mkdir()
            pdf = task / 'paper.pdf'
            with fitz.open() as source:
                source.new_page().insert_text((50, 50), 'Portable source')
                source.save(pdf)
            run = subprocess.run([sys.executable, str(installed/'scripts/paper_artifacts.py'),
                                  'init', '--pdf', str(pdf), '--output-root', str(task/'outputs')],
                                 cwd=task, capture_output=True, timeout=30)
            self.assertEqual(run.returncode, 0, run.stderr.decode(errors='replace'))
            papers = list((task/'outputs').iterdir())
            self.assertEqual(len(papers), 1)
            paper = papers[0]
            for folder in ('source', 'assets', 'draft', 'review', 'memory', 'final'):
                self.assertTrue((paper/folder).is_dir(), folder)
            self.assertTrue((paper/'memory/INDEX.md').is_file())
            manifest = json.loads((paper/'manifest.json').read_text(encoding='utf-8'))
            self.assertEqual((paper/manifest['source_pdf']).read_bytes(), pdf.read_bytes())
            self.assertFalse((installed/'outputs').exists())
            self.assertEqual(workspace(paper), paper.resolve())
            (paper/'final').rmdir()  # Empty synthetic output directory only.
            with self.assertRaisesRegex(ValueError, 'missing final'):
                workspace(paper)


if __name__ == '__main__':
    unittest.main()
