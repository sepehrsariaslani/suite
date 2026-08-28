#!/usr/bin/env python3
"""Audit Persian gettext coverage for literal runtime strings in Suite Mail."""

from __future__ import annotations

import argparse
import ast
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIL_ROOT = ROOT / "frontend" / "src" / "apps" / "mail"
DEFAULT_CATALOGUE = ROOT / "suite" / "locale" / "fa.po"
SOURCE_SUFFIXES = {".js", ".ts", ".vue"}
PLACEHOLDER = re.compile(
    r"\{(?:\d+|[A-Za-z_][A-Za-z0-9_]*)\}|%\([^)]+\)[#0+\-]?\d*(?:\.\d+)?[a-zA-Z]|%[#0+\-]?\d*(?:\.\d+)?[a-zA-Z]"
)


def _decode_javascript_string(raw: str, quote: str) -> str:
    if quote in {"'", '"'}:
        return ast.literal_eval(f"{quote}{raw}{quote}")
    return bytes(raw, "utf-8").decode("unicode_escape") if "\\" in raw else raw


def literal_runtime_keys(source: str) -> list[str]:
    keys: list[str] = []
    pattern = re.compile(r"(?<![\w$])__\s*\(\s*(['\"`])")
    for match in pattern.finditer(source):
        quote = match.group(1)
        index = match.end()
        escaped = False
        chars: list[str] = []
        while index < len(source):
            char = source[index]
            if escaped:
                chars.extend(("\\", char))
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                raw = "".join(chars)
                if quote != "`" or "${" not in raw:
                    key = _decode_javascript_string(raw, quote)
                    if key:
                        keys.append(key)
                break
            else:
                chars.append(char)
            index += 1
    return keys


def mail_runtime_keys() -> set[str]:
    keys: set[str] = set()
    for path in MAIL_ROOT.rglob("*"):
        if path.is_file() and path.suffix in SOURCE_SUFFIXES and not path.name.endswith(".test.ts"):
            keys.update(literal_runtime_keys(path.read_text(encoding="utf-8")))
    return keys


def _po_value(lines: list[str], field: str) -> str | None:
    for index, line in enumerate(lines):
        if not line.startswith(f"{field} "):
            continue
        parts = [line[len(field) + 1 :]]
        for continuation in lines[index + 1 :]:
            if not continuation.startswith('"'):
                break
            parts.append(continuation)
        try:
            return "".join(ast.literal_eval(part) for part in parts)
        except (SyntaxError, ValueError):
            return None
    return None


def read_catalogue(path: Path) -> tuple[dict[str, str], set[str]]:
    entries: list[tuple[str, str]] = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8")):
        lines = block.splitlines()
        msgid = _po_value(lines, "msgid")
        msgstr = _po_value(lines, "msgstr")
        if msgid:
            entries.append((msgid, msgstr or ""))

    counts = Counter(msgid for msgid, _ in entries)
    duplicates = {msgid for msgid, count in counts.items() if count > 1}
    return dict(entries), duplicates


def placeholders(value: str) -> Counter[str]:
    return Counter(PLACEHOLDER.findall(value))


def audit(catalogue: Path) -> tuple[list[str], list[str], list[str]]:
    keys = mail_runtime_keys()
    translations, duplicates = read_catalogue(catalogue)
    missing = sorted((key for key in keys if not translations.get(key, "").strip()), key=str.casefold)
    mismatches = sorted(
        (
            key
            for key in keys
            if translations.get(key, "").strip()
            and placeholders(key) != placeholders(translations[key])
        ),
        key=str.casefold,
    )
    return missing, sorted(duplicates, key=str.casefold), mismatches


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalogue", type=Path, default=DEFAULT_CATALOGUE)
    parser.add_argument("--show", action="store_true", help="Print individual failures")
    args = parser.parse_args()

    missing, duplicates, mismatches = audit(args.catalogue)
    print(
        f"runtime_keys={len(mail_runtime_keys())} "
        f"missing_or_empty={len(missing)} duplicates={len(duplicates)} "
        f"placeholder_mismatches={len(mismatches)}"
    )
    if args.show:
        for label, values in (
            ("missing_or_empty", missing),
            ("duplicate", duplicates),
            ("placeholder_mismatch", mismatches),
        ):
            for value in values:
                print(f"{label}: {value}")
    if missing or duplicates or mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
