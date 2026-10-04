import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import { EpistemicChip } from '../components/EpistemicChip'
import { useSession } from '../state/session'

export function AlertsPage() {
  const { session } = useSession()
  const [alerts, setAlerts] = useState<Array<{ id: string; status: string; severity: string }>>([])

  useEffect(() => {
    api.alerts().then((body) => setAlerts(body.alerts)).catch(() => setAlerts([]))
  }, [session])

  return (
    <section className="panel">
      <h2>Alerts</h2>
      {alerts.length === 0 ? (
        <p className="muted">No alerts. Bootstrap the DEMO session from Overview.</p>
      ) : (
        <ul className="list">
          {alerts.map((alert) => (
            <li key={alert.id}>
              <Link to={`/alerts/${alert.id}`}>
                {alert.severity} · {alert.status} · {alert.id}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export function AlertDetailPage() {
  const { alertId = '' } = useParams()
  const { session } = useSession()
  const [alert, setAlert] = useState<Record<string, unknown> | null>(null)
  const [context, setContext] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([api.alert(alertId), api.alertContext(alertId)])
      .then(([a, c]) => {
        setAlert(a)
        setContext(c)
      })
      .catch((err: Error) => setError(err.message))
  }, [alertId])

  if (error) return <p className="error">{error}</p>
  if (!alert || !context) return <p className="muted">Loading alert…</p>

  const signals = (context.signals as Array<Record<string, unknown>>) ?? []
  const signal = signals[0] ?? {}

  return (
    <div className="stack">
      <section className="panel">
        <div className="row">
          <h2>Alert</h2>
          <EpistemicChip kind="DEMO / NON-SCIENTIFIC" />
        </div>
        <p className="muted">Alert is not a Decision. Severity comes from the backend RuleVersion.</p>
        <table className="table">
          <tbody>
            <tr>
              <th>ID</th>
              <td>{String(alert.id)}</td>
            </tr>
            <tr>
              <th>Severity</th>
              <td>{String(alert.severity)}</td>
            </tr>
            <tr>
              <th>Status</th>
              <td>{String(alert.status)}</td>
            </tr>
            <tr>
              <th>Spot</th>
              <td>
                {session ? (
                  <Link to={`/spots/${session.spot_id}`}>{session.spot_id}</Link>
                ) : (
                  'DEMO-CRW-ORIG24-HERITAGE-POINT'
                )}
              </td>
            </tr>
            <tr>
              <th>Rule / version</th>
              <td>
                {String(signal.rule_id ?? session?.rule_name ?? 'UNKNOWN')} @{' '}
                {String(signal.rule_version ?? session?.rule_version ?? 'UNKNOWN')}
              </td>
            </tr>
            <tr>
              <th>Threshold status</th>
              <td>{String(context.threshold_status ?? 'DEMO / NON-SCIENTIFIC')}</td>
            </tr>
            <tr>
              <th>Is decision?</th>
              <td>{String(alert.is_decision ?? false)}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section className="panel">
        <h3>Why this alert exists</h3>
        <p>
          Rule <strong>{String(signal.rule_version ?? session?.rule_version)}</strong> evaluated input{' '}
          <strong>{String(signal.observed_value ?? 'UNKNOWN')}</strong> against threshold{' '}
          <strong>{JSON.stringify(signal.thresholds ?? {})}</strong>.
        </p>
        <p>
          Result: <strong>{String(signal.outcome ?? 'UNKNOWN')}</strong>
        </p>
        <p className="muted">Reason: {String(signal.reason ?? 'Explanation unavailable')}</p>
        <div className="notice" style={{ marginTop: '0.75rem' }}>
          <strong>Not a scientific bleaching threshold</strong>
          This DEMO / NON-SCIENTIFIC watch is for DSS demonstration only.
          SCIENTIFICALLY_VALIDATED = false.
        </div>
      </section>

      <section className="panel">
        <h3>Next</h3>
        {session ? (
          <Link className="button" to={`/dss/${session.dss_package_id}`}>
            Open DSS package
          </Link>
        ) : (
          <p className="muted">Load DEMO session to open DSS.</p>
        )}
      </section>
    </div>
  )
}
