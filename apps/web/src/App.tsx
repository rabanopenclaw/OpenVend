import { useEffect, useState } from "react";
import { Shell } from "./components/Shell";
import { applyTheme, getStoredTheme, type ThemePreference } from "./lib/theme";

export function App() {
  const [theme, setTheme] = useState<ThemePreference>(() => getStoredTheme());

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  return <Shell theme={theme} onThemeChange={setTheme} />;
}
