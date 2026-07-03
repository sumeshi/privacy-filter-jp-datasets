#!/usr/bin/env python3
"""Validate span-annotated JSONL training/benchmark files.

Checks each row against this project's format: {"text": str, "spans":
[{"start": int, "end": int, "label": str}]} with Unicode character offsets
(start inclusive, end exclusive). Errors set the exit code to 1.

Usage:
  python3 validate_jsonl.py FILE [FILE...] [--labels PATH]
                            [--against FILE ...] [--quiet]

--against reports an error for any row whose normalized text also appears in
one of the given files (train/benchmark leakage check).
"""
import argparse
import collections
import json
from pathlib import Path
import sys

DEFAULT_LABELS = Path(__file__).resolve().parents[3] / "label_space" / "jp-basic.json"


def load_labels(path: str) -> set[str]:
    with open(path, encoding="utf-8") as f:
        spec = json.load(f)
    return {entry["name"] for entry in spec["labels"]}


def validate_row(row, allowed: set[str], errors: list[str], lineno: int) -> int:
    if not isinstance(row, dict):
        errors.append(f"line {lineno}: row is not an object")
        return 0
    text = row.get("text")
    spans = row.get("spans")
    if not isinstance(text, str) or not text:
        errors.append(f"line {lineno}: missing or empty 'text'")
        return 0
    if not isinstance(spans, list):
        errors.append(f"line {lineno}: 'spans' is not a list")
        return 0
    seen: list[tuple[int, int]] = []
    for i, span in enumerate(spans):
        where = f"line {lineno} span {i}"
        if not isinstance(span, dict):
            errors.append(f"{where}: span is not an object")
            continue
        start, end, label = span.get("start"), span.get("end"), span.get("label")
        if not isinstance(start, int) or not isinstance(end, int):
            errors.append(f"{where}: start/end must be int")
            continue
        if not (0 <= start < end <= len(text)):
            errors.append(f"{where}: bad offsets [{start},{end}) for text length {len(text)}")
            continue
        if label not in allowed:
            errors.append(f"{where}: unknown label {label!r}")
        if not text[start:end].strip():
            errors.append(f"{where}: span text is whitespace-only")
        for s2, e2 in seen:
            if start < e2 and s2 < end:
                errors.append(f"{where}: overlaps span [{s2},{e2})")
        seen.append((start, end))
    return len(spans)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--labels", default=str(DEFAULT_LABELS))
    ap.add_argument("--against", nargs="*", default=[])
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    allowed = load_labels(args.labels)
    against_texts: dict[str, str] = {}
    for path in args.against:
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line:
                against_texts.setdefault(json.loads(line)["text"].strip(), path)

    any_error = False
    for path in args.files:
        errors: list[str] = []
        label_hist: collections.Counter = collections.Counter()
        texts: collections.Counter = collections.Counter()
        n_rows = n_spans = 0
        for lineno, line in enumerate(open(path, encoding="utf-8"), 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"line {lineno}: invalid JSON ({e})")
                continue
            n_rows += 1
            n_spans += validate_row(row, allowed, errors, lineno)
            if isinstance(row, dict) and isinstance(row.get("text"), str):
                texts[row["text"]] += 1
                for span in row.get("spans") or []:
                    if isinstance(span, dict) and span.get("label"):
                        label_hist[span["label"]] += 1
                hit = against_texts.get(row["text"].strip())
                if hit:
                    errors.append(f"line {lineno}: text also present in {hit} (leak)")

        dups = sum(c - 1 for c in texts.values() if c > 1)
        status = "FAIL" if errors else "ok"
        print(f"{path}: {status} rows={n_rows} spans={n_spans} dup_texts={dups}")
        if not args.quiet:
            for label in sorted(label_hist):
                print(f"    {label}: {label_hist[label]}")
            for msg in errors[:50]:
                print(f"    ERROR {msg}")
            if len(errors) > 50:
                print(f"    ... and {len(errors) - 50} more errors")
        if dups and not args.quiet:
            print(f"    WARNING: {dups} duplicate text rows")
        any_error = any_error or bool(errors)

    return 1 if any_error else 0


if __name__ == "__main__":
    sys.exit(main())
