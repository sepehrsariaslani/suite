#!/usr/bin/env python3
"""Audit Persian gettext coverage for literal runtime strings in Suite Mail."""

from __future__ import annotations

import argparse
import ast
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
MAIL_ROOT = ROOT / "frontend" / "src" / "apps" / "mail"
SHELL_ROOT = ROOT / "frontend" / "src" / "shell"
DEFAULT_CATALOGUE = ROOT / "suite" / "locale" / "fa.po"
SOURCE_SUFFIXES = {".js", ".ts", ".vue"}
PLACEHOLDER = re.compile(
    r"\{(?:\d+|[A-Za-z_][A-Za-z0-9_]*)\}|%\([^)]+\)[#0+\-]?\d*(?:\.\d+)?[a-zA-Z]|%[#0+\-]?\d*(?:\.\d+)?[a-zA-Z]"
)

DIRECT_ATTRIBUTE = re.compile(
    r"(?<![:\w-])(?:aria-label|label|title|placeholder|description|message|tooltip|text)\s*=\s*"
    r"(?P<quote>['\"])(?P<value>.*?)(?P=quote)"
)
SCRIPT_PROPERTY = re.compile(
    r"\b(?:label|title|placeholder|description|message|tooltip|text)\s*:\s*"
    r"(?P<quote>['\"`])(?P<value>.*?)(?P=quote)"
)
TEXT_NODE = re.compile(r">(?P<value>[^<{][^<{]*?)<")
TECHNICAL_ONLY = re.compile(
    r"^(?:#[0-9A-Fa-f]{3,8}|[A-Z\d_.:/+-]+|[\w.+*-]+@[\w.-]+|"
    r"(?:[\w*-]+\.)+[A-Za-z]{2,}|https?://\S+|/\S+|v=[A-Z][^ ]*)$"
)
TECHNICAL_TERMS = {
    "API",
    "ARF",
    "CSV",
    "DKIM",
    "DMARC",
    "DNS",
    "HTML",
    "IMAP",
    "JMAP",
    "JSON",
    "OAuth",
    "SMTP",
    "SPF",
    "TLS",
    "URL",
    "XLSX",
}


@dataclass(frozen=True)
class UICandidate:
    path: Path
    line: int
    column: int
    text: str


def _without_comments(source: str) -> str:
    """Remove comments while preserving newlines for useful audit locations."""

    def preserve_newlines(match: re.Match[str]) -> str:
        marker = " i18n-audit-ignore " if "i18n-audit-ignore" in match.group(0) else ""
        return marker + "\n" * match.group(0).count("\n")

    source = re.sub(r"<!--.*?-->", preserve_newlines, source, flags=re.DOTALL)
    source = re.sub(r"/\*.*?\*/", preserve_newlines, source, flags=re.DOTALL)
    return source


def _is_user_facing(value: str) -> bool:
    value = " ".join(value.split()).strip()
    if not value or value in TECHNICAL_TERMS or TECHNICAL_ONLY.fullmatch(value):
        return False
    if (
        "${" in value
        or any(character in value for character in "{}<>")
        or re.fullmatch(r"[a-z][a-z\d_-]*", value)
        or re.fullmatch(r"(?:&[A-Za-z]+;)+", value)
        or value.startswith(("lucide-", "suite.", "mail-"))
    ):
        return False
    return bool(re.search(r"[A-Za-z]", value))


def candidates_from_source(path: Path, source: str) -> list[UICandidate]:
    """Return likely untranslated visible strings from one Vue/TS/JS source file."""

    if ".test." in path.name or ".spec." in path.name:
        return []

    source = _without_comments(source)
    candidates: list[UICandidate] = []
    in_technical_block = False
    in_template = False

    for line_number, raw_line in enumerate(source.splitlines(), 1):
        if "i18n-audit-ignore" in raw_line or raw_line.lstrip().startswith("//"):
            continue

        line = raw_line
        if path.suffix == ".vue" and "<template" in line:
            in_template = True
        if path.suffix == ".vue" and "</template>" in line:
            template_ends = True
        else:
            template_ends = False
        if re.search(r"<(?:code|pre)\b", line, flags=re.IGNORECASE):
            in_technical_block = True
        visible_line = re.sub(
            r"<(?:code|pre)\b[^>]*>.*?</(?:code|pre)>", "", line, flags=re.IGNORECASE
        )

        matches: list[tuple[int, str]] = []
        if not in_technical_block or visible_line != line:
            patterns = (DIRECT_ATTRIBUTE,) if in_template else (SCRIPT_PROPERTY,)
            for pattern in patterns:
                for match in pattern.finditer(visible_line):
                    matches.append((match.start(), match.group("value")))
            if in_template:
                for match in TEXT_NODE.finditer(visible_line):
                    matches.append((match.start(), match.group("value")))

        for column, value in sorted(matches):
            normalized = " ".join(value.split()).strip()
            if _is_user_facing(normalized):
                candidates.append(UICandidate(path, line_number, column + 1, normalized))

        if re.search(r"</(?:code|pre)>", line, flags=re.IGNORECASE):
            in_technical_block = False
        if template_ends:
            in_template = False

    return candidates


def audited_source_paths() -> list[Path]:
    paths: list[Path] = []
    for root in (MAIL_ROOT, SHELL_ROOT):
        paths.extend(
            path
            for path in root.rglob("*")
            if path.is_file()
            and path.suffix in SOURCE_SUFFIXES
            and ".test." not in path.name
            and ".spec." not in path.name
        )
    return sorted(paths)


def untranslated_ui_candidates(paths: Iterable[Path] | None = None) -> list[UICandidate]:
    paths = audited_source_paths() if paths is None else paths
    return sorted(
        (
            candidate
            for path in paths
            for candidate in candidates_from_source(path, path.read_text(encoding="utf-8"))
        ),
        key=lambda item: (str(item.path), item.line, item.column, item.text.casefold()),
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


def audit(catalogue: Path) -> tuple[list[str], list[str], list[str], list[UICandidate]]:
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
    return missing, sorted(duplicates, key=str.casefold), mismatches, untranslated_ui_candidates()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalogue", type=Path, default=DEFAULT_CATALOGUE)
    parser.add_argument("--show", action="store_true", help="Print individual failures")
    args = parser.parse_args()

    missing, duplicates, mismatches, direct_candidates = audit(args.catalogue)
    print(
        f"runtime_keys={len(mail_runtime_keys())} "
        f"missing_or_empty={len(missing)} duplicates={len(duplicates)} "
        f"placeholder_mismatches={len(mismatches)} "
        f"direct_ui_candidates={len(direct_candidates)}"
    )
    if args.show:
        for label, values in (
            ("missing_or_empty", missing),
            ("duplicate", duplicates),
            ("placeholder_mismatch", mismatches),
        ):
            for value in values:
                print(f"{label}: {value}")
        for candidate in direct_candidates:
            print(
                f"direct_ui: {candidate.path.relative_to(ROOT)}:{candidate.line}:"
                f"{candidate.column}: {candidate.text}"
            )
    if missing or duplicates or mismatches or direct_candidates:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
