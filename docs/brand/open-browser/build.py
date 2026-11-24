import json
import math
import shutil
import subprocess
import sys
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np

sys.setrecursionlimit(200000)

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"
ROOT = HERE.parent.parent.parent
OUT = ROOT / "output/brand/open-browser/final"

ICON_SIZES = [16, 32, 64, 128, 256, 512, 1024]
WINDOWS_SIZES = [16, 24, 32, 48, 64, 128, 256]
LINUX_SIZES = [16, 24, 32, 48, 64, 128, 256, 512]

NTP_COLORS = {
    "green": (33, 74, 56),
    "plum": (94, 54, 86),
    "blue": (40, 78, 122),
    "purple": (86, 62, 132),
    "pink": (150, 62, 104),
    "red": (146, 52, 46),
    "orange": (168, 96, 40),
    "yellow": (176, 140, 40),
    "neutral": (92, 92, 90),
}

ALTERNATES = {
    "midnight": ((18, 20, 24), (6, 7, 9)),
    "daylight": ((242, 240, 234), (206, 202, 194)),
    "plum": ((70, 36, 62), (32, 14, 28)),
    "ocean": ((24, 54, 84), (8, 22, 38)),
    "noir": ((34, 34, 34), (0, 0, 0)),
    "mono": ((236, 236, 236), (188, 188, 188)),
}

COMPANY = "The Open Browser Company"


def load(name):
    return Image.open(SOURCE / name).convert("RGBA")


def rounded_mask(size, radius, feather=1.0):
    scale = 4
    big = Image.new("L", (size * scale, size * scale), 0)
    d = ImageDraw.Draw(big)
    d.rounded_rectangle((0, 0, size * scale - 1, size * scale - 1), radius * scale, fill=255)
    return big.resize((size, size), Image.LANCZOS)


def squircle_mask(size):
    return rounded_mask(size, size * 0.2237)


def alpha_bbox(im):
    a = np.array(im)[:, :, 3]
    ys, xs = np.where(a > 24)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def crop_alpha(im):
    box = alpha_bbox(im)
    return im.crop((box[0], box[1], box[2] + 1, box[3] + 1))


def place(canvas_size, content_size):
    inset = (canvas_size - content_size) // 2
    return inset


def icon_canvas(tile, size):
    content = round(size * 824 / 1024)
    art = tile.resize((content, content), Image.LANCZOS)
    if size <= 64:
        art = art.filter(ImageFilter.UnsharpMask(radius=1.2, percent=90, threshold=0))
    mask = squircle_mask(content)
    art.putalpha(mask)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    off = place(size, content)
    canvas.alpha_composite(art, (off, off))
    return canvas


def master_tile():
    return crop_alpha(load("app-icon-tile.png"))


def small_icon(size):
    tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    for y in range(size):
        v = int(round(26 - 26 * y / max(1, size - 1)))
        d.line((0, y, size, y), fill=(v, v, v, 255))
    tile.putalpha(squircle_mask(size))
    frac = 0.66 if size <= 16 else 0.72 if size <= 32 else 0.74
    g = glyph_layer(glyph_master(), size, (255, 255, 255), frac)
    tile.alpha_composite(g, ((size - g.size[0]) // 2, (size - g.size[1]) // 2))
    return tile


def icon_at(tile, size):
    if size <= 48:
        return small_icon(size)
    return icon_canvas(tile, size)


def glyph_mask_in_tile(tile):
    size = tile.size[0]
    art = np.array(tile)
    alpha = art[:, :, 3]
    lum = art[:, :, :3].astype(float).mean(axis=2)
    ys, xs = np.where((lum > 140) & (alpha > 200))
    gx0, gx1, gy0, gy1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
    mark = glyph_master()
    bw, bh = gx1 - gx0 + 1, gy1 - gy0 + 1
    scale = min(bw / mark.size[0], bh / mark.size[1])
    mw, mh = max(1, round(mark.size[0] * scale)), max(1, round(mark.size[1] * scale))
    scaled = mark.resize((mw, mh), Image.LANCZOS)
    gm = np.zeros((size, size), float)
    ox = gx0 + (bw - mw) // 2
    oy = gy0 + (bh - mh) // 2
    gm[oy:oy + mh, ox:ox + mw] = np.array(scaled)[:, :, 3].astype(float) / 255.0
    return np.clip(gm, 0, 1)


def themed_tile(tile, top, bottom):
    size = tile.size[0]
    art = np.array(tile)
    alpha = art[:, :, 3]
    rgb = art[:, :, :3].astype(float)
    gm = glyph_mask_in_tile(tile)
    grad = np.linspace(0, 1, size)[:, None]
    bg = np.zeros((size, size, 3), float)
    for c in range(3):
        bg[:, :, c] = top[c] + (bottom[c] - top[c]) * grad
    out = bg * (1 - gm[:, :, None]) + rgb * gm[:, :, None]
    out = np.clip(out, 0, 255).astype(np.uint8)
    res = np.dstack([out, alpha])
    return Image.fromarray(res, "RGBA")


def glyph_master():
    return crop_alpha(load("mark-white.png"))


def glyph_square(size, color):
    mark = glyph_master()
    scale = min(size / mark.size[0], size / mark.size[1])
    w = max(1, round(mark.size[0] * scale))
    h = max(1, round(mark.size[1] * scale))
    g = mark.resize((w, h), Image.LANCZOS)
    solid = Image.new("RGBA", (w, h), color + (255,))
    solid.putalpha(g.getchannel("A"))
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.alpha_composite(solid, ((size - w) // 2, (size - h) // 2))
    return out


def glyph_layer(mark, size, color, height_frac=1.0):
    target_h = max(1, round(size * height_frac))
    w = max(1, round(target_h * mark.size[0] / mark.size[1]))
    g = mark.resize((w, target_h), Image.LANCZOS)
    solid = Image.new("RGBA", g.size, color + (255,))
    solid.putalpha(g.getchannel("A"))
    return solid


def split_glyph(mark):
    a = np.array(mark)[:, :, 3]
    h, w = a.shape
    m = a > 128
    seen = np.zeros_like(m, bool)
    comps = []
    for y in range(h):
        for x in range(w):
            if m[y, x] and not seen[y, x]:
                q = deque([(x, y)])
                seen[y, x] = True
                pts = []
                while q:
                    cx, cy = q.popleft()
                    pts.append((cx, cy))
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < w and 0 <= ny < h and m[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            q.append((nx, ny))
                comps.append(pts)
    comps.sort(key=len, reverse=True)
    layers = []
    for pts in comps[:3]:
        layer = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(layer)
        for x, y in pts:
            d.point((x, y), 255)
        layers.append(layer.filter(ImageFilter.GaussianBlur(0.5)))
    ys, xs = np.where(m)
    return layers, (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))


def render_layers(layers, bbox, size, color, width_frac=0.92):
    x0, y0, x1, y1 = bbox
    bw, bh = x1 - x0 + 1, y1 - y0 + 1
    scale = (size * width_frac) / max(bw, bh)
    tw = max(1, round(bw * scale))
    th = max(1, round(bh * scale))
    offx = (size - tw) // 2
    offy = (size - th) // 2
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    for layer in layers:
        crop = layer.crop((x0, y0, x1 + 1, y1 + 1)).resize((tw, th), Image.LANCZOS)
        solid = Image.new("RGBA", (tw, th), color + (255,))
        solid.putalpha(crop)
        out.alpha_composite(solid, (offx, offy))
    return out


NEIGHBOURS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


def flood(mask, start, allowed=None):
    h, w = mask.shape
    seen = np.zeros_like(mask, bool)
    q = deque([start])
    seen[start[1], start[0]] = True
    pts = []
    while q:
        x, y = q.popleft()
        pts.append((x, y))
        for dx, dy in NEIGHBOURS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] and not seen[ny, nx]:
                if allowed and not allowed(nx, ny):
                    continue
                seen[ny, nx] = True
                q.append((nx, ny))
    return pts


def trace_boundary(mask, start):
    h, w = mask.shape
    cur = start
    prev = (start[0] - 1, start[1])
    loop = [start]
    guard = 0
    while True:
        guard += 1
        if guard > 400000:
            break
        dx, dy = cur[0] - prev[0], cur[1] - prev[1]
        try:
            first = NEIGHBOURS.index((dx, dy))
        except ValueError:
            first = 4
        found = None
        for step in range(1, 9):
            idx = (first + step) % 8
            nd = NEIGHBOURS[idx]
            nx, ny = cur[0] + nd[0], cur[1] + nd[1]
            if 0 <= nx < w and 0 <= ny < h and mask[ny, nx]:
                found = (nx, ny)
                break
        if found is None:
            break
        prev, cur = cur, found
        if cur == start:
            break
        loop.append(cur)
    return loop


def shape_loops(mask):
    h, w = mask.shape
    remaining = mask.copy()
    loops = []
    for y in range(h):
        for x in range(w):
            if remaining[y, x]:
                comp = flood(remaining, (x, y))
                for cx, cy in comp:
                    remaining[cy, cx] = False
                comp_mask = np.zeros_like(mask)
                for cx, cy in comp:
                    comp_mask[cy, cx] = True
                top = min(comp, key=lambda p: (p[1], p[0]))
                loops.append(trace_boundary(comp_mask, top))
                x0 = min(p[0] for p in comp)
                x1 = max(p[0] for p in comp)
                y0 = min(p[1] for p in comp)
                y1 = max(p[1] for p in comp)
                hole = ~comp_mask
                seen = np.zeros_like(mask, bool)
                for hy in range(y0, y1 + 1):
                    for hx in range(x0, x1 + 1):
                        if not hole[hy, hx] or seen[hy, hx]:
                            continue
                        region = flood(hole, (hx, hy), allowed=lambda nx, ny: x0 <= nx <= x1 and y0 <= ny <= y1)
                        for rx, ry in region:
                            seen[ry, rx] = True
                        touches = any(rx in (x0, x1) or ry in (y0, y1) for rx, ry in region)
                        if not touches and len(region) > 40:
                            hole_mask = np.zeros_like(mask)
                            for rx, ry in region:
                                hole_mask[ry, rx] = True
                            htop = min(region, key=lambda p: (p[1], p[0]))
                            loops.append(trace_boundary(hole_mask, htop))
    return loops


def rdp(points, eps):
    if len(points) < 3:
        return points
    x1, y1 = points[0]
    x2, y2 = points[-1]
    dx, dy = x2 - x1, y2 - y1
    norm = math.hypot(dx, dy)
    best, index = 0.0, 0
    for i in range(1, len(points) - 1):
        px, py = points[i]
        dist = abs(dy * px - dx * py + x2 * y1 - y2 * x1) / norm if norm else math.hypot(px - x1, py - y1)
        if dist > best:
            best, index = dist, i
    if best > eps:
        left = rdp(points[:index + 1], eps)
        right = rdp(points[index:], eps)
        return left[:-1] + right
    return [points[0], points[-1]]


def mark_svg(size=1024, pad=0.04, eps=0.7):
    mark = glyph_master()
    w, h = mark.size
    up = 3
    alpha = mark.getchannel("A").resize((w * up, h * up), Image.LANCZOS)
    mask = (np.array(alpha) > 120).astype(np.uint8)
    loops = shape_loops(mask)
    inner = 1 - pad * 2
    scale = min(size * inner / (w * up), size * inner / (h * up))
    ox = (size - (w * up) * scale) / 2
    oy = (size - (h * up) * scale) / 2
    parts = []
    for loop in loops:
        area = 0.0
        for i in range(len(loop)):
            x1, y1 = loop[i]
            x2, y2 = loop[(i + 1) % len(loop)]
            area += x1 * y2 - x2 * y1
        if abs(area) / 2 < 60:
            continue
        closed = loop + [loop[0]]
        anchor = max(range(len(loop)), key=lambda i: math.hypot(loop[i][0] - loop[0][0], loop[i][1] - loop[0][1]))
        first = rdp(closed[:anchor + 1], eps)
        second = rdp(closed[anchor:], eps)
        simple = first[:-1] + second
        cmds = []
        for i, (px, py) in enumerate(simple):
            cmd = "M" if i == 0 else "L"
            cmds.append(f"{cmd}{ox + px * scale:.1f} {oy + py * scale:.1f}")
        parts.append("".join(cmds) + "Z")
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}"><path fill="#111111" fill-rule="evenodd" d="{"".join(parts)}"/></svg>\n'


def font(size):
    for p in ("/System/Library/Fonts/SFNS.ttf", "/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/HelveticaNeue.ttc"):
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def banner(width, height):
    mark = glyph_master()
    out = Image.new("RGB", (width, height), (6, 6, 7))
    d = ImageDraw.Draw(out)
    g = glyph_layer(mark, int(height * 0.40), (236, 236, 238))
    label = COMPANY
    f = font(int(height * 0.115))
    while d.textlength(label, font=f) > width * 0.58 and f.size > 8:
        f = font(f.size - 1)
    tw = int(round(d.textlength(label, font=f)))
    gap = int(width * 0.035)
    total = g.size[0] + gap + tw
    x = (width - total) // 2
    box = d.textbbox((0, 0), label, font=f)
    th = box[3] - box[1]
    out.paste(g, (x, (height - g.size[1]) // 2), g)
    d.text((x + g.size[0] + gap - box[0], (height - th) // 2 - box[1]), label, font=f, fill=(214, 216, 220))
    return out


def social(width, height):
    base = banner(width, height)
    return base


def write_icns(path, images):
    iconset = OUT / "tmp.iconset"
    if iconset.exists():
        shutil.rmtree(iconset)
    iconset.mkdir()
    pairs = [
        ("icon_16x16.png", 16), ("icon_16x16@2x.png", 32),
        ("icon_32x32.png", 32), ("icon_32x32@2x.png", 64),
        ("icon_128x128.png", 128), ("icon_128x128@2x.png", 256),
        ("icon_256x256.png", 256), ("icon_256x256@2x.png", 512),
        ("icon_512x512.png", 512), ("icon_512x512@2x.png", 1024),
    ]
    for name, px in pairs:
        images[px].save(iconset / name)
    subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(path)], check=True)
    shutil.rmtree(iconset)


def install():
    mac = ROOT / "apps/browser/macos/Ardia-macOS"
    assets = ROOT / "apps/browser/assets"
    site = ROOT / "apps/site"
    copies = []

    def put(src, dst):
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        copies.append(dst)

    appicon = {
        "icon_16x16_1x.png": 16, "icon_16x16_2x.png": 32,
        "icon_32x32_1x.png": 32, "icon_32x32_2x.png": 64,
        "icon_128x128_1x.png": 128, "icon_128x128_2x.png": 256,
        "icon_256x256_1x.png": 256, "icon_256x256_2x.png": 512,
        "icon_512x512_1x.png": 512, "icon_512x512_2x.png": 1024,
    }
    for name, size in appicon.items():
        put(OUT / f"icon-{size}.png", mac / "Assets.xcassets/AppIcon.appiconset" / name)

    blank = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    blank_path = OUT / "icon-blank-1024.png"
    blank.save(blank_path)
    for appearance in ("light", "dark", "tinted"):
        put(OUT / "icon-1024.png", mac / f"AppIcon.icon/Assets/back-{appearance}.png")
        put(blank_path, mac / f"AppIcon.icon/Assets/front-{appearance}.png")
        put(blank_path, mac / f"AppIcon.icon/Assets/sun-{appearance}.png")

    dev = themed_tile(master_tile(), (46, 120, 105), (20, 60, 52))
    icon_canvas(dev, 1024).save(OUT / "icon-dev-1024.png")
    for name in ("back", "front", "sun", "board"):
        put(OUT / "icon-dev-1024.png", mac / f"AppIcon-Dev.icon/Assets/{name}.png")

    for ident in ALTERNATES:
        put(OUT / f"icon-alt-{ident}.png", mac / f"Assets.xcassets/AppIcon-{ident}.imageset/icon.png")

    put(OUT / "app-icon-512.png", assets / "app-icon.png")
    for f in sorted(OUT.glob("ntp-mark-*.png")):
        if "-green-" not in f.name:
            put(f, assets / f.name)
    for slot in ("back", "front", "sun"):
        for suffix in ("", "@2x"):
            put(OUT / f"ntp-mark-green-{slot}{suffix}.png", assets / f"ntp-mark-{slot}{suffix}.png")
    for f in sorted(OUT.glob("new-tab-mark*.png")):
        put(f, assets / f.name)

    put(OUT / "favicon.ico", site / "public/favicon.ico")
    put(OUT / "favicon.png", site / "public/favicon.png")
    put(OUT / "apple-touch-icon.png", site / "public/apple-touch-icon.png")
    put(OUT / "og.png", site / "public/og.png")
    put(OUT / "app-icon-512.png", site / "src/assets/app-icon.png")
    put(OUT / "mark-silver-1024.png", site / "src/assets/ardia-mark.png")
    put(OUT / "mark-silver-1024.png", site / "src/assets/mark-colour.png")
    put(OUT / "mark-ink-1024.png", site / "src/assets/mark-black.png")
    put(OUT / "mark-white-1024.png", site / "src/assets/mark-white.png")

    put(OUT / "app-icon-512.png", ROOT / "extras/raycast-ardia/assets/icon.png")
    put(OUT / "app.ico", ROOT / "apps/browser/windows/Ardia/Ardia.ico")
    return copies


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    tile = master_tile()
    mark = glyph_master()

    tile.save(OUT / "app-icon-tile.png")

    icons = {}
    for size in ICON_SIZES:
        im = icon_at(tile, size)
        icons[size] = im
        im.save(OUT / f"icon-{size}.png")

    for ident, (top, bottom) in ALTERNATES.items():
        alt = themed_tile(tile, top, bottom)
        icon_canvas(alt, 512).save(OUT / f"icon-alt-{ident}.png")

    write_icns(OUT / "app.icns", icons)

    for ident in ALTERNATES:
        alt_sizes = [16, 32, 64, 128, 256, 512]
        alt = themed_tile(tile, *ALTERNATES[ident])
        for s in alt_sizes:
            icon_canvas(alt, s).save(OUT / f"icon-alt-{ident}-{s}.png")

    icons[512].save(OUT / "app-icon-512.png")

    fav = {}
    for size in (16, 32, 48, 64):
        fav[size] = icon_at(tile, size)
        fav[size].save(OUT / f"favicon-{size}.png")
    fav[64].save(OUT / "favicon.png")
    fav[48].save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    icon_canvas(tile, 180).convert("RGB").save(OUT / "apple-touch-icon.png")

    social(1200, 630).save(OUT / "og.png")
    banner(1280, 640).save(OUT / "banner-1280x640.png")

    glyph_square(512, (18, 18, 18)).save(OUT / "mark-ink-512.png")
    glyph_square(1024, (18, 18, 18)).save(OUT / "mark-ink-1024.png")
    glyph_square(1024, (255, 255, 255)).save(OUT / "mark-white-1024.png")
    silver = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    silver_mask = glyph_square(1024, (255, 255, 255)).getchannel("A")
    grad = Image.new("RGBA", (1024, 1024))
    gd = ImageDraw.Draw(grad)
    for y in range(1024):
        t = y / 1023
        r = int(246 - 96 * t)
        gd.line((0, y, 1024, y), fill=(r, r, r, 255))
    silver.paste(grad, (0, 0), silver_mask)
    silver.save(OUT / "mark-silver-1024.png")

    for size in WINDOWS_SIZES:
        icon_at(tile, size).save(OUT / f"windows-{size}.png")
    icon_at(tile, 256).save(OUT / "app.ico", sizes=[(s, s) for s in WINDOWS_SIZES])

    for size in LINUX_SIZES:
        icon_at(tile, size).save(OUT / f"linux-{size}.png")

    components, bbox = split_glyph(mark)
    for ident, color in NTP_COLORS.items():
        for idx, slot in enumerate(("back", "front", "sun")):
            comp = components[idx:idx + 1]
            for scale, suffix in ((1, ""), (2, "@2x")):
                render_layers(comp, bbox, 100 * scale, color).save(OUT / f"ntp-mark-{ident}-{slot}{suffix}.png")

    for scale, suffix in ((1, ""), (2, "@2x")):
        icon_at(tile, 16 * scale).save(OUT / f"new-tab-mark{suffix}.png")

    manifest = {
        "company": COMPANY,
        "product_name": None,
        "sources": {
            "banner": "source/banner.png",
            "app_icon": "source/app-icon.png",
            "mark_light": "source/mark-light.png",
            "mark_dark": "source/mark-dark.png",
        },
        "outputs": sorted(p.name for p in OUT.iterdir() if p.is_file()),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    nil = [s for s in ICON_SIZES if s not in icons]
    if nil:
        raise SystemExit(f"missing icon sizes: {nil}")
    print(f"built {len(manifest['outputs'])} files into {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
    if "--install" in sys.argv:
        written = install()
        print(f"installed {len(written)} files")
