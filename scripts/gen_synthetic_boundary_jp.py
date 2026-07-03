#!/usr/bin/env python3
"""Generate Japanese boundary-focused PII examples.

These examples target common over-span errors: prefixes like "氏名 ", particles
before names, honorifics/roles after names, URL colons, and two addresses in one
sentence that must remain separate spans. All names/addresses are fabricated.
"""

import argparse
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pii_values as pv

DEFAULT_OUT = Path(__file__).resolve().parents[1] / "generated" / "synthetic_boundary_jp.jsonl"


NAMES = [
    "山田 太郎",
    "佐藤花子",
    "鈴木 一郎",
    "小林由美",
    "斎藤 一郎",
    "山本健一",
    "田中",
    "伊藤 美咲",
]

ADDRESSES = [
    "東京都目黒区中根1-2-3",
    "東京都目黒区中根1-99-99",
    "福岡県福岡市博多区博多駅前1-99-9",
    "大阪市北区梅田3-99-1",
    "京都府京都市中京区錦小路通烏丸東入元法然寺町99",
    "〒160-0022 東京都新宿区新宿3-99-88 サンプルマンション101号室",
]

NEGATIVES = [
    "受付番号は公開サンプルです。",
    "公開サンプルは個人名ではありません。",
    "テスト担当へ確認してください。",
    "サンプル株式会社の公開資料です。",
    "住所サンプルは架空データです。",
]


def one_span(text: str, value: str, label: str) -> dict:
    start = text.index(value)
    end = start + len(value)
    return {"text": text, "spans": [{"start": start, "end": end, "label": label}]}


def person_example(rng: random.Random) -> dict:
    # Fixed legacy pool sometimes; otherwise draw from the shared name pools
    # so the template space is large enough for thousands of unique rows.
    if rng.random() < 0.2:
        name = rng.choice(NAMES)
    else:
        name = pv.random_person(rng, style=rng.choice(["kanji", "kanji_space", "surname"]))
    template = rng.choice([
        "申込者氏名 {name}",
        "契約者名：{name}様",
        "経理部 {name}様から請求先住所の連絡です。",
        "お問い合わせ本文：先日申し込んだ{name}です。",
        "サンプル株式会社 代表取締役社長 {name}",
        "{name}部長様",
        "担当の{name}さんへ共有してください。",
        "営業部の{name}課長に確認してください。",
    ])
    if "{name}部長様" in template and len(name) > 2:
        name = name.replace(" ", "")[:2]
    text = template.format(name=name)
    return one_span(text, name, "private_person")


def address_example(rng: random.Random) -> dict:
    a = rng.choice(ADDRESSES)
    b = rng.choice([x for x in ADDRESSES if x != a])
    template = rng.choice([
        "住所変更前：{a} 住所変更後：{b}",
        "旧住所：{a} / 新住所：{b}",
        "配送先：{a} 請求先：{b}",
    ])
    text = template.format(a=a, b=b)
    spans = []
    first = text.index(a)
    spans.append({"start": first, "end": first + len(a), "label": "private_address"})
    second = text.index(b, first + len(a))
    spans.append({"start": second, "end": second + len(b), "label": "private_address"})
    return {"text": text, "spans": spans}


def url_boundary_example(rng: random.Random) -> dict:
    value = rng.choice([
        "https://example.invalid/verify/user-0001?token=test",
        "https://example.invalid/orders/test-001",
        "https://example.test/accounts/R20260401",
    ])
    text = rng.choice([
        f"本人確認URL：{value}",
        f"確認URLは{value}です。",
        f"URL：{value} を開いてください。",
    ])
    return one_span(text, value, "private_url")


def generate(count: int, seed: int, exclude: set[str]) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    seen: set[str] = set()
    makers = [person_example, address_example, url_boundary_example]
    attempts = 0
    max_attempts = count * 50
    while len(rows) < count and attempts < max_attempts:
        attempts += 1
        if rng.random() < 1 / 7 and len(NEGATIVES) > sum(1 for r in rows if not r["spans"]):
            row = {"text": rng.choice(NEGATIVES), "spans": []}
        else:
            row = rng.choice(makers)(rng)
        key = row["text"].strip()
        # Emit each text once, and never emit a benchmark text as training data.
        if key in seen or key in exclude:
            continue
        seen.add(key)
        rows.append(row)
    if len(rows) < count:
        print(f"warning: template space exhausted, emitted {len(rows)} unique rows", file=sys.stderr)
    rng.shuffle(rows)
    return rows


def load_exclude_texts(paths: list[str]) -> set[str]:
    texts: set[str] = set()
    for path in paths:
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line:
                texts.add(json.loads(line)["text"].strip())
    return texts


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("-n", "--count", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="JSONL files (e.g. benchmark splits) whose texts must not be emitted",
    )
    args = ap.parse_args()

    rows = generate(args.count, args.seed, load_exclude_texts(args.exclude))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    counts = {"negative": 0}
    for row in rows:
        if not row["spans"]:
            counts["negative"] += 1
        for span in row["spans"]:
            counts[span["label"]] = counts.get(span["label"], 0) + 1
    for key in sorted(counts):
        print(f"{key}: {counts[key]}", file=sys.stderr)
    print(f"wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
