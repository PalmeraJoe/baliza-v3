import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, type SpotSummary } from '../api/client'
import { EpistemicChip } from '../components/EpistemicChip'
import { SpotMap } from '../components/SpotMap'
import { useSession } from '../state/session'

export function OverviewPage() {
  const { session, setSession } = useSession()
  const [spots, setSpots] = useState<SpotSummary[]>([])
  const [alerts, setAlerts] = useState<Array<{ id: string; status: string; severity: string }>>([])
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<string>('UNKNOWN')

  async function refresh() {
    const listed = await api.listSpots()
    setSpots(listed.spots)
    try {
      const alertBody = await api.alerts()
      setAlerts(alertBody.alerts)
    } catch {
      setAlerts([])
    }
    setLastUpdated(new Date().toISOString())
  }

  useEffect(() => {
    refresh().catch((err: Error) => setError(err.message))
  }, [])

  async function bootstrap() {
    setBusy(true)
    setError(null)
    try {
      const body = await api.bootstrap()
      setSession(body.session)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setBusy(false)
    }
  }

  const demo = spots[0]
  const gaps = session ? 1 : 0

  return (
    <div className="stack">
      <section className="panel">
        <h2>Scientific Decision Support</h2>
        <p className="muted">
          BALIZA presents public scientific evidence for human review. It does not invent risk scores
          or local bleaching predictions.
        </p>
        <div className="row" style={{ marginTop: '0.75rem' }}>
          <button type="button" onClick={bootstrap} disabled={busy} data-testid="bootstrap-btn">
            {busy ? 'Loading DEMO session…' : 'Load DEMO scientific session'}
          </button>
          {session ? (
            <span className="muted">Session ready for Spot → Alert → DSS → Decision</span>
          ) : (
            <span className="muted">Bootstrap seeds Alert + DSS; Decision stays human.</span>
          )}
        </div>
        {error ? <p className="error" style={{ marginTop: '0.75rem' }}>{error}</p> : null}
      </section>

      <section className="grid grid-3">
        <div className="panel">
          <h3>Active Spots</h3>
          <p className="metric">{spots.length}</p>
        </div>
        <div className="panel">
          <h3>Active Alerts</h3>
          <p className="metric">{alerts.filter((a) => a.status === 'OPEN').length}</p>
        </div>
        <div className="panel">
          <h3>Data Gaps</h3>
          <p className="metric">{gaps > 0 ? 'VISIBLE' : 'SEE SPOT'}</p>
          <p className="muted">Absence of MERMAID match is a gap, not “healthy”.</p>
        </div>
      </section>

      <section className="panel">
        <div className="row">
          <h2>Spots</h2>
          <span className="muted">Last refreshed: {lastUpdated}</span>
        </div>
        {demo ? (
          <div className="stack">
            <SpotMap
              latitude={demo.latitude}
              longitude={demo.longitude}
              label={demo.spot_id}
              precisionNote={demo.spatial_precision_note ?? `CRS ${demo.crs}`}
            />
            <ul className="list">
              <li>
                <div className="row">
                  <div>
                    <strong>
                      <Link to={`/spots/${demo.spot_id}`}>{demo.spot_id}</Link>
                    </strong>
                    <div className="muted">
                      {demo.latitude}, {demo.longitude} · CRS {demo.crs}
                    </div>
                  </div>
                  <div className="banner" style={{ margin: 0 }}>
                    <EpistemicChip kind="REAL SCIENTIFIC DATA" />
                    {session ? <EpistemicChip kind="DEMO / NON-SCIENTIFIC" /> : null}
                  </div>
                </div>
              </li>
            </ul>
          </div>
        ) : (
          <p className="muted">No Spots available from API.</p>
        )}
      </section>

      <section className="panel">
        <h2>Alerts</h2>
        {alerts.length === 0 ? (
          <p className="muted">No alerts in memory. Load the DEMO scientific session first.</p>
        ) : (
          <ul className="list">
            {alerts.map((alert) => (
              <li key={alert.id}>
                <Link to={`/alerts/${alert.id}`}>
                  {alert.severity.toUpperCase()} · {alert.status}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
