from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCREEN = ROOT / 'qa_output' / 'screenshots' / 'startup.png'
OUT_DIR = ROOT / 'qa_output' / 'reports'
OUT_DIR.mkdir(parents=True, exist_ok=True)

img = Image.open(SCREEN).convert('RGBA')
w, h = img.size
overlay = Image.new('RGBA', img.size, (255,255,255,0))
draw = ImageDraw.Draw(overlay)

# Helper to convert fractions
def rbox(x1, y1, x2, y2):
    return (int(x1*w), int(y1*h), int(x2*w), int(y2*h))

regions = [
    (rbox(0.02, 0.06, 0.18, 0.92), '1', 'Left sidebar (navigation)'),
    (rbox(0.22, 0.06, 0.74, 0.80), '2', 'Main content panel'),
    (rbox(0.76, 0.06, 0.98, 0.30), '3', 'Top-right calendar/card'),
    (rbox(0.76, 0.32, 0.98, 0.56), '4', 'Middle-right notes/list'),
    (rbox(0.76, 0.58, 0.98, 0.86), '5', 'Lower-right activity panel'),
    (rbox(0.22, 0.82, 0.74, 0.94), '6', 'Footer controls/quick actions'),
    (rbox(0.02, 0.02, 0.12, 0.08), '7', 'Top-left logo/header'),
]

# Draw boxes and numbers
for box, num, label in regions:
    draw.rectangle(box, outline=(255,0,0,200), width=max(3, int(w/400)))
    # number circle
    cx = box[0] + 8
    cy = box[1] + 8
    r = 18
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(255,0,0,220))
    # number text
    try:
        font = ImageFont.truetype('arial.ttf', 20)
    except Exception:
        font = ImageFont.load_default()
    draw.text((cx-7, cy-11), num, fill='white', font=font)

# Create debug overlay version with grid
debug = Image.new('RGBA', img.size, (255,255,255,0))
d = ImageDraw.Draw(debug)
# draw grid lines every 10% for debug
for i in range(1,10):
    d.line((i*w/10,0,i*w/10,h), fill=(0,255,0,80), width=1)
    d.line((0,i*h/10,w,i*h/10), fill=(0,255,0,80), width=1)
# emphasize regions in debug
for box, num, label in regions:
    d.rectangle(box, outline=(0,255,255,200), width=max(2, int(w/500)))
    cx = box[0] + 8
    cy = box[1] + 8
    r = 18
    d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(0,255,255,180))
    d.text((cx-7, cy-11), num, fill='black', font=font)

# Composite images
annotated = Image.alpha_composite(img, overlay)
annotated_debug = Image.alpha_composite(img, debug)

annotated.save(OUT_DIR / 'startup_annotated.png')
annotated_debug.save(OUT_DIR / 'startup_annotated_debug.png')

print('Wrote:', OUT_DIR / 'startup_annotated.png')
print('Wrote:', OUT_DIR / 'startup_annotated_debug.png')
