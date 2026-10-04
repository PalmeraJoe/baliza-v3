import { createContext, useContext, useMemo, useState } from 'react'
import type { MvpSession } from '../api/client'

type SessionState = {
  session: MvpSession | null
  setSession: (session: MvpSession | null) => void
  decisionId: string | null
  setDecisionId: (id: string | null) => void
  actionId: string | null
  setActionId: (id: string | null) => void
  outcomeId: string | null
  setOutcomeId: (id: string | null) => void
}

const Ctx = createContext<SessionState | null>(null)

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<MvpSession | null>(null)
  const [decisionId, setDecisionId] = useState<string | null>(null)
  const [actionId, setActionId] = useState<string | null>(null)
  const [outcomeId, setOutcomeId] = useState<string | null>(null)
  const value = useMemo(
    () => ({
      session,
      setSession,
      decisionId,
      setDecisionId,
      actionId,
      setActionId,
      outcomeId,
      setOutcomeId,
    }),
    [session, decisionId, actionId, outcomeId],
  )
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useSession() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('SessionProvider required')
  return ctx
}
