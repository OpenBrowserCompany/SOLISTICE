import assert from "node:assert/strict";
import { test } from "node:test";
await import("../../test-native/index.ts");
const { useBrowser } = await import("../browser/store.ts");
const { openExternalUrls } = await import("./actions.ts");
const { admitIncomingUrl } = await import("./incomingUrls.ts");
const { setLinkGate } = await import("./linkGate.ts");
const { noteIncomingLinksRefused, takeExternalAppCounts } = await import("../telemetry/externalAppCounts.ts");

const S = () => useBrowser.getState();
const PERSONAL = { id: "default", name: "Personal", color: "plum", icon: null, createdAt: 0 };

const ADMITTED = [
  ["https://example.com/a?b#c", "https://example.com/a?b#c"],
  ["HTTP://Example.com/", "HTTP://Example.com/"],
  ["file:///Users/me/page.html", "file:///Users/me/page.html"],
  ["file:///C:/Users/me/doc.pdf", "file:///C:/Users/me/doc.pdf"],
  ["about:blank", "about:blank"],
  ["solstice://history", "solstice://history"],
  ["solstice://bookmarks?q=otters", "solstice://bookmarks?q=otters"],
  ["solstice://downloads", "solstice://downloads"],
  ["solstice://newtab", "solstice://newtab"],
  ["solstice://settings", "solstice://settings"],
  ["solstice://settings/passwords", "solstice://settings/passwords"],
  ["ARDIA://Settings/Appearance", "solstice://settings/Appearance"],
  ["ardia:history", "solstice://history"],
  ["solstice://game", "solstice://game"],
  ["solstice://version", "solstice://version"],
  ["chrome://history", "solstice://history"],
  ["netnyahoo://yahu", "solstice://game"],
  ["netnyahoo://bookmarks", "solstice://bookmarks"],
];

const REFUSED = [
  "solstice://restart",
  "solstice://quit",
  "solstice://kill",
  "solstice://crash",
  "solstice://hang",
  "solstice://gpuclean",
  "solstice://gpucrash",
  "solstice://inducebrowsercrashforrealz",
  "solstice://flags",
  "solstice://flags/#enable-x",
  "solstice://net-internals",
  "solstice://net-export",
  "solstice://extensions",
  "solstice://extensions/?id=abc",
  "solstice://policy",
  "solstice://inspect",
  "solstice://password-manager/passwords",
  "solstice://settings-reset",
  "solstice://settings/reset",
  "solstice://settings/clearBrowserData",
  "solstice://chrome-urls",
  "solstice://downloads-internals",
  "solstice://",
  "ardia:",
  "ARDIA://FLAGS",
  "Solstice://Restart",
  "ardia:flags",
  "ardia:restart",
  "solstice://%66lags",
  "solstice://%72estart",
  "solstice://history%2f..%2fflags",
  "solstice://history@flags",
  "solstice://settings@restart",
  "solstice://version\\..\\restart",
  " solstice://flags",
  "solstice://flags ",
  "\tsolstice://restart",
  "solstice://restart\n",
  "solstice://fl\nags",
  "solstice://re\u0000start",
  "\u200bsolstice://flags",
  "\ufeffsolstice://quit",
  "solstice://quit\u00a0",
  "chrome://flags",
  "chrome://restart",
  "CHROME://quit",
  "chrome:kill",
  "chrome://version\u2028",
  "netnyahoo://flags",
  "NETNYAHOO://restart",
  "netnyahoo:quit",
  "about:flags",
  "about:restart",
  "about:version ",
  "ABOUT:crash",
  "view-source:solstice://settings",
  "view-source:chrome://flags",
  "view-source:netnyahoo://version",
  "view-source:https://example.com/",
  "VIEW-SOURCE:solstice://history",
  "chrome-untrusted://terminal",
  "devtools://devtools/bundled/inspector.html",
  "chrome-extension://abc/page.html",
  "data:text/html,<b>x</b>",
  "blob:https://example.com/123",
  "filesystem:https://example.com/temporary/x",
  "javascript:alert(1)",
  "JaVaScRiPt:alert(1)",
  "mailto:a@example.com",
  "http:/example.com",
  "http:\\\\example.com",
  "https://",
  "https:///flags",
  "https:example.com",
  " https://example.com/",
  "https://exa mple.com/",
  "https://example.com/\r\nx",
  "about:srcdoc",
  "",
];

for (const [given, expected] of ADMITTED) {
  test(`a link from another app to ${JSON.stringify(given)} is admitted as ${expected}`, () => {
    assert.equal(admitIncomingUrl(given), expected);
  });
}

for (const given of REFUSED) {
  test(`a link from another app to ${JSON.stringify(given)} is refused`, () => {
    assert.equal(admitIncomingUrl(given), null);
  });
}

function mainWindow(settings = {}) {
  S().hydrate({ profiles: { default: PERSONAL }, profileOrder: ["default"], windows: {}, tabs: {} });
  const main = S().createWindow({ url: "https://main.example/" });
  S().setFocusedWindow(main);
  S().updateSettings({ openLinksInLittleArdia: false, allowJavaScriptFromAppleEvents: false, ...settings });
  return main;
}

const allTabUrls = () => Object.values(S().tabs).map((t) => t.url);
const settle = () => new Promise((resolve) => setTimeout(resolve, 10));

for (const gated of [false, true]) {
  test(`links from other apps never open internal pages, legacy aliases included (${gated ? "with" : "without"} a link gate)`, async () => {
    setLinkGate(gated ? (url) => ({ url, route: null, decided: false }) : null);
    mainWindow();
    const refused = openExternalUrls(["solstice://restart", "netnyahoo://flags", "chrome://quit", "about:kill", "view-source:solstice://settings", "https://ok.example/", "solstice://history"]);
    await settle();
    const urls = allTabUrls();
    assert.ok(urls.includes("https://ok.example/"));
    assert.ok(urls.includes("solstice://history"));
    for (const url of urls) assert.ok(!/restart|flags|quit|kill|view-source/i.test(url ?? ""), `opened ${url}`);
    assert.equal(refused, 5);
    setLinkGate(null);
  });
}

test("a link gate can't turn a link from another app into an internal page", async () => {
  setLinkGate(() => ({ url: "solstice://flags", route: null, decided: true }));
  mainWindow();
  openExternalUrls(["https://ok.example/"]);
  await settle();
  assert.ok(!allTabUrls().some((url) => /flags/.test(url ?? "")));
  setLinkGate(null);
});

test("a routed link from another app is still checked when the gate rewrites it", async () => {
  setLinkGate(() => ({ url: "chrome://restart", route: { profileId: null, open: "tab", windowId: null, groupKey: null }, decided: true }));
  mainWindow();
  openExternalUrls(["https://ok.example/"]);
  await settle();
  assert.ok(!allTabUrls().some((url) => /restart/.test(url ?? "")));
  setLinkGate(null);
});

test("JavaScript links from other apps open only with Allow JavaScript from Apple Events on", async () => {
  mainWindow();
  openExternalUrls(["javascript:void(1)"]);
  await settle();
  assert.ok(!allTabUrls().some((url) => /^javascript:/i.test(url ?? "")));
});

test("refused links from other apps are summed into the hourly external app counts", () => {
  takeExternalAppCounts();
  noteIncomingLinksRefused(2);
  noteIncomingLinksRefused(0);
  assert.equal(takeExternalAppCounts().incoming_links_refused, 2);
  assert.equal(takeExternalAppCounts().incoming_links_refused, 0);
});
