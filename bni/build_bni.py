# -*- coding: utf-8 -*-
"""
BNI 1to1シート 公開ページ ビルドスクリプト。

data/members/*.json を読み込み、各メンバーの `<slug>/index.html` と
一覧 `index.html` を生成する。

使い方:
    cd bni
    python build_bni.py

メンバーを追加する手順は README.md を参照。
"""
import json
import html
import pathlib
import sys

BASE_DIR = pathlib.Path(__file__).resolve().parent
MEMBERS_DIR = BASE_DIR / "data" / "members"
SITE_ROOT = "https://hiro0183.github.io/uplink-lp/"
LP_URL = "https://hiro0183.github.io/uplink-lp/"
BNI_ROOT = "https://hiro0183.github.io/uplink-lp/bni/"


def esc(s):
    if s is None:
        return ""
    return html.escape(str(s), quote=True)


def load_members():
    members = []
    for path in sorted(MEMBERS_DIR.glob("*.json")):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["_path"] = path
        members.append(data)
    return members


# ---------------------------------------------------------------------------
# 共通スタイル（自己完結・外部CSS/JSは読まない。Google Fontsのみ可）
# ---------------------------------------------------------------------------
STYLE = """
:root{
  --bg:#F7F3E8; --card:#FFFFFF; --line:#DCD6BF;
  --ink:#1F3329; --ink2:#3E5548; --mut:#71806F;
  --green:#2F5D46; --greend:#1D3A2C; --cream:#F1EAD3;
  --accent:#2F5D46;
  --ff:"Noto Sans JP","Hiragino Kaku Gothic ProN","Yu Gothic","Meiryo",sans-serif;
  --fm:"Shippori Mincho","Hiragino Mincho ProN","Yu Mincho",serif;
}
@media (prefers-color-scheme: dark){
  :root{
    --bg:#12201A; --card:#1A2C24; --line:#2E4438;
    --ink:#EDF3EC; --ink2:#C8D6C9; --mut:#8FA192;
    --green:#7FD1A8; --greend:#0E1913; --cream:#20302A;
    --accent:#7FD1A8;
  }
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--bg); color:var(--ink); font-family:var(--ff);
  font-size:16px; line-height:1.7; -webkit-font-smoothing:antialiased;
}
.wrap{max-width:640px;margin:0 auto;padding:28px 20px 56px}
a{color:var(--green)}
h1,h2,h3{font-family:var(--fm); color:var(--ink); line-height:1.5; letter-spacing:.02em}
p{margin:0 0 1em}

/* ---- ヘッダー（名刺の続き） ---- */
.card-head{text-align:center; padding-top:8px}
.photo{width:120px;height:120px;border-radius:50%;object-fit:cover;
  border:3px solid var(--card); box-shadow:0 0 0 3px var(--green); margin:0 auto 16px; display:block}
.chapter{font-size:13px; letter-spacing:.14em; color:var(--mut); margin-bottom:6px}
.category{display:inline-block; background:var(--cream); color:var(--green);
  border:1px solid var(--line); border-radius:999px; padding:6px 16px; font-size:13.5px;
  font-weight:700; letter-spacing:.04em; margin-bottom:14px}
.name{font-size:26px; font-weight:700; margin:0 0 4px}
.kana{font-size:13.5px; color:var(--mut); margin-bottom:14px}
.tagline{font-size:16.5px; color:var(--ink2); font-weight:600}

/* ---- セクション共通 ---- */
section{margin-top:36px}
.sec-title{display:flex; align-items:center; gap:10px; font-size:13px; letter-spacing:.18em;
  color:var(--green); font-weight:700; margin-bottom:14px}
.sec-title::after{content:"";flex:1;height:1px;background:var(--line)}

/* ---- 引用カード（紹介のお願い） ---- */
.ask-card{background:var(--card); border:1px solid var(--line); border-left:4px solid var(--green);
  border-radius:10px; padding:22px 20px; font-size:16.5px; line-height:1.8; color:var(--ink)}

/* ---- 番号リスト ---- */
.numlist{list-style:none; margin:0; padding:0; counter-reset:n}
.numlist li{counter-increment:n; display:grid; grid-template-columns:28px 1fr; gap:10px;
  padding:12px 0; border-bottom:1px solid var(--line); font-size:15.5px; color:var(--ink2)}
.numlist li:last-child{border-bottom:none}
.numlist li::before{content:counter(n); font-family:var(--fm); font-weight:700; color:var(--green); font-size:16px}
.note{font-size:13.5px; color:var(--mut); margin-top:12px}

/* ---- CTA ---- */
.cta-box{text-align:center; background:var(--cream); border:1px solid var(--line);
  border-radius:14px; padding:26px 18px; margin-top:14px}
.cta-btn{display:inline-block; background:var(--green); color:#FFFFFF !important; text-decoration:none;
  font-weight:700; font-size:17px; letter-spacing:.03em; padding:16px 30px; border-radius:999px;
  box-shadow:0 8px 20px rgba(47,93,70,.28)}
.cta-sub{font-size:13.5px; color:var(--mut); margin-top:14px; margin-bottom:0}

/* ---- 紹介できる専門家（チップ） ---- */
.give-intro{font-size:14.5px; color:var(--mut); margin-bottom:16px}
.give-group{margin-bottom:16px}
.give-field{font-size:14.5px; font-weight:700; color:var(--ink); margin-bottom:8px}
.give-field .cnt{color:var(--mut); font-weight:400; font-size:13px}
.chips{display:flex; flex-wrap:wrap; gap:8px}
.chip{background:var(--card); border:1px solid var(--line); border-radius:999px;
  padding:6px 13px; font-size:13.5px; color:var(--ink2)}

/* ---- details ---- */
details{background:var(--card); border:1px solid var(--line); border-radius:10px;
  padding:16px 18px; margin-bottom:12px}
details > summary{cursor:pointer; font-weight:700; font-size:15.5px; color:var(--ink); list-style:none;
  display:flex; align-items:center; justify-content:space-between}
details > summary::-webkit-details-marker{display:none}
details > summary::after{content:"▾"; color:var(--green); font-size:13px; margin-left:8px}
details[open] > summary::after{content:"▴"}
.gains-block{margin-top:14px}
.gains-block h4{font-size:12.5px; letter-spacing:.14em; color:var(--green); margin:0 0 8px; font-weight:700}
.gains-block ul{margin:0 0 14px; padding-left:1.2em}
.gains-block li{font-size:14.5px; color:var(--ink2); margin-bottom:6px; line-height:1.65}
.bio-block{margin-top:6px}
.bio-block dl{margin:0 0 14px}
.bio-block dt{font-size:12px; color:var(--mut); letter-spacing:.06em; margin-top:10px}
.bio-block dd{font-size:14.5px; color:var(--ink2); margin:2px 0 0; line-height:1.7}

/* ---- フッター ---- */
footer{margin-top:48px; padding-top:20px; border-top:1px solid var(--line);
  font-size:12.5px; color:var(--mut); text-align:center; line-height:1.9}
footer a{color:var(--mut)}

/* ---- 一覧ページ用 ---- */
.member-list{list-style:none; margin:0; padding:0; display:grid; gap:14px}
.member-card{display:flex; align-items:center; gap:16px; background:var(--card);
  border:1px solid var(--line); border-radius:12px; padding:16px; text-decoration:none}
.member-card img{width:64px;height:64px;border-radius:50%;object-fit:cover;flex:none}
.member-card .mc-name{font-weight:700; color:var(--ink); font-size:16px; margin:0 0 2px}
.member-card .mc-cat{font-size:13px; color:var(--green)}
"""


def render_member_page(m):
    name = esc(m["name"])
    kana = esc(m.get("kana", ""))
    chapter = esc(m.get("chapter", ""))
    category = esc(m.get("category", ""))
    tagline = esc(m.get("tagline", ""))
    photo = esc(m.get("photo", "photo.jpg"))
    ask = esc(m.get("ask", ""))
    updated = esc(m.get("updated", ""))

    referral_items = "".join(
        f"<li>{esc(t)}</li>" for t in m.get("referral_targets", [])
    )
    referral_note = m.get("referral_note", "")
    referral_main = m.get("referral_main", "")
    action_request = m.get("action_request", "")
    referral_partners = m.get("referral_partners", [])
    referral_partners_items = "".join(f"<li>{esc(t)}</li>" for t in referral_partners)

    # 紹介できる専門家
    give_groups = ""
    for g in m.get("giving", []):
        chips = "".join(f'<span class="chip">{esc(i)}</span>' for i in g.get("items", []))
        give_groups += (
            f'<div class="give-group">'
            f'<div class="give-field">{esc(g.get("field",""))}'
            f' <span class="cnt">（{esc(g.get("count",""))}名）</span></div>'
            f'<div class="chips">{chips}</div>'
            f"</div>"
        )
    total_giving = sum(g.get("count", 0) for g in m.get("giving", []))

    # G.A.I.N.S.
    gains = m.get("gains", {})
    def gains_ul(key):
        items = gains.get(key, [])
        return "".join(f"<li>{esc(i)}</li>" for i in items)

    work_steps_html = (
        f"<h4>仕事の中身（3ステップ）｜「社長を現場から解放する」とは具体的に何をするか</h4><ul>{gains_ul('work_steps')}</ul>"
        if gains.get("work_steps") else ""
    )

    gains_html = f"""
      <div class="gains-block">
        <h4>GOALS｜目標</h4><ul>{gains_ul('goals')}</ul>
        {work_steps_html}
        <h4>ACCOMPLISHMENTS｜実績</h4><ul>{gains_ul('accomplishments')}</ul>
        <h4>INTERESTS｜興味・関心</h4><ul>{gains_ul('interests')}</ul>
        <h4>NETWORKS｜人脈</h4><ul>{gains_ul('networks')}</ul>
        <h4>SKILLS｜スキル</h4><ul>{gains_ul('skills')}</ul>
      </div>
    """

    # 略歴
    bio = m.get("bio", {})
    def dl(section):
        d = bio.get(section, {})
        out = ""
        for k, v in d.items():
            out += f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>"
        return out

    bio_html = f"""
      <div class="bio-block">
        <h4 class="gains-block-h">ビジネス</h4>
        <dl>{dl('business')}</dl>
        <h4 class="gains-block-h">個人</h4>
        <dl>{dl('personal')}</dl>
        <h4 class="gains-block-h">その他</h4>
        <dl>{dl('more')}</dl>
      </div>
    """
    bio_html = bio_html.replace(
        '<h4 class="gains-block-h">',
        '<h4 style="font-size:12.5px;letter-spacing:.14em;color:var(--green);margin:14px 0 8px;font-weight:700">',
    )

    links = m.get("links", [])
    timerex_url = ""
    for l in links:
        if "timerex" in l.get("url", "").lower():
            timerex_url = l["url"]
            break
    if not timerex_url and links:
        timerex_url = links[0]["url"]

    lp_link = LP_URL

    page = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name}｜1to1シート（BNI白樺）</title>
<meta name="description" content="{name}（{chapter}）の1to1シート。紹介のお願い、紹介できる専門家、G.A.I.N.S.をまとめた個人ページです。">
<meta name="robots" content="noindex,nofollow">
<meta property="og:type" content="profile">
<meta property="og:title" content="{name}｜1to1シート（BNI白樺）">
<meta property="og:description" content="{tagline}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Shippori+Mincho:wght@500;700&display=swap" rel="stylesheet">
<style>{STYLE}</style>
</head>
<body>
<div class="wrap">

  <div class="card-head">
    <img class="photo" src="{photo}" alt="{name}">
    <div class="chapter">{chapter}</div>
    <div class="category">{category}</div>
    <h1 class="name">{name}</h1>
    <div class="kana">（{kana}）</div>
    <p class="tagline">{tagline}</p>
  </div>

  <section>
    <div class="sec-title">紹介のお願い</div>
    <div class="ask-card">{ask}</div>
  </section>

  <section>
    <div class="sec-title">こんな社長をご紹介ください</div>
    {'<p class="note" style="margin-top:0">【お客さんとして】</p>' if referral_partners else ''}
    {f'<p><strong>本命はこれ1つです：{esc(referral_main)}</strong></p>' if referral_main else ''}
    {'<p class="sec-title" style="margin-top:0">こんな様子が見えたら、その社長です</p>' if referral_main else ''}
    <ol class="numlist">{referral_items}</ol>
    {f'<p class="note">※{esc(referral_note)}</p>' if referral_note else ''}
    {f'''<p class="sec-title" style="margin-top:22px">【一緒に組む方として】</p>
    <ol class="numlist">{referral_partners_items}</ol>''' if referral_partners else ''}
  </section>

  {f'''<section>
    <div class="sec-title">見込み客に、こう言ってください</div>
    <div class="ask-card">{esc(action_request)}</div>
  </section>''' if action_request else ''}

  <section>
    <div class="sec-title">1to1を申し込む</div>
    <div class="cta-box">
      <a class="cta-btn" href="{esc(timerex_url)}" target="_blank" rel="noopener">1to1を申し込む（TimeRex）</a>
      <p class="cta-sub">定例会・Messengerで声をかけてもらえれば、その場で日程を決めます</p>
    </div>
  </section>

  <section>
    <div class="sec-title">紹介できる専門家（{total_giving}名・分野）</div>
    <p class="give-intro">お名前は1to1でお伝えします。探している分野を教えてください。</p>
    {give_groups}
  </section>

  <section>
    <div class="sec-title">G.A.I.N.S.</div>
    <details open>
      <summary>Goals / Accomplishments / Interests / Networks / Skills</summary>
      {gains_html}
    </details>
  </section>

  <section>
    <div class="sec-title">略歴</div>
    <details open>
      <summary>ビジネス・個人・その他</summary>
      {bio_html}
    </details>
  </section>

  <footer>
    合同会社UPLINK<br>
    <a href="{lp_link}" target="_blank" rel="noopener">{lp_link}</a><br>
    更新日 {updated}<br>
    このページはBNIメンバー向けです（検索には出しません）
  </footer>

</div>
</body>
</html>
"""
    return page


def render_index(members):
    cards = ""
    for m in members:
        slug = m["slug"]
        cards += (
            f'<li><a class="member-card" href="{slug}/">'
            f'<img src="{slug}/{esc(m.get("photo","photo.jpg"))}" alt="{esc(m["name"])}">'
            f'<div><p class="mc-name">{esc(m["name"])}</p>'
            f'<p class="mc-cat">{esc(m.get("category",""))}</p></div>'
            f"</a></li>"
        )

    page = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BNI 1to1シート一覧</title>
<meta name="robots" content="noindex,nofollow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Shippori+Mincho:wght@500;700&display=swap" rel="stylesheet">
<style>{STYLE}</style>
</head>
<body>
<div class="wrap">
  <h1 style="text-align:center;margin-bottom:24px">BNI 1to1シート</h1>
  <ul class="member-list">
    {cards}
  </ul>
  <footer>合同会社UPLINK<br><a href="{LP_URL}" target="_blank" rel="noopener">{LP_URL}</a></footer>
</div>
</body>
</html>
"""
    return page


def main():
    members = load_members()
    if not members:
        print("メンバーデータが見つかりません: data/members/*.json", file=sys.stderr)
        sys.exit(1)

    written = []

    for m in members:
        slug = m["slug"]
        member_dir = BASE_DIR / slug
        member_dir.mkdir(parents=True, exist_ok=True)
        out_path = member_dir / "index.html"
        html_out = render_member_page(m)
        out_path.write_text(html_out, encoding="utf-8", newline="\n")
        written.append(out_path)

    index_path = BASE_DIR / "index.html"
    index_html = render_index(members)
    index_path.write_text(index_html, encoding="utf-8", newline="\n")
    written.append(index_path)

    print("生成したファイル一覧:")
    for p in written:
        print(f"  {p}")


if __name__ == "__main__":
    main()
