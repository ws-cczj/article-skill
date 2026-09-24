import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from setup_environment import setup, interpreter


class SetupTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)
        self.requirements=self.root/'requirements.txt'
        self.requirements.write_text('python-docx>=1.1,<2')
        self.env=self.root/'.venv'

    def prepare(self):
        python=interpreter(self.env);python.parent.mkdir(parents=True);python.touch()
        (self.env/'article-skill-environment.json').write_text(json.dumps({
            'requirements_sha256':hashlib.sha256(self.requirements.read_bytes()).hexdigest()}))

    def test_refuses_nonempty_broken_directory_without_deleting(self):
        self.env.mkdir();keep=self.env/'keep.txt';keep.write_text('keep')
        with self.assertRaisesRegex(RuntimeError,'nonempty'):setup(self.env,self.requirements)
        self.assertEqual(keep.read_text(),'keep')

    def test_valid_cached_environment_does_not_install(self):
        self.prepare()
        with patch('setup_environment.subprocess.run',return_value=subprocess.CompletedProcess([],0)) as run:
            self.assertEqual(setup(self.env,self.requirements),interpreter(self.env))
            self.assertEqual(run.call_count,1)
            self.assertNotIn('pip',run.call_args.args[0])

    def test_failed_install_does_not_stamp_new_requirements(self):
        self.prepare();stamp=self.env/'article-skill-environment.json';old=stamp.read_bytes()
        self.requirements.write_text('new-requirement')
        with patch('setup_environment.subprocess.run',side_effect=[
            subprocess.CompletedProcess([],0),subprocess.CompletedProcess([],0),
            subprocess.CalledProcessError(1,['pip'])]):
            with self.assertRaises(subprocess.CalledProcessError):setup(self.env,self.requirements)
        self.assertEqual(stamp.read_bytes(),old)


if __name__=='__main__':unittest.main()
