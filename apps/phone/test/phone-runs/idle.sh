#!/system/bin/sh
P=com.openbrowsercompany.solstice.android.dev
dumpsys gfxinfo $P reset >/dev/null; date -u +%FT%TZ; sleep $1; dumpsys gfxinfo $P; date -u +%FT%TZ
