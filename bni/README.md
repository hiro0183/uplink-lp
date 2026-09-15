# BNI 1to1シート 公開ページ

名刺のQRコード1個から開く、BNIメンバー個人の1to1シート公開ページ。
`data/members/*.json` にデータを1枚足して `build_bni.py` を走らせるだけで、メンバーページが増える。

公開URL: `https://hiro0183.github.io/uplink-lp/bni/`
一覧: `https://hiro0183.github.io/uplink-lp/bni/`
個人ページ例: `https://hiro0183.github.io/uplink-lp/bni/nariai/`

## メンバーを1人足す手順

1. `data/members/<slug>.json` を `nariai.json` をコピーして書く
2. 写真を `<slug>/photo.jpg` に置く（長辺600px。Pillowで縮小: `im.resize(...)` 参考は `build_bni.py` 同ディレクトリの作業ログ、または下記コマンド例）
3. `cd bni && python build_bni.py`
4. `python make_qr.py <slug>`
5. `git add bni && git commit -m "..."` → `git push`（Pages反映は数分）

写真の縮小コマンド例（Pythonワンライナー）:
```python
from PIL import Image
im = Image.open("元画像.jpg").convert("RGB")
w, h = im.size
scale = 600 / max(w, h)
im.resize((round(w*scale), round(h*scale))).save("bni/<slug>/photo.jpg", quality=85)
```

## 注意

- **第三者の実名・メールアドレス・電話番号は載せない。** `giving`（紹介できる専門家）は分野・肩書だけにする。
- 他メンバーのシートを追加するときは、**本人の許可をもらってから**。
- URLは検索エンジンに出さない（全ページ `noindex,nofollow`）。ただし**URLを知っている人は誰でも開ける**ので、載せる個人情報の粒度はBNIのGAINSシート程度（家族構成・趣味・拠点の町名くらい）にとどめ、住所の番地や連絡先までは書かない。
- QR画像の出力先は `C:\Users\tujid\OneDrive\Desktop\BNI\06_QRコード\`（印刷用PNG・印刷用SVG・待受用PNGの3種）。サイト内 `bni/<slug>/` にも `qr.png` `qr.svg` のみ複製される（待受用は置かない）。

## ファイル構成

```
bni/
  README.md                 このファイル
  build_bni.py               data/members/*.json → HTML生成
  make_qr.py                 slugを渡すとQR画像を出力
  data/members/nariai.json   成相さんのデータ
  index.html                 メンバー一覧（生成物）
  nariai/index.html          成相さんの1to1ページ（生成物）
  nariai/photo.jpg           顔写真（長辺600px）
  nariai/qr.png / qr.svg     QRコード（サイト内用）
```
