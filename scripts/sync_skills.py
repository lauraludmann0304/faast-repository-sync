#!/usr/bin/env python3
"""Synchronize FAAST Markdown skill files between local repository clones."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def markdown_files(root: Path) -> dict[Path, Path]:
    if not root.is_dir():
        raise FileNotFoundError(f"Skills directory does not exist: {root}")
    return {
        path.relative_to(root): path
        for path in root.rglob("*.md")
        if path.is_file()
    }


def inject_token(repository_url: str, token: str, token_user: str) -> str:
    parts = urlsplit(repository_url)
    if parts.scheme != "https" or not parts.hostname:
        raise ValueError("Token injection supports HTTPS repository URLs only")
    if parts.username or parts.password:
        raise ValueError("Repository URL must not already contain credentials")
    host = parts.hostname
    if parts.port:
        host += f":{parts.port}"
    netloc = f"{quote(token_user, safe='')}:{quote(token, safe='')}@{host}"
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


def synchronize(source_root: Path, target_root: Path, delete: bool, dry_run: bool) -> dict:
    source = markdown_files(source_root)
    target_root.mkdir(parents=True, exist_ok=True)
    target = markdown_files(target_root)

    result = {"copied": [], "updated": [], "deleted": [], "unchanged": []}

    for relative_path, source_path in sorted(source.items(), key=lambda item: str(item[0])):
        target_path = target_root / relative_path
        if not target_path.exists():
            result["copied"].append(relative_path.as_posix())
            if not dry_run:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path)
        elif sha256(source_path) != sha256(target_path):
            result["updated"].append(relative_path.as_posix())
            if not dry_run:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path)
        else:
            result["unchanged"].append(relative_path.as_posix())

    if delete:
        for relative_path, target_path in sorted(target.items(), key=lambda item: str(item[0])):
            if relative_path not in source:
                result["deleted"].append(relative_path.as_posix())
                if not dry_run:
                    target_path.unlink()
                    parent = target_path.parent
                    while parent != target_root and parent.exists() and not any(parent.iterdir()):
                        parent.rmdir()
                        parent = parent.parent

    result["summary"] = {key: len(value) for key, value in result.items() if isinstance(value, list)}
    result["dry_run"] = dry_run
    result["delete_enabled"] = delete
    result["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repo", type=Path)
    parser.add_argument("--target-repo", type=Path)
    parser.add_argument("--source-skills-path", default="content/skills")
    parser.add_argument("--target-skills-path", default="content/skills")
    parser.add_argument("--delete", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", type=Path, default=Path("sync-report.json"))
    parser.add_argument("--inject-token", nargs=2, metavar=("URL", "TOKEN"))
    parser.add_argument("--token-user", default="oauth2")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.inject_token:
        url, token = args.inject_token
        print(inject_token(url, token, args.token_user))
        return 0
    if args.source_repo is None or args.target_repo is None:
        raise SystemExit("--source-repo and --target-repo are required")

    source_root = args.source_repo / args.source_skills_path
    target_root = args.target_repo / args.target_skills_path
    result = synchronize(source_root, target_root, args.delete, args.dry_run)
    args.report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
