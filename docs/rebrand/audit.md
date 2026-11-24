# Rebrand audit

Status: **rebrand implemented.** This document is the baseline audit from before the work began; the counts below describe the original checkout.

| Identity | Value |
|---|---|
| Product | Solstice |
| Company | The Open Browser Company |
| Company description | An independent software company building open-source browsers and tools for a better web. |
| Master logo | Supplied in `Archive.zip`, preserved in `branding-assets/` and `docs/brand/open-browser/source/` |

The naming decisions and the identifiers intentionally left unchanged are documented in `PRODUCT_NAME.md`.

The machine-readable list of every affected file is `docs/rebrand/inventory.tsv`
(columns: `file`, `category`, `action`, `occurrences`).

## 1. Measured scope

The old identity is in **4,438 of 9,117 tracked files**, **32,892 mentions**.

| Action | Category | Files | Mentions |
|---|---|---:|---:|
| rename | `browser-ui` (`apps/browser/src`) | 748 | 2,971 |
| rename | `docs` | 58 | 2,864 |
| rename | `scripts` | 190 | 2,484 |
| rename | `packages-other` | 356 | 2,373 |
| rename | `linux-ui` (`apps/linux`) | 284 | 2,192 |
| rename | `phone-app` | 343 | 1,479 |
| rename | `windows-app` | 88 | 366 |
| rename | `site` | 46 | 350 |
| rename | `browser-other` | 63 | 381 |
| rename | `videos` | 132 | 378 |
| rename | `root-other` | 23 | 378 |
| rename | `ci`, `infra`, `dashboard`, `agent-skills`, `extras` | 121 | 574 |
| rename-native | `ios-pods` (`packages/*/ios`) | 384 | 4,356 |
| rename-native | `phone-native` | 580 | 1,892 |
| rename-native | `windows-native` | 121 | 504 |
| rename-native | `mac-native` | 10 | 138 |
| keep-historical | `release-notes` | 101 | 662 |
| **keep-engine-key** | `linux-engine`, `mac-engine`, `chromium-patches`, `engine-other`, `rn-patches`, `offline-game` | **799** | **8,441** |

Two numbers matter more than the rest: **2,443 files can be rebranded freely**, and **799 files must not be touched** unless a new browser engine is built.

## 2. The hard boundary: the engine key

`engine/engine-key.sh` hashes every file the platform's engine is built from. Today the macOS key is
`a40945952f4f`, matched to a prebuilt engine by `packages/ardiacore/prebuilt-engines.tsv`
(release `engine-a40945952f4f`, SHA-256 `7254eda910ab0558336060381596ee6ba0d862d83b56ddc3253debf8ff45bf2b`).

The key covers:

- everything under `engine/`, including `engine/chromium/src` and `engine/patches/build/ardia-icons`;
- `apps/browser/assets/offline-game` and its pipeline;
- any file a layer's `copies.tsv` pulls in, even from outside `engine/`.

Consequences:

1. Renaming or editing anything in those paths produces a **new key**, the prebuilt engine no longer matches, and the app cannot build until a Chromium engine is compiled (about 5 hours, and you have ruled out building on this Mac).
2. **Chromium's own product logos are inside the key.** `engine/chromium/src/chrome/app/theme/chromium/product_logo*`, the notification helper's `app.icns` and `Assets.car`, and the glyphs in `engine/patches/build/ardia-icons` cannot be rebranded without a new engine, per platform.
3. Internal engine identifiers (`ArdiaCore`, `AC*` C entry points, `ardiacore` module, `ARDIACORE_*` variables) live behind that boundary. A "rename everything" pass is therefore not a text substitution — it is an engine project.

**Recommended split:**

- **Phase A, brand shell.** Rebrand every surface a user can see or that macOS/Windows/Linux expose: app name, bundle identity, icons, menus, UI copy, onboarding, site, installer, CLI display. Engine stays byte-identical. No rebuild risk.
- **Phase B, engine brand.** Chromium-level logos and internal identifiers, built on a separate Mac (the linked Mac mini or CI), then published as a new engine key for all three platforms.

Phase B is real work but it does not block Phase A, and doing it on the owner's machine is what you have excluded.

## 3. Single sources of truth for identity

| Surface | File | Current value |
|---|---|---|
| Display name (JS) | `apps/browser/app.json` | `"Solstice"` |
| Display name (macOS) | `apps/browser/macos/Ardia-macOS/Info.plist` | `CFBundleDisplayName = Solstice` |
| Product name / binary | `apps/browser/macos/Ardia.xcodeproj/project.pbxproj` | `PRODUCT_NAME = Solstice` |
| Bundle id | same | `com.openbrowsercompany.solstice` |
| Development team | same | `U5L5T3NGVV` (owner's; no account on this Mac) |
| Target / scheme | `Ardia.xcodeproj`, `Ardia.xcworkspace`, `Ardia-macOS.xcscheme` | `Ardia-macOS` |
| Native source folder | `apps/browser/macos/Ardia-macOS/` | `Ardia-macOS` |
| Update feed | `Info.plist` | `https://ardia.dev/appcast.xml` |
| Update signing key | `Info.plist` `SUPublicEDKey` | Sparkle EdDSA key |
| Helpers | build products | `ArdiaPluginHost`, `ArdiaDockTile.plugin` |
| Engine release repo | `.github/workflows/release.yml` | `ardia-browser/ardia` |
| CLI command | `apps/browser/official-plugins.json` | program `ardia`, repo `ardia-browser/plugins` |
| iOS display name | `apps/phone/ios/Ardia/Info.plist` | `Solstice` |
| Android id | `apps/phone/android/app/build.gradle` | `com.openbrowsercompany.solstice.android` |
| Package scope | every `package.json` | `@ardia/*` |
| Site domain | `apps/site` | `ardia.dev` |
| Brand pipeline | `docs/brand/ardia/` | `build.py`, `source/` |
| Legal | `NOTICE` | `Solstice`, Copyright 2026 Mantra Patel |

The bundle id is the highest-risk single value. Changing it moves Application Support, Keychain items, WebAuthn credentials, cookies, safaris' data, the update feed and every native host path at once. It is a deliberate decision, not a find-and-replace.

## 4. User-visible brand constants

The UI does not have one central brand constant; it has several, plus about 700 files that mention the name.

| Constant | File |
|---|---|
| `WORDMARK` (onboarding intro) | `apps/browser/src/components/onboarding/introCues.ts` |
| `APP` (import flow) | `apps/browser/src/components/import/model.ts` |
| `APP` (settings rows type) | `apps/browser/src/components/settings/rows/types.ts` |
| `APP` (General pane) | `apps/browser/src/components/settings/panes/General.tsx` |
| `APP` (Tabs pane) | `apps/browser/src/components/settings/panes/Tabs.tsx` |
| `APP` (Updates pane) | `apps/browser/src/components/settings/panes/UpdatesSection.tsx` |

A single shared constant is the first refactor to make before string replacement, or every later rename costs another pass over 748 files.

Feature names also carry the brand, for example **Little Solstice** (the small window), which needs a new feature name that is not a concatenation of the product name.

## 5. Asset matrix and its slots

The repo already documents its brand pipeline in `docs/brand/ardia/README.md`, including where every generated file goes. The new logo plugs into this, and each slot needs its own export — not one resized image.

| Asset | Slot | Notes |
|---|---|---|
| `AppIcon.icon` (`<part>-light`, `-dark`, `-tinted`) | `apps/browser/macos/Ardia-macOS/` | Icon Composer layers, macOS 26+ |
| `AppIcon.appiconset/*` | `Assets.xcassets/` | 16–512 at 1x/2x, rendered with `ictool` |
| Six alternate icons | `Assets.xcassets/AppIcon-<id>.imageset` | Settings › App Icon: midnight, daylight, plum, ocean, mono, noir |
| `app-icon.png` | `apps/browser/assets/` | 512 px, onboarding and check-in banner |
| `ntp-mark*` layers | `apps/browser/assets/` | New Tab page, three layers, per profile colour |
| `apple-touch-icon.png` | `apps/site/public/` | 180 px |
| Favicon set | `apps/site/public/`, browser UI | `.ico`, 16/32/48 PNG |
| Social preview | `apps/site/public/og.png` | 1200×630 |
| Windows `.ico` | Windows app packaging | multi-size 16–256 |
| Linux PNG sizes | Linux packaging | 16–512, plus desktop entry |
| Raycast icon | `extras/raycast-ardia/assets/icon.png` | 512 px |
| Docs branding | `docs/`, README | header mark |

Not present today and required by the brief: a splash/loading treatment, an installer background, GitHub organization presentation, and a light/dark wordmark for the toolbar and About screen. The current repo has a painted icon with no separate wordmark lockup, so that lockup has to be derived from the supplied master.

## 6. Naming layers that need a decision

1. Product display name: `[NEW_BROWSER_NAME]`.
2. Company and copyright line: "The Open Browser Company" versus the existing `Copyright 2026 Mantra Patel` notice.
3. Reverse-DNS bundle id: `com.openbrowsercompany.solstice` → new prefix. Affects data location, Keychain, WebAuthn, updates.
4. Domains: `ardia.dev`, the appcast, the release repo.
5. Repositories and organization presentation.
6. CLI command: `ardia` → new command name, and the plugin release repo.
7. Internal identifiers: keep (Phase A) or rename (Phase B, engine rebuild).
8. Feature names containing the brand: "Little Solstice" and any others.
9. Historical release notes: keep as written, or relabel the archive.

## 7. Licensing constraint

`NOTICE` states that the app as distributed is GPL-3.0 because its engine carries Helium's patches, while Solstice's own source files are Apache-2.0. Rebranding does **not** change either licence, and Apache-2.0 §4 and GPL-3.0 §5 require keeping the copyright notices and the offer of corresponding source.

So: the product name, icons and UI can all change, but `NOTICE` keeps the upstream copyright line and the source links must keep resolving to a repository containing this code. A rebrand that deletes the attribution is a licence violation, and a rebrand that keeps the name is a trademark problem. This plan does the first correctly.

## 8. Verification constraint

No build will run on this Mac, so the rebrand cannot be verified the usual way here. The checks that remain:

- `pnpm -C apps/browser typecheck` and the unit tests for touched packages;
- `pnpm -C apps/linux typecheck` and `test:graph`/`test:host` for shared-UI changes;
- asset validation (dimensions, alpha, `.icon` layers, `.ico` sizes);
- a build on CI or another Mac before any release.

The macOS build is currently unbuildable here for signing reasons as well (`com.openbrowsercompany.solstice` has no provisioning profile and the only identity has no validated team), so the rebrand does not remove an existing capability.

## 9. Sequence

1. **Inputs.** Name and master logo.
2. **One brand module.** A single exported identity (name, company, tagline, bundle prefix, domains) consumed by the UI, so later changes are one edit.
3. **macOS identity.** `app.json`, `Info.plist`, product name, bundle id, target and scheme names, helper names, update feed.
4. **Icons.** Generate the full matrix from the master; validate each slot.
5. **UI copy.** Onboarding, settings, About, menus, error text, import flow.
6. **Site and distribution.** Domain, appcast, installer, release scripts, CLI display name.
7. **Platforms.** Windows manifest, Linux desktop entry and packaging, phone display name.
8. **Docs and org.** README, docs, GitHub presentation.
9. **Phase B.** Engine-level logos after a separate engine build.
