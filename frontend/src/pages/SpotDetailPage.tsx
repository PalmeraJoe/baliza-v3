import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import { EpistemicChip } from '../components/EpistemicChip'
import { SpotMap } from '../components/SpotMap'
import { useSession } from '../state/session'

type IndicatorRow = {
  what?: string
  value?: number | string
  unit?: string
  dataset_id?: string
  epistemic?: string
  applies_to?: string
  temporal_association?: { source_time?: string }
  cell?: { latitude?: number; longitude?: number }
}

export function SpotDetailPage() {
  const { spotId = '' } = useParams()
  const { session } = useSession()
  const [intel, setIntel] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .intelligence(spotId)
      .then(setIntel)
      .catch((err: Error) => setError(err.message))
  }, [spotId])

  if (error) return <p className="error">{error}</p>
  if (!intel) return <p className="muted">Loading Spot Intelligence…</p>

  const spot = intel.spot as {
    spot_id: string
    latitude: number
    longitude: number
    crs: string
  }
  const thermal = intel.thermal_evidence as {
    indicators: IndicatorRow[]
    product_status: Record<string, string>
    epistemic: string
  }
  const habitat = intel.ecological_habitat_context as {
    coverage: string
    epistemic: string
    summary: string
  }
  const field = intel.field_ecological_observations as {
    status_label: string
    summary: string
    compatible_count: number
  }
  const gaps = (intel.data_gaps as Array<{ source: string; detail: string; availability?: string }>) ?? []
  const uncertainty = intel.uncertainty as Record<string, string>
  const acceptance = intel.scientific_acceptance as Record<string, string>

  return (
    <div className="stack">
      <section className="panel">
        <div className="row">
          <div>
            <h2>{spot.spot_id}</h2>
            <p className="muted">
              {spot.latitude}, {spot.longitude} · CRS {spot.crs} · Spatial association production: UNKNOWN
            </p>
          </div>
          <div className="banner" style={{ margin: 0 }}>
            <EpistemicChip kind="REAL SCIENTIFIC DATA" />
            {session ? <EpistemicChip kind="DEMO / NON-SCIENTIFIC" /> : null}
          </div>
        </div>
        <div className="grid grid-3" style={{ marginTop: '0.75rem' }}>
          <div>
            <strong>What is known?</strong>
            <p className="muted">{acceptance.THERMAL}</p>
            <p className="muted">{acceptance.HABITAT}</p>
          </div>
          <div>
            <strong>What is unknown?</strong>
            <p className="muted">{acceptance.FIELD_ECOLOGY}</p>
            <p className="muted">Thermal ground truth: {acceptance.THERMAL_GROUND_TRUTH}</p>
          </div>
          <div>
            <strong>Is there an alert?</strong>
            <p className="muted">
              {session?.alert_id ? (
                <>
                  Yes — <Link to={`/alerts/${session.alert_id}`}>open alert</Link> (DEMO rule)
                </>
              ) : (
                'UNKNOWN until DEMO session is loaded'
              )}
            </p>
          </div>
        </div>
      </section>

      <SpotMap
        latitude={spot.latitude}
        longitude={spot.longitude}
        label={spot.spot_id}
        precisionNote={`CRS ${spot.crs}. Point shown; no reef boundary invented.`}
      />

      <section className="panel">
        <h3>Indicators — NOAA CRW</h3>
        <p className="muted">
          Epistemic: <EpistemicChip kind="EXTERNAL INDICATOR" /> — not measured local temperature.
        </p>
        <table className="table">
          <thead>
            <tr>
              <th>Indicator</th>
              <th>Value</th>
              <th>Source time</th>
              <th>Epistemic</th>
            </tr>
          </thead>
          <tbody>
            {thermal.indicators.map((row) => (
              <tr key={row.dataset_id}>
                <td>
                  <strong>{row.what}</strong>
                  <div className="muted">{row.dataset_id}</div>
                </td>
                <td>
                  {row.value} {row.unit}
                </td>
                <td>{row.temporal_association?.source_time ?? 'UNKNOWN'}</td>
                <td>
                  <EpistemicChip kind="EXTERNAL INDICATOR" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="grid grid-2">
        <div className="panel">
          <h3>Sources</h3>
          <ul className="list">
            <li>
              NOAA Coral Reef Watch — PARTIAL (cell retrieved; spatial association UNKNOWN)
              <div>
                <EpistemicChip kind="EXTERNAL INDICATOR" />
              </div>
            </li>
            <li>
              Allen Coral Atlas — {habitat.coverage}
              <div>
                <EpistemicChip kind="CONTEXT ONLY" />
              </div>
              <p className="muted">{habitat.summary}</p>
            </li>
            <li>
              MERMAID — {field.status_label}
              <div>
                <EpistemicChip kind="DATA GAP" />
              </div>
              <p className="muted">{field.summary}</p>
            </li>
          </ul>
        </div>
        <div className="panel">
          <h3>Uncertainty</h3>
          <ul className="list">
            {Object.entries(uncertainty)
              .filter(([key]) => key.includes('uncertainty') || key === 'model_uncertainty')
              .map(([key, value]) => (
                <li key={key}>
                  {key}: {String(value)}
                </li>
              ))}
          </ul>
          <p className="muted">No aggregate uncertainty score is computed in the UI.</p>
        </div>
      </section>

      <section className="panel">
        <h3>Data gaps</h3>
        <div className="notice">
          <strong>MERMAID</strong>
          No compatible field observation found for this Spot.
          <br />
          This does NOT mean: “No bleaching”.
          <br />
          It means: “No compatible observation is currently available.”
        </div>
        <ul className="list" style={{ marginTop: '0.75rem' }}>
          {gaps.slice(0, 8).map((gap, index) => (
            <li key={`${gap.source}-${index}`}>
              <strong>{gap.source}</strong> [{gap.availability ?? 'SOURCE_REPORTED'}]
              <div className="muted">{gap.detail}</div>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel">
        <h3>Evidence chain</h3>
        <div className="chain">
          <div className="step">Source: NOAA Coral Reef Watch / Allen / MERMAID</div>
          <div className="step">Dataset / product → raw artifact + checksum (backend)</div>
          <div className="step">Normalized EXTERNAL_INDICATOR / CONTEXT_ONLY / field gap</div>
          <div className="step">Spot Intelligence contract</div>
          <div className="step">
            {session ? (
              <>
                RuleEvaluation → Alert →{' '}
                <Link to={`/dss/${session.dss_package_id}`}>DSS package</Link>
              </>
            ) : (
              'RuleEvaluation / Alert available after DEMO session bootstrap'
            )}
          </div>
        </div>
      </section>

      <section className="panel">
        <h3>AI analysis</h3>
        <p className="muted">Not enabled in MVP. Assistive AI is not on the critical path.</p>
      </section>
    </div>
  )
}
