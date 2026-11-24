import { readFileSync } from "node:fs";
import sharp from "sharp";
import { COLOURS, FACTS, LONG, SHORT, SHOTS, SITE, ZIP_NAME } from "../data/press";
import { zip } from "./zip";

const siteRoot = process.cwd();

const builders: Record<string, () => Promise<Buffer> | Buffer> = {
  "ardia-app-icon.png": () => readFileSync(`${siteRoot}/src/assets/app-icon.png`),
  "ardia-mark-painted.png": () =>
    sharp(`${siteRoot}/src/assets/ardia-mark.png`).trim({ threshold: 16 }).png({ compressionLevel: 9 }).toBuffer(),
  "ardia-mark-colour.png": () => readFileSync(`${siteRoot}/src/assets/mark-colour.png`),
  "ardia-mark-black.png": () => readFileSync(`${siteRoot}/src/assets/mark-black.png`),
  "ardia-mark-white.png": () => readFileSync(`${siteRoot}/src/assets/mark-white.png`),
  ...Object.fromEntries(
    SHOTS.map(({ id }) => [
      `ardia-screenshot-${id}.jpg`,
      () => sharp(`${siteRoot}/src/assets/shots/${id}.webp`).jpeg({ quality: 92, mozjpeg: true }).toBuffer(),
    ]),
  ),
};

export const PRESS_FILES = Object.keys(builders);

const built = new Map<string, Promise<Buffer>>();
export const pressFile = (name: string) => {
  if (!built.has(name)) built.set(name, Promise.resolve(builders[name]!()));
  return built.get(name)!;
};

const readme = () =>
  [
    "The Open Browser Company press kit",
    "",
    SHORT,
    "",
    LONG,
    "",
    ...FACTS.map((f) => `${f.term}: ${f.href ?? f.value}`),
    "",
    "Colors",
    ...COLOURS.map((c) => `${c.name} ${c.hex}: ${c.use}`),
    "",
    "Use the marks as they are: no redrawing, recoloring, stretching or effects.",
    "The Open Browser Company isn’t affiliated with Google or The Browser Company. Arc, Dia and Chrome are their trademarks.",
    `More at https://${SITE}/press`,
    "",
  ].join("\n");

const zipEntryPath = (name: string) =>
  name.startsWith("ardia-screenshot-") ? `screenshots/${name}` : `logo/${name}`;

let kit: Promise<Buffer> | undefined;
export const pressZip = () =>
  (kit ??= Promise.all(PRESS_FILES.map(async (name) => ({ path: zipEntryPath(name), data: await pressFile(name) }))).then(
    (files) => zip(ZIP_NAME.replace(/\.zip$/, ""), [{ path: "README.txt", data: Buffer.from(readme(), "utf8") }, ...files]),
  ));
