#!/usr/bin/env python3
"""Generate the favicon set and the Open Graph card from the portrait.

Derived assets, committed to the repo so no build step is needed. Re-run after
changing the source photo:

    .venv/bin/python scripts/make_icons.py

The crop and the tone curve were chosen by rendering candidates at 16/32/64px
and comparing them -- the source is a low-key, side-lit portrait, so it needs a
tight crop on the face and a lift before it survives being 32 pixels wide.
"""

import os

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(ROOT, 'src', 'static')
PORTRAIT = os.path.join(STATIC, 'images', 'sb_photos_bw.jpg')
ICON_DIR = os.path.join(STATIC, 'images', 'icons')
OG_DIR = os.path.join(STATIC, 'images', 'og')

# Face position in the source frame, as fractions of its width/height.
FACE_X, FACE_Y, FACE_SIZE = 0.415, 0.400, 0.22

SERIF_CANDIDATES = [
    ('/System/Library/Fonts/Supplemental/Didot.ttc', 0),
    ('/System/Library/Fonts/Supplemental/Baskerville.ttc', 0),
    ('/System/Library/Fonts/Supplemental/Georgia.ttf', 0),
]
SANS_CANDIDATES = [
    ('/System/Library/Fonts/Helvetica.ttc', 0),
    ('/System/Library/Fonts/Supplemental/Arial.ttf', 0),
]


def load_font(candidates, size):
    for path, index in candidates:
        try:
            return ImageFont.truetype(path, size, index=index)
        except OSError:
            continue
    return ImageFont.load_default()


def face_square():
    """Square crop of the face, lifted so it reads at small sizes."""
    src = Image.open(PORTRAIT).convert('L')
    w, h = src.size
    side = int(FACE_SIZE * w)
    cx, cy = int(FACE_X * w), int(FACE_Y * h)
    crop = src.crop((cx - side // 2, cy - side // 2,
                     cx + side // 2, cy + side // 2))
    crop = ImageOps.autocontrast(crop, cutoff=1)
    crop = ImageEnhance.Brightness(crop).enhance(1.9)
    return ImageEnhance.Contrast(crop).enhance(1.4).convert('RGB')


def write_icons(face):
    os.makedirs(ICON_DIR, exist_ok=True)
    for size in (16, 32, 180, 192, 512):
        name = {
            180: 'apple-touch-icon.png',
        }.get(size, f'icon-{size}.png')
        face.resize((size, size), Image.LANCZOS).save(
            os.path.join(ICON_DIR, name), optimize=True
        )
        print('wrote', name)

    # Multi-resolution .ico for /favicon.ico, which crawlers and older
    # browsers request directly regardless of what the markup declares.
    face.resize((256, 256), Image.LANCZOS).save(
        os.path.join(ICON_DIR, 'favicon.ico'),
        sizes=[(16, 16), (32, 32), (48, 48)],
    )
    print('wrote favicon.ico')


def write_og(face):
    """A 1200x630 share card: portrait left, name right, same as the site."""
    os.makedirs(OG_DIR, exist_ok=True)
    W, H = 1200, 630
    card = Image.new('RGB', (W, H), (0, 0, 0))

    # Portrait bleeding off the left edge, matching the homepage layout.
    src = Image.open(PORTRAIT).convert('L')
    sw, sh = src.size
    target_h = H
    scale = target_h / sh * 1.9
    portrait = src.resize((int(sw * scale), int(sh * scale)), Image.LANCZOS)
    # Keep the face in frame after scaling up.
    px = int(FACE_X * portrait.width) - 250
    py = int(FACE_Y * portrait.height) - 300
    portrait = portrait.crop((px, py, px + 520, py + H)).convert('RGB')
    card.paste(portrait, (0, 0))

    # Fade the portrait's right edge into the black field.
    fade_w = 170
    fade = Image.new('L', (fade_w, H))
    for x in range(fade_w):
        ImageDraw.Draw(fade).line(
            [(x, 0), (x, H)], fill=int(255 * (x / fade_w))
        )
        
    card.paste(Image.new('RGB', (fade_w, H), (0, 0, 0)),
               (520 - fade_w, 0), fade)

    draw = ImageDraw.Draw(card)
    x = 610
    draw.text((x, 232), 'Sasha Bagrov',
              font=load_font(SERIF_CANDIDATES, 76), fill=(240, 240, 240))
    draw.line([(x, 348), (x + 54, 348)], fill=(240, 240, 240), width=2)
    draw.text((x, 382), 'developer, founder, photographer',
              font=load_font(SANS_CANDIDATES, 27), fill=(150, 150, 150))
    draw.text((x, 424), 'London',
              font=load_font(SANS_CANDIDATES, 27), fill=(150, 150, 150))
    draw.text((x, 520), 'alexanderbagrov.com',
              font=load_font(SANS_CANDIDATES, 23), fill=(110, 110, 110))

    path = os.path.join(OG_DIR, 'og-card.jpg')
    card.save(path, quality=88, optimize=True, progressive=True)
    print('wrote og-card.jpg', os.path.getsize(path) // 1024, 'KB')


if __name__ == '__main__':
    face = face_square()
    write_icons(face)
    write_og(face)
