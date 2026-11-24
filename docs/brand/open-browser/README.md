# The Open Browser Company brand

This directory holds the master brand artwork and the generator that adapts it for the browser,
the site, the press kit and platform packaging.

The supplied archive was extracted unchanged to `branding-assets/` at the repository root. The four
supplied files were copied here under descriptive names and are never edited:

| Master | Supplied file | Role |
|---|---|---|
| `source/banner.png` | `1795451584013_2026-11-23_08-16-21.png` | Company banner: emblem and "The Open Browser Company", for GitHub and social. |
| `source/app-icon.png` | `1795451562701_2026-11-23_08-16-46.png` | Browser application icon: black tile with the metallic emblem. |
| `source/mark-light.png` | `1795451570679_2026-11-23_08-16-39.png` | Dark metallic emblem on white: light backgrounds and documentation. |
| `source/mark-dark.png` | `1795451578816_2026-11-23_08-16-31.png` | White emblem on black: dark backgrounds, small UI and watermarks. |

`source/app-icon-tile.png` is the cleaned tile crop of the application icon, with the surrounding
white card removed and an analytic rounded mask applied. It is the master for every icon size.

The company is **The Open Browser Company**: "An independent software company building open-source
browsers and tools for a better web." The browser is **Solstice**; the company and product identities are kept separate.
See `docs/rebrand/PRODUCT_NAME.md` for the naming decisions.

## Rebuilding

```
python3 docs/brand/open-browser/build.py --install
```

Without `--install` the generator writes only to `output/brand/open-browser/final/`, which is ignored
by git. With `--install` it copies the generated files into the slots listed below. The generator
requires Pillow and numpy.

## Size and variant policy

The supplied mockups are small rasters: the icon tile is 400 px and the emblem is 266 px. The
generator therefore does three different things rather than resizing one image everywhere:

- **Application icons (64–1024 px).** The original tile is upscaled with Lanczos and placed on
  Apple's 824/1024 grid with a squircle mask. The artwork, metallic shading and proportions are
  the supplied ones.
- **Small icons (16–48 px).** A purpose-built flat rendering: the white emblem at a larger
  fraction of the tile, with no metallic detail. This stays legible at favicon size.
- **Marks and watermarks.** The white silhouette in `source/mark-dark.png` is extracted as an alpha
  mask, then rendered in ink, white or a silver gradient at any size, with transparency. No colour
  is baked into the geometry.

Six alternate app icons keep the existing Settings › App Icon feature: midnight, daylight, plum,
ocean, noir and mono. Each uses the same emblem with a different tile background, so the identity
does not change between them.

## Installed slots

| Generated | Destination |
|---|---|
| `icon-{16,32,64,128,256,512,1024}.png` | `apps/browser/macos/Ardia-macOS/Assets.xcassets/AppIcon.appiconset/` |
| `icon-1024.png`, transparent layers | `apps/browser/macos/Ardia-macOS/AppIcon.icon/Assets/` |
| green themed tile | `apps/browser/macos/Ardia-macOS/AppIcon-Dev.icon/Assets/` |
| `icon-alt-*.png` | `apps/browser/macos/Ardia-macOS/Assets.xcassets/AppIcon-*.imageset/` |
| `app.icns` | `output/` only, for packaging |
| `app-icon-512.png` | `apps/browser/assets/app-icon.png`, `apps/site/src/assets/app-icon.png`, Raycast |
| `ntp-mark-*.png`, `new-tab-mark*.png` | `apps/browser/assets/` |
| `favicon.ico`, `favicon.png`, `apple-touch-icon.png`, `og.png` | `apps/site/public/` |
| silver, ink and white marks | `apps/site/src/assets/mark-*.png` |
| `app.ico` | `apps/browser/windows/Ardia/Ardia.ico` |
| `linux-*.png` | `output/` only, for packaging |

## Known limits

- No vector master was supplied, so the press kit ships high-resolution PNG marks. The old raster
  SVG path data was removed rather than redrawn, because tracing it would have changed the logo's
  geometry.
- Chromium's own product logos and notification-helper icons live under `engine/`. They are hashed
  by `engine/engine-key.sh`, so changing them would invalidate the prebuilt engine and requires a
  new engine build on each platform. They are deliberately untouched here.
- The New Tab page keeps its three-layer rise animation. The emblem's silhouette is split into three
  pieces, one per existing layer, tinted with the existing profile colours.
