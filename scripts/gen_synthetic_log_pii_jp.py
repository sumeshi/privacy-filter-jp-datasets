#!/usr/bin/env python3
"""Generate synthetic key=value log / .env / HTTP-header style PII examples.

Covers a blind spot found in demo documents: PII values embedded in English
key=value lines (``customer_id=C0092841``, ``temporary_token=pf_test_...``)
were undetected even at very low thresholds because all other training data
uses Japanese business phrasing. Values come from pii_values.py; everything is
fabricated.

Non-PII keys (status, region, duration_ms, ...) are mixed in as in-line
negatives. Ambiguous identifier keys (trace_id, build_id) are deliberately
NOT used as negatives to avoid contradicting the PII-side supervision.
"""
import argparse
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pii_values as pv

DEFAULT_OUT = Path(__file__).resolve().parents[1] / "generated" / "synthetic_log_pii_jp.jsonl"

# (key, value_fn, label). Keys are customer-linked identifiers or credentials.
def _id_value(rng):
    if rng.random() < 0.5:
        return pv.random_generic_id(rng)
    return pv.random_jp_id(rng, kind=rng.choice(["mynumber", "bank"]))[0].replace(" ", "")


def _log_secret(rng):
    # pv.random_secret plus vendor-test-key shapes seen in real logs.
    if rng.random() < 0.4:
        prefix = rng.choice(["pf_test_sk_", "ghp_", "xoxb-", "AKIA", "glpat-"])
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        return prefix + "".join(rng.choice(alphabet) for _ in range(rng.randint(20, 32)))
    return pv.random_secret(rng)


PII_KEYS = [
    ("customer_id", _id_value, "account_number"),
    ("member_id", _id_value, "account_number"),
    ("user_id", _id_value, "account_number"),
    ("account_id", _id_value, "account_number"),
    ("order_id", _id_value, "account_number"),
    ("contract_no", _id_value, "account_number"),
    ("request_id", _id_value, "account_number"),
    ("api_key", _log_secret, "secret"),
    ("API_KEY", _log_secret, "secret"),
    ("AWS_SECRET_ACCESS_KEY", _log_secret, "secret"),
    ("temporary_token", _log_secret, "secret"),
    ("access_token", _log_secret, "secret"),
    ("PASSWORD", _log_secret, "secret"),
    ("email", pv.random_email, "private_email"),
    ("contact_email", pv.random_email, "private_email"),
    ("mail_to", pv.random_email, "private_email"),
    ("tel", lambda rng: pv.random_phone_jp(rng, fmt=rng.choice(["hyphen", "none"])), "private_phone"),
    ("phone", lambda rng: pv.random_phone_jp(rng, fmt=rng.choice(["hyphen", "none"])), "private_phone"),
    ("callback_url", pv.random_url, "private_url"),
    ("endpoint", pv.random_url, "private_url"),
    ("birth_date", lambda rng: pv.random_date_jp(rng, "birth"), "private_date"),
    ("created_at", lambda rng: pv.random_date_jp(rng, "recent"), "private_date"),
]

NONPII_LINES = [
    "status=200", "status=failed", "level=INFO", "level=WARN",
    "region=ap-northeast-1", "duration_ms=412", "retry_count=3",
    "service=notification", "env=staging", "version=2.3.1",
    "cache=miss", "http_method=POST",
]

JP_CONTEXT_LINES = [
    "以下のログを確認してください。",
    "問い合わせ対応時の抜粋です。",
    "検証環境の設定値は次のとおりです。",
    "エラー発生時のリクエスト情報:",
    "設定ファイルの該当箇所:",
]


def kv_piece(rng, key, value):
    style = rng.random()
    if style < 0.55:
        return f"{key}={value}"
    if style < 0.75:
        return f"{key}: {value}"
    if style < 0.9:
        return f'"{key}": "{value}"'
    return f"{key} = {value}"


def make_single(rng) -> dict:
    key, fn, label = rng.choice(PII_KEYS)
    value = fn(rng)
    line = kv_piece(rng, key, value)
    start = line.index(value)
    return {"text": line, "spans": [{"start": start, "end": start + len(value), "label": label}]}


def make_block(rng) -> dict:
    lines = []
    spans = []
    if rng.random() < 0.4:
        lines.append(rng.choice(JP_CONTEXT_LINES))
    n_pii = rng.randint(1, 4)
    n_neg = rng.randint(1, 4)
    entries = [("pii", rng.choice(PII_KEYS)) for _ in range(n_pii)]
    entries += [("neg", rng.choice(NONPII_LINES)) for _ in range(n_neg)]
    rng.shuffle(entries)
    offset = sum(len(l) + 1 for l in lines)
    for kind, entry in entries:
        if kind == "neg":
            lines.append(entry)
            offset += len(entry) + 1
            continue
        key, fn, label = entry
        value = fn(rng)
        line = kv_piece(rng, key, value)
        start = offset + line.index(value)
        spans.append({"start": start, "end": start + len(value), "label": label})
        lines.append(line)
        offset += len(line) + 1
    text = "\n".join(lines)
    for s in spans:
        assert text[s["start"]:s["end"]].strip(), "bad span"
    return {"text": text, "spans": spans}


def generate(n: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        row = make_single(rng) if rng.random() < 0.6 else make_block(rng)
        for s in row["spans"]:
            assert row["text"][s["start"]:s["end"]], "empty span"
        rows.append(row)
    rng.shuffle(rows)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("-n", "--count", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    rows = generate(args.count, args.seed)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    from collections import Counter
    hist = Counter(s["label"] for r in rows for s in r["spans"])
    for label in sorted(hist):
        print(f"{label}: {hist[label]}", file=sys.stderr)
    print(f"wrote {args.out} ({len(rows)} rows)", file=sys.stderr)


if __name__ == "__main__":
    main()
