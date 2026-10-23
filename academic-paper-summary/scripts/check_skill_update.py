"""Read-only official-version comparison. Never clone, fetch, or replace files.

Uses only the Python standard library and Git when available. ZIP installs are
compared against GitHub's blob manifest, without downloading the source archive.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import urllib.request
import urllib.parse

REPO = 'ws-cczj/article-skill'
REMOTE = 'https://github.com/' + REPO + '.git'
PREFIX = 'academic-paper-summary/'


def git(*args):
    return subprocess.check_output(['git', *args], stderr=subprocess.PIPE,
                                   timeout=45).decode('utf-8').strip()


def api(path):
    req = urllib.request.Request('https://api.github.com/repos/' + REPO + path,
                                 headers={'User-Agent': 'article-skill-update-check',
                                          'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def remote_head():
    if shutil.which('git'):
        lines = git('ls-remote', '--symref', REMOTE, 'HEAD').splitlines()
        branch = next(x.split()[1].removeprefix('refs/heads/')
                      for x in lines if x.startswith('ref:'))
        sha = next(x.split()[0] for x in lines if not x.startswith('ref:'))
        return branch, sha
    branch = api('')['default_branch']
    return branch, api('/commits/' + urllib.parse.quote(branch, safe=''))['sha']


def blob_hash(content):
    return hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()


def compare_tree(skill, tree):
    if tree.get('truncated'):
        raise ValueError('Remote manifest truncated; cannot confirm current version')
    expected = {x['path'][len(PREFIX):]: x['sha'] for x in tree['tree']
                if x['path'].startswith(PREFIX) and x['type'] == 'blob'}
    if 'SKILL.md' not in expected or 'scripts/paper_artifacts.py' not in expected:
        raise ValueError('Remote skill manifest incomplete')
    changed = []
    for name, sha in expected.items():
        path = skill / name
        if not path.is_file():
            changed.append(name)
            continue
        data = path.read_bytes()
        # Git on Windows may check out text with CRLF; accept either form.
        hashes = {blob_hash(data)}
        if b'\0' not in data:
            hashes.add(blob_hash(data.replace(b'\r\n', b'\n')))
            hashes.add(blob_hash(data.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')))
        if sha not in hashes:
            changed.append(name)
    extra = [p.relative_to(skill).as_posix() for p in skill.rglob('*')
             if p.is_file() and not any(x in ('.git', '__pycache__', '.venv') for x in p.relative_to(skill).parts)
             and p.suffix not in ('.pyc', '.pyo') and p.relative_to(skill).as_posix() not in expected]
    return changed, sorted(extra)


def check(skill):
    skill = Path(skill).resolve()
    if not (skill / 'SKILL.md').is_file():
        raise ValueError('Pass the actual installed skill directory containing SKILL.md')
    branch, remote_sha = remote_head()
    result = dict(skill_dir=str(skill), remote=REMOTE, branch=branch, remote_sha=remote_sha)
    local_sha = None
    if shutil.which('git'):
        try:
            root = Path(git('-C', str(skill), 'rev-parse', '--show-toplevel')).resolve()
            if skill == root / 'academic-paper-summary':
                local_sha = git('-C', str(root), 'rev-parse', 'HEAD')
                dirty = git('-C', str(root), 'status', '--porcelain', '--untracked-files=all', '--', 'academic-paper-summary')
                result['local_sha'] = local_sha
                if local_sha == remote_sha:
                    result['status'] = 'local_changes' if dirty else 'current'
                    return result
        except (subprocess.SubprocessError, OSError):
            pass  # A copied skill need not retain Git metadata.
    changed, extra = compare_tree(skill, api('/git/trees/' + remote_sha + '?recursive=1'))
    result.update(changed_files=changed, extra_files=extra)
    if not changed and not extra:
        result['status'] = 'content_equal'
    elif local_sha:
        comparison = api('/compare/' + local_sha + '...' + remote_sha)
        result['status'] = {'ahead': 'update_available', 'behind': 'local_ahead',
                            'diverged': 'diverged', 'identical': 'local_changes'}[comparison['status']]
    else:
        result['status'] = 'different_unversioned'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-dir', default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.skill_dir), ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({'status': 'unknown', 'error': str(exc)}, ensure_ascii=False))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
