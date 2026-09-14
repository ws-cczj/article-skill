"""Emit the welcome once per local Codex user; store no paper or user content."""
from __future__ import annotations

import os
import sys
from pathlib import Path


WELCOME = "欢迎使用捶捶自己开发的article-skill。"


def first_use(state_dir: Path) -> bool:
    """Claim first use atomically, including concurrent invocations."""
    state_dir.mkdir(parents=True, exist_ok=True)
    try:
        with (state_dir / "welcomed").open("x", encoding="utf-8") as marker:
            marker.write("1\n")
    except FileExistsError:
        return False
    return True


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    codex_root = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex").expanduser()
    try:
        if first_use(codex_root / "skill-state" / "article-skill"):
            print(WELCOME)
    except OSError:
        print("Welcome state unavailable; use the current-conversation fallback.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
