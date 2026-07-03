#!/usr/bin/env python3
"""Generate O-only negative examples (rows with no PII spans) for Japanese
business text. Pure template generation -- no external data, no real PII.

The rest of the training mix is nearly 100% PII-dense, which biases the model
toward over-detection. These rows teach it NOT to fire on ordinary business
prose and PII-lookalike numbers (prices, model numbers, versions, error
codes). Dates are deliberately excluded so we never contradict the base
model's DATE behavior with O labels.
"""
import argparse
import json
from pathlib import Path
import random
import re
import sys

DEFAULT_OUT = Path(__file__).resolve().parents[1] / "generated" / "synthetic_negative_jp.jsonl"

# Patterns a negative row must never contain: emails, URLs, phone-shaped
# sequences, long digit runs, date expressions, and personal-ID keywords.
FORBIDDEN = [
    re.compile(r"[0-9]{6,}"),
    re.compile(r"0\d{1,3}[-(（]\d"),
    re.compile(r"\d{4}[/.\-年]\d{1,2}[/.\-月]"),
    re.compile(r"[@＠]"),
    re.compile(r"https?://"),
    re.compile(r"顧客番号|会員番号|受付番号|契約番号|口座|マイナンバー"),
]

FICTIONAL_COMPANIES = [
    "株式会社サンプル商事", "テスト工業株式会社", "サンプル物流株式会社",
    "合同会社みらいデザイン", "テスト建設株式会社", "株式会社サンプルフーズ",
]
DEPARTMENTS = [
    "営業部", "カスタマーサポート部", "経理部", "開発部", "総務部",
    "人事部", "法務部", "品質保証部", "情報システム部", "広報部",
]


def _price(rng: random.Random) -> str:
    n = rng.choice([rng.randint(100, 999), rng.randint(1000, 9999)]) * rng.choice([1, 10, 100])
    return f"{n:,}"


def gen_amount(rng: random.Random) -> str:
    return rng.choice([
        f"お見積金額は¥{_price(rng)}（税込）です。",
        f"請求額：{_price(rng)}円",
        f"今月の売上は{_price(rng)}円でした。",
        f"予算上限は¥{_price(rng)}となります。",
        f"単価{rng.randint(100, 9800):,}円で{rng.randint(2, 90)}個の発注です。",
    ])


def gen_quantity(rng: random.Random) -> str:
    return rng.choice([
        f"在庫数：{rng.randint(10, 9999):,}個",
        f"月間出荷数は{rng.randint(100, 9999):,}台です。",
        f"座席は残り{rng.randint(2, 80)}席です。",
        f"対象拠点は全{rng.randint(2, 48)}カ所です。",
    ])


def gen_model_number(rng: random.Random) -> str:
    code = f"{rng.choice(['PF', 'AB', 'XR', 'KD', 'ZW'])}-{rng.randint(100, 9899)}{rng.choice(['', 'X', 'S', 'II'])}"
    return rng.choice([
        f"型番：{code}",
        f"対象製品：{code}シリーズ",
        f"{code}の後継機種は来期発表予定です。",
        f"部品番号{code}は在庫切れです。",
    ])


def gen_version(rng: random.Random) -> str:
    ver = f"{rng.randint(1, 12)}.{rng.randint(0, 9)}.{rng.randint(0, 20)}"
    return rng.choice([
        f"バージョン{ver}へ更新してください。",
        f"v{ver}で修正済みです。",
        f"本不具合はv{ver}以降で発生します。",
        f"ファームウェア{ver}をリリースしました。",
    ])


def gen_error_code(rng: random.Random) -> str:
    return rng.choice([
        f"エラーコード：0x{rng.randint(0, 0xFFFF):04X}{rng.choice(['B', '5', 'F', '0'])}",
        f"E-{rng.randint(1000, 9899)}が表示された場合は再起動してください。",
        f"ステータス{rng.choice([400, 403, 404, 500, 502, 503])}が返却されます。",
    ])


def gen_place(rng: random.Random) -> str:
    return rng.choice([
        f"{rng.randint(9, 18)}時から第{rng.randint(1, 9)}会議室で定例会議を行います。",
        f"受付は{rng.randint(1, 9)}階ロビーです。",
        f"倉庫の{rng.choice('ABCDE')}-{rng.randint(1, 99)}棚に保管しています。",
        f"会場は本社{rng.randint(2, 15)}階の大会議室です。",
    ])


def gen_stats(rng: random.Random) -> str:
    pct = f"{rng.randint(1, 99)}.{rng.randint(0, 9)}"
    return rng.choice([
        f"前年比{pct}%増となりました。",
        f"回答率は{rng.randint(10, 99)}%でした。",
        f"稼働率が{pct}%まで改善しています。",
        f"不良率は{rng.randint(0, 5)}.{rng.randint(1, 9)}%以下を維持しています。",
    ])


def gen_org_only(rng: random.Random) -> str:
    company = rng.choice(FICTIONAL_COMPANIES)
    dept = rng.choice(DEPARTMENTS)
    return rng.choice([
        f"{company} {dept}より回答いたします。",
        f"本件は{dept}が窓口となります。",
        f"{company}の担当部署へ転送しました。",
        f"{dept}にて内容を確認中です。",
    ])


def gen_boilerplate(rng: random.Random) -> str:
    return rng.choice([
        "いつもお世話になっております。",
        "標記の件についてご確認をお願いいたします。",
        "添付資料をご査収ください。",
        "引き続きよろしくお願いいたします。",
        "ご多忙のところ恐れ入りますが、ご対応のほどお願い申し上げます。",
        "会議の議事録は共有フォルダに格納済みです。",
        "本メールは送信専用アドレスから配信されています。",
        "仕様の詳細は別紙をご参照ください。",
    ])


GENERATORS = [
    gen_amount, gen_quantity, gen_model_number, gen_version,
    gen_error_code, gen_place, gen_stats, gen_org_only, gen_boilerplate,
]


def generate(n: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    counts = {g.__name__: 0 for g in GENERATORS}
    while len(rows) < n:
        gen = GENERATORS[len(rows) % len(GENERATORS)]
        text = gen(rng)
        # Occasionally join two sentences for slightly longer negatives.
        if rng.random() < 0.25:
            text = f"{gen_boilerplate(rng)}{text}"
        if any(p.search(text) for p in FORBIDDEN):
            raise AssertionError(f"forbidden pattern in negative row: {text!r}")
        rows.append({"text": text, "spans": []})
        counts[gen.__name__] += 1
    rng.shuffle(rows)
    for name, c in counts.items():
        print(f"{name}: {c}", file=sys.stderr)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("-n", "--count", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    rows = generate(args.count, args.seed)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
