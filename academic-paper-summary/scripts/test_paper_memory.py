import tempfile
import unittest
from pathlib import Path
import fitz
from paper_artifacts import initialize as paper_init
from paper_memory import initialize,put,resolve,check,read


class MemoryTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        base=Path(tmp.name);source=base/'test.pdf'
        with fitz.open() as doc:
            doc.new_page().insert_text((50,50),'Synthetic memory source');doc.save(source)
        self.root=paper_init(source,base/'outputs')

    def issue(self):
        return put(self.root,dict(kind='issue',summary='Incorrect object in figure explanation',
            locator='Page 1 figure 1',depends_on=['draft/report.json']))

    def test_initialization_is_idempotent(self):
        ident=self.issue();initialize(self.root)
        self.assertTrue((self.root/f'memory/records/{ident}.json').exists())
        self.assertTrue((self.root/'memory/INDEX.md').exists())

    def test_resolve_tracks_replacement_dependencies_and_history(self):
        ident=self.issue()
        replacement=self.root/'draft/replacement.txt';replacement.write_text('reviewed replacement')
        resolve(self.root,ident,'Inspected the replacement source and corrected the identified defect.',
                ['draft/report.json','draft/replacement.txt'])
        record=read(self.root/f'memory/records/{ident}.json')
        self.assertIn('draft/replacement.txt',record['dependencies'])
        self.assertNotIn('draft/replacement.txt',record['history'][0]['dependencies'])
        replacement.write_text('changed replacement')
        self.assertTrue(check(self.root)['blockers'])

    def test_unresolved_and_stale_records_block(self):
        ident=self.issue();self.assertTrue(check(self.root)['blockers'])
        resolve(self.root,ident,'Source page inspected and incorrect object description corrected.')
        self.assertFalse(check(self.root)['blockers'])
        with (self.root/'draft/report.json').open('a') as f:f.write(' ')
        self.assertIn('stale',check(self.root)['blockers'][0])
        resolve(self.root,ident,'Rechecked modified content against the source and confirmed the correction.')
        self.assertFalse(check(self.root)['blockers'])
        self.assertEqual(len(read(self.root/f'memory/records/{ident}.json')['history']),2)

    def test_unverified_evidence_is_not_promoted(self):
        ident=put(self.root,dict(kind='evidence',summary='Candidate term definition',
            locator='Source page 1',depends_on=['source/paper.pdf']))
        self.assertIn(ident,check(self.root)['unverified_records'])
        resolve(self.root,ident,'Read the source page and verified the specific term definition.')
        self.assertNotIn(ident,check(self.root)['unverified_records'])

    def test_source_change_and_path_escape(self):
        with (self.root/'source/paper.pdf').open('ab') as f:f.write(b'changed')
        self.assertTrue(check(self.root)['blockers'])
        with self.assertRaises(ValueError):
            put(self.root,dict(kind='index',summary='Bad external pointer',locator='elsewhere',depends_on=['../../outside']))

    def test_missing_dependency_invalidates_memory(self):
        ident=self.issue();resolve(self.root,ident,'Inspected source and fixed the incorrect explanation in content.')
        (self.root/'draft/report.json').unlink()
        self.assertTrue(check(self.root)['blockers'])


if __name__=='__main__':unittest.main()
