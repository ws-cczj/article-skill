#!/bin/sh
# Python-independent entry point for macOS/Linux. Invoke with sh; no chmod needed.
set -eu
python_path=''
runtime_python=''
venv_path=''
check_only=0
while [ "$#" -gt 0 ]; do
    case "$1" in
        --python|--venv|--runtime-python)
            [ "$#" -ge 2 ] || { echo "Missing value for $1" >&2; exit 2; }
            case "$1" in
                --python) python_path=$2 ;;
                --runtime-python) runtime_python=$2 ;;
                --venv) venv_path=$2 ;;
            esac
            shift 2 ;;
        --check-only) check_only=1; shift ;;
        *) echo "Unknown option: $1" >&2; exit 2 ;;
    esac
done
script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
probe='import sys; assert sys.version_info >= (3,10), "Python 3.10+ required"; import venv, ensurepip; print(sys.executable)'
find_python() {
    if [ -n "$python_path" ]; then
        "$python_path" -c "$probe"
        return
    fi
    target=${venv_path:-${CODEX_HOME:-$HOME/.codex}/skill-state/article-skill/.venv}
    for candidate in "$target/bin/python" "$runtime_python" python3 python; do
        [ -n "$candidate" ] || continue
        if resolved=$("$candidate" -c "$probe"); then
            printf '%s\n' "$resolved"
            return 0
        fi
        printf 'Candidate unavailable or incompatible: %s (see diagnostics above)\n' "$candidate" >&2
    done
    return 1
}
if ! resolved=$(find_python); then
    echo 'No usable Python 3.10+ with venv and ensurepip found. No packages were installed.' >&2
    echo 'This does NOT prove Python is uninstalled. Check path/permission/sandbox and runtime diagnostics. In Codex discover Python with load_workspace_dependencies and pass --runtime-python <returned-path>. Only if no compatible accessible runtime exists, install Python and venv/ensurepip via your OS package manager or https://www.python.org/downloads/; then rerun.' >&2
    exit 2
fi
if [ "$check_only" -eq 1 ]; then
    printf 'Python ready: %s\nDiscovery only; packages, fonts and renderer not checked.\n' "$resolved"
    exit 0
fi
if [ -n "$venv_path" ]; then
    exec "$resolved" "$script_dir/setup_environment.py" --venv "$venv_path"
fi
exec "$resolved" "$script_dir/setup_environment.py"
