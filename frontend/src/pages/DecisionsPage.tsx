import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import { EpistemicChip } from '../components/EpistemicChip'
import { useSession } from '../state/session'

export function DecisionsPage() {
  const [decisions, setDecisions] = useState<Array<Record<string, unknown>>>([])

  useEffect(() => {
    api.decisions().then((body) => setDecisions(body.decisions)).catch(() => setDecisions([]))
  }, [])

  return (
    <section className="panel">
      <h2>Decisions</h2>
      {decisions.length === 0 ? (
        <p className="muted">No human decisions recorded yet.</p>
      ) : (
        <ul className="list">
          {decisions.map((item) => (
            <li key={String(item.id)}>
              <Link to={`/decisions/${item.id}`}>{String(item.id)}</Link>
              <div className="muted">
                {String(item.selected_option)} · {String(item.decided_at)}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export function DecisionDetailPage() {
  const { decisionId = '' } = useParams()
  const { session, actionId, setActionId, outcomeId, setOutcomeId } = useSession()
  const [decision, setDecision] = useState<Record<string, unknown> | null>(null)
  const [action, setAction] = useState<Record<string, unknown> | null>(null)
  const [outcome, setOutcome] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api
      .decision(decisionId)
      .then(setDecision)
      .catch((err: Error) => setError(err.message))
  }, [decisionId])

  useEffect(() => {
    if (actionId) {
      api.getAction(actionId).then(setAction).catch(() => setAction(null))
    }
  }, [actionId])

  useEffect(() => {
    if (outcomeId) {
      api.getOutcome(outcomeId).then(setOutcome).catch(() => setOutcome(null))
    }
  }, [outcomeId])

  async function onAction(event: FormEvent) {
    event.preventDefault()
    if (!session || !decision) return
    setBusy(true)
    setError(null)
    try {
      const created = await api.recordAction({
        actor_id: session.actor_id,
        decision_id: String(decision.id),
        action_type: 'continue_monitoring',
        description: 'Human-recorded follow-up after decision (MVP). No external automation.',
      })
      setActionId(String(created.id))
      setAction(created)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setBusy(false)
    }
  }

  async function onOutcome(event: FormEvent) {
    event.preventDefault()
    if (!decision || !actionId) return
    setBusy(true)
    setError(null)
    try {
      const created = await api.recordOutcome({
        action_id: actionId,
        decision_id: String(decision.id),
        notes: 'Outcome observed for MVP demo. Does not rewrite Alert, Decision, Snapshot, or Evidence.',
      })
      setOutcomeId(String(created.id))
      setOutcome(created)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setBusy(false)
    }
  }

  if (error && !decision) return <p className="error">{error}</p>
  if (!decision) return <p className="muted">Loading decision…</p>

  return (
    <div className="stack">
      <section className="panel">
        <div className="row">
          <h2>Decision</h2>
          <EpistemicChip kind="DECISION" />
        </div>
        <table className="table">
          <tbody>
            <tr>
              <th>ID</th>
              <td>{String(decision.id)}</td>
            </tr>
            <tr>
              <th>Actor</th>
              <td>{String(decision.actor_id)}</td>
            </tr>
            <tr>
              <th>Decided at</th>
              <td>{String(decision.decided_at)}</td>
            </tr>
            <tr>
              <th>Selected option</th>
              <td>{String(decision.selected_option)}</td>
            </tr>
            <tr>
              <th>Justification</th>
              <td>{String(decision.justification)}</td>
            </tr>
            <tr>
              <th>DSS Snapshot</th>
              <td>{String(decision.snapshot_id)}</td>
            </tr>
            <tr>
              <th>Snapshot hash</th>
              <td>{String(decision.snapshot_hash)}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section className="panel">
        <h3>Action</h3>
        <p className="muted">Actions require a Decision. No automatic email, pump, beach closure, or protocol run.</p>
        {action ? (
          <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(action, null, 2)}</pre>
        ) : (
          <form onSubmit={onAction}>
            <button type="submit" disabled={busy} data-testid="record-action">
              Record Action
            </button>
          </form>
        )}
      </section>

      <section className="panel">
        <h3>Outcome</h3>
        <p className="muted">Outcome is after Action. It does not rewrite prior evidence or the frozen snapshot.</p>
        {outcome ? (
          <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(outcome, null, 2)}</pre>
        ) : (
          <form onSubmit={onOutcome}>
            <button type="submit" disabled={busy || !actionId} data-testid="record-outcome">
              Record Outcome
            </button>
          </form>
        )}
        {error ? <p className="error">{error}</p> : null}
      </section>

      <p className="muted">
        <Link to="/">Back to Overview</Link>
      </p>
    </div>
  )
}
