#!/usr/bin/env bash
set -euo pipefail
usage="usage: scripts/release/check-packages.sh <dist> <version>  (the update zip holds exactly one app, named as installs from before the rename, with this build's id and version; the DMG holds exactly Solstice.app and the Applications link)"
dist="${1:?$usage}"
version="${2:?$usage}"
root="$(cd "$(dirname "$0")/../.." && pwd -P)"
zip="$dist/Solstice-$version.zip"
dmg="$dist/Solstice-$version.dmg"
legacy="$("$root/scripts/lib/legacy-name.sh" appFileName)"
status=0
fail() { echo "FAIL $*"; status=1; }
tops="$(zipinfo -1 "$zip" | cut -d/ -f1 | sort -u)"
[ "$tops" = "$legacy" ] || fail "$zip's top-level entries are '$(echo $tops)', not exactly $legacy (Sparkle 2.9.6 finds pre-rename installs only by that file name)"
plist="$(mktemp)"
unzip -p "$zip" "$legacy/Contents/Info.plist" > "$plist" 2>/dev/null || fail "$zip has no $legacy/Contents/Info.plist"
[ "$(plutil -extract CFBundleIdentifier raw "$plist" 2>/dev/null)" = com.openbrowsercompany.solstice ] || fail "$zip's app isn't com.openbrowsercompany.solstice"
[ "$(plutil -extract CFBundleShortVersionString raw "$plist" 2>/dev/null)" = "$version" ] || fail "$zip's app isn't $version"
rm -f "$plist"
mnt="$(mktemp -d)"
hdiutil attach -nobrowse -readonly -mountpoint "$mnt" "$dmg" >/dev/null 2>&1 || fail "can't mount $dmg"
shown="$(ls "$mnt" | sort | tr '\n' ' ')"
[ "$shown" = "Applications Solstice.app " ] || fail "$dmg shows '$shown', not exactly Solstice.app and Applications"
[ "$(plutil -extract CFBundleShortVersionString raw "$mnt/Solstice.app/Contents/Info.plist" 2>/dev/null)" = "$version" ] || fail "$dmg's Solstice.app isn't $version"
hdiutil detach "$mnt" >/dev/null 2>&1 || true
[ "$status" = 0 ] && echo "packages ok: $zip holds $legacy (com.openbrowsercompany.solstice $version); $dmg holds Solstice.app"
exit "$status"
