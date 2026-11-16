"""Official-version comparison and optional verified ZIP download. Never installs.

Uses only Python standard-library HTTPS requests. All installs are
compared against GitHub's blob manifest, without downloading the source archive.
"""
import argparse
import hashlib
import json
import os
import io
import re
import socket
import ssl
import time
import zipfile
from pathlib import Path
import urllib.request
import urllib.parse
import urllib.error

REPO = 'ws-cczj/article-skill'
REMOTE = 'https://github.com/' + REPO + '.git'
PREFIX = ''
LOCAL_DIRS = {'.git', '.venv', 'outputs', 'artifacts', 'tmp', '__pycache__', '.agents', '.skill-check', '.pytest_cache'}


def http_status(exc):
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code
    # urllib wraps HTTPS CONNECT failures in URLError(OSError(...)).
    # Extract only the status; never expose the proxy's response text.
    if isinstance(exc, urllib.error.URLError):
        match = re.match(r'^Tunnel connection failed: (\d{3})(?:\s|$)', str(exc.reason))
        if match:
            return int(match.group(1))
    return None


class Network:
    """One HTTPS transport for manifests and snapshots; never changes Git settings."""
    def __init__(self, proxy=None, direct=False, timeout=15):
        proxy = proxy or os.environ.get('ARTICLE_SKILL_PROXY')
        if direct:
            proxies = {}
        elif proxy:
            parsed = urllib.parse.urlsplit(proxy)
            if parsed.scheme != 'http' or not parsed.hostname:
                raise ValueError('Proxy must be an http://host:port HTTP/mixed proxy endpoint; SOCKS/PAC is not supported')
            proxies = {'http': proxy, 'https': proxy}
        else:
            proxies = urllib.request.getproxies()
            if any(urllib.parse.urlsplit(proxies.get(k, '')).scheme.startswith('socks') for k in ('http', 'https')):
                raise ValueError('SOCKS proxy is unsupported; select the proxy application HTTP/mixed endpoint')
        self.mode = 'direct' if direct else ('explicit_proxy' if proxy else 'environment_or_system')
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxies))
        self.timeout = timeout

    def read(self, url):
        req = urllib.request.Request(url, headers={
            'User-Agent': 'article-skill-update-check', 'Accept': 'application/vnd.github+json'})
        for attempt in range(2):
            try:
                with self.opener.open(req, timeout=self.timeout) as response:
                    return response.read()
            except urllib.error.HTTPError as exc:
                if exc.code not in (500, 502, 503, 504) or attempt:
                    raise
            except (urllib.error.URLError, TimeoutError) as exc:
                reason = getattr(exc, 'reason', exc)
                status = http_status(exc)
                if (isinstance(reason, ssl.SSLError) or attempt
                        or (status is not None and status not in (500, 502, 503, 504))):
                    raise
            time.sleep(1)


NETWORK = None


def transport():
    global NETWORK
    if NETWORK is None:
        NETWORK = Network()
    return NETWORK


def failure(exc):
    # Do not print exception URLs: proxy credentials may be present.
    reason = getattr(exc, 'reason', exc)
    status = http_status(exc)
    code, hint = 'network_error', '检查网络及代理的 HTTP/mixed 端口；浏览器可访问不代表 Python 可访问。'
    if status is not None:
        code = 'http_' + str(status)
        hint = {403: 'GitHub 拒绝访问或 API 限流，请检查响应权限或稍后重试。',
                429: 'GitHub 限流，请稍后重试。',
                407: '代理要求身份验证，请检查代理配置。'}.get(status, '远程 HTTP 请求失败，请稍后重试或检查网络。')
    elif isinstance(reason, ssl.SSLError):
        code, hint = 'tls_error', '检查系统时间和可信证书配置，不要关闭证书验证。'
    elif isinstance(reason, (TimeoutError, socket.timeout)):
        code, hint = 'timeout', '连接或读取超时，请检查代理和网络。'
    elif isinstance(reason, socket.gaierror):
        code, hint = 'dns_error', '域名解析失败，请检查 DNS 或代理地址。'
    elif isinstance(exc, FileExistsError):
        code, hint = 'output_exists', '目标 ZIP 已存在，未覆盖；请选择新的暂存文件路径。'
    elif isinstance(exc, PermissionError):
        code, hint = 'filesystem_permission_error', '本地文件访问被拒绝，请检查技能目录或输出路径的权限。'
    elif isinstance(exc, zipfile.BadZipFile):
        code, hint = 'invalid_snapshot', '下载内容不是有效 ZIP 或已损坏，未保存；请检查下载来源或稍后重试。'
    elif isinstance(exc, ValueError):
        code, hint = 'invalid_configuration_or_snapshot', str(exc)
    return {'status': 'unknown', 'error_code': code, 'hint': hint}


def api(path):
    return json.loads(transport().read('https://api.github.com/repos/' + REPO + path))


def download_snapshot(sha, destination):
    if not re.fullmatch(r'[0-9a-f]{40}', sha):
        raise ValueError('Use the full 40-character remote_sha returned by the check')
    tree = api('/git/trees/' + sha + '?recursive=1')
    if tree.get('truncated'):
        raise ValueError('Remote manifest truncated')
    expected = {x['path']: x['sha'] for x in tree['tree'] if x['type'] == 'blob'}
    if 'SKILL.md' not in expected or 'scripts/paper_artifacts.py' not in expected:
        raise ValueError('Remote skill manifest incomplete')
    data = transport().read('https://codeload.github.com/' + REPO + '/zip/' + sha)
    prefix = 'article-skill-' + sha + '/'
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = [x for x in archive.infolist() if not x.is_dir()]
        names = [x.filename for x in members]
        if len(names) != len(set(names)) or set(names) != {prefix + n for n in expected}:
            raise ValueError('Snapshot file list does not match the pinned commit')
        for name, digest in expected.items():
            if '..' in Path(name).parts or Path(name).is_absolute() or '\\' in name:
                raise ValueError('Unsafe snapshot path')
            if blob_hash(archive.read(prefix + name)) != digest:
                raise ValueError('Snapshot content does not match the pinned commit')
    destination = Path(destination).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as handle:
        handle.write(data)
    return {'status': 'snapshot_verified', 'remote_sha': sha, 'archive': str(destination)}


def remote_head():
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
    extra = []
    for folder, dirs, files in os.walk(skill):
        dirs[:] = [name for name in dirs if name not in LOCAL_DIRS]
        for name in files:
            path = Path(folder) / name
            relative = path.relative_to(skill).as_posix()
            if path.suffix in ('.pyc', '.pyo') or relative == 'article-skill.zip':
                continue
            if relative not in expected:
                extra.append(relative)
    return changed, sorted(extra)


def check(skill):
    skill = Path(skill).resolve()
    if not (skill / 'SKILL.md').is_file():
        raise ValueError('Pass the actual installed skill directory containing SKILL.md')
    branch, remote_sha = remote_head()
    result = dict(skill_dir=str(skill), remote=REMOTE, branch=branch, remote_sha=remote_sha)
    changed, extra = compare_tree(skill, api('/git/trees/' + remote_sha + '?recursive=1'))
    result.update(changed_files=changed, extra_files=extra)
    result['status'] = 'content_equal' if not changed and not extra else 'different_unversioned'
    return result



def main():
    global NETWORK
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-dir', default=str(Path(__file__).resolve().parents[1]))
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--proxy', help='HTTP/mixed proxy endpoint, e.g. http://127.0.0.1:<port>')
    group.add_argument('--direct', action='store_true', help='Explicitly bypass proxy for this invocation')
    parser.add_argument('--download-sha', help='Download and verify this already checked commit, without installing')
    parser.add_argument('--output', help='New ZIP path; existing files are never overwritten')
    args = parser.parse_args()
    try:
        NETWORK = Network(args.proxy, args.direct)
        if bool(args.download_sha) != bool(args.output):
            raise ValueError('--download-sha and --output must be used together')
        result = download_snapshot(args.download_sha, args.output) if args.download_sha else check(args.skill_dir)
        result['network_mode'] = NETWORK.mode
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps(failure(exc), ensure_ascii=False))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
