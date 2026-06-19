export type ThemePreference = "light" | "dark" | "system";

const storageKey = "openvend.theme";

export function getStoredTheme(): ThemePreference {
  const value = window.localStorage.getItem(storageKey);
  if (value === "light" || value === "dark" || value === "system") {
    return value;
  }
  return "system";
}

export function resolveTheme(preference: ThemePreference): "light" | "dark" {
  if (preference === "system") {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  return preference;
}

export function applyTheme(preference: ThemePreference): void {
  const resolved = resolveTheme(preference);
  document.documentElement.dataset.theme = resolved;
  window.localStorage.setItem(storageKey, preference);
}
