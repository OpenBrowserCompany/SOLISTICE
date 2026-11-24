# Product identity

The browser is **Solstice**, produced by **The Open Browser Company**.

Company description: "An independent software company building open-source browsers and tools for a better web."

The product name is used for the application display name, window and menu labels, UI copy, documentation, website copy, download filenames and release assets. The company name is used for authorship, the press kit and the About/Version detail in Settings.

## Naming decisions

| Surface | Value | Note |
|---|---|---|
| macOS display name | Solstice | `CFBundleDisplayName` and `PRODUCT_NAME` |
| macOS bundle id | `com.openbrowsercompany.solstice` | Deliberate clean break from the old bundle id; existing user data does not migrate |
| Android application id | `com.openbrowsercompany.solstice` | Same clean break |
| iOS display name | Solstice | `CFBundleDisplayName` |
| Linux package and update artefacts | `Solstice-*` | Release scripts and CI updated together |
| Windows installer label | Solstice | Inno Setup `UninstallDisplayName` and packaging scripts |
| Sparkle archive and nightly asset | `Solstice.zip`, `Solstice-Nightly.dmg` | Update feed paths updated with the filenames |

## Intentionally unchanged

These are build plumbing or third-party identifiers, not product branding. Renaming them would break the build without changing anything a user sees:

- Xcode project, workspace, target and scheme names (`Ardia.xcodeproj`, `Ardia.xcworkspace`, `Ardia-macOS`), the phone Xcode project and scheme (`Solstice`), and file names such as `Ardia.sdef`, `Ardia.entitlements` and `Ardia.build.json`.
- Native module and API identifiers (`ArdiaCore`, `ArdiaWebView`, `ArdiaHost`, the `AC*` C entry points, `ARDIA_*` environment variables) and npm package scope `@ardia/*`.
- The Windows launcher executable name `Ardia.exe` and its project directory. Changing it requires a coordinated Windows native rebuild and installer change.
- The Chromium product logos and helper icons under `engine/`. These are hashed by `engine/engine-key.sh`; changing them invalidates the prebuilt engine and needs a new engine build on every platform.
- Upstream project names, URLs and legal credits: `ardia-browser/ardia`, `ardia.dev`, Apache/GPL notices, `NOTICE`, `LICENSE*`, `CLA.md`, and historical entries under `docs/release-notes/`.
- The bundled command-line plugin still exposes the `ardia` command; it is an external plugin release pinned by `apps/browser/official-plugins.json`, not first-party code in this repository.
