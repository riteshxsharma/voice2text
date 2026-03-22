from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ICON_SIZE = 1024
OUTPUT_DIR = Path(__file__).resolve().parent


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/SFNSRounded.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def save_on_icon() -> None:
    image = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (16, 22, 28, 255))
    draw = ImageDraw.Draw(image)

    border = 48
    draw.rounded_rectangle(
        [border, border, ICON_SIZE - border, ICON_SIZE - border],
        radius=180,
        fill=(20, 20, 20, 255),
        outline=(245, 245, 245, 255),
        width=10,
    )

    bars = [
        (255, 64, 64),
        (255, 147, 41),
        (255, 214, 10),
        (49, 192, 92),
        (38, 148, 255),
        (109, 76, 255),
    ]
    inner_left = 90
    inner_top = 120
    inner_right = ICON_SIZE - 90
    inner_bottom = ICON_SIZE - 120
    width = (inner_right - inner_left) / len(bars)
    for index, color in enumerate(bars):
        x0 = int(inner_left + index * width)
        x1 = int(inner_left + (index + 1) * width)
        draw.rectangle([x0, inner_top, x1, inner_bottom], fill=color)

    for y in range(170, 850, 90):
        draw.rectangle([140, y, 884, y + 16], fill=(245, 245, 245, 110))

    draw.ellipse([250, 250, 774, 774], fill=(8, 8, 8, 90))
    draw.arc([300, 300, 724, 724], start=35, end=325, fill=(255, 255, 255, 255), width=42)
    draw.line([512, 190, 512, 460], fill=(255, 255, 255, 255), width=42)

    image.save(OUTPUT_DIR / "voice2text_on.png")

    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">
  <rect x="48" y="48" width="928" height="928" rx="180" fill="#141414" stroke="#f5f5f5" stroke-width="10"/>
  <rect x="90" y="120" width="141" height="784" fill="#ff4040"/>
  <rect x="231" y="120" width="141" height="784" fill="#ff9329"/>
  <rect x="372" y="120" width="141" height="784" fill="#ffd60a"/>
  <rect x="513" y="120" width="141" height="784" fill="#31c05c"/>
  <rect x="654" y="120" width="141" height="784" fill="#2694ff"/>
  <rect x="795" y="120" width="139" height="784" fill="#6d4cff"/>
  <g opacity="0.45" stroke="#f5f5f5" stroke-width="16">
    <line x1="140" y1="178" x2="884" y2="178"/>
    <line x1="140" y1="268" x2="884" y2="268"/>
    <line x1="140" y1="358" x2="884" y2="358"/>
    <line x1="140" y1="448" x2="884" y2="448"/>
    <line x1="140" y1="538" x2="884" y2="538"/>
    <line x1="140" y1="628" x2="884" y2="628"/>
    <line x1="140" y1="718" x2="884" y2="718"/>
    <line x1="140" y1="808" x2="884" y2="808"/>
  </g>
  <ellipse cx="512" cy="512" rx="262" ry="262" fill="#080808" opacity="0.35"/>
  <path d="M 686 400 A 212 212 0 1 1 338 400" fill="none" stroke="#ffffff" stroke-width="42" stroke-linecap="round"/>
  <line x1="512" y1="190" x2="512" y2="460" stroke="#ffffff" stroke-width="42" stroke-linecap="round"/>
</svg>
"""
    (OUTPUT_DIR / "voice2text_on.svg").write_text(svg, encoding="utf-8")


def save_off_icon() -> None:
    image = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (20, 110, 40, 255))
    draw = ImageDraw.Draw(image)
    border = 48

    draw.rounded_rectangle(
        [border, border, ICON_SIZE - border, ICON_SIZE - border],
        radius=180,
        fill=(20, 110, 40, 255),
        outline=(230, 255, 235, 255),
        width=12,
    )

    for y in range(150, 900, 120):
        draw.rectangle([130, y, 894, y + 8], fill=(160, 235, 175, 255))

    font = load_font(310)
    text = "OFF"
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font, stroke_width=18)
    text_w = right - left
    text_h = bottom - top
    origin = ((ICON_SIZE - text_w) / 2, (ICON_SIZE - text_h) / 2 - 40)
    draw.text(
        origin,
        text,
        font=font,
        fill=(255, 255, 255, 255),
        stroke_width=18,
        stroke_fill=(18, 70, 30, 255),
    )

    image.save(OUTPUT_DIR / "voice2text_off.png")

    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">
  <rect x="48" y="48" width="928" height="928" rx="180" fill="#146e28" stroke="#e6ffeb" stroke-width="12"/>
  <g opacity="0.7" stroke="#a0ebb0" stroke-width="8">
    <line x1="130" y1="154" x2="894" y2="154"/>
    <line x1="130" y1="274" x2="894" y2="274"/>
    <line x1="130" y1="394" x2="894" y2="394"/>
    <line x1="130" y1="514" x2="894" y2="514"/>
    <line x1="130" y1="634" x2="894" y2="634"/>
    <line x1="130" y1="754" x2="894" y2="754"/>
    <line x1="130" y1="874" x2="894" y2="874"/>
  </g>
  <text x="512" y="585" text-anchor="middle" font-size="310" font-family="Arial, Helvetica, sans-serif" font-weight="700" fill="#ffffff" stroke="#12461e" stroke-width="18">OFF</text>
</svg>
"""
    (OUTPUT_DIR / "voice2text_off.svg").write_text(svg, encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    save_on_icon()
    save_off_icon()


if __name__ == "__main__":
    main()
