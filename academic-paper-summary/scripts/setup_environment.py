"""Create/reuse a user-local article-skill venv; never install into the host Python."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import venv


def default_directory():
    return Path(os.environ.get('CODEX_HOME') or Path.home()/'.codex').expanduser()/'skill-state/article-skill/.venv'


def interpreter(directory):
    return directory/('Scripts/python.exe' if os.name=='nt' else 'bin/python')


def setup(directory, requirements, repair=False):
    directory=directory.expanduser().resolve()
    python=interpreter(directory)
    stamp=directory/'article-skill-environment.json'
    fingerprint=hashlib.sha256(requirements.read_bytes()).hexdigest()
    if not python.exists():
        if directory.exists() and any(directory.iterdir()):
            raise RuntimeError('Environment directory is nonempty but has no Python; choose a new --venv path. Nothing was deleted.')
        venv.EnvBuilder(with_pip=True).create(directory)
    probe=subprocess.run([str(python),'-c',
        'import sys; assert sys.version_info >= (3,10); assert sys.prefix != sys.base_prefix; import docx, fitz, PIL'],
        capture_output=True,text=True)
    try:
        saved=json.loads(stamp.read_text(encoding='utf-8'))
    except (OSError,ValueError):
        saved={}
    if repair or probe.returncode or saved.get('requirements_sha256')!=fingerprint:
        # Refuse a directory containing an ordinary/global interpreter.
        subprocess.run([str(python),'-c',
            'import sys; assert sys.version_info >= (3,10); assert sys.prefix != sys.base_prefix'],check=True)
        subprocess.run([str(python),'-m','pip','install','-r',str(requirements)],check=True)
        subprocess.run([str(python),'-m','pip','check'],check=True)
        verification=subprocess.run([str(python),str(requirements.parent/'scripts/check_environment.py'),'--json','--smoke'],
                                    capture_output=True,text=True,encoding='utf-8')
        print(verification.stdout)
        if verification.returncode not in (0,2):
            raise RuntimeError('Environment verification failed: '+verification.stdout+verification.stderr)
        stamp.write_text(json.dumps({'requirements_sha256':fingerprint,'python':str(python)},indent=2),encoding='utf-8')
    return python


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--venv',type=Path,default=default_directory())
    parser.add_argument('--repair',action='store_true',help='Recheck/install required packages without deleting the environment')
    args=parser.parse_args()
    try:
        if sys.version_info < (3,10):
            raise RuntimeError('Use Python 3.10 or newer to create the environment')
        python=setup(args.venv,Path(__file__).resolve().parents[1]/'requirements.txt',args.repair)
        print(json.dumps({'python':str(python),'note':'Use this absolute interpreter path for all skill scripts; no activation needed.'},ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f'ERROR [{type(exc).__name__}]: {exc}\n'
              'This is an environment setup failure, not proof that Python is uninstalled. '
              'For permission/path errors use a writable --venv path in the current execution context; '
              'for pip errors fix the reported dependency/network issue and retry. '
              'No fallback to global package installation and no directory was deleted.',file=sys.stderr)
        return 1


if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
