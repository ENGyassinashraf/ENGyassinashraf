from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "animations"
OUT.mkdir(parents=True, exist_ok=True)

BG = (11, 20, 32)
CARD = (17, 31, 44)
BORDER = (43, 65, 82)
WHITE = (229, 242, 248)
MUTED = (135, 161, 180)
CYAN = (56, 189, 248)
TEAL = (45, 212, 191)
PALE = (186, 247, 255)

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

def font(size: int, bold: bool = False, mono: bool = False):
    path = FONT_MONO if mono else FONT_BOLD if bold else FONT_REG
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()

def center(draw, xy, text, fnt, fill):
    draw.text(xy, text, font=fnt, fill=fill, anchor="mm")

def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def save_gif(frames, name, duration=100):
    # A shared 96-colour palette reduces file size while preserving the dark UI palette.
    palette = frames[len(frames) // 2].convert("RGB").quantize(colors=96, method=Image.Quantize.MEDIANCUT)
    frames = [frame.convert("RGB").quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    path = OUT / name
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=duration, loop=0, optimize=True, disposal=2)
    print(f"{path.name}: {path.stat().st_size} bytes, {len(frames)} frames")

def backend_frame(frame_index, total=28):
    w, h = 1000, 238
    im = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(im)
    for y in range(h):
        d.line((0, y, w, y), fill=lerp((10, 19, 30), (16, 30, 43), y / (h - 1)))
    d.rounded_rectangle((1, 1, w - 2, h - 2), radius=18, outline=BORDER, width=2)
    d.text((26, 22), "BACK-END REQUEST FLOW", font=font(16, True), fill=WHITE)
    d.text((26, 44), "A request moving through a layered .NET API", font=font(12), fill=MUTED)
    nodes = [
        (24, 83, 178, 182, "Client", "HTTP request", "<>"),
        (212, 83, 393, 182, "ASP.NET Core API", "Controllers · REST", "API"),
        (423, 83, 604, 182, "Application Services", "Business logic", "{}"),
        (633, 83, 787, 182, "EF Core", "Data access", "EF"),
        (815, 83, 976, 182, "SQL Server", "Relational data", "DB"),
    ]
    links = [(178, 132, 211, 132), (393, 132, 422, 132), (604, 132, 632, 132), (787, 132, 814, 132)]
    for x1, y1, x2, y2 in links:
        d.line((x1, y1, x2, y2), fill=(65, 99, 119), width=2)
        d.polygon([(x2 - 4, y2 - 4), (x2, y2), (x2 - 4, y2 + 4)], fill=(110, 154, 175))
    for i, (x1, y1, x2, y2) in enumerate(links):
        p = ((frame_index / total) + i * 0.24) % 1.0
        cx = x1 + (x2 - x1) * p
        d.ellipse((cx - 3, y1 - 3, cx + 3, y1 + 3), fill=PALE)
    for i, (x1, y1, x2, y2, title, subtitle, icon) in enumerate(nodes):
        active = i == 1
        d.rounded_rectangle((x1, y1, x2, y2), radius=12, fill=(16, 46, 63) if active else CARD,
                            outline=(42, 184, 207) if active else (53, 82, 103), width=2 if active else 1)
        cx = (x1 + x2) // 2
        d.ellipse((cx - 14, 97, cx + 14, 125), fill=(23, 55, 74), outline=(78, 144, 173))
        center(d, (cx, 111), icon, font(10, True, True), PALE)
        center(d, (cx, 146), title, font(13 if len(title) > 15 else 14, True), WHITE)
        center(d, (cx, 164), subtitle, font(10), (157, 203, 220) if active else MUTED)
    d.text((974, 215), "REQUEST  →  DATA", font=font(10, True), fill=(95, 129, 149), anchor="ra")
    return im

def terminal_frame(frame_index, total=48):
    w, h = 900, 286
    im = Image.new("RGB", (w, h), (11, 19, 30))
    d = ImageDraw.Draw(im)
    for y in range(h):
        d.line((0, y, w, y), fill=lerp((16, 28, 41), (10, 19, 30), y / h))
    d.rounded_rectangle((1, 1, w - 2, h - 2), radius=15, outline=(42, 64, 81), width=2)
    d.rounded_rectangle((1, 1, w - 2, 43), radius=14, fill=(23, 38, 53))
    d.rectangle((1, 29, w - 2, 43), fill=(23, 38, 53))
    for x, color in [(22, (247, 118, 118)), (40, (234, 191, 106)), (58, (88, 201, 154))]:
        d.ellipse((x - 5, 17, x + 5, 27), fill=color)
    d.text((82, 13), "TasksController.cs", font=font(12), fill=(197, 215, 226))
    d.rounded_rectangle((755, 10, 878, 34), radius=6, fill=(16, 47, 60), outline=(36, 85, 106))
    pulse = 0.72 + 0.28 * math.sin(frame_index * 2 * math.pi / total)
    d.ellipse((765, 18, 772, 25), fill=tuple(int(v * pulse) for v in (67, 209, 195)))
    d.text((780, 15), "C# · API CONTROLLER", font=font(9, True), fill=(145, 220, 228))
    d.line((55, 44, 55, 285), fill=(34, 53, 68), width=1)
    code = [
        ("[ApiController]", (199, 146, 234)),
        ('[Route("api/tasks")]', (199, 146, 234)),
        ("public sealed class TasksController : ControllerBase", (137, 196, 244)),
        ("{", WHITE),
        ("    [HttpGet]", (199, 146, 234)),
        ("    public IActionResult Get() => Ok(_tasks);", (137, 196, 244)),
        ("}", WHITE),
    ]
    ys = [65, 92, 119, 146, 173, 200, 227]
    mono = font(14, False, True)
    for i, y in enumerate(ys, start=1):
        d.text((42, y + 1), str(i), font=font(12, False, True), fill=(98, 125, 144), anchor="ra")
    reveal_steps = 38
    all_chars = sum(len(line[0]) for line in code)
    target = min(all_chars, int((frame_index / max(1, reveal_steps - 1)) * all_chars)) if frame_index < reveal_steps else all_chars
    remain = target
    cursor_x, cursor_y = 76, ys[0]
    for idx, (line, color) in enumerate(code):
        visible = min(len(line), remain)
        shown = line[:visible]
        x = 110 if idx in (4, 5) else 76
        if visible:
            d.text((x, ys[idx]), shown, font=mono, fill=color)
        if remain < len(line):
            cursor_x, cursor_y = x + d.textlength(shown, font=mono), ys[idx]
            break
        remain -= len(line)
        cursor_x, cursor_y = x + d.textlength(line, font=mono), ys[idx]
    if frame_index >= reveal_steps:
        d.rounded_rectangle((67, 197, 875, 222), radius=4, outline=(26, 61, 77), width=1)
        cursor_x, cursor_y = 110 + d.textlength(code[5][0], font=mono), ys[5]
    if frame_index < reveal_steps or frame_index % 8 < 5:
        d.rounded_rectangle((int(cursor_x) + 1, cursor_y + 2, int(cursor_x) + 3, cursor_y + 20), radius=1, fill=(73, 199, 217))
    d.text((859, 258), "BUILDING API LOGIC", font=font(10, True), fill=(86, 115, 135), anchor="ra")
    return im

def tech_frame(frame_index, total=28):
    w, h = 900, 112
    im = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((1, 1, w - 2, h - 2), radius=13, fill=(11, 20, 32), outline=(38, 59, 75))
    items = [
        (14, 132, "C#", "LANGUAGE", 23),
        (160, 132, "C++", "LANGUAGE", 23),
        (306, 132, ".NET", "BACK-END", 23),
        (452, 132, "SQL Server", "DATABASE", 17),
        (598, 132, "REST API", "INTEGRATION", 19),
        (744, 142, "Git", "VERSION CONTROL", 23),
    ]
    active_index = frame_index % len(items)
    for idx, (x, width, title, subtitle, size) in enumerate(items):
        active = idx == active_index
        d.rounded_rectangle((x, 20, x + width, 88), radius=10, fill=(16, 31, 44),
                            outline=(51, 146, 169) if active else (49, 83, 104), width=1)
        d.ellipse((x + 16, 32, x + 22, 38), fill=(60, 210, 216) if active else CYAN)
        center(d, (x + width // 2, 48), title, font(size, True), (236, 249, 253) if active else (229, 244, 251))
        center(d, (x + width // 2, 69), subtitle, font(9, True), (115, 158, 177))
    sweep_x = -110 + (w + 220) * (frame_index / (total - 1))
    d.rounded_rectangle((int(sweep_x), 17, int(sweep_x + 76), 19), radius=1, fill=TEAL)
    return im

def main():
    save_gif([backend_frame(i) for i in range(28)], "backend-architecture.gif")
    save_gif([terminal_frame(i) for i in range(48)], "coding-terminal.gif")
    save_gif([tech_frame(i) for i in range(28)], "tech-stack.gif")

if __name__ == "__main__":
    main()
