"""
Generates the sample memes and forum screenshots in data/images with Pillow, so the project uses no images made
by other people. Arial is used on macOS and Windows, DejaVu Sans on Linux.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "images"

FONTS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]

MEMES = [
    ("meme_01.png", "#2f3b52", "KIEDY PYTASZ NA FORUM", "A ODPOWIADA CI IDIOTA, KTÓRY NIC NIE UMIE"),
    ("meme_02.png", "#3d5a40", "WHEN THE BUILD PASSES", "ON THE FIRST TRY"),
    ("meme_03.png", "#5a2f2f", "NAPISZ JESZCZE RAZ", "A ZNAJDĘ CIĘ PO PRACY"),
]

SCREENSHOTS = [
    (
        "screenshot_01.png",
        "marek_dev",
        "2 h temu",
        "Earn $500 a day from home!!! Register at cash-fast.example, bonus code FAST50",
    ),
    ("screenshot_02.png", "ola.codes", "wczoraj", "Dzięki, po dodaniu indeksu zapytanie działa 10 razy szybciej."),
    ("screenshot_03.png", "anon_77", "5 min temu", "You are a useless clown, stop posting your garbage code here."),
]


def font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONTS:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def wrap(draw: ImageDraw.ImageDraw, text: str, face, width: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=face) <= width:
            line = candidate
        else:
            lines.append(line)
            line = word
    return lines + [line]


def caption(draw, text: str, top: int, size: tuple[int, int], face) -> None:
    for index, line in enumerate(wrap(draw, text, face, size[0] - 60)):
        width = draw.textlength(line, font=face)
        position = ((size[0] - width) / 2, top + index * (face.size + 8))
        draw.text(position, line, font=face, fill="white", stroke_width=3, stroke_fill="black")


def meme(name: str, color: str, top: str, bottom: str) -> None:
    size = (720, 540)
    image = Image.new("RGB", size, color)
    draw = ImageDraw.Draw(image)
    for step in range(0, size[1], 6):
        draw.line(
            [(0, step), (size[0], step)],
            fill=tuple(min(255, int(c, 16) + 12) for c in (color[1:3], color[3:5], color[5:7])),
        )
    draw.ellipse((290, 200, 430, 340), fill="#f2c14e", outline="black", width=4)
    draw.arc((320, 240, 400, 310), 20, 160, fill="black", width=5)
    face = font(40)
    caption(draw, top, 28, size, face)
    lines = len(wrap(draw, bottom, face, size[0] - 60))
    caption(draw, bottom, size[1] - 40 - lines * (face.size + 8), size, face)
    image.save(OUTPUT / name)


def screenshot(name: str, user: str, when: str, text: str) -> None:
    size = (760, 260)
    image = Image.new("RGB", size, "#f4f5f7")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((20, 20, 740, 240), 14, fill="white", outline="#d0d4dc", width=2)
    draw.ellipse((40, 40, 92, 92), fill="#7b8cde")
    draw.text((56, 50), user[0].upper(), font=font(30), fill="white")
    draw.text((108, 44), user, font=font(24), fill="#1f2430")
    draw.text((108, 74), f"Kod po godzinach · {when}", font=font(18), fill="#7a8194")
    for index, line in enumerate(wrap(draw, text, font(24), 640)):
        draw.text((44, 120 + index * 34), line, font=font(24), fill="#1f2430")
    image.save(OUTPUT / name)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for item in MEMES:
        meme(*item)
    for item in SCREENSHOTS:
        screenshot(*item)
    print(f"{len(MEMES) + len(SCREENSHOTS)} images in {OUTPUT}")


if __name__ == "__main__":
    main()
