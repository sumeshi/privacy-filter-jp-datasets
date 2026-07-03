#!/usr/bin/env python3
"""Generate synthetic long multi-PII Japanese business documents for NER training.

All data is entirely fabricated. No real PII is used.
Document types: business_mail, application_form, support_log, order_delivery,
                minutes, incident_report.
Labels: private_person, private_address, private_email, private_phone,
        private_date, account_number, private_url, secret.
"""
import argparse
import json
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pii_values as pv

DEFAULT_OUT = Path(__file__).resolve().parents[1] / "generated" / "synthetic_docs_jp.jsonl"

MAX_DOC_LEN = 600

FALLBACK_ADDRESSES: list[str] = [
    "東京都新宿区新宿3-99-88 サンプルマンション101号室",
    "〒530-9999 大阪府大阪市北区梅田9-99-9 テストビル7F",
    "東京都渋谷区道玄坂1-2-3 みらいハイツ402号室",
    "〒060-0001 北海道札幌市中央区北1条西2丁目99",
    "神奈川県横浜市西区みなとみらい3-7-10",
    "〒460-0008 愛知県名古屋市中区栄4-16-99 第一テストビル5F",
    "福岡県福岡市博多区博多駅前2-10-9 テストレジデンス307号室",
    "〒980-0021 宮城県仙台市青葉区中央1-3-1 サンプルマンション1502号室",
    "京都府京都市下京区四条通烏丸東入99番地 グランドテストコーポ201号室",
    "〒550-0015 大阪府大阪市西区南堀江1-5-99",
    "兵庫県神戸市中央区三宮町2-11-3 さくらコート1001号室",
    "〒102-0083 東京都千代田区麹町4-7-99 セントラルテストタワー8F",
]

DOC_TYPES = [
    "business_mail",
    "application_form",
    "support_log",
    "order_delivery",
    "minutes",
    "incident_report",
]
DOC_WEIGHTS = [25, 25, 15, 15, 10, 10]

# ---------------------------------------------------------------------------
# Core segment builder
# ---------------------------------------------------------------------------

Seg = tuple[str, "str | None"]


def _build(segments: list[Seg]) -> dict:
    """Concatenate segments, accumulate char offsets, emit and verify spans."""
    parts: list[str] = []
    spans: list[dict] = []
    pieces_labeled: list[str] = []
    pos = 0
    for piece, label in segments:
        if label is not None and piece:
            start = pos
            end = pos + len(piece)
            spans.append({"start": start, "end": end, "label": label})
            pieces_labeled.append(piece)
        parts.append(piece)
        pos += len(piece)
    text = "".join(parts)
    for piece, span in zip(pieces_labeled, spans):
        assert text[span["start"]:span["end"]] == piece, (
            f"offset mismatch: {text[span['start']:span['end']]!r} != {piece!r}"
        )
    return {"text": text, "spans": spans}


# ---------------------------------------------------------------------------
# Address pool
# ---------------------------------------------------------------------------

def _load_address_pool(address_file: "str | None") -> list[str]:
    if address_file:
        p = Path(address_file)
        if p.exists():
            pool: list[str] = []
            with open(p, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        row = json.loads(line)
                        text = row["text"]
                        for span in row.get("spans", []):
                            if span.get("label") == "private_address":
                                pool.append(text[span["start"]:span["end"]])
                    except (json.JSONDecodeError, KeyError):
                        pass
            if pool:
                return pool
    return list(FALLBACK_ADDRESSES)


def _pick_addr(rng: random.Random, pool: list[str]) -> str:
    return rng.choice(pool)


# ---------------------------------------------------------------------------
# Date helper with optional zenkaku coercion
# ---------------------------------------------------------------------------

def _date(rng: random.Random, zk: bool = False, year_key: str = "any") -> str:
    d = pv.random_date_jp(rng, year_key=year_key)
    return pv.to_zenkaku(d) if zk else d


# ---------------------------------------------------------------------------
# Shared O-text banks
# ---------------------------------------------------------------------------

GREETINGS = [
    "いつもお世話になっております。\n",
    "平素より格別のご高配を賜り、厚く御礼申し上げます。\n",
    "お世話になっております。\n",
    "急なご連絡となり恐れ入ります。\n",
]

CLOSINGS = [
    "ご確認のほどよろしくお願いいたします。\n",
    "どうぞよろしくお願いいたします。\n",
    "引き続きよろしくお願い申し上げます。\n",
    "ご不明点がございましたら、お気軽にお問い合わせください。\n",
]

# ---------------------------------------------------------------------------
# Document generators
# ---------------------------------------------------------------------------


def _doc_business_mail(rng: random.Random, pool: list[str], zk: bool) -> dict:
    segs: list[Seg] = []

    # recipient header
    recip_co = rng.choice(pv.COMPANIES)
    recip_dept = rng.choice(pv.DEPARTMENTS)
    recip_name = pv.random_person(rng, style="kanji")
    segs += [(recip_co + "\n", None), (recip_dept + " ", None),
             (recip_name, "private_person"), ("様\n\n", None)]

    # greeting
    segs.append((rng.choice(GREETINGS), None))

    # sender person — reused in signature
    sender_kanji, sender_kana = pv.random_person_pair(rng)

    # body sentence bank (pick 2-4)
    body_bank: list[list[Seg]] = []

    date_val = _date(rng, zk, year_key="recent")
    body_bank.append(rng.choice([
        [(date_val, "private_date"), ("までにご対応いただけますと幸いです。\n", None)],
        [("締め切りは", None), (date_val, "private_date"), ("となっております。\n", None)],
        [("ご予約日は", None), (date_val, "private_date"), ("でございます。何卒よろしくお願いします。\n", None)],
    ]))

    phone_val = pv.random_phone_jp(rng, fmt="zenkaku" if zk else None)
    body_bank.append(rng.choice([
        [("折り返しは", None), (phone_val, "private_phone"), ("までお電話ください。\n", None)],
        [("ご不明点は", None), (phone_val, "private_phone"), ("へご連絡ください。\n", None)],
        [("お問い合わせ先：", None), (phone_val, "private_phone"), ("までご連絡いただけますようお願いいたします。\n", None)],
    ]))

    url_val = pv.random_url(rng)
    body_bank.append(rng.choice([
        [("詳細はこちらよりご確認ください：", None), (url_val, "private_url"), ("\n", None)],
        [("ご注文内容は", None), (url_val, "private_url"), ("よりご確認いただけます。\n", None)],
        [("資料は下記URLからご確認ください：", None), (url_val, "private_url"), ("\n", None)],
    ]))

    acct_val = pv.random_generic_id(rng)
    body_bank.append(rng.choice([
        [("ご注文番号：", None), (acct_val, "account_number"), ("でご確認いただけます。\n", None)],
        [("受付番号は", None), (acct_val, "account_number"), ("でございます。\n", None)],
        [("会員番号", None), (acct_val, "account_number"), ("のお客様はお早めにご連絡ください。\n", None)],
    ]))

    n_body = rng.randint(2, 4)
    for item in rng.sample(body_bank, n_body):
        segs += item

    # closing
    segs.append((rng.choice(CLOSINGS), None))

    # signature block
    sig_co = rng.choice(pv.COMPANIES)
    sig_dept = rng.choice(pv.DEPARTMENTS)
    sig_phone_a = pv.random_phone_jp(rng, fmt="zenkaku" if zk else None)
    # FAX lines should carry landline-style numbers, not mobile prefixes.
    sig_phone_b = pv.random_phone_jp(
        rng,
        kind=rng.choice(["landline2", "landline3", "landline4"]),
        fmt="zenkaku" if zk else None,
    )
    sig_email = pv.random_email(rng)
    sig_addr = _pick_addr(rng, pool)
    sig_url = pv.random_url(rng)

    segs += [
        ("――――\n", None),
        (sig_co + " ", None), (sig_dept + "\n", None),
        (sender_kanji, "private_person"), ("（", None), (sender_kana, "private_person"), ("）\n", None),
        ("TEL：", None), (sig_phone_a, "private_phone"), ("／FAX：", None), (sig_phone_b, "private_phone"), ("\n", None),
        ("Mail：", None), (sig_email, "private_email"), ("\n", None),
        (sig_addr, "private_address"), ("\n", None),
        (sig_url, "private_url"), ("\n", None),
        ("――――", None),
    ]

    return _build(segs)


def _doc_application_form(rng: random.Random, pool: list[str], zk: bool) -> dict:
    segs: list[Seg] = []

    form_hdrs = ["■ 申込書\n", "【お申込みフォーム】\n", "◆ 会員登録申請書\n", "▼ 利用登録申請書\n"]
    segs.append((rng.choice(form_hdrs), None))

    kanji_name, kana_name = pv.random_person_pair(rng, spaced=rng.random() < 0.3)

    segs += [(rng.choice(["フリガナ：", "ふりがな：", "カナ氏名：", "読み："]), None),
             (kana_name, "private_person"), ("\n", None)]
    segs += [(rng.choice(["氏名：", "お名前：", "名前：", "氏名（漢字）："]), None),
             (kanji_name, "private_person"), ("\n", None)]

    dob_val = _date(rng, zk, year_key="birth")
    segs += [(rng.choice(["生年月日：", "誕生日：", "生年月日（西暦）："]), None),
             (dob_val, "private_date"), ("\n", None)]

    addr_val = _pick_addr(rng, pool)
    segs += [(rng.choice(["住所：", "ご住所：", "現住所：", "お住まいの住所："]), None),
             (addr_val, "private_address"), ("\n", None)]

    phone_val = pv.random_phone_jp(rng, fmt="zenkaku" if zk else None)
    segs += [(rng.choice(["電話番号：", "お電話番号：", "連絡先電話番号：", "携帯番号："]), None),
             (phone_val, "private_phone"), ("\n", None)]

    email_val = pv.random_email(rng)
    segs += [(rng.choice(["メールアドレス：", "メール：", "Eメール：", "連絡先メール："]), None),
             (email_val, "private_email"), ("\n", None)]

    # ID — mix generic vs jp_id with appropriate key
    if rng.random() < 0.5:
        id_val = pv.random_generic_id(rng)
        id_key = rng.choice(["会員番号：", "申込番号：", "顧客番号：", "登録番号："])
    else:
        id_val, id_kind = pv.random_jp_id(rng)
        kind_key_map = {
            "mynumber": "マイナンバー：",
            "license": "運転免許証番号：",
            "passport": "旅券番号：",
            "nenkin": "基礎年金番号：",
            "hoken": "保険証記号番号：",
            "bank": "口座番号：",
            "yucho": "ゆうちょ記号番号：",
            "zairyu": "在留カード番号：",
        }
        id_key = kind_key_map.get(id_kind, "番号：")
    segs += [(id_key, None), (id_val, "account_number"), ("\n", None)]

    # O-only filler lines
    o_lines_all = [
        "ご職業：会社員\n",
        "性別：回答しない\n",
        "利用目的：新規申込\n",
        "国籍：日本\n",
        "契約種別：個人\n",
        "ご希望のプラン：スタンダードプラン\n",
    ]
    for line in rng.sample(o_lines_all, rng.randint(1, 3)):
        segs.append((line, None))

    return _build(segs)


def _doc_support_log(rng: random.Random, pool: list[str], zk: bool) -> dict:
    segs: list[Seg] = []

    segs.append((rng.choice([
        "【問い合わせ対応ログ】\n",
        "◆ カスタマーサポート対応記録\n",
        "■ 受付対応メモ\n",
    ]), None))

    receipt_id = pv.random_generic_id(rng)
    segs += [(rng.choice(["受付ID：", "対応番号：", "チケット番号："]), None),
             (receipt_id, "account_number"), ("\n", None)]

    date_val = _date(rng, zk, year_key="recent")
    segs += [(rng.choice(["受付日：", "対応日時：", "問い合わせ日："]), None),
             (date_val, "private_date"), ("\n", None)]

    cust_name = pv.random_person(rng, style="kanji")
    segs += [(rng.choice(["顧客名：", "お客様名：", "ご担当者名："]), None),
             (cust_name, "private_person"), ("様\n", None)]

    phone_val = pv.random_phone_jp(rng, fmt="zenkaku" if zk else None)
    segs += [(rng.choice(["折返し先：", "連絡先電話番号：", "ご連絡先：", "コールバック先："]), None),
             (phone_val, "private_phone"), ("\n", None)]

    segs.append((rng.choice([
        "対応メモ：返品対応希望。商品の状態を確認中。\n",
        "対応内容：請求書の再発行を依頼された。経理部へ連携済み。\n",
        "対応メモ：配送遅延に関するお問い合わせ。現在確認中。\n",
        "対応内容：パスワードリセットのご依頼。手順をご案内済み。\n",
        "対応メモ：商品の使い方についてのご質問。取扱説明書をご案内。\n",
    ]), None))

    # second mention of customer name
    segs += rng.choice([
        [(cust_name, "private_person"), ("様より再度お電話があった場合は担当者へ転送。\n", None)],
        [("折り返し連絡は", None), (cust_name, "private_person"), ("様ご希望により上記番号。\n", None)],
        [("担当者より", None), (cust_name, "private_person"), ("様へ折り返し済み。\n", None)],
    ])

    next_date = _date(rng, zk, year_key="recent")
    segs += [(rng.choice(["次回連絡予定日：", "フォローアップ予定：", "次回対応日："]), None),
             (next_date, "private_date"), ("\n", None)]

    return _build(segs)


def _doc_order_delivery(rng: random.Random, pool: list[str], zk: bool) -> dict:
    segs: list[Seg] = []

    segs.append((rng.choice([
        "【注文確認】\n",
        "◆ ご注文内容のご確認\n",
        "■ 配送のご連絡\n",
        "▼ 発送完了通知\n",
    ]), None))

    order_id = pv.random_generic_id(rng)
    segs += [(rng.choice(["ご注文番号：", "注文ID：", "受注番号：", "お取引番号："]), None),
             (order_id, "account_number"), ("\n", None)]

    addr_val = _pick_addr(rng, pool)
    deliv_name = pv.random_person(rng, style="kanji")
    segs += [(rng.choice(["お届け先：", "配送先：", "送付先：", "お届け先住所："]), None),
             (addr_val, "private_address"), ("　", None),
             (deliv_name, "private_person"), ("様\n", None)]

    date_val = _date(rng, zk, year_key="recent")
    segs += [(rng.choice(["お届け予定日：", "配送予定日：", "到着予定：", "お届け日："]), None),
             (date_val, "private_date"), ("\n", None)]

    phone_val = pv.random_phone_jp(rng, fmt="zenkaku" if zk else None)
    segs += [(rng.choice(["お問い合わせ：", "配送問い合わせ先：", "フリーダイヤル：", "サポート電話："]), None),
             (phone_val, "private_phone"), ("\n", None)]

    url_val = pv.random_url(rng)
    segs += [(rng.choice(["注文詳細：", "ご注文確認URL：", "詳細URL：", "追跡URL："]), None),
             (url_val, "private_url"), ("\n", None)]

    segs.append((rng.choice([
        "お荷物の準備が整い次第、発送いたします。\n",
        "ご注文ありがとうございます。\n",
        "発送完了後、メールにてご連絡いたします。\n",
        "到着後、内容をご確認のうえご連絡ください。\n",
    ]), None))

    return _build(segs)


def _doc_minutes(rng: random.Random, pool: list[str], zk: bool) -> dict:
    segs: list[Seg] = []

    segs.append((rng.choice([
        "【議事録】\n",
        "◆ 会議議事録\n",
        "■ ミーティング記録\n",
    ]), None))

    date_val = _date(rng, zk, year_key="recent")
    segs += [(rng.choice(["開催日：", "会議日時：", "実施日："]), None),
             (date_val, "private_date"), ("\n", None)]

    n_attendees = rng.randint(3, 5)
    names = [pv.random_person(rng, style="kanji") for _ in range(n_attendees)]
    segs.append(("出席者：", None))
    for i, name in enumerate(names):
        segs.append((name, "private_person"))
        if i < len(names) - 1:
            segs.append(("、", None))
    segs.append(("\n", None))

    segs.append((rng.choice([
        "議題：第2四半期売上報告および来期予算の審議\n",
        "議題：新システム導入に関する進捗確認\n",
        "議題：組織改編に伴う業務分担の見直し\n",
        "議題：顧客満足度調査結果の共有と改善策の検討\n",
        "議題：セキュリティポリシーの改定について\n",
    ]), None))

    segs.append((rng.choice([
        "決定事項：来月中に提案書を提出すること。\n",
        "決定事項：プロジェクト計画書を次回会議までに完成させること。\n",
        "決定事項：関係各所への通知は総務部が担当する。\n",
        "決定事項：予算案を経理部に提出し承認を得ること。\n",
    ]), None))

    url_val = pv.random_url(rng)
    segs += [(rng.choice(["資料URL：", "参考資料：", "添付資料リンク："]), None),
             (url_val, "private_url"), ("\n", None)]

    next_date = _date(rng, zk, year_key="recent")
    segs += [(rng.choice(["次回開催日：", "次回会議：", "次回ミーティング予定："]), None),
             (next_date, "private_date"), ("\n", None)]

    return _build(segs)


def _doc_incident_report(rng: random.Random, pool: list[str], zk: bool) -> dict:
    segs: list[Seg] = []

    segs.append((rng.choice([
        "【社内インシデント報告書】\n",
        "◆ セキュリティインシデント報告\n",
        "■ 情報漏えいインシデント報告\n",
    ]), None))

    date_val = _date(rng, zk, year_key="recent")
    segs += [(rng.choice(["発生日時：", "発見日時：", "報告日："]), None),
             (date_val, "private_date"), ("\n", None)]

    finder_name = pv.random_person(rng, style="kanji")
    segs += [(rng.choice(["発見者：", "報告者：", "担当者："]), None),
             (finder_name, "private_person"), ("\n", None)]

    segs.append((rng.choice([
        "概要：社内システムへの不正アクセスが検知されました。\n",
        "概要：認証情報が外部に漏えいした可能性があります。\n",
        "概要：本番サーバーへの不正ログインが確認されました。\n",
        "概要：フィッシングメールによる認証情報の窃取が疑われます。\n",
        "概要：内部関係者による機密データへの不正アクセスが発覚しました。\n",
    ]), None))

    secret_val = pv.random_secret(rng)
    segs += [(rng.choice(["漏えいした認証情報：", "流出した認証情報：", "対象クレデンシャル："]), None),
             (secret_val, "secret"), ("\n", None)]

    acct_val = pv.random_generic_id(rng)
    segs += [(rng.choice(["対象アカウント：", "影響を受けたアカウント：", "侵害アカウント："]), None),
             (acct_val, "account_number"), ("\n", None)]

    if rng.random() < 0.5:
        contact_val = pv.random_phone_jp(rng, fmt="zenkaku" if zk else None)
        contact_label = "private_phone"
        contact_key = rng.choice(["対応者連絡先：", "緊急連絡先：", "担当者電話："])
    else:
        contact_val = pv.random_email(rng)
        contact_label = "private_email"
        contact_key = rng.choice(["対応者メール：", "報告先：", "担当者メールアドレス："])
    segs += [(contact_key, None), (contact_val, contact_label), ("\n", None)]

    segs.append((rng.choice([
        "対応状況：関係部署へ報告済み。パスワードリセット実施中。\n",
        "対応状況：セキュリティ部門が調査中。詳細は追って連絡。\n",
        "対応状況：影響範囲を特定中。外部専門家へのヒアリングを予定。\n",
        "対応状況：アカウントをロック済み。原因究明を進めています。\n",
    ]), None))

    return _build(segs)


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_DOC_GENERATORS = {
    "business_mail": _doc_business_mail,
    "application_form": _doc_application_form,
    "support_log": _doc_support_log,
    "order_delivery": _doc_order_delivery,
    "minutes": _doc_minutes,
    "incident_report": _doc_incident_report,
}


def _generate_one(rng: random.Random, pool: list[str]) -> tuple[dict, str]:
    doc_type = rng.choices(DOC_TYPES, weights=DOC_WEIGHTS)[0]
    zk = rng.random() < 0.10
    gen = _DOC_GENERATORS[doc_type]
    for _ in range(5):
        doc = gen(rng, pool, zk)
        if len(doc["text"]) <= MAX_DOC_LEN:
            return doc, doc_type
    # Return as-is after retries (rare edge case)
    return doc, doc_type


def generate(n: int, seed: int, address_file: "str | None") -> tuple[list[dict], dict]:
    rng = random.Random(seed)
    pool = _load_address_pool(address_file)
    rows: list[dict] = []
    type_counts: dict[str, int] = {}
    for _ in range(n):
        doc, doc_type = _generate_one(rng, pool)
        rows.append(doc)
        type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
    return rows, type_counts


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("-n", "--count", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--address-file", default=None,
                    help="Path to address JSONL (e.g. synthetic_address_jp.jsonl); "
                         "span text extracted as address pool.")
    args = ap.parse_args()

    rows, type_counts = generate(args.count, args.seed, args.address_file)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # --- stderr stats ---
    label_counts: dict[str, int] = {}
    char_lengths: list[int] = []
    for row in rows:
        char_lengths.append(len(row["text"]))
        for span in row["spans"]:
            lbl = span["label"]
            label_counts[lbl] = label_counts.get(lbl, 0) + 1

    print("=== doc type counts ===", file=sys.stderr)
    for dt in DOC_TYPES:
        print(f"  {dt}: {type_counts.get(dt, 0)}", file=sys.stderr)

    print("=== spans per label ===", file=sys.stderr)
    for lbl, cnt in sorted(label_counts.items()):
        print(f"  {lbl}: {cnt}", file=sys.stderr)

    median_len = int(statistics.median(char_lengths))
    over_cap = sum(1 for ln in char_lengths if ln > MAX_DOC_LEN)
    print("=== char length stats ===", file=sys.stderr)
    print(f"  min={min(char_lengths)}  median={median_len}  max={max(char_lengths)}", file=sys.stderr)
    print(f"  docs over {MAX_DOC_LEN} chars: {over_cap}", file=sys.stderr)
    print(f"wrote {args.out} ({len(rows)} rows)", file=sys.stderr)


if __name__ == "__main__":
    main()
