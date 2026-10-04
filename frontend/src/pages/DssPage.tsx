import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api/client'
import { EpistemicChip } from '../components/EpistemicChip'
import { useSession } from '../state/session'

export function DssListPage() {
  const { session } = useSession()
  const [packages, setPackages] = useState<Array<Record<string, unknown>>>([])

  useEffect(() => {
    api.dssPackages().then((body) => setPackages(body.packages)).catch(() => setPackages([]))
  }, [session])

  return (
    <section className="panel">
      <h2>DSS Packages</h2>
      {packages.length === 0 ? (
        <p className="muted">No DSS packages. Bootstrap from Overview.</p>
      ) : (
        <ul className="list">
          {packages.map((pkg) => (
            <li key={String(pkg.id)}>
              <Link to={`/dss/${pkg.id}`}>{String(pkg.id)}</Link>
              <div className="muted">Opened {String(pkg.opened_at)}</div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export function DssDetailPage() {
  const { packageId = '' } = useParams()
  const navigate = useNavigate()
  const { session, setDecisionId } = useSession()
  const [brief, setBrief] = useState<Record<string, unknown> | null>(null)
  const [options, setOptions] = useState<
    Array<{
      recommendation_id: string
      text: string
      epistemic_label: string
      is_decision: boolean
    }>
  >([])
  const [evidence, setEvidence] = useState<Record<string, unknown> | null>(null)
  const [selected, setSelected] = useState('')
  const [justification, setJustification] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    Promise.all([api.dssBrief(packageId), api.dssOptions(packageId), api.dssEvidence(packageId)])
      .then(([b, o, e]) => {
        setBrief(b)
        setOptions(o.options)
        setEvidence(e)
        if (o.options[0]) setSelected(o.options[0].recommendation_id.split(':').slice(-1)[0] || o.options[0].text)
      })
      .catch((err: Error) => setError(err.message))
  }, [packageId])

  async function onDecide(event: FormEvent) {
    event.preventDefault()
    if (!session) {
      setError('MVP session missing actor. Bootstrap first.')
      return
    }
    if (!justification.trim()) {
      setError('Justification is required for a human decision.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      // selected_option in backend is the option code/text used by protocol
      const optionCode = selected.includes(':') ? selected.split(':').slice(-1)[0] : selected
      const decision = await api.recordDecision({
        actor_id: session.actor_id,
        package_id: packageId,
        justification: justification.trim(),
        selected_option: optionCode,
      })
      setDecisionId(String(decision.id))
      navigate(`/decisions/${decision.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setBusy(false)
    }
  }

  if (error && !brief) return <p className="error">{error}</p>
  if (!brief) return <p className="muted">Loading DSS…</p>

  return (
    <div className="stack">
      <section className="panel">
        <div className="row">
          <h2>DSS Package</h2>
          <EpistemicChip kind="DEMO / NON-SCIENTIFIC" />
        </div>
        <p className="muted">
          What is happening, what evidence supports it, what is uncertain, what is missing, and which
          options are available — without converting recommendations into decisions.
        </p>
      </section>

      <section className="grid grid-2">
        <div className="panel">
          <h3>Situation</h3>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem' }}>
            {JSON.stringify(brief.signals ?? brief, null, 2).slice(0, 1200)}
          </pre>
        </div>
        <div className="panel">
          <h3>Evidence / synthesis</h3>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem' }}>
            {JSON.stringify(evidence ?? {}, null, 2).slice(0, 1200)}
          </pre>
        </div>
      </section>

      <section className="panel">
        <h3>Uncertainty & data gaps</h3>
        <p className="muted">Threshold status: {String(brief.threshold_status)}</p>
        <div className="notice">
          <strong>Visible scientific limits</strong>
          Thermal ground truth: NOT_AVAILABLE · Local estimation: NOT_AUTHORIZED · ML: NOT_AUTHORIZED
          · MERMAID compatible observation: NOT_AVAILABLE
        </div>
      </section>

      <section className="panel">
        <h3>Options</h3>
        <p className="muted">Each option is a RECOMMENDATION / protocol option. None execute automatically.</p>
        <ul className="list">
          {options.map((option) => (
            <li key={option.recommendation_id}>
              <div className="row">
                <div>
                  <strong>{option.text}</strong>
                  <div className="muted">{option.recommendation_id}</div>
                </div>
                <EpistemicChip kind="RECOMMENDATION" />
              </div>
              <div className="muted">is_decision: {String(option.is_decision)}</div>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel">
        <h3>Record human decision</h3>
        <p>
          <EpistemicChip kind="DECISION" /> This is a human decision.
        </p>
        <form className="stack" onSubmit={onDecide} data-testid="decision-form">
          <label>
            Actor
            <input value={session?.actor_id ?? ''} readOnly />
          </label>
          <label>
            Available option
            <select
              value={selected}
              onChange={(event) => setSelected(event.target.value)}
              data-testid="option-select"
            >
              {options.map((option) => {
                const code = option.recommendation_id.includes(':')
                  ? option.recommendation_id.split(':').slice(-1)[0]
                  : option.recommendation_id
                return (
                  <option key={option.recommendation_id} value={code}>
                    {option.text}
                  </option>
                )
              })}
            </select>
          </label>
          <label>
            Justification (required)
            <textarea
              value={justification}
              onChange={(event) => setJustification(event.target.value)}
              placeholder="Why are you selecting this option?"
              data-testid="justification"
              required
            />
          </label>
          {error ? <p className="error">{error}</p> : null}
          <button type="submit" disabled={busy || !session} data-testid="record-decision">
            {busy ? 'Recording…' : 'Record Decision'}
          </button>
        </form>
      </section>
    </div>
  )
}
