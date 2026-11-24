import assert from "node:assert/strict";
import { test } from "node:test";
const { useBrowser } = await import("../browser/store.ts");
const { useSettingsNav } = await import("../settings/settingsWindows.ts");

const S = () => useBrowser.getState();
const tabCount = () => Object.keys(S().tabs).length;

test("solstice://settings and solstice://newtab open what they name instead of loading in a tab, with only the store loaded", () => {
  S().hydrate({});
  const w = S().createWindow({ url: "https://a.example/" });
  const page = Object.keys(S().tabs)[0];
  const before = tabCount();
  assert.equal(S().newTab(w, { url: "solstice://settings/passwords" }), "");
  assert.equal(useSettingsNav.getState().pane, "profiles");
  assert.equal(tabCount(), before, "no tab for a settings address");
  S().navigate(page, "solstice://settings/privacy");
  assert.equal(useSettingsNav.getState().pane, "general");
  assert.equal(S().tabs[page].url, "https://a.example/", "the page stays where it was");
  assert.equal(S().newTab(w, { url: "solstice://newtab" }), "");
  assert.equal(tabCount(), before + 1, "a blank new tab");
  assert.equal(S().newTab(w, { url: "solstice://history" }) !== "", true, "an app page is a tab");
});
