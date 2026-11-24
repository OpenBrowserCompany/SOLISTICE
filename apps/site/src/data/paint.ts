import { GRAPHIC, TEXT, clearOf, contrast, hexOf, mix, rgbOf, softest, towards, weakest, type Rgb } from "../lib/contrast.ts";

export const BRUSH_HEADROOM = 1.1;
export const INK_FLOOR = 8;
const SECONDARY_SHARE = 0.5;
const LABEL_SHARE = 0.36;
const SECONDARY_LIFT = 1.2;

const INK = "#16130f";
const NIGHT_INK = "#e8ecf3";
const FOREST_DEEP = "#1c2d4b";
const SUN = "#c9d6ea";
const RUST = "#9fb6d6";

export type BandName =
  | "noon"
  | "golden"
  | "afternoon"
  | "dusk"
  | "plum"
  | "night"
  | "latenight"
  | "midnight"
  | "midmorning"
  | "daylong"
  | "sundown";

interface Band {
  readonly stops: readonly (readonly [string, number])[];
  readonly dab: string;
}

export const BANDS: Record<BandName, Band> = {
  noon: { stops: [["#0f1626", 0], ["#101a2e", 45], ["#16223b", 100]], dab: "var(--figure)" },
  golden: { stops: [["#142039", 0], ["#1a2a48", 40], ["#23355a", 100]], dab: "var(--figure)" },
  afternoon: { stops: [["#1b2b49", 0], ["#273c63", 100]], dab: "var(--figure)" },
  dusk: { stops: [["#202f50", 0], ["#2d3f66", 40], ["#35476f", 100]], dab: "var(--figure)" },
  plum: { stops: [["#1c2440", 0], ["#252d4f", 50], ["#2e3659", 100]], dab: "var(--figure)" },
  night: { stops: [["#141c31", 0], ["#18233c", 40], ["#1e2c4b", 100]], dab: "var(--figure)" },
  latenight: { stops: [["#101828", 0], ["#121e34", 45], ["#17243d", 100]], dab: "var(--figure)" },
  midnight: { stops: [["#0a101c", 0], ["#0c1424", 40], ["#101a2c", 100]], dab: "var(--figure)" },
  midmorning: { stops: [["#121c31", 0], ["#18253f", 40], ["#1f2f4d", 100]], dab: "var(--figure)" },
  daylong: { stops: [["#101a2c", 0], ["#16243d", 22], ["#1c2d4b", 70], ["#223456", 100]], dab: "var(--figure)" },
  sundown: { stops: [["#1a2642", 0], ["#223153", 50], ["#2b3c60", 100]], dab: "var(--figure)" },
};

export interface Tokens {
  readonly dark: boolean;
  readonly ink: string;
  readonly ink2: string;
  readonly ink3: string;
  readonly inkOn: string;
  readonly figure: string;
  readonly stamp: string;
  readonly rival: string;
  readonly ground: string;
}

const groundsOf = (band: Band): Rgb[] => band.stops.map(([colour]) => rgbOf(colour));

export function tokensOf(name: BandName): Tokens {
  const grounds = groundsOf(BANDS[name]);
  const text = TEXT + BRUSH_HEADROOM;
  const graphic = GRAPHIC + BRUSH_HEADROOM / 3;
  const dark = weakest(rgbOf(NIGHT_INK), grounds) > weakest(rgbOf(INK), grounds);
  const ink = rgbOf(dark ? NIGHT_INK : INK);
  const away = dark ? "lighter" : "darker";
  return {
    dark,
    ink: hexOf(ink),
    ink2: hexOf(towards(ink, grounds, Math.max(text * SECONDARY_LIFT, weakest(ink, grounds) * SECONDARY_SHARE))),
    ink3: hexOf(towards(ink, grounds, Math.max(text, weakest(ink, grounds) * LABEL_SHARE))),
    inkOn: dark ? INK : NIGHT_INK,
    figure: hexOf(clearOf(rgbOf(dark ? SUN : FOREST_DEEP), grounds, text, away)),
    stamp: hexOf(clearOf(rgbOf(dark ? SUN : RUST), grounds, text, away)),
    rival: hexOf(softest(ink, grounds, graphic, 0.6)),
    ground: hexOf(grounds[Math.floor(grounds.length / 2)]),
  };
}

export interface Pair {
  readonly band: BandName;
  readonly token: string;
  readonly ground: string;
  readonly ratio: number;
  readonly need: number;
}

export function pairs(): Pair[] {
  return (Object.keys(BANDS) as BandName[]).flatMap((band) => {
    const tokens = tokensOf(band);
    const roles: [string, string, number][] = [
      ["ink", tokens.ink, TEXT],
      ["ink-2", tokens.ink2, TEXT],
      ["ink-3", tokens.ink3, TEXT],
      ["figure", tokens.figure, TEXT],
      ["stamp", tokens.stamp, TEXT],
      ["rival", tokens.rival, GRAPHIC],
    ];
    return BANDS[band].stops.flatMap(([ground]) =>
      roles.map(([token, colour, need]) => ({ band, token, ground, ratio: contrast(rgbOf(colour), rgbOf(ground)), need })),
    );
  });
}

export function paintCss(): string {
  return (Object.keys(BANDS) as BandName[])
    .map((name) => {
      const band = BANDS[name];
      const tokens = tokensOf(name);
      const ink = rgbOf(tokens.ink);
      const ground = rgbOf(tokens.ground);
      const wash = band.stops.map(([colour, at]) => `${colour} ${at}%`).join(", ");
      const declarations = [
        `--bg: ${tokens.ground}`,
        `--bg-top: ${band.stops[0][0]}`,
        `--wash: linear-gradient(180deg, ${wash})`,
        `--dab: ${band.dab}`,
        `--ink: ${tokens.ink}`,
        `--ink-2: ${tokens.ink2}`,
        `--ink-3: ${tokens.ink3}`,
        `--ink-on: ${tokens.inkOn}`,
        `--figure: ${tokens.figure}`,
        `--stamp: ${tokens.stamp}`,
        `--rival: ${tokens.rival}`,
        `--ground: ${tokens.ground}`,
        `--rule: ${hexOf(mix(ground, ink, 0.2))}`,
        `--rule-strong: ${hexOf(mix(ground, ink, 0.85))}`,
        `--selection: ${tokens.dark ? "rgb(201 214 234 / 0.30)" : "rgb(28 45 75 / 0.22)"}`,
        `color: var(--ink)`,
      ];
      return `[data-paint="${name}"]{${declarations.join(";")}}`;
    })
    .join("\n");
}
