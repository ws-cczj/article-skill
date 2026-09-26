"""Exercise the push helper against disposable local repositories, never GitHub."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


@unittest.skipUnless(shutil.which('powershell.exe') and shutil.which('git'), 'Windows PowerShell and Git required')
class PushTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='article push test ')
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.repo = base / 'project with spaces'
        self.remote = base / 'remote.git'
        self.repo.mkdir()
        self.env = os.environ.copy()
        self.env.pop('ARTICLE_SKILL_GIT_PROXY', None)
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1', GIT_TERMINAL_PROMPT='0')
        self.git('init', '--bare', str(self.remote))
        self.git('init', '-b', 'master')
        self.git('config', 'user.name', 'Push test')
        self.git('config', 'user.email', 'push-test@example.invalid')
        self.git('remote', 'add', 'origin', str(self.remote))
        (self.repo / 'scripts').mkdir()
        shutil.copy2(Path(__file__).with_name('push.ps1'), self.repo / 'scripts/push.ps1')
        shutil.copy2(Path(__file__).parent.parent / 'push.bat', self.repo / 'push.bat')
        (self.repo / '.gitignore').write_text('outputs/\n', encoding='utf-8')
        (self.repo / 'old.txt').write_text('old\n', encoding='utf-8')
        self.git('add', '--all')
        self.git('commit', '-m', 'initial')
        self.git('push', '-u', 'origin', 'master')

    def git(self, *args, check=True):
        return subprocess.run(['git', '-C', str(self.repo), *args], env=self.env,
                              capture_output=True, text=True, encoding='utf-8', errors='replace', check=check).stdout.strip()

    def run_helper(self, bat=False):
        cmd = ['cmd.exe', '/c', 'push.bat'] if bat else [
            'powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
            '-File', str(self.repo / 'scripts/push.ps1')]
        return subprocess.run(cmd, cwd=self.repo if bat else self.temp.name, env=self.env,
                              input='\n', capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=40)

    def assert_pushed(self):
        remote_sha = self.git('ls-remote', 'origin', 'refs/heads/master').split()[0]
        self.assertEqual(self.git('rev-parse', 'HEAD'), remote_sha)

    def test_bat_commits_additions_deletions_and_respects_ignore(self):
        (self.repo / 'old.txt').unlink()
        (self.repo / '新 文件.txt').write_text('new\n', encoding='utf-8')
        (self.repo / 'outputs').mkdir()
        (self.repo / 'outputs/private.txt').write_text('not for publication', encoding='utf-8')
        result = self.run_helper(bat=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assert_pushed()
        self.assertEqual(self.git('status', '--porcelain'), '')
        self.assertNotIn('outputs/', self.git('ls-files'))
        self.assertNotIn('old.txt', self.git('ls-files'))

    def test_no_changes_pushes_existing_commit(self):
        (self.repo / 'old.txt').write_text('changed', encoding='utf-8')
        self.git('commit', '-am', 'pending')
        before = self.git('rev-parse', 'HEAD')
        result = self.run_helper()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, self.git('rev-parse', 'HEAD'))
        self.assert_pushed()

    def test_detached_head_stops_before_staging(self):
        self.git('checkout', '--detach')
        (self.repo / 'new.txt').write_text('retain')
        result = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git('diff', '--cached', '--name-only'), '')
        self.assertTrue((self.repo / 'new.txt').exists())

    def test_missing_remote_stops_before_commit(self):
        before = self.git('rev-parse', 'HEAD')
        self.git('remote', 'remove', 'origin')
        (self.repo / 'new.txt').write_text('retain')
        self.assertNotEqual(self.run_helper().returncode, 0)
        self.assertEqual(before, self.git('rev-parse', 'HEAD'))

    def test_commit_failure_does_not_push(self):
        before = self.git('rev-parse', 'HEAD')
        (self.repo / '.git/hooks/pre-commit').write_text('#!/bin/sh\nexit 1\n', encoding='utf-8')
        (self.repo / 'new.txt').write_text('retain')
        self.assertNotEqual(self.run_helper().returncode, 0)
        self.assertEqual(before, self.git('rev-parse', 'HEAD'))
        self.assert_pushed()
        self.assertTrue((self.repo / 'new.txt').exists())

    def test_remote_rejection_keeps_local_commit_and_remote(self):
        original = self.git('rev-parse', 'HEAD')
        self.git('checkout', '-b', 'other')
        (self.repo / 'remote.txt').write_text('remote update')
        self.git('add', '--all')
        self.git('commit', '-m', 'remote update')
        remote_sha = self.git('rev-parse', 'HEAD')
        self.git('push', 'origin', 'HEAD:master')
        self.git('checkout', 'master')
        (self.repo / 'local.txt').write_text('local update')
        result = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotEqual(original, self.git('rev-parse', 'HEAD'))
        self.assertEqual(remote_sha, self.git('ls-remote', 'origin', 'refs/heads/master').split()[0])
        self.assertTrue((self.repo / 'local.txt').exists())


if __name__ == '__main__':
    unittest.main()
