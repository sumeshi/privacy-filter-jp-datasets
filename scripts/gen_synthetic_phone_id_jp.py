#!/usr/bin/env python3
"""Generate synthetic Japanese phone-number and government/official-ID examples.

All data is entirely fabricated. No real PII is used.
Labels: private_phone, account_number.
"""
import argparse
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).parent))
import pii_values as pv

DEFAULT_OUT = Path(__file__).resolve().parents[1] / "generated" / "synthetic_phone_id_jp.jsonl"

# Templates: (prefix, suffix). Span = phone number between them.
PHONE_TEMPLATES_SIMPLE = [
    ("TEL：", ""),
    ("Tel: ", ""),
    ("FAX：", ""),
    ("携帯：", ""),
    ("代表電話：", ""),
    ("緊急連絡先：", ""),
    ("日中のご連絡先：", ""),
    ("お電話番号：", ""),
    ("", ""),
]

PHONE_TEMPLATES_SENTENCE = [
    ("折り返しは", "までお願いします。"),
    ("ご不明点は", "へご連絡ください。"),
    ("お問い合わせは", "まで。"),
    ("担当者へは", "にてご連絡ください。"),
]

LANDLINE_KINDS = ["landline2", "landline3", "landline4"]

# Some prefixes imply a phone kind; keep number and label text consistent.
TEMPLATE_KIND_CONSTRAINTS: dict[str, list[str]] = {
    "携帯：": ["mobile"],
    "FAX：": LANDLINE_KINDS,
    "代表電話：": LANDLINE_KINDS + ["freedial", "navi"],
}

PHONE_DOUBLE_TEMPLATES = [
    # Inline double: "TEL：{a}／FAX：{b}"
    "inline_slash",
    # Two-line: "TEL：{a}\nFAX：{b}"
    "newline",
]

INFIX_LABEL_A = "TEL："
INFIX_LABEL_B = "FAX："

# Mapping: jp_id kind → list of (prefix, suffix) templates
ID_TEMPLATES: dict[str, list[tuple[str, str]]] = {
    "mynumber": [
        ("マイナンバー：", ""),
        ("個人番号：", ""),
        ("個人番号（マイナンバー）：", ""),
        ("マイナンバーは", "です。"),
    ],
    "license": [
        ("運転免許証番号：", ""),
        ("免許証番号：第", "号"),  # span = digits only; 第/号 outside
    ],
    "passport": [
        ("旅券番号：", ""),
        ("パスポート番号：", ""),
    ],
    "nenkin": [
        ("基礎年金番号：", ""),
    ],
    "hoken": [
        ("保険証記号番号：", ""),
        ("被保険者記号・番号：", ""),
    ],
    "bank": [
        ("口座番号：", ""),
        # bank prefix with fictional bank name (suffix always "")
        ("__bank__", ""),
        ("__bank_tooza__", ""),
    ],
    "yucho": [
        ("ゆうちょ記号番号：", ""),
    ],
    "zairyu": [
        ("在留カード番号：", ""),
    ],
}


def _bank_prefix(rng: random.Random, tooza: bool = False) -> str:
    bank = rng.choice(pv.FICTIONAL_BANKS)
    branch = rng.choice(pv.BANK_BRANCHES)
    acct_type = "当座" if tooza else "普通"
    return f"{bank}　{branch}　{acct_type}　"


def _make_phone_row(rng: random.Random) -> dict:
    """Build a row with one or two phone spans."""
    double = rng.random() < 0.10
    if double:
        style = rng.choice(PHONE_DOUBLE_TEMPLATES)
        phone_a = pv.random_phone_jp(rng)
        phone_b = pv.random_phone_jp(rng, kind=rng.choice(LANDLINE_KINDS))
        if style == "inline_slash":
            text = f"{INFIX_LABEL_A}{phone_a}／{INFIX_LABEL_B}{phone_b}"
            start_a = len(INFIX_LABEL_A)
            end_a = start_a + len(phone_a)
            start_b = end_a + len("／") + len(INFIX_LABEL_B)
            end_b = start_b + len(phone_b)
        else:  # newline
            text = f"{INFIX_LABEL_A}{phone_a}\n{INFIX_LABEL_B}{phone_b}"
            start_a = len(INFIX_LABEL_A)
            end_a = start_a + len(phone_a)
            start_b = end_a + len("\n") + len(INFIX_LABEL_B)
            end_b = start_b + len(phone_b)
        assert text[start_a:end_a] == phone_a, f"double-a mismatch: {text[start_a:end_a]!r} != {phone_a!r}"
        assert text[start_b:end_b] == phone_b, f"double-b mismatch: {text[start_b:end_b]!r} != {phone_b!r}"
        spans = [
            {"start": start_a, "end": end_a, "label": "private_phone"},
            {"start": start_b, "end": end_b, "label": "private_phone"},
        ]
        return {"text": text, "spans": spans}

    # Single phone
    if rng.random() < 0.4:
        prefix, suffix = rng.choice(PHONE_TEMPLATES_SENTENCE)
    else:
        prefix, suffix = rng.choice(PHONE_TEMPLATES_SIMPLE)
    kinds = TEMPLATE_KIND_CONSTRAINTS.get(prefix)
    phone = pv.random_phone_jp(rng, kind=rng.choice(kinds) if kinds else None)
    text = f"{prefix}{phone}{suffix}"
    start = len(prefix)
    end = start + len(phone)

    # ~8% append 内線 (outside span)
    if rng.random() < 0.08:
        ext = rng.randint(1, 999)
        text = text + f"（内線{ext}）"

    assert text[start:end] == phone, f"phone mismatch: {text[start:end]!r} != {phone!r}"
    return {"text": text, "spans": [{"start": start, "end": end, "label": "private_phone"}]}


def _make_id_row(rng: random.Random) -> dict:
    """Build a row with one account_number span."""
    value, kind = pv.random_jp_id(rng)
    templates = ID_TEMPLATES[kind]
    prefix, suffix = rng.choice(templates)

    # Resolve bank prefix placeholders
    if prefix == "__bank__":
        prefix = _bank_prefix(rng, tooza=False)
    elif prefix == "__bank_tooza__":
        prefix = _bank_prefix(rng, tooza=True)

    text = f"{prefix}{value}{suffix}"
    start = len(prefix)
    end = start + len(value)
    assert text[start:end] == value, f"id mismatch: {text[start:end]!r} != {value!r}"
    return {"text": text, "spans": [{"start": start, "end": end, "label": "account_number"}]}


def generate(n: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        if rng.random() < 0.5:
            rows.append(_make_phone_row(rng))
        else:
            rows.append(_make_id_row(rng))
    rng.shuffle(rows)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("-n", "--count", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    rows = generate(args.count, args.seed)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # --- stderr stats ---
    label_counts: dict[str, int] = {}
    kind_counts: dict[str, int] = {}
    for row in rows:
        for span in row["spans"]:
            lbl = span["label"]
            label_counts[lbl] = label_counts.get(lbl, 0) + 1

    print("=== label counts ===", file=sys.stderr)
    for lbl, cnt in sorted(label_counts.items()):
        print(f"  {lbl}: {cnt}", file=sys.stderr)
    print(f"wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
