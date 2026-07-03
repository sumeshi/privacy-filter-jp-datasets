#!/usr/bin/env python3
"""Emit the hand-curated benchmark v2 files (eval2.jsonl / challenge2.jsonl).

Each row is authored as a list of pieces; a piece is either a plain string
(no span) or a (text, label) tuple. The builder concatenates pieces and
computes character offsets, so no offset is ever hand-counted.

All values are fictional: names are common-name combinations, addresses use
implausible banchi and fictional buildings, digits are random-looking
inventions, domains are example.jp/.test/.invalid. Coverage per file: all
8 labels, multi-line documents, Japanese phone-format variants, Japan-specific
identifiers (mapped to account_number), furigana name pairs, O-only negatives,
and span-boundary traps (titles, honorifics, company names, 様方).

challenge2.jsonl is the blind split: do not inspect per-row errors on it while
tuning; use eval2.jsonl for that.
"""
import argparse
import collections
import json
from pathlib import Path

DEFAULT_OUTDIR = Path(__file__).resolve().parents[3] / "datasets" / "benchmark"

PER = "private_person"
ADR = "private_address"
EML = "private_email"
PHN = "private_phone"
DAT = "private_date"
ACC = "account_number"
URL = "private_url"
SEC = "secret"

EVAL2 = [
    # --- multi-line documents -------------------------------------------
    [
        "サンプル精機株式会社\n購買部 ", ("西村健二", PER), "様\n\n",
        "いつもお世話になっております。みらい電子の", ("柴田", PER), "です。\n",
        "ご依頼の見積書を", ("2026年7月10日", DAT), "までにお送りいたします。\n",
        "ご不明点は", ("052-761-4498", PHN), "までご連絡ください。\n\n",
        "――――――――――\nみらい電子株式会社 営業一課\n",
        ("柴田孝之", PER), "（", ("シバタタカユキ", PER), "）\n",
        "TEL:", ("０５２－７６１－４４９８", PHN), "／Mail:", ("t.shibata@example.jp", EML), "\n",
        ("〒460-0008 愛知県名古屋市中区栄3-99-12 テストタワー9F", ADR), "\n――――――――――",
    ],
    [
        "【入会申込書】\n",
        "フリガナ:", ("オカベ　ミナコ", PER), "\n",
        "氏名:", ("岡部　美奈子", PER), "\n",
        "生年月日:", ("昭和58年4月12日", DAT), "\n",
        "住所:", ("〒221-0835 神奈川県横浜市神奈川区鶴屋町2-99-1 サンプルレジデンス803", ADR), "\n",
        "電話番号:", ("08034567821", PHN), "\n",
        "メール:", ("minako_okabe@example.test", EML), "\n",
        "会員番号:", ("M-882901", ACC), "\nご職業:会社員",
    ],
    [
        "受付ID:", ("R20260702-0031", ACC), "\n",
        "お客様:", ("堀田", PER), "様（会員番号 ", ("C4407219", ACC), "）\n",
        ("2026/07/02", DAT), " 14:05 入電。請求金額の相違について。\n",
        "折り返し先:", ("070-5566-0912", PHN), "（", ("堀田", PER), "様携帯）\n",
        "次回連絡予定:", ("7月4日", DAT), "の午前中\n対応者:カスタマーサポート部",
    ],
    [
        "ご注文ありがとうございます。\n",
        "注文番号:", ("A2026063011", ACC), "\n",
        "お届け先:", ("大阪府枚方市香里園町9-99-9", ADR), "　", ("池内洋介", PER), "様\n",
        "お届け予定日:", ("2026/07/06", DAT), "\n",
        "配送状況の確認:", ("https://track.example.test/p/8842xu", URL), "\n",
        "お問い合わせ:", ("0120-330-118", PHN), "（9時〜18時）",
    ],
    [
        "第12回定例会 議事録\n",
        "日時:", ("2026年6月27日", DAT), " 10:00〜11:00\n",
        "出席者:", ("三宅", PER), "、", ("小田切", PER), "、", ("葛西", PER), "（記）\n",
        "決定事項:次期リリースをv3.2に延期する。\n",
        "資料:", ("https://docs.example.jp/minutes/0627", URL), "\n",
        "次回:", ("7月11日", DAT), " 同時刻",
    ],
    [
        "【インシデント報告】\n",
        "発見者:開発部 ", ("浅野誠", PER), "\n",
        "概要:社内リポジトリにAPIキーが誤ってコミットされていた。\n",
        "該当キー:", ("sk-test-Vg82LmNpQr44TzWwXy19AbCd", SEC), "\n",
        "対象アカウント:", ("svc-deploy-102", ACC), "\n",
        "対応:キーを失効し、", ("a.asano@example.jp", EML), "へ完了報告済み。",
    ],
    [
        "請求書\n",
        "請求番号:", ("INV-2026-0455", ACC), "\n",
        "請求先:", ("〒812-0011 福岡県福岡市博多区博多駅前2-99-3", ADR), " 村井商店 御中\n",
        "お支払期日:", ("2026年7月31日", DAT), "\n",
        "振込先:サンプル銀行 中央支店 普通 ", ("8814452", ACC), "\n",
        "金額:¥152,900（税込）",
    ],
    [
        "【スタッフ登録シート】\n",
        "氏名:", ("高村　沙耶", PER), "（", ("タカムラ　サヤ", PER), "）\n",
        "生年月日:", ("1995-11-02", DAT), "\n最寄駅:荻窪駅\n",
        "連絡先:", ("+81-90-6633-2810", PHN), "\n",
        "メール:", ("saya.t@mail.example.jp", EML), "\n",
        "基礎年金番号:", ("6210-448121", ACC),
    ],
    [
        "人事部内メモ（取扱注意）\n",
        "対象社員:", ("長谷部亮", PER), "（社員番号 ", ("S-30412", ACC), "）\n",
        "マイナンバー:", ("8102 4467 9035", ACC), "\n",
        "提出書類:扶養控除等申告書\n",
        "提出期限:", ("2026年7月15日", DAT),
    ],
    [
        "ご予約を承りました。\n",
        "予約番号:", ("Y-77015", ACC), "\n",
        "ご宿泊者:", ("ONO Rika", PER), "様\n",
        "チェックイン:", ("2026/08/01", DAT), "\n",
        "ご登録の電話番号:", ("06(6412)8890", PHN), "\n",
        "前日までの変更は", ("https://stay.example.jp/r/Y-77015", URL), "から可能です。",
    ],
    # --- person boundaries ----------------------------------------------
    ["氏名:", ("榊原元治", PER), "（", ("サカキバラモトハル", PER), "）"],
    ["フリガナ:", ("クドウ　レイナ", PER), "\n氏名:", ("工藤　玲奈", PER)],
    ["ご担当の", ("水島", PER), "様よりご連絡いただけますと幸いです。"],
    ["営業部長の", ("大森和樹", PER), "が本件を担当します。"],
    ["テスト建設株式会社の", ("井口紗英", PER), "と申します。"],
    [("松岡海斗", PER), "・", ("松岡未来", PER), "（ご連名）でのお申込みです。"],
    ["署名:", ("MATSUOKA Kaito", PER)],
    # --- addresses --------------------------------------------------------
    ["送付先:", ("東京都杉並区高円寺南4-99-1 コーポあおぞら202号室", ADR), " ", ("田中", PER), "様方"],
    ["住所:", ("京都府京都市中京区寺町通御池上る上本能寺前町488-99", ADR)],
    ["勤務先住所:", ("大阪府吹田市江坂町１－９９－８ 江坂サンプルビル４Ｆ", ADR)],
    [("北海道札幌市中央区北一条西2丁目99番地 テストビルヂング5階", ADR), "に移転しました。"],
    # --- phones -----------------------------------------------------------
    ["緊急連絡先:", ("０８０－４４２１－９９７６", PHN)],
    ["TEL ", ("03-5544-0011", PHN), "（代表）"],
    ["携帯は", ("09077653302", PHN), "です。"],
    ["海外からは", ("+81-3-4433-2211", PHN), "へおかけください。"],
    ["ご予約は", ("0570-064-880", PHN), "（ナビダイヤル）まで。"],
    # --- emails / urls ------------------------------------------------------
    ["確認用アドレス:", ("k.mizushima@example.invalid", EML)],
    ["書類は", ("soumu-uketsuke@corp.example.jp", EML), "宛にお送りください。"],
    ["口座振替の設定は", ("https://pay.example.jp/setup?uid=88213", URL), "からお願いします。"],
    ["解約手続き:", ("https://example.invalid/cancel/UX-2210", URL)],
    ["障害情報は", ("https://status.example.test/", URL), "で公開しています。"],
    # --- secrets ------------------------------------------------------------
    ["APIキー:", ("pk_test_YttW3k9BqLm22ZxCvA815Dq0", SEC)],
    ["認証トークン:", ("eyJhbGciOiJub25l.dGVzdC1wYXlsb2Fk.ZmFrZXNpZw", SEC)],
    ["初期パスワード:", ("Temp!2026-start", SEC)],
    ["環境変数 API_SECRET=", ("api_Qm4vv81LkOPzz73Wd0aYt2Xc", SEC), " を平文で共有しないでください。"],
    ["Bearerトークンは", ("Bearer 4uXp0qLmVz88TTwRkAaY21GhcNvB", SEC), "です。"],
    # --- dates ---------------------------------------------------------------
    ["お誕生日:", ("平成9年3月30日", DAT)],
    ["契約日:", ("R8.1.20", DAT)],
    ["納品予定:", ("2026.07.22", DAT)],
    # --- japan-specific ids ---------------------------------------------------
    ["運転免許証番号:第", ("302886414375", ACC), "号"],
    ["旅券番号:", ("TR8812995", ACC)],
    ["保険証記号番号:", ("44913022-08", ACC)],
    ["在留カード番号:", ("AB84203175CD", ACC)],
    ["ゆうちょ記号番号:", ("14560-22981406", ACC)],
    # --- negatives -------------------------------------------------------------
    ["お見積金額は¥482,900（税込）です。"],
    ["対象製品:XR-2200シリーズ"],
    ["v11.0.3で修正済みです。"],
    ["エラーコード:0x8004FE21"],
    ["15時から第2会議室で品質会議を行います。"],
    ["アンケートの回収は締め切りました。"],
    ["広報経由の取材依頼は書面でお願いします。"],
    ["添付の仕様書をご査収ください。"],
]

CHALLENGE2 = [
    # --- multi-line documents -------------------------------------------
    [
        "テスト管財株式会社\n管理部 ", ("矢部聡美", PER), "様\n\n",
        "お世話になっております。サンプル設備の", ("小柳", PER), "でございます。\n",
        "点検報告書を", ("2026年8月3日", DAT), "までに提出いたします。\n",
        "当日の入館手続きについては", ("0742-55-3108", PHN), "の", ("小柳", PER), "までお願いします。\n\n",
        "＝＝＝＝＝＝＝＝\nサンプル設備株式会社 保守二課\n",
        ("小柳達也", PER), "（", ("コヤナギタツヤ", PER), "）\n",
        "携帯:", ("０７０－８８１２－４４０６", PHN), "\nMail:", ("t-koyanagi@example.test", EML), "\n",
        ("〒630-8228 奈良県奈良市上三条町9-99 みらい上三条ビル2F", ADR), "\n＝＝＝＝＝＝＝＝",
    ],
    [
        "【賃貸入居申込書】\n",
        "フリガナ：", ("ニシオカ　ケンタ", PER), "\n",
        "氏名：", ("西岡　健太", PER), "\n",
        "生年月日：", ("平成2年12月8日", DAT), "\n",
        "現住所：", ("兵庫県尼崎市南塚口町8-99-2 あおぞら荘105号室", ADR), "\n",
        "日中連絡先：", ("06-6301-7742", PHN), "（勤務先）\n",
        "メールアドレス：", ("kenta.nishioka3@example.jp", EML), "\n",
        "緊急連絡先：", ("西岡　文枝", PER), "（母） ", ("0798-44-2210", PHN), "\n",
        "性別：回答しない",
    ],
    [
        "対応履歴 #", ("T-2026-08812", ACC), "\n",
        ("ヤマグチ", PER), "様より解約希望の入電。\n",
        "契約番号:", ("CNTR-2024-118", ACC), "\n",
        "本人確認:生年月日 ", ("1988/02/29", DAT), " → ", ("1988/02/19", DAT), "の誤りと判明\n",
        "折返し:", ("050-3355-8241", PHN), "（19時以降）\n",
        "エスカレーション先:リテンション担当 ", ("布施", PER),
    ],
    [
        "発送完了のお知らせ\n\n", ("桐生美月", PER), "様\n",
        "以下の内容で発送いたしました。\n",
        "伝票番号:", ("482-2109-3376", ACC), "\n",
        "お届け先:", ("〒903-0801 沖縄県那覇市首里末吉町4-99-9 ひまわりアパート303", ADR), "\n",
        "配達予定:", ("7月8日", DAT), " 午前中\n",
        "再配達の依頼:", ("https://redeliver.example.test/e/482-2109-3376", URL), "\n",
        "ドライバー直通:", ("090 4418 7726", PHN),
    ],
    [
        "採用面接メモ（社外秘）\n",
        "候補者:", ("柚木遥", PER), "（", ("ユノキハルカ", PER), "）\n",
        "面接日:", ("令和8年6月30日", DAT), "\n",
        "紹介元:株式会社山本製作所（エージェント経由）\n",
        "評価:コミュニケーション良好。二次面接へ進める。\n",
        "候補者連絡先:", ("haruka-yunoki@example.invalid", EML),
    ],
    [
        "【障害報告 第2報】\n",
        "検知者:", ("氏家", PER), "係長\n",
        "内容:検証環境の.envがアーカイブに混入。\n",
        "流出値:AWS_SECRET_KEY=", ("wJalrTESTKEY44xPq0BbFAKE0demo", SEC), "\n",
        "同梱ログに顧客メール ", ("y.kirishima@example.jp", EML), " を含む行を確認。\n",
        "対象システム利用ID:", ("app-batch-077", ACC), "\n",
        "次回報告:", ("7月5日", DAT), " 17時",
    ],
    [
        "領収書（控）\n",
        "取引番号:", ("RCP-88-120445", ACC), "\n",
        "お客様:", ("大池", PER), "様\n",
        "お支払方法:口座振替（テスト銀行 北支店 普通 ", ("1120884", ACC), "）\n",
        "領収日:", ("2026-07-01", DAT), "\n",
        "但書:年会費として\n",
        "お問い合わせ:", ("0800-777-2245", PHN),
    ],
    [
        "健康診断のご案内\n",
        "対象:", ("戸田優子", PER), "様（社員番号 ", ("E-11208", ACC), "）\n",
        "受診期限:", ("2026年9月30日", DAT), "\n",
        "会場:", ("東京都港区芝公園1-99-2 サンプルメディカルビル6F", ADR), "\n",
        "予約サイト:", ("https://kenshin.example.jp/booking", URL), "\n",
        "保険証記号番号 ", ("50288114-03", ACC), " を受付でご提示ください。",
    ],
    [
        "> ", ("大西", PER), "さん\n> 先日の見積の件、いかがでしょうか。\n\n",
        "お待たせしております。", ("2026/07/09", DAT), "までに回答いたします。\n",
        "至急の場合は", ("011-676-4432", PHN), "（内線204）へお願いします。\n\n",
        "株式会社サンプル商事 ", ("大西亮平", PER), "\n",
        ("r.onishi@example.jp", EML),
    ],
    [
        "【会員情報変更受付】\n",
        "受付番号:", ("W20260701-118", ACC), "\n",
        "会員:", ("コバヤシ　ナオ", PER), "様\n",
        "変更項目:住所\n",
        "新住所:", ("愛媛県松山市大街道3-99-1 パークサイドマンション701", ADR), "\n",
        "変更手続き完了通知:", ("https://member.example.test/done/W20260701-118", URL),
    ],
    # --- person boundaries ----------------------------------------------
    [("佐々木", PER), "係長が承認済みです。"],
    ["経理部 ", ("戸川", PER), "宛に回付してください。"],
    ["氏名:", ("三好　凛", PER), "（", ("ミヨシ　リン", PER), "）"],
    ["申請者:", ("Sato Masaki", PER), "（在外勤務）"],
    [("小谷野遥人", PER), "様、", ("小谷野真央", PER), "様の2名でご案内します。"],
    ["株式会社山本製作所の担当窓口までお問い合わせください。"],
    # --- addresses --------------------------------------------------------
    ["帰省先:", ("鹿児島県霧島市国分中央3-99-22", ADR), " ", ("原口", PER), "様方"],
    ["本籍地:", ("石川県金沢市広坂１丁目９９番９号", ADR)],
    ["新店舗は", ("東京都新宿区西新宿8-99-5 サンプル第2ビル3F", ADR), "にオープンします。"],
    ["請求書送付先:", ("〒760-0017 香川県高松市番町5-99-1", ADR), "（経理部気付）"],
    # --- phones -----------------------------------------------------------
    ["夜間窓口:", ("0120-990-556", PHN)],
    ["直通:", ("082(544)7810", PHN)],
    ["SMSは", ("08044921183", PHN), "に届きます。"],
    ["国際発信:", ("+81 45 682 3319", PHN)],
    ["総合案内:", ("０５７０－０２２－３３８", PHN), "（有料）"],
    ["FAX:", ("098-869-2214", PHN), "でも受け付けます。"],
    # --- emails / urls ------------------------------------------------------
    ["請求書PDFは", ("seikyu@billing.example.jp", EML), "から送付されます。"],
    ["返信は", ("m_toda99@example.invalid", EML), "までお願いします。"],
    ["本人確認リンク:", ("https://auth.example.invalid/verify?sid=ZZ8123&exp=600", URL)],
    ["採用ページ:", ("https://recruit.example.jp/2027/entry", URL)],
    ["メンテナンス告知:", ("https://info.example.test/maintenance/2026-q3", URL)],
    # --- secrets ------------------------------------------------------------
    ["デプロイキー:", ("sk-test-N0realKeyZZ917Abqm44LpXe", SEC)],
    ["ワンタイムパスワード:", ("884213", SEC), "（10分間有効）"],
    ["接続文字列のパスワード部 ", ("Passw0rd-dummy-77", SEC), " は失効済みです。"],
    ["旧トークン ", ("api_LEGACYtok88MMqz31WvvC0xTe", SEC), " は使用しないでください。"],
    ["署名鍵:", ("pk_test_Zw31MnB77QpLtY0acV92Ks8d", SEC)],
    # --- dates ---------------------------------------------------------------
    ["生年月日:", ("昭和41年11月3日", DAT)],
    ["初回利用日:", ("令和元年5月1日", DAT)],
    ["解約受付日:", ("2026/6/28", DAT)],
    ["お引越し予定日:", ("２０２６年８月１日", DAT)],
    # --- japan-specific ids ---------------------------------------------------
    ["個人番号:", ("482210937566", ACC)],
    ["免許証番号:", ("505477281930", ACC), "（第一種）"],
    ["パスポート番号:", ("TK4471820", ACC)],
    ["基礎年金番号:", ("3308-114452", ACC)],
    ["被保険者記号・番号:", ("77120945-16", ACC)],
    ["法人口座:みらい銀行 東支店 当座 ", ("0084417", ACC)],
    # --- negatives -------------------------------------------------------------
    ["第3四半期の出荷は12,400台でした。"],
    ["型番:KD-880IIの保証期間は2年です。"],
    ["バージョン3.1.7を適用後に再検証します。"],
    ["ステータス503が断続的に返却されています。"],
    ["10時より4階の応接室Bで打ち合わせです。"],
    ["歩留まりは目標水準を維持しています。"],
    ["合同会社みらいデザインとの契約を更新しました。"],
    ["定例の朝会は司会持ち回りです。"],
]


def build_rows(rows_spec):
    rows = []
    for spec in rows_spec:
        text = ""
        spans = []
        for piece in spec:
            if isinstance(piece, tuple):
                value, label = piece
                spans.append({"start": len(text), "end": len(text) + len(value), "label": label})
                text += value
            else:
                text += piece
        for s in spans:
            assert text[s["start"]:s["end"]], "empty span"
        rows.append({"text": text, "spans": spans})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", default=str(DEFAULT_OUTDIR))
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    for name, spec in (("eval2.jsonl", EVAL2), ("challenge2.jsonl", CHALLENGE2)):
        rows = build_rows(spec)
        path = outdir / name
        with open(path, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        hist = collections.Counter(s["label"] for r in rows for s in r["spans"])
        n_neg = sum(1 for r in rows if not r["spans"])
        print(f"{path}: rows={len(rows)} negatives={n_neg}")
        for label in sorted(hist):
            print(f"    {label}: {hist[label]}")


if __name__ == "__main__":
    main()
