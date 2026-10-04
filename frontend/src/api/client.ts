const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  })
  if (!response.ok) {
    const detail = await response.text()
    throw new Error(detail || `${response.status} ${response.statusText}`)
  }
  return response.json() as Promise<T>
}

export type MvpSession = {
  spot_id: string
  alert_id: string
  dss_package_id: string
  actor_id: string
  evaluation_id: string
  rule_name: string
  rule_version: string
  threshold_status: string
  demo_only: boolean
  scientifically_validated: boolean
  thermal_ground_truth: string
  ml_implementation: string
}

export type SpotSummary = {
  spot_id: string
  label: string
  latitude: number
  longitude: number
  crs: string
  spatial_precision?: string
  spatial_precision_note?: string
  thermal_ground_truth?: string
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  listSpots: () => request<{ spots: SpotSummary[] }>('/scientific/spots'),
  intelligence: (spotId: string) => request<Record<string, unknown>>(`/scientific/spots/${spotId}/intelligence`),
  bootstrap: () =>
    request<{ session: MvpSession; brief: string; summary: Record<string, unknown> }>(
      '/scientific/mvp/bootstrap',
      { method: 'POST' },
    ),
  session: () => request<{ session: MvpSession }>('/scientific/mvp/session'),
  alerts: () => request<{ alerts: Array<{ id: string; status: string; severity: string }> }>('/alerts'),
  alert: (id: string) => request<Record<string, unknown>>(`/alerts/${id}`),
  alertContext: (id: string) => request<Record<string, unknown>>(`/alerts/${id}/context`),
  dssPackages: () => request<{ packages: Array<Record<string, unknown>> }>('/dss/packages'),
  dssBrief: (id: string) => request<Record<string, unknown>>(`/dss/packages/${id}/brief`),
  dssEvidence: (id: string) => request<Record<string, unknown>>(`/dss/packages/${id}/evidence`),
  dssOptions: (id: string) =>
    request<{
      options: Array<{
        recommendation_id: string
        text: string
        epistemic_label: string
        source: string
        is_decision: boolean
      }>
    }>(`/dss/packages/${id}/options`),
  dssSnapshots: (id: string) => request<{ snapshots: Array<Record<string, unknown>> }>(`/dss/packages/${id}/snapshots`),
  decisions: () => request<{ decisions: Array<Record<string, unknown>> }>('/decisions'),
  decision: (id: string) => request<Record<string, unknown>>(`/decisions/${id}`),
  recordDecision: (body: {
    actor_id: string
    package_id: string
    justification: string
    selected_option: string
  }) => request<Record<string, unknown>>('/decisions', { method: 'POST', body: JSON.stringify(body) }),
  recordAction: (body: {
    actor_id: string
    decision_id: string
    action_type: string
    description: string
  }) => request<Record<string, unknown>>('/actions', { method: 'POST', body: JSON.stringify(body) }),
  recordOutcome: (body: { action_id: string; decision_id: string; notes: string }) =>
    request<Record<string, unknown>>('/outcomes', { method: 'POST', body: JSON.stringify(body) }),
  getAction: (id: string) => request<Record<string, unknown>>(`/actions/${id}`),
  getOutcome: (id: string) => request<Record<string, unknown>>(`/outcomes/${id}`),
}
