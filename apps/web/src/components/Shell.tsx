import {
  Activity,
  BarChart3,
  Boxes,
  CalendarDays,
  FileDown,
  Home,
  KeyRound,
  Moon,
  PackageCheck,
  Settings,
  ShieldCheck,
  Sun,
  Users,
} from "lucide-react";
import type { ThemePreference } from "../lib/theme";

const navigation = [
  { label: "Dashboard", icon: Home, active: true },
  { label: "Agenda", icon: CalendarDays },
  { label: "Contacts", icon: Users },
  { label: "Inventory", icon: Boxes },
  { label: "Quotes", icon: PackageCheck },
  { label: "Reports", icon: BarChart3 },
  { label: "Exports", icon: FileDown },
  { label: "AI Agents", icon: KeyRound },
  { label: "Audit Log", icon: Activity },
  { label: "Settings", icon: Settings },
];

type ShellProps = {
  theme: ThemePreference;
  onThemeChange: (theme: ThemePreference) => void;
};

export function Shell({ theme, onThemeChange }: ShellProps) {
  return (
    <div className="app-shell min-h-screen">
      <aside className="sidebar" aria-label="Main navigation">
        <div className="brand-lockup">
          <div className="brand-mark">OV</div>
          <div>
            <strong>OpenVend</strong>
            <span>ERP workspace</span>
          </div>
        </div>

        <nav className="nav-list">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <a className={item.active ? "nav-item active" : "nav-item"} href="/" key={item.label}>
                <Icon size={18} aria-hidden="true" />
                <span>{item.label}</span>
              </a>
            );
          })}
        </nav>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Phase 0 foundation</p>
            <h1>Dashboard</h1>
          </div>
          <div className="topbar-actions">
            <label className="theme-control">
              <span>Theme</span>
              <select value={theme} onChange={(event) => onThemeChange(event.target.value as ThemePreference)}>
                <option value="system">System</option>
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </label>
            <div className="theme-icon" aria-hidden="true">
              {theme === "dark" ? <Moon size={18} /> : <Sun size={18} />}
            </div>
          </div>
        </header>

        <section className="kpi-grid" aria-label="Selected KPIs">
          <Metric label="Revenue" value="€0" trend="No orders yet" />
          <Metric label="Open quotes" value="0" trend="Pipeline ready" />
          <Metric label="Low stock" value="0" trend="Inventory module pending" />
          <Metric label="Agent actions" value="0" trend="MCP gateway pending" />
        </section>

        <section className="dashboard-layout">
          <div className="panel main-panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Readiness</p>
                <h2>Phase 0 service map</h2>
              </div>
              <span className="status-pill">Foundation</span>
            </div>
            <div className="service-map">
              {[
                ["Traefik", "edge routing"],
                ["Ory Kratos", "identity flows"],
                ["Authorization Adapter", "roles and scopes"],
                ["PostgreSQL", "one database per module"],
                ["Valkey", "cache and queue"],
                ["Web UI", "human API parity surface"],
              ].map(([name, detail]) => (
                <div className="service-row" key={name}>
                  <ShieldCheck size={18} aria-hidden="true" />
                  <div>
                    <strong>{name}</strong>
                    <span>{detail}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <aside className="panel assistant-panel" aria-label="Assistant actions">
            <p className="eyebrow">Agent access</p>
            <h2>Scoped by default</h2>
            <p>
              MCP and CLI actions will use the same REST APIs, scopes, audit log, and confirmation
              queues as human workflows.
            </p>
            <button type="button">View token plan</button>
          </aside>
        </section>
      </main>
    </div>
  );
}

function Metric({ label, value, trend }: { label: string; value: string; trend: string }) {
  return (
    <article className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{trend}</small>
    </article>
  );
}
