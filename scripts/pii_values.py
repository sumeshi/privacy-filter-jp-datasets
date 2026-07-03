"""Shared library of Japanese PII value generators.

Everything in this module is entirely fabricated. No real person's name, phone
number, email address, ID number or other personal information is used. Email
and URL domains are restricted to example.jp / example.test / example.invalid
and their subdomains. Company names and bank names are clearly fictional.
"""

import random
import string

# ---------------------------------------------------------------------------
# Name data
# ---------------------------------------------------------------------------

SURNAMES: list[tuple[str, str, str]] = [
    ("佐藤", "サトウ", "sato"),
    ("鈴木", "スズキ", "suzuki"),
    ("高橋", "タカハシ", "takahashi"),
    ("田中", "タナカ", "tanaka"),
    ("伊藤", "イトウ", "ito"),
    ("渡辺", "ワタナベ", "watanabe"),
    ("山本", "ヤマモト", "yamamoto"),
    ("中村", "ナカムラ", "nakamura"),
    ("小林", "コバヤシ", "kobayashi"),
    ("加藤", "カトウ", "kato"),
    ("吉田", "ヨシダ", "yoshida"),
    ("山田", "ヤマダ", "yamada"),
    ("佐々木", "ササキ", "sasaki"),
    ("山口", "ヤマグチ", "yamaguchi"),
    ("松本", "マツモト", "matsumoto"),
    ("井上", "イノウエ", "inoue"),
    ("木村", "キムラ", "kimura"),
    ("林", "ハヤシ", "hayashi"),
    ("斎藤", "サイトウ", "saito"),
    ("清水", "シミズ", "shimizu"),
    ("山崎", "ヤマザキ", "yamazaki"),
    ("阿部", "アベ", "abe"),
    ("池田", "イケダ", "ikeda"),
    ("橋本", "ハシモト", "hashimoto"),
    ("山下", "ヤマシタ", "yamashita"),
    ("石川", "イシカワ", "ishikawa"),
    ("中島", "ナカジマ", "nakajima"),
    ("前田", "マエダ", "maeda"),
    ("藤田", "フジタ", "fujita"),
    ("後藤", "ゴトウ", "goto"),
    ("小川", "オガワ", "ogawa"),
    ("岡田", "オカダ", "okada"),
    ("村上", "ムラカミ", "murakami"),
    ("長谷川", "ハセガワ", "hasegawa"),
    ("近藤", "コンドウ", "kondo"),
    ("石田", "イシダ", "ishida"),
    ("坂本", "サカモト", "sakamoto"),
    ("遠藤", "エンドウ", "endo"),
    ("藤井", "フジイ", "fujii"),
    ("西村", "ニシムラ", "nishimura"),
    ("福田", "フクダ", "fukuda"),
    ("太田", "オオタ", "ota"),
    ("三浦", "ミウラ", "miura"),
    ("岡本", "オカモト", "okamoto"),
    ("松田", "マツダ", "matsuda"),
    ("中野", "ナカノ", "nakano"),
    ("原田", "ハラダ", "harada"),
    ("小野", "オノ", "ono"),
    ("竹内", "タケウチ", "takeuchi"),
    ("金子", "カネコ", "kaneko"),
    ("藤原", "フジワラ", "fujiwara"),
    ("上田", "ウエダ", "ueda"),
    ("森田", "モリタ", "morita"),
    ("原", "ハラ", "hara"),
    ("柴田", "シバタ", "shibata"),
    ("酒井", "サカイ", "sakai"),
    ("工藤", "クドウ", "kudo"),
    ("横山", "ヨコヤマ", "yokoyama"),
    ("宮崎", "ミヤザキ", "miyazaki"),
    ("宮本", "ミヤモト", "miyamoto"),
    ("内田", "ウチダ", "uchida"),
    ("高木", "タカギ", "takagi"),
    ("安藤", "アンドウ", "ando"),
    ("島田", "シマダ", "shimada"),
    ("大野", "オオノ", "ono2"),
    ("谷口", "タニグチ", "taniguchi"),
    ("大塚", "オオツカ", "otsuka"),
    ("川口", "カワグチ", "kawaguchi"),
    ("新井", "アライ", "arai"),
    ("永井", "ナガイ", "nagai"),
    ("杉山", "スギヤマ", "sugiyama"),
    ("増田", "マスダ", "masuda"),
    ("丸山", "マルヤマ", "maruyama"),
    ("今井", "イマイ", "imai"),
    ("村田", "ムラタ", "murata"),
    ("吉川", "ヨシカワ", "yoshikawa"),
    ("河野", "コウノ", "kono"),
    ("和田", "ワダ", "wada"),
    ("浜田", "ハマダ", "hamada"),
]

GIVEN_NAMES: list[tuple[str, str, str]] = [
    ("太郎", "タロウ", "taro"),
    ("花子", "ハナコ", "hanako"),
    ("美咲", "ミサキ", "misaki"),
    ("蓮", "レン", "ren"),
    ("一郎", "イチロウ", "ichiro"),
    ("由美", "ユミ", "yumi"),
    ("健一", "ケンイチ", "kenichi"),
    ("真由美", "マユミ", "mayumi"),
    ("翔", "ショウ", "sho"),
    ("あかり", "アカリ", "akari"),
    ("拓也", "タクヤ", "takuya"),
    ("さくら", "サクラ", "sakura"),
    ("大輝", "ダイキ", "daiki"),
    ("陽菜", "ヒナ", "hina"),
    ("悠人", "ユウト", "yuto"),
    ("結衣", "ユイ", "yui"),
    ("颯太", "ソウタ", "sota"),
    ("愛", "アイ", "ai"),
    ("海斗", "カイト", "kaito"),
    ("麻衣", "マイ", "mai"),
    ("蒼", "アオ", "ao"),
    ("莉子", "リコ", "riko"),
    ("大和", "ヤマト", "yamato"),
    ("夏帆", "カホ", "kaho"),
    ("悠", "ユウ", "yu"),
    ("心", "ここ", "koko"),  # unusual reading
    ("陸", "リク", "riku"),
    ("葵", "アオイ", "aoi"),
    ("湊", "ミナト", "minato"),
    ("菜々子", "ナナコ", "nanako"),
    ("輝", "ヒカル", "hikaru"),
    ("茜", "アカネ", "akane"),
    ("優斗", "ユウト", "yuto2"),
    ("詩織", "シオリ", "shiori"),
    ("朝陽", "アサヒ", "asahi"),
    ("千尋", "チヒロ", "chihiro"),
    ("龍之介", "リュウノスケ", "ryunosuke"),
    ("七海", "ナナミ", "nanami"),
    ("達也", "タツヤ", "tatsuya"),
    ("理沙", "リサ", "risa"),
    ("二郎", "ジロウ", "jiro"),
    ("智子", "トモコ", "tomoko"),
    ("誠", "マコト", "makoto"),
    ("恵美", "エミ", "emi"),
    ("浩二", "コウジ", "koji"),
    ("京子", "キョウコ", "kyoko"),
    ("修", "オサム", "osamu"),
    ("幸子", "サチコ", "sachiko"),
    ("博", "ヒロシ", "hiroshi"),
    ("節子", "セツコ", "setsuko"),
    ("勇", "イサム", "isamu"),
    ("典子", "ノリコ", "noriko"),
    ("清", "キヨシ", "kiyoshi"),
    ("文子", "フミコ", "fumiko"),
    ("実", "ミノル", "minoru"),
    ("和子", "カズコ", "kazuko"),
    ("進", "ススム", "susumu"),
    ("順子", "ジュンコ", "junko"),
    ("明", "アキラ", "akira"),
    ("洋子", "ヨウコ", "yoko"),
    ("茂", "シゲル", "shigeru"),
    ("弘子", "ヒロコ", "hiroko"),
    ("豊", "ユタカ", "yutaka"),
    ("美代子", "ミヨコ", "miyoko"),
    ("保", "タモツ", "tamotsu"),
    ("春子", "ハルコ", "haruko"),
    ("昭", "アキ", "aki"),
    ("道子", "ミチコ", "michiko"),
    ("武", "タケシ", "takeshi"),
    ("澄子", "スミコ", "sumiko"),
    ("隆", "タカシ", "takashi"),
    ("美恵子", "ミエコ", "mieko"),
    ("守", "マモル", "mamoru"),
    ("雅子", "マサコ", "masako"),
    ("稔", "ミノル2", "minoru2"),
    ("静子", "シズコ", "shizuko"),
    ("健", "ケン", "ken"),
    ("久美子", "クミコ", "kumiko"),
    ("正", "タダシ", "tadashi"),
    ("百合子", "ユリコ", "yuriko"),
    ("忠", "タダシ2", "tadashi2"),
]

# ---------------------------------------------------------------------------
# Organisational data
# ---------------------------------------------------------------------------

COMPANIES: list[str] = [
    "株式会社サンプル商事",
    "テスト工業株式会社",
    "合同会社みらいデザイン",
    "サンプル物流株式会社",
    "テスト情報システム株式会社",
    "株式会社みらいコンサルティング",
    "サンプルサービス合同会社",
    "テスト建設株式会社",
    "みらい医療株式会社",
    "株式会社サンプルテクノロジー",
    "テスト食品株式会社",
    "合同会社サンプルクリエイティブ",
    "株式会社みらい不動産",
    "テスト教育株式会社",
    "サンプル金融株式会社",
]

DEPARTMENTS: list[str] = [
    "営業部",
    "カスタマーサポート部",
    "経理部",
    "開発部",
    "総務部",
    "人事部",
    "法務部",
    "品質保証部",
    "マーケティング部",
    "企画部",
    "情報システム部",
    "購買部",
]

FICTIONAL_BANKS: list[str] = [
    "サンプル銀行",
    "テスト銀行",
    "みらい銀行",
    "サンプル信用金庫",
    "テスト信用組合",
]

BANK_BRANCHES: list[str] = [
    "本店",
    "新宿支店",
    "渋谷支店",
    "池袋支店",
    "銀座支店",
    "品川支店",
    "梅田支店",
    "難波支店",
    "名古屋支店",
    "札幌支店",
]

BUILDING_NAMES: list[str] = [
    "サンプルマンション",
    "グランドテストコーポ",
    "みらいハイツ",
    "さくらコート",
    "けやき荘",
    "第一テストビル",
    "パークサイドマンション",
    "ひまわりアパート",
    "グリーンヒルズ",
    "セントラルテストタワー",
    "テストレジデンス",
    "あおぞら荘",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ZENKAKU_MAP: dict[str, str] = {
    "0": "０", "1": "１", "2": "２", "3": "３", "4": "４",
    "5": "５", "6": "６", "7": "７", "8": "８", "9": "９",
    "-": "－", "(": "（", ")": "）", "+": "＋", ".": "．",
    " ": "　",
}


def to_zenkaku(s: str) -> str:
    """Convert ASCII digits, '-', '(', ')', '+', '.', space to fullwidth."""
    return "".join(_ZENKAKU_MAP.get(c, c) for c in s)


# ---------------------------------------------------------------------------
# Name generators
# ---------------------------------------------------------------------------

def random_person(rng: random.Random, style: str | None = None) -> str:
    """Return a single name string in one of several style variants."""
    sur_k, sur_r, sur_en = rng.choice(SURNAMES)
    giv_k, giv_r, giv_en = rng.choice(GIVEN_NAMES)
    if style is None:
        style = rng.choices(
            ["kanji", "kanji_space", "kana_space", "kana", "romaji", "romaji_caps", "surname"],
            weights=[40, 20, 10, 5, 10, 5, 10],
        )[0]
    if style == "kanji":
        return f"{sur_k}{giv_k}"
    if style == "kanji_space":
        return f"{sur_k} {giv_k}"
    if style == "kana_space":
        return f"{sur_r} {giv_r}"
    if style == "kana":
        return f"{sur_r}{giv_r}"
    if style == "romaji":
        return f"{giv_en.capitalize()} {sur_en.capitalize()}"
    if style == "romaji_caps":
        return f"{sur_en.upper()} {giv_en.capitalize()}"
    # "surname"
    return sur_k


def random_person_pair(rng: random.Random, spaced: bool = False) -> tuple[str, str]:
    """Return the SAME person as (漢字フル, カタカナフル).

    Example: ("山田太郎", "ヤマダタロウ") or with space ("山田 太郎", "ヤマダ タロウ").
    """
    sur_k, sur_r, _ = rng.choice(SURNAMES)
    giv_k, giv_r, _ = rng.choice(GIVEN_NAMES)
    if spaced:
        return f"{sur_k} {giv_k}", f"{sur_r} {giv_r}"
    return f"{sur_k}{giv_k}", f"{sur_r}{giv_r}"


# ---------------------------------------------------------------------------
# Phone generator
# ---------------------------------------------------------------------------

def random_phone_jp(rng: random.Random, kind: str | None = None, fmt: str | None = None) -> str:
    """Generate a fictional Japanese phone number."""
    if kind is None:
        kind = rng.choices(
            ["mobile", "landline2", "landline3", "landline4", "ip", "freedial", "navi", "intl"],
            weights=[30, 15, 15, 10, 8, 10, 4, 8],
        )[0]

    def _digits(n: int) -> str:
        return "".join(str(rng.randint(0, 9)) for _ in range(n))

    if kind == "intl":
        mobile_num = rng.choices(["90", "80", "70"])[0]
        sub1 = _digits(4)
        sub2 = _digits(4)
        style = rng.choice(["hyphens_mobile", "space_landline", "hyphens_landline"])
        if style == "hyphens_mobile":
            return f"+81-{mobile_num}-{sub1}-{sub2}"
        city = rng.choice(["3", "6"])
        sub1_l = _digits(4)
        sub2_l = _digits(4)
        if style == "space_landline":
            return f"+81 {city} {sub1_l} {sub2_l}"
        return f"+81-{city}-{sub1_l}-{sub2_l}"

    # Build hyphen form first
    if kind == "mobile":
        prefix = rng.choice(["090", "080", "070"])
        a, b = _digits(4), _digits(4)
        hyphen = f"{prefix}-{a}-{b}"
        paren_form = hyphen  # not a landline, paren falls back to hyphen
    elif kind == "landline2":
        prefix = rng.choice(["03", "06"])
        a, b = _digits(4), _digits(4)
        hyphen = f"{prefix}-{a}-{b}"
        paren_form = f"{prefix}({a}){b}"
    elif kind == "landline3":
        prefix = rng.choice(["011", "022", "045", "052", "075", "078", "082", "092", "098"])
        a, b = _digits(3), _digits(4)
        hyphen = f"{prefix}-{a}-{b}"
        paren_form = f"{prefix}({a}){b}"
    elif kind == "landline4":
        prefix = rng.choice(["0422", "0466", "0561", "0742", "0836", "0952"])
        a, b = _digits(2), _digits(4)
        hyphen = f"{prefix}-{a}-{b}"
        paren_form = f"{prefix}({a}){b}"
    elif kind == "ip":
        prefix = "050"
        a, b = _digits(4), _digits(4)
        hyphen = f"{prefix}-{a}-{b}"
        paren_form = hyphen
    elif kind == "freedial":
        if rng.random() < 0.6:
            prefix = "0120"
            a, b = _digits(3), _digits(3)
            hyphen = f"{prefix}-{a}-{b}"
        else:
            prefix = "0800"
            a, b = _digits(3), _digits(4)
            hyphen = f"{prefix}-{a}-{b}"
        paren_form = hyphen
    else:  # navi
        prefix = "0570"
        a, b = _digits(3), _digits(3)
        hyphen = f"{prefix}-{a}-{b}"
        paren_form = hyphen

    if fmt is None:
        fmt = rng.choices(
            ["hyphen", "none", "paren", "space", "zenkaku"],
            weights=[55, 15, 10, 5, 15],
        )[0]

    if fmt == "hyphen":
        return hyphen
    if fmt == "none":
        return hyphen.replace("-", "")
    if fmt == "paren":
        return paren_form
    if fmt == "space":
        return hyphen.replace("-", " ")
    # zenkaku
    return to_zenkaku(hyphen)


# ---------------------------------------------------------------------------
# Email generator
# ---------------------------------------------------------------------------

_EMAIL_DOMAINS = [
    "example.jp",
    "example.test",
    "example.invalid",
    "mail.example.jp",
    "info.example.jp",
    "contact.example.test",
]


def random_email(rng: random.Random) -> str:
    """Generate a fictional email address using only reserved/example domains."""
    sur_k, sur_r, sur_en = rng.choice(SURNAMES)
    giv_k, giv_r, giv_en = rng.choice(GIVEN_NAMES)
    # Keep romaji ascii-only (strip digits from name component used as key)
    s = sur_en.replace("2", "")
    g = giv_en.replace("2", "")
    pattern = rng.choice([
        "initial_sur",   # t.yamada
        "sur_giv",       # yamada.taro
        "giv_sur",       # taro_yamada
        "sur_only",      # yamada
        "giv_num",       # taro99
        "init_hyp_giv",  # y-taro
    ])
    sep = rng.choice([".", "_", "-"])
    if pattern == "initial_sur":
        local = f"{g[0]}{sep}{s}"
    elif pattern == "sur_giv":
        local = f"{s}{sep}{g}"
    elif pattern == "giv_sur":
        local = f"{g}{sep}{s}"
    elif pattern == "sur_only":
        local = s
    elif pattern == "giv_num":
        local = f"{g}{rng.randint(1, 999):02d}"
    else:  # init_hyp_giv
        local = f"{s[0]}-{g}"

    # Optional trailing digits (1-3)
    if rng.random() < 0.25:
        local += str(rng.randint(1, 999))

    domain = rng.choice(_EMAIL_DOMAINS)
    return f"{local}@{domain}"


# ---------------------------------------------------------------------------
# URL generator
# ---------------------------------------------------------------------------

def _token(rng: random.Random, n: int) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(rng.choice(alphabet) for _ in range(n))


def random_url(rng: random.Random) -> str:
    """Generate a fictional URL on a reserved domain."""
    host = rng.choice([
        "example.invalid",
        "example.test",
        "privacy.example.invalid",
        "secure.example.jp",
        "portal.example.test",
    ])
    path = rng.choice(["orders", "verify", "accounts", "tickets", "download",
                        "profile", "invoice", "receipt"])
    ident_style = rng.choice(["test_num", "user_num", "date_code", "token_path"])
    if ident_style == "test_num":
        ident = f"test-{rng.randint(1, 9999):04d}"
    elif ident_style == "user_num":
        ident = f"user-{rng.randint(1, 9999):04d}"
    elif ident_style == "date_code":
        ident = f"R2026{rng.randint(1, 12):02d}{rng.randint(1, 28):02d}"
    else:
        ident = _token(rng, 12)

    url = f"https://{host}/{path}/{ident}"
    if rng.random() < 0.35:
        url += f"?token={_token(rng, 12)}"
    if rng.random() < 0.15:
        url += f"/{rng.choice(['confirm', 'done', 'details'])}"
    return url


# ---------------------------------------------------------------------------
# Secret generator
# ---------------------------------------------------------------------------

def random_secret(rng: random.Random) -> str:
    """Generate a fictional API key / token / password."""
    kind = rng.choice(["sk", "pk", "bearer", "password", "jwt", "api"])
    if kind == "sk":
        return "sk-test-" + _token(rng, 24)
    if kind == "pk":
        return "pk_test_" + _token(rng, 24)
    if kind == "bearer":
        return "Bearer " + _token(rng, 32)
    if kind == "jwt":
        return ".".join(_token(rng, n) for n in [16, 24, 16])
    if kind == "api":
        return "api_" + _token(rng, 28)
    return rng.choice(["P@ssw0rd-test-001", "dummy-password-0000", "TempPass-123456"])


# ---------------------------------------------------------------------------
# Date generator
# ---------------------------------------------------------------------------

ERAS = [
    ("令和", (1, 8)),
    ("平成", (1, 31)),
    ("昭和", (1, 64)),
    ("大正", (1, 15)),
]

YEAR_RANGES: dict[str, tuple[int, int]] = {
    "birth": (1940, 2015),
    "recent": (2015, 2026),
    "any": (1940, 2026),
}

_ZEN_DIGITS = str.maketrans("0123456789", "０１２３４５６７８９")


def random_date_jp(rng: random.Random, year_key: str = "any") -> str:
    """Generate a fictional Japanese date string in various styles."""
    year = rng.randint(*YEAR_RANGES[year_key])
    month, day = rng.randint(1, 12), rng.randint(1, 28)
    style = rng.choices(
        ["kanji", "slash", "slash_zero", "hyphen", "dot", "wareki",
         "wareki_short", "no_year", "zenkaku"],
        weights=[15, 10, 10, 10, 10, 20, 10, 10, 5],
    )[0]
    if style == "kanji":
        return f"{year}年{month}月{day}日"
    if style == "slash":
        return f"{year}/{month}/{day}"
    if style == "slash_zero":
        return f"{year}/{month:02d}/{day:02d}"
    if style == "hyphen":
        return f"{year}-{month:02d}-{day:02d}"
    if style == "dot":
        return f"{year}.{month:02d}.{day:02d}"
    if style == "wareki_short":
        era_name, (lo, hi) = rng.choice(ERAS)
        era_abbr = era_name[0]  # 令, 平, 昭, 大
        ey = rng.randint(lo, hi)
        return f"{era_abbr}{ey}.{month}.{day}"
    if style == "no_year":
        return f"{month}月{day}日"
    if style == "zenkaku":
        return f"{year}年{month}月{day}日".translate(_ZEN_DIGITS)
    # wareki
    era_name, (lo, hi) = rng.choice(ERAS)
    ey = rng.randint(lo, hi)
    ey_str = "元" if ey == 1 else str(ey)
    return f"{era_name}{ey_str}年{month}月{day}日"


# ---------------------------------------------------------------------------
# Generic ID generator (ported from gen_synthetic_date_id_jp.py)
# ---------------------------------------------------------------------------

def random_generic_id(rng: random.Random, kind: str | None = None) -> str:
    """Generate a fictional internal identifier (customer/member/contract etc.)."""
    if kind is None or kind == "any":
        kind = rng.choice(["cust", "member", "contract", "app", "receipt"])
    if kind == "cust":
        return "C" + "".join(str(rng.randint(0, 9)) for _ in range(7))
    if kind == "member":
        return "M-" + "".join(str(rng.randint(0, 9)) for _ in range(6))
    if kind == "contract":
        return f"CNTR-{rng.randint(2015, 2026)}-{rng.randint(1, 999):03d}"
    if kind == "app":
        return "A" + "".join(str(rng.randint(0, 9)) for _ in range(8))
    # receipt
    y, m, d = rng.randint(2015, 2026), rng.randint(1, 12), rng.randint(1, 28)
    return f"R{y}{m:02d}{d:02d}-{rng.randint(1, 9999):04d}"


# ---------------------------------------------------------------------------
# Japanese government / official ID generator
# ---------------------------------------------------------------------------

def random_jp_id(rng: random.Random, kind: str | None = None) -> tuple[str, str]:
    """Return (value, kind) for a fictional Japanese official ID."""
    _KINDS = ["mynumber", "license", "passport", "nenkin", "hoken",
              "bank", "yucho", "zairyu"]
    _WEIGHTS = [25, 15, 12, 12, 12, 12, 6, 6]
    if kind is None:
        kind = rng.choices(_KINDS, weights=_WEIGHTS)[0]

    def _d(n: int) -> str:
        return "".join(str(rng.randint(0, 9)) for _ in range(n))

    def _uc(n: int) -> str:
        return "".join(rng.choice(string.ascii_uppercase) for _ in range(n))

    if kind == "mynumber":
        digits = _d(12)
        fmt = rng.choice(["space", "plain", "hyphen"])
        if fmt == "space":
            value = f"{digits[:4]} {digits[4:8]} {digits[8:]}"
        elif fmt == "hyphen":
            value = f"{digits[:4]}-{digits[4:8]}-{digits[8:]}"
        else:
            value = digits
    elif kind == "license":
        value = _d(12)
    elif kind == "passport":
        value = _uc(2) + _d(7)
    elif kind == "nenkin":
        value = f"{_d(4)}-{_d(6)}"
    elif kind == "hoken":
        value = f"{_d(8)}-{_d(2)}"
    elif kind == "bank":
        value = _d(7)
    elif kind == "yucho":
        # 記号5桁 (starts with 1, ends with 0) - 番号8桁
        sym = "1" + _d(3) + "0"
        num = _d(8)
        value = f"{sym}-{num}"
    else:  # zairyu
        value = _uc(2) + _d(8) + _uc(2)

    return value, kind


# ---------------------------------------------------------------------------
# Building name generator (ported from gen_synthetic_address_jp.py)
# ---------------------------------------------------------------------------

def random_building(rng: random.Random) -> str:
    """Generate a fictional building name with room/floor suffix."""
    name = rng.choice(BUILDING_NAMES)
    floor, room = rng.randint(1, 12), rng.randint(1, 20)
    style = rng.choice(["room_go", "room_only", "floor_only"])
    if style == "room_go":
        return f"{name}{floor}{room:02d}号室"
    if style == "room_only":
        return f"{name}{room}"
    return f"{name}{floor}F"
