import { NavLink } from 'react-router-dom'
import { EpistemicChip } from './EpistemicChip'

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="brand">BALIZA</p>
          <p className="tagline">Scientific Decision Support — Visual MVP</p>
        </div>
        <nav className="nav" aria-label="Main">
          <NavLink to="/" end>
            Overview
          </NavLink>
          <NavLink to="/spots">Spots</NavLink>
          <NavLink to="/alerts">Alerts</NavLink>
          <NavLink to="/dss">DSS</NavLink>
          <NavLink to="/decisions">Decisions</NavLink>
        </nav>
      </header>
      <div className="banner">
        <EpistemicChip kind="REAL SCIENTIFIC DATA" />
        <EpistemicChip kind="DEMO / NON-SCIENTIFIC" />
        <EpistemicChip kind="DATA GAP" />
      </div>
      {children}
      <p className="footnote">
        Backend is the source of truth. This UI does not recalculate SST, HotSpot, DHW, thresholds,
        severity, or risk. ML and local estimation remain not authorized. Thermal ground truth is not
        available.
      </p>
    </div>
  )
}
