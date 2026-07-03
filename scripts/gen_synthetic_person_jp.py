#!/usr/bin/env python3
"""Generate synthetic Japanese personal-name examples.

All names are entirely fabricated. No real person's information is used.
Label: private_person.
"""
import argparse
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).parent))
import pii_values as pv

DEFAULT_OUT = Path(__file__).resolve().parents[1] / "generated" / "synthetic_person_jp.jsonl"

BUSINESS_TEMPLATES_SIMPLE = [
    ("氏名：", ""),
    ("お名前：", ""),
    ("担当：", ""),
    ("担当者：", ""),
    ("申込者：", ""),
    ("記入者：", ""),
    ("契約者名：", ""),
    ("宛名：", ""),
    ("", ""),
    ("ご注文者：", ""),
]

BUSINESS_TEMPLATES_SENTENCE = [
    ("本日の担当は", "です。"),
    ("", "が対応いたします。"),
    ("担当者は", "です。"),
    ("お客様担当は", "となっております。"),
]


def _make_business_row(rng: random.Random) -> dict:
    name = pv.random_person(rng)
    if rng.random() < 0.4:
        prefix, suffix = rng.choice(BUSINESS_TEMPLATES_SENTENCE)
    else:
        prefix, suffix = rng.choice(BUSINESS_TEMPLATES_SIMPLE)
    text = f"{prefix}{name}{suffix}"
    start = len(prefix)
    end = start + len(name)
    assert text[start:end] == name, f"biz mismatch: {text[start:end]!r} != {name!r}"
    return {"text": text, "spans": [{"start": start, "end": end, "label": "private_person"}]}


def _make_honorific_row(rng: random.Random) -> dict:
    name = pv.random_person(rng)
    honorific = rng.choice(["様", "さん", "殿", "先生"])
    template = rng.choice([
        "plain_suffix",
        "gotan_prefix",
    ])
    if template == "gotan_prefix":
        prefix = "ご担当の"
        text = f"{prefix}{name}{honorific}"
        start = len(prefix)
    else:
        text = f"{name}{honorific}"
        start = 0
    end = start + len(name)
    assert text[start:end] == name, f"honorific mismatch: {text[start:end]!r} != {name!r}"
    return {"text": text, "spans": [{"start": start, "end": end, "label": "private_person"}]}


def _make_company_row(rng: random.Random) -> dict:
    name = pv.random_person(rng)
    company = rng.choice(pv.COMPANIES)
    dept = rng.choice(pv.DEPARTMENTS)
    style = rng.choice(["company_name", "company_dept_name", "dept_name_san"])
    if style == "company_name":
        prefix = f"{company}の"
        text = f"{prefix}{name}"
        start = len(prefix)
        end = start + len(name)
        assert text[start:end] == name
        return {"text": text, "spans": [{"start": start, "end": end, "label": "private_person"}]}
    if style == "company_dept_name":
        prefix = f"{company}　{dept}　"
        text = f"{prefix}{name}"
        start = len(prefix)
        end = start + len(name)
        assert text[start:end] == name
        return {"text": text, "spans": [{"start": start, "end": end, "label": "private_person"}]}
    # dept_name_san
    prefix = f"{dept}の"
    suffix = "さん"
    text = f"{prefix}{name}{suffix}"
    start = len(prefix)
    end = start + len(name)
    assert text[start:end] == name
    return {"text": text, "spans": [{"start": start, "end": end, "label": "private_person"}]}


def _make_furigana_row(rng: random.Random) -> dict:
    spaced = rng.random() < 0.5
    kanji_name, kana_name = pv.random_person_pair(rng, spaced=spaced)
    style = rng.choice(["paren", "two_line"])
    if style == "paren":
        # "氏名：山田太郎（ヤマダタロウ）"
        prefix = "氏名："
        inner = f"（{kana_name}）"
        text = f"{prefix}{kanji_name}{inner}"
        start_k = len(prefix)
        end_k = start_k + len(kanji_name)
        start_r = end_k + len("（")
        end_r = start_r + len(kana_name)
        assert text[start_k:end_k] == kanji_name, f"paren kanji mismatch"
        assert text[start_r:end_r] == kana_name, f"paren kana mismatch"
        return {
            "text": text,
            "spans": [
                {"start": start_k, "end": end_k, "label": "private_person"},
                {"start": start_r, "end": end_r, "label": "private_person"},
            ],
        }
    # two_line: "フリガナ：ヤマダ　タロウ\n氏名：山田　太郎"
    # Force spaced for two-line
    sur_k, sur_r, _ = rng.choice(pv.SURNAMES)
    giv_k, giv_r, _ = rng.choice(pv.GIVEN_NAMES)
    kana_spaced = f"{sur_r}　{giv_r}"
    kanji_spaced = f"{sur_k}　{giv_k}"
    line1_prefix = "フリガナ："
    line2_prefix = "氏名："
    text = f"{line1_prefix}{kana_spaced}\n{line2_prefix}{kanji_spaced}"
    start_r = len(line1_prefix)
    end_r = start_r + len(kana_spaced)
    start_k = len(line1_prefix) + len(kana_spaced) + len("\n") + len(line2_prefix)
    end_k = start_k + len(kanji_spaced)
    assert text[start_r:end_r] == kana_spaced, f"two_line kana mismatch: {text[start_r:end_r]!r} != {kana_spaced!r}"
    assert text[start_k:end_k] == kanji_spaced, f"two_line kanji mismatch: {text[start_k:end_k]!r} != {kanji_spaced!r}"
    return {
        "text": text,
        "spans": [
            {"start": start_r, "end": end_r, "label": "private_person"},
            {"start": start_k, "end": end_k, "label": "private_person"},
        ],
    }


def _make_renme_row(rng: random.Random) -> dict:
    name_a = pv.random_person(rng)
    # Ensure second name is different (simple: re-roll)
    name_b = pv.random_person(rng)
    style = rng.choice(["dot", "slash_label", "honorific_pair"])
    if style == "dot":
        sep = "・"
        text = f"{name_a}{sep}{name_b}"
        start_a = 0
        end_a = len(name_a)
        start_b = end_a + len(sep)
        end_b = start_b + len(name_b)
    elif style == "slash_label":
        prefix_a = "担当："
        mid = "／副担当："
        text = f"{prefix_a}{name_a}{mid}{name_b}"
        start_a = len(prefix_a)
        end_a = start_a + len(name_a)
        start_b = end_a + len(mid)
        end_b = start_b + len(name_b)
    else:  # honorific_pair
        sep = "様、"
        suffix_b = "様"
        text = f"{name_a}{sep}{name_b}{suffix_b}"
        start_a = 0
        end_a = len(name_a)
        start_b = end_a + len(sep)
        end_b = start_b + len(name_b)
    assert text[start_a:end_a] == name_a, f"renme a mismatch"
    assert text[start_b:end_b] == name_b, f"renme b mismatch"
    return {
        "text": text,
        "spans": [
            {"start": start_a, "end": end_a, "label": "private_person"},
            {"start": start_b, "end": end_b, "label": "private_person"},
        ],
    }


def _make_romaji_row(rng: random.Random) -> dict:
    name = pv.random_person(rng, style=rng.choice(["romaji", "romaji_caps"]))
    prefix, suffix = rng.choice([
        ("Name: ", ""),
        ("署名：", ""),
        ("担当者名：", ""),
    ])
    text = f"{prefix}{name}{suffix}"
    start = len(prefix)
    end = start + len(name)
    assert text[start:end] == name, f"romaji mismatch: {text[start:end]!r} != {name!r}"
    return {"text": text, "spans": [{"start": start, "end": end, "label": "private_person"}]}


_ROW_MAKERS = [
    ("business", _make_business_row, 40),
    ("honorific", _make_honorific_row, 15),
    ("company", _make_company_row, 15),
    ("furigana", _make_furigana_row, 15),
    ("renme", _make_renme_row, 10),
    ("romaji", _make_romaji_row, 5),
]
_MAKER_NAMES = [m[0] for m in _ROW_MAKERS]
_MAKER_FNS = [m[1] for m in _ROW_MAKERS]
_MAKER_WEIGHTS = [m[2] for m in _ROW_MAKERS]


def generate(n: int, seed: int) -> tuple[list[dict], dict[str, int]]:
    rng = random.Random(seed)
    rows = []
    style_counts: dict[str, int] = {name: 0 for name in _MAKER_NAMES}
    for _ in range(n):
        name, fn, _ = rng.choices(_ROW_MAKERS, weights=_MAKER_WEIGHTS)[0]
        rows.append(fn(rng))
        style_counts[name] += 1
    rng.shuffle(rows)
    return rows, style_counts


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("-n", "--count", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    rows, style_counts = generate(args.count, args.seed)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print("=== style distribution ===", file=sys.stderr)
    for style, cnt in style_counts.items():
        print(f"  {style}: {cnt}", file=sys.stderr)
    print(f"wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
