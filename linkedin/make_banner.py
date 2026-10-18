from PIL import Image, ImageDraw, ImageFont
import sys

W, H = 1584, 396
out = sys.argv[1]

# 落ち着いた緑のグラデーション（左が濃く、右が少し明るい）
img = Image.new("RGB", (W, H))
px = img.load()
c1 = (24, 62, 52)
c2 = (46, 96, 78)
for x in range(W):
    t = x / (W - 1)
    col = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    for y in range(H):
        px[x, y] = col

d = ImageDraw.Draw(img)
bold = "C:/Windows/Fonts/NotoSansJP-Bold.ttf"
med = "C:/Windows/Fonts/YuGothM.ttc"
f_main = ImageFont.truetype(bold, 64)
f_sub = ImageFont.truetype(bold, 34)
f_co = ImageFont.truetype(med, 28)

R = W - 90  # 右寄せの基準線
gold = (226, 196, 120)
white = (250, 248, 240)
soft = (200, 220, 210)

def right(text, y, font, fill):
    w = d.textlength(text, font=font)
    d.text((R - w, y), text, font=font, fill=fill)
    return w

right("1日2時間、経営者の時間をつくる", 92, f_main, white)
lw = right("社長を現場から解放する仕掛け人", 196, f_sub, gold)
# 細い金の線
d.line([(R - lw, 258), (R, 258)], fill=gold, width=2)
right("合同会社UP LINK 代表　成相 裕康", 276, f_co, soft)

img.save(out, quality=92)
print("saved", out, img.size)
