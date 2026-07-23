from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCREEN = ROOT / 'qa_output' / 'screenshots' / 'startup.png'
OUT_DIR = ROOT / 'qa_output' / 'reports'
OUT_DIR.mkdir(parents=True, exist_ok=True)

img = Image.open(SCREEN).convert('RGBA')
w, h = img.size

regions = [
    (0.02, 0.06, 0.18, 0.92, 'Left sidebar (navigation)'),
    (0.22, 0.06, 0.74, 0.80, 'Main content panel'),
    (0.76, 0.06, 0.98, 0.30, 'Top-right calendar/card'),
    (0.76, 0.32, 0.98, 0.56, 'Middle-right notes/list'),
    (0.76, 0.58, 0.98, 0.86, 'Lower-right activity panel'),
    (0.22, 0.82, 0.74, 0.94, 'Footer controls/quick actions'),
    (0.02, 0.02, 0.12, 0.08, 'Top-left logo/header'),
]

for idx, (x1, y1, x2, y2, label) in enumerate(regions, start=1):
    box = (int(x1*w), int(y1*h), int(x2*w), int(y2*h))
    crop = img.crop(box)
    crop.save(OUT_DIR / f'widget_{idx}.png')

    # debug variant: overlay border and number
    debug = crop.convert('RGBA')
    d = ImageDraw.Draw(debug)
    try:
        font = ImageFont.truetype('arial.ttf', 20)
    except Exception:
        font = ImageFont.load_default()
    # border
    d.rectangle((0,0,crop.width-1,crop.height-1), outline=(255,0,0,200), width=4)
    # number
    d.ellipse((8,8,44,44), fill=(255,0,0,220))
    d.text((18,14), str(idx), fill='white', font=font)
    debug.save(OUT_DIR / f'widget_{idx}_debug.png')

print('Wrote widget crops to', OUT_DIR)
