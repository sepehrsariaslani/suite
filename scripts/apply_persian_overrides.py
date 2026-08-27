#!/usr/bin/env python3
"""Apply reviewed Persian override dictionaries to Suite's gettext catalogue."""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path

from persian_core_ux_overrides import CORE_VISIBLE_UX_OVERRIDES
from persian_overrides import PERSIAN_OVERRIDES

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOGUE = ROOT / "suite" / "locale" / "fa.po"
PLACEHOLDER = re.compile(r"\{\d+\}")


def quoted(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def message_id(block: str) -> str | None:
    match = re.search(r"^msgid (.+)$", block, re.MULTILINE)
    if not match:
        return None
    try:
        return ast.literal_eval(match.group(1))
    except (SyntaxError, ValueError):
        return None


def apply(catalogue: Path, *, check: bool = False) -> tuple[int, int]:
    overrides = {**PERSIAN_OVERRIDES, **CORE_VISIBLE_UX_OVERRIDES}
    source = catalogue.read_text(encoding="utf-8")
    blocks = source.rstrip().split("\n\n")
    seen: set[str] = set()
    updated = 0

    for index, block in enumerate(blocks):
        msgid = message_id(block)
        if not msgid or msgid not in overrides:
            continue
        translation = overrides[msgid]
        if set(PLACEHOLDER.findall(msgid)) != set(PLACEHOLDER.findall(translation)):
            raise ValueError(f"Placeholder mismatch: {msgid!r} -> {translation!r}")
        seen.add(msgid)
        replacement = f"msgstr {quoted(translation)}"
        changed = re.sub(r"^msgstr .*$", replacement, block, count=1, flags=re.MULTILINE)
        if changed != block:
            blocks[index] = changed
            updated += 1

    missing = sorted(set(overrides) - seen, key=str.casefold)
    for msgid in missing:
        translation = overrides[msgid]
        if set(PLACEHOLDER.findall(msgid)) != set(PLACEHOLDER.findall(translation)):
            raise ValueError(f"Placeholder mismatch: {msgid!r} -> {translation!r}")
        blocks.append(f"msgid {quoted(msgid)}\nmsgstr {quoted(translation)}")

    rendered = "\n\n".join(blocks).rstrip() + "\n"
    if check:
        if rendered != source:
            raise SystemExit("Persian catalogue is not synchronized with reviewed overrides")
    else:
        catalogue.write_text(rendered, encoding="utf-8")
    return updated, len(missing)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--catalogue", type=Path, default=DEFAULT_CATALOGUE)
    args = parser.parse_args()
    updated, added = apply(args.catalogue, check=args.check)
    print(f"updated={updated} added={added} catalogue={args.catalogue}")


if __name__ == "__main__":
    main()
