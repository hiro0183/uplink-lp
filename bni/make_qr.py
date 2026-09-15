# -*- coding: utf-8 -*-
"""
BNI 1to1シートのQRコードを生成する。

使い方:
    python make_qr.py <slug>

例:
    python make_qr.py nariai

出力（3種）:
  1. QR_<slug>_印刷用.png  2000x2000 余白あり 黒/白 誤り訂正H
  2. QR_<slug>_印刷用.svg
  3. QR_<slug>_待受用.png  1170x2532 iPhone待受（QR＋2行のキャッチ＋URL）

出力先:
  - C:\\Users\\tujid\\OneDrive\\Desktop\\BNI\\06_QRコード\\ （3枚すべて）
  - bni/<slug>/ 内にも qr.png / qr.svg のみコピー（待受用は置かない）
"""
import json
import pathlib
import sys

import qrcode
from qrcode.image.pil import PilImage
import qrcode.image.svg
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = pathlib.Path(__file__).resolve().parent
MEMBERS_DIR = BASE_DIR / "data" / "members"
BNI_ROOT_URL = "https://hiro0183.github.io/uplink-lp/bni/"
DESKTOP_QR_DIR = pathlib.Path(
    r"C:\Users\tujid\OneDrive\Desktop\BNI\06_QRコード"
)

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\msgothic.ttc",
]

# 待受用の配色（薄いクリーム背景／濃い緑文字）
WALL_BG = (247, 243, 232)      # 薄いクリーム
WALL_INK = (29, 58, 44)        # 濃い緑


def load_font(size):
    for path in FONT_CANDIDATES:
        p = pathlib.Path(path)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except OSError:
                continue
    return ImageFont.load_default()


def load_member(slug):
    path = MEMBERS_DIR / f"{slug}.json"
    if not path.exists():
        print(f"メンバーデータが見つかりません: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def make_print_png(url, out_path, size=2000):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(image_factory=PilImage, fill_color="black", back_color="white")
    img = img.convert("RGB").resize((size, size), Image.NEAREST)
    img.save(out_path)
    return img


def make_print_svg(url, out_path):
    factory = qrcode.image.svg.SvgPathImage
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
        image_factory=factory,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(str(out_path))


def make_wallpaper(url, name, tagline, out_path, w=1170, h=2532):
    canvas = Image.new("RGB", (w, h), WALL_BG)
    draw = ImageDraw.Draw(canvas)

    # QRコード本体（幅の70%、誤り訂正H、余白なしで作って自前で貼る）
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(image_factory=PilImage, fill_color=WALL_INK, back_color=WALL_BG)
    qr_img = qr_img.convert("RGB")

    qr_size = int(w * 0.70)
    qr_img = qr_img.resize((qr_size, qr_size), Image.NEAREST)

    qr_x = (w - qr_size) // 2
    qr_y = int(h * 0.16)
    canvas.paste(qr_img, (qr_x, qr_y))

    # テキスト2行
    line1 = f"{name}｜1to1シート・紹介できる専門家"
    line2 = tagline

    font1 = load_font(46)
    font2 = load_font(38)
    font3 = load_font(30)

    text_y = qr_y + qr_size + 70

    def draw_centered(text, font, y, fill=WALL_INK):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (w - tw) // 2
        draw.text((x, y), text, font=font, fill=fill)
        return bbox[3] - bbox[1]

    # 1行目が幅を超える場合はフォントを段階的に縮小
    f1 = font1
    for size in (46, 40, 34, 28):
        f1 = load_font(size)
        bbox = draw.textbbox((0, 0), line1, font=f1)
        if (bbox[2] - bbox[0]) <= w - 100:
            break

    lh1 = draw_centered(line1, f1, text_y)
    text_y += lh1 + 28

    f2 = font2
    for size in (38, 32, 26):
        f2 = load_font(size)
        bbox = draw.textbbox((0, 0), line2, font=f2)
        if (bbox[2] - bbox[0]) <= w - 100:
            break
    draw_centered(line2, f2, text_y)

    # 最下段にURL
    url_y = h - 110
    draw_centered(url, font3, url_y, fill=WALL_INK)

    canvas.save(out_path, quality=90)
    return canvas


def main():
    if len(sys.argv) != 2:
        print("使い方: python make_qr.py <slug>", file=sys.stderr)
        sys.exit(1)

    slug = sys.argv[1]
    member = load_member(slug)
    url = f"{BNI_ROOT_URL}{slug}/"
    name = member.get("name", slug)
    tagline = member.get("tagline", "")

    print(f"生成対象URL: {url}")

    DESKTOP_QR_DIR.mkdir(parents=True, exist_ok=True)
    member_dir = BASE_DIR / slug
    member_dir.mkdir(parents=True, exist_ok=True)

    print_png_path = DESKTOP_QR_DIR / f"QR_{slug}_印刷用.png"
    print_svg_path = DESKTOP_QR_DIR / f"QR_{slug}_印刷用.svg"
    wall_png_path = DESKTOP_QR_DIR / f"QR_{slug}_待受用.png"

    make_print_png(url, print_png_path)
    print(f"作成: {print_png_path}")

    make_print_svg(url, print_svg_path)
    print(f"作成: {print_svg_path}")

    make_wallpaper(url, name, tagline, wall_png_path)
    print(f"作成: {wall_png_path}")

    # bni/<slug>/ にも qr.png / qr.svg のみ複製（待受用は置かない）
    site_png_path = member_dir / "qr.png"
    site_svg_path = member_dir / "qr.svg"
    make_print_png(url, site_png_path)
    print(f"作成: {site_png_path}")
    make_print_svg(url, site_svg_path)
    print(f"作成: {site_svg_path}")

    print("完了。")


if __name__ == "__main__":
    main()
