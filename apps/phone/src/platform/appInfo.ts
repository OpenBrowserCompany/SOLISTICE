import Constants from "expo-constants";
import { pages } from "@ardia/phone-native";
import { appVersionLabel } from "../lib/appVersionLabel";

export const appVersion = () => {
  const release = pages.appRelease();
  return release ? appVersionLabel(release, __DEV__) : `Solstice ${Constants.expoConfig?.version ?? "1.0"}`;
};
