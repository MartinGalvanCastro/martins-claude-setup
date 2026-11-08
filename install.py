#!/usr/bin/env python3
"""Idempotent installer for Windows, macOS and Linux. Backs up every file it would change.

Usage: python install.py [--target claude|opencode|codex|all] [--no-plugins]
  (on macOS/Linux: python3; on Windows: python or py)
Target folders: CLAUDE_HOME (~/.claude), OPENCODE_CONFIG_DIR (~/.config/opencode), CODEX_HOME (~/.codex).
Installs only the /ship command and the grill-me skill (sources in claude/; the opencode and codex files are
generated from them) and, for claude, the plugin settings. Agents are NOT copied: INSTALL.md lists them.
"""
import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

here = Path(__file__).resolve().parent
home = Path.home()
stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

PORTABILITY = (
    "> Portability note: names like `superpowers:*` and `ecc:*`, and the Skill tool, exist only in Claude Code. "
    "Elsewhere do the same by hand: write the plan file, use TDD, work in a git worktree. "
    "Use the OpenCode, Codex column of the Agents table, and skip the language reviewers. "
    "Agent names are role definitions: if this tool cannot launch subagents, adopt the role inline.\n\n"
)


def put(dst: Path, text: str) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        if dst.read_text(encoding="utf-8") == text:
            return
        shutil.copy2(dst, dst.with_name(f"{dst.name}.bak-{stamp}"))
    dst.write_text(text, encoding="utf-8")


def parse(path: Path) -> tuple[dict, str]:
    _, front, body = path.read_text(encoding="utf-8").split("---\n", 2)
    meta = dict(line.split(": ", 1) for line in front.strip().splitlines())
    return meta, body.lstrip("\n")


def sources(kind: str) -> list[Path]:
    return sorted((here / "claude" / kind).glob("*.md"))


def skill_dirs() -> list[Path]:
    return [d for d in sorted((here / "claude" / "skills").iterdir()) if d.is_dir()]


def install_claude(no_plugins: bool) -> None:
    dest = Path(os.environ.get("CLAUDE_HOME") or home / ".claude")
    for f in sources("commands"):
        put(dest / "commands" / f.name, f.read_text(encoding="utf-8"))
    for d in skill_dirs():
        put(dest / "skills" / d.name / "SKILL.md", (d / "SKILL.md").read_text(encoding="utf-8"))

    # Merge marketplaces and the global plugin list. Existing values win: nothing already set
    # (model, statusLine, a plugin you turned off) is changed.
    plan = json.loads((here / "plugins.json").read_text(encoding="utf-8"))
    path = dest / "settings.json"
    cur = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    markets = cur.setdefault("extraKnownMarketplaces", {})
    for name, repo in plan["marketplaces"].items():
        markets.setdefault(name, {"source": {"source": "github", "repo": repo}})
    enabled = cur.setdefault("enabledPlugins", {})
    for plugin in plan["global"]:
        enabled.setdefault(plugin, True)
    put(path, json.dumps(cur, indent=2, ensure_ascii=False))
    print(f"claude: settings merged ({len(plan['marketplaces'])} marketplaces, {len(plan['global'])} global plugins)")

    claude = shutil.which("claude")
    if no_plugins:
        print("claude: skipped plugin download (--no-plugins)")
    elif not claude:
        print("claude: CLI not found; add the marketplaces and plugins from plugins.json with /plugin")
    else:
        steps = [["plugin", "marketplace", "add", r] for r in plan["marketplaces"].values()]
        steps += [["plugin", "install", p] for p in plan["global"]]
        for args in steps:
            print("+ claude", " ".join(args))
            if subprocess.run([claude, *args]).returncode != 0:
                print("  failed, continuing")
    print(f"claude: done in {dest}. Restart Claude Code.")


def install_opencode() -> None:
    dest = Path(os.environ.get("OPENCODE_CONFIG_DIR") or home / ".config" / "opencode")
    for f in sources("commands"):
        meta, body = parse(f)
        put(dest / "command" / f.name, f"---\ndescription: {meta['description']}\n---\n\n{PORTABILITY}{body}")
    for d in skill_dirs():
        put(dest / "skill" / d.name / "SKILL.md", (d / "SKILL.md").read_text(encoding="utf-8"))
    print(f"opencode: done in {dest}. Restart OpenCode.")


def install_codex() -> None:
    dest = Path(os.environ.get("CODEX_HOME") or home / ".codex")
    for d in skill_dirs():
        put(dest / "skills" / d.name / "SKILL.md", (d / "SKILL.md").read_text(encoding="utf-8"))
    for f in sources("commands"):
        meta, body = parse(f)
        put(dest / "prompts" / f.name, f"---\ndescription: {meta['description']}\n---\n\n{PORTABILITY}{body}")
    print(f"codex: done in {dest}. Restart Codex; run the command as /prompts:ship.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=["claude", "opencode", "codex", "all"], default="claude")
    ap.add_argument("--no-plugins", action="store_true", help="claude target: skip plugin download")
    a = ap.parse_args()
    if a.target in ("claude", "all"):
        install_claude(a.no_plugins)
    if a.target in ("opencode", "all"):
        install_opencode()
    if a.target in ("codex", "all"):
        install_codex()
