#!/usr/bin/env python3
"""Validate the Flare-Chronos release document system.

Checks
  1. Every entry line in CHANGELOG.md matches the entry format:
         [<hash>: ]dd/mm/yyyy — <file> — <action>: <summary>
     (the optional `<hash>: ` prefix names the commit that changed the
     document; stock `changeset version` output has no prefix and is accepted)
  2. Every non-empty summary line in new/changed fragments
     (.changeset/*.md) matches the fragment format (same, without hash).
  3. A change to a tracked document (a file submitted outside this repo)
     carries a fragment or a changelog update in the same change set.
  4. The `Phiên bản` in the exported Markdown files equals the one inside
     their corresponding PDFs.

Usage
    python3 scripts/check-docs.py --staged          # git hook (staged files)
    python3 scripts/check-docs.py --base <sha>      # CI (diff <sha>..HEAD)
    python3 scripts/check-docs.py --scan            # tree checks only

Options
    --require-tools   fail (instead of warn) when pdftotext is missing.
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # git repo root
CHANGELOG = ROOT / "CHANGELOG.md"
CHANGESET_DIR = ROOT / ".changeset"

# Documents submitted outside this repo. Extend as new submission docs appear.
TRACKED = {
    "exports/PROPOSAL.md",
    "exports/REPORT.md",
    "exports/MODEL_FLOW.md",
}
VERSIONED_DOCS = [
    ("exports/PROPOSAL.md", "exports/PROPOSAL.pdf"),
    ("exports/REPORT.md", "exports/REPORT.pdf"),
    ("exports/MODEL_FLOW.md", "exports/MODEL_FLOW.pdf"),
]

ACTIONS = "thay thế|thêm|sửa|xoá|cập nhật"
ENTRY_RE = re.compile(
    rf"^(?:[0-9a-f]{{7,40}}: )?\d{{2}}/\d{{2}}/\d{{4}} — \S+ — ({ACTIONS}): .+$"
)
FRAGMENT_RE = re.compile(rf"^\d{{2}}/\d{{2}}/\d{{4}} — \S+ — ({ACTIONS}): .+$")
MD_VERSION_RE = re.compile(r"\*\*Phiên bản:\*\*[^\n]*?(\d+\.\d+\.\d+)")
PDF_VERSION_RE = re.compile(r"Phiên bản[^\n]{0,80}?(\d+\.\d+\.\d+)")

failures: list[str] = []
warnings: list[str] = []


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], check=False, cwd=ROOT, text=True, capture_output=True
    )
    return result.stdout


def changed_files(mode: str, base: str | None) -> set[str]:
    if mode == "staged":
        out = git("diff", "--cached", "--name-only", "--diff-filter=ACMR")
        return {line for line in out.splitlines() if line}
    if base and set(base) != {"0"}:
        out = git("diff", "--name-only", "--diff-filter=ACMR", f"{base}..HEAD")
        return {line for line in out.splitlines() if line}
    previous = git("rev-parse", "--verify", "HEAD~1").strip()
    if previous:
        out = git("diff", "--name-only", "--diff-filter=ACMR", f"{previous}..HEAD")
        return {line for line in out.splitlines() if line}
    return set()


def check_changelog_format() -> None:
    if not CHANGELOG.exists():
        failures.append("CHANGELOG.md is missing")
        return
    for number, line in enumerate(CHANGELOG.read_text("utf8").splitlines(), 1):
        if line.startswith("- ") and not ENTRY_RE.match(line[2:]):
            failures.append(
                f"CHANGELOG.md:{number}: entry does not match the format "
                f"'[<hash>: ]dd/mm/yyyy — <file> — <action>: <summary>': {line}"
            )


def check_fragment_format(files: set[str]) -> None:
    for path in sorted(files):
        if not path.startswith(".changeset/") or not path.endswith(".md"):
            continue
        if Path(path).name in {"README.md", "config.json"}:
            continue
        file = ROOT / path
        if not file.exists():
            continue
        body = re.sub(r"^---[\s\S]*?---\s*", "", file.read_text("utf8"), count=1)
        for line in body.splitlines():
            line = line.strip()
            if line and not FRAGMENT_RE.match(line):
                failures.append(
                    f"{path}: fragment summary does not match the format "
                    f"'dd/mm/yyyy — <file> — <action>: <summary>': {line}"
                )


def check_presence(files: set[str]) -> None:
    touched = TRACKED & files
    if not touched:
        return
    has_fragment = any(
        path.startswith(".changeset/")
        and path.endswith(".md")
        and Path(path).name not in {"README.md", "config.json"}
        for path in files
    )
    has_changelog = "CHANGELOG.md" in files
    if not (has_fragment or has_changelog):
        for path in sorted(touched):
            failures.append(
                f"{path} changed without a changelog fragment. Add "
                f".changeset/<slug>.md in the same commit."
            )


def check_version_match(require_tools: bool) -> None:
    if not shutil.which("pdftotext"):
        message = "pdftotext not found; PDF/MD version check skipped"
        (failures if require_tools else warnings).append(message)
        return

    for md_name, pdf_name in VERSIONED_DOCS:
        md_file = ROOT / md_name
        pdf_file = ROOT / pdf_name
        if not (md_file.exists() and pdf_file.exists()):
            failures.append(f"{md_name} or {pdf_name} is missing")
            continue
        md_match = MD_VERSION_RE.search(md_file.read_text("utf8"))
        if not md_match:
            failures.append(f"{md_name} has no '**Phiên bản:**' line")
            continue
        pdf_text = subprocess.run(
            ["pdftotext", "-q", str(pdf_file), "-"],
            check=False,
            text=True,
            capture_output=True,
        ).stdout
        pdf_match = PDF_VERSION_RE.search(pdf_text)
        if not pdf_match:
            failures.append(f"{pdf_name}: no 'Phiên bản' version found in the text")
            continue
        if md_match.group(1) != pdf_match.group(1):
            failures.append(
                f"version mismatch: {md_name} v{md_match.group(1)} "
                f"≠ {pdf_name} v{pdf_match.group(1)} — re-export the PDFs "
                f"(uv run python exports/export_pdf.py)"
            )
        else:
            print(f"version match: v{md_match.group(1)} in {md_name} and {pdf_name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--staged", action="store_true")
    group.add_argument("--base")
    group.add_argument("--scan", action="store_true")
    parser.add_argument("--require-tools", action="store_true")
    args = parser.parse_args()

    files = (
        set()
        if args.scan
        else changed_files("staged" if args.staged else "diff", args.base)
    )

    check_version_match(args.require_tools)
    check_changelog_format()
    check_fragment_format(files)
    if not args.scan:
        check_presence(files)

    for warning in warnings:
        print(f"warning: {warning}")
    for failure in failures:
        print(f"error: {failure}")
    if failures:
        print(f"\ncheck-docs: {len(failures)} problem(s) found")
        return 1
    print("check-docs: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
