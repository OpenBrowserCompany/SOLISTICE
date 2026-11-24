import assert from "node:assert/strict";
import { test } from "node:test";
const { WHATS_SENT } = await import("./copy.ts");

const MAC_NOTE =
  "Every 10 minutes Solstice notes on this Mac its tab, window and profile counts, its memory use, rough free disk space, the Mac's memory pressure, how long it has been open, and which of Solstice's own pages (like Settings or History) the tab in front was on, never a website's address. Solstice also takes that note when you open or leave one of those pages, and keeps the last 3 of those pages with how many minutes ago you were on each. That note is sent only with a crash report, or at the next launch after Solstice didn't quit cleanly, with whether the Mac restarted since. Turning sharing off or deleting a profile erases it";

test("the Mac's What's Sent keeps its ten-minute note word for word", () => {
  assert.ok(WHATS_SENT.some((group) => group.items.includes(MAC_NOTE)));
});
