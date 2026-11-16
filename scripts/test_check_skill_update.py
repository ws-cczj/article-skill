import tempfile
import io
import json
import ssl
import urllib.error
import zipfile
import unittest
from pathlib import Path
from unittest.mock import patch
import check_skill_update as update


class UpdateTests(unittest.TestCase):
    def test_explicit_proxy_and_direct_do_not_need_git(self):
        with patch.object(update.urllib.request, 'build_opener') as build:
            self.assertEqual(update.Network('http://localhost:1234').mode, 'explicit_proxy')
            self.assertEqual(build.call_args.args[0].proxies['https'], 'http://localhost:1234')
            update.Network('http://localhost:1234', direct=True)
            self.assertEqual(build.call_args.args[0].proxies, {})

    def test_transient_errors_retry_once_but_tls_and_rate_limit_do_not(self):
        net = update.Network(direct=True)
        for error, count in [(TimeoutError(), 2),
                             (urllib.error.URLError(ssl.SSLError()), 1),
                             (urllib.error.HTTPError('https://example.com', 429, 'limit', {}, None), 1)]:
            with patch.object(net.opener, 'open', side_effect=error) as request, patch.object(update.time, 'sleep'):
                with self.assertRaises(Exception):
                    net.read('https://example.com')
                self.assertEqual(request.call_count, count)

    def test_failure_does_not_disclose_proxy_credentials(self):
        result = update.failure(urllib.error.URLError('http://user:secret@localhost'))
        self.assertNotIn('secret', json.dumps(result))

    def test_https_connect_status_controls_retry_and_is_sanitized(self):
        net = update.Network(direct=True)
        for status, count in ((403, 1), (407, 1), (429, 1), (503, 2)):
            error = urllib.error.URLError(OSError(
                f'Tunnel connection failed: {status} http://user:secret@localhost'))
            with self.subTest(status=status), patch.object(net.opener, 'open', side_effect=error) as request, \
                    patch.object(update.time, 'sleep'):
                with self.assertRaises(urllib.error.URLError) as caught:
                    net.read('https://example.com')
                self.assertEqual(request.call_count, count)
                result = update.failure(caught.exception)
                self.assertEqual(result['error_code'], f'http_{status}')
                self.assertNotIn('secret', json.dumps(result))

    def test_local_and_archive_errors_are_not_network_errors(self):
        for error, code in ((FileExistsError('private path'), 'output_exists'),
                            (PermissionError('private path'), 'filesystem_permission_error'),
                            (zipfile.BadZipFile('private content'), 'invalid_snapshot')):
            with self.subTest(code=code):
                result = update.failure(error)
                self.assertEqual(result['status'], 'unknown')
                self.assertEqual(result['error_code'], code)
                self.assertNotIn('private', json.dumps(result))

    def test_corrupt_archive_is_not_saved(self):
        destination = self.root / 'corrupt.zip'
        with patch.object(update, 'api', return_value=self.tree), patch.object(update, 'transport') as network:
            network.return_value.read.return_value = b'not a ZIP'
            with self.assertRaises(zipfile.BadZipFile):
                update.download_snapshot('a' * 40, destination)
        self.assertFalse(destination.exists())

    def test_verified_download_rejects_tampered_content_and_preserves_existing_file(self):
        sha = 'a' * 40
        dest = self.root / 'snapshot.zip'
        def archive(content):
            stream = io.BytesIO()
            with zipfile.ZipFile(stream, 'w') as z:
                z.writestr('article-skill-' + sha + '/SKILL.md', content)
                z.writestr('article-skill-' + sha + '/scripts/paper_artifacts.py', b'init\n')
            return stream.getvalue()
        with patch.object(update, 'api', return_value=self.tree), patch.object(update, 'transport') as network:
            network.return_value.read.return_value = archive(b'wrong')
            with self.assertRaises(ValueError):
                update.download_snapshot(sha, dest)
            self.assertFalse(dest.exists())
            network.return_value.read.return_value = archive(b'test\n')
            self.assertEqual(update.download_snapshot(sha, dest)['status'], 'snapshot_verified')
            original = dest.read_bytes()
            with self.assertRaises(FileExistsError):
                update.download_snapshot(sha, dest)
            self.assertEqual(dest.read_bytes(), original)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.skill = self.root / 'article-skill'
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

    def test_root_install_ignores_local_output_but_checks_root_rules(self):
        for folder in ('outputs', '.git', '.agents', '.skill-check', '.venv'):
            (self.skill/folder).mkdir()
            (self.skill/folder/'local.txt').write_text('local data')
        self.assertEqual(update.compare_tree(self.skill, self.tree), ([], []))
        (self.skill/'README.md').write_text('local root rule')
        self.assertEqual(update.compare_tree(self.skill, self.tree)[1], ['README.md'])


if __name__ == '__main__':
    unittest.main()
