import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useEffect } from 'react'
import { AppShell } from '../components/AppShell'
import { OverviewPage } from '../pages/OverviewPage'
import { SpotDetailPage } from '../pages/SpotDetailPage'
import { AlertDetailPage } from '../pages/AlertsPage'
import { DssDetailPage } from '../pages/DssPage'
import { SessionProvider, useSession } from '../state/session'
import type { MvpSession } from '../api/client'

vi.mock('../components/SpotMap', () => ({
  SpotMap: () => <div data-testid="spot-map">map</div>,
}))

const intelligence = {
  spot: {
    spot_id: 'DEMO-CRW-ORIG24-HERITAGE-POINT',
    latitude: -23.5,
    longitude: 152.0,
    crs: 'UNKNOWN',
  },
  thermal_evidence: {
    epistemic: 'EXTERNAL_INDICATOR',
    indicators: [
      {
        what: 'crw_coraltemp_sst',
        value: 22.72,
        unit: 'degree_C',
        dataset_id: 'noaacrwsstDaily',
        temporal_association: { source_time: '2026-09-26T12:00:00Z' },
      },
    ],
    product_status: { SST: 'available' },
  },
  ecological_habitat_context: {
    coverage: 'NOT_AVAILABLE',
    epistemic: 'CONTEXT_ONLY',
    summary: 'Allen context not attached',
  },
  field_ecological_observations: {
    status_label: 'DATA EXISTS BUT NO COMPATIBLE MATCH',
    summary: 'MERMAID FIELD OBSERVATION: NOT AVAILABLE FOR THIS SPOT',
    compatible_count: 0,
  },
  data_gaps: [
    {
      source: 'MERMAID',
      availability: 'DATA_EXISTS_NO_COMPATIBLE_MATCH',
      detail: 'No compatible field observation',
    },
  ],
  uncertainty: {
    measurement_uncertainty: 'UNKNOWN',
    spatial_uncertainty: 'PARTIAL',
    temporal_uncertainty: 'PARTIAL',
    association_uncertainty: 'PARTIAL',
  },
  scientific_acceptance: {
    THERMAL: 'CRW evidence available',
    HABITAT: 'Allen context partially available',
    FIELD_ECOLOGY: 'MERMAID data exists BUT NO COMPATIBLE MATCH',
    THERMAL_GROUND_TRUTH: 'NOT_AVAILABLE',
    LOCAL_ESTIMATION: 'NOT_AUTHORIZED',
  },
}

const session: MvpSession = {
  spot_id: 'DEMO-CRW-ORIG24-HERITAGE-POINT',
  alert_id: 'alert-1',
  dss_package_id: 'pkg-1',
  actor_id: 'actor-1',
  evaluation_id: 'eval-1',
  rule_name: 'demo_crw_external_sst_watch',
  rule_version: '0.0.1-demo',
  threshold_status: 'DEMO / NON-SCIENTIFIC',
  demo_only: true,
  scientifically_validated: false,
  thermal_ground_truth: 'NOT_AVAILABLE',
  ml_implementation: 'NOT_AUTHORIZED',
}

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function mockFetch(url: string, init?: RequestInit) {
  const path = url.replace(/^.*\/api/, '')
  if (path === '/scientific/spots') {
    return json({
      spots: [
        {
          spot_id: 'DEMO-CRW-ORIG24-HERITAGE-POINT',
          label: 'DEMO',
          latitude: -23.5,
          longitude: 152.0,
          crs: 'UNKNOWN',
          spatial_precision_note: 'CRS UNKNOWN',
        },
      ],
    })
  }
  if (path.includes('/intelligence')) return json(intelligence)
  if (path === '/scientific/mvp/bootstrap' && init?.method === 'POST') {
    return json({ session, brief: 'brief', summary: {} })
  }
  if (path === '/alerts') return json({ alerts: [{ id: 'alert-1', status: 'OPEN', severity: 'warning' }] })
  if (path.startsWith('/alerts/alert-1/context')) {
    return json({
      threshold_status: 'DEMO / NON-SCIENTIFIC',
      decision: null,
      signals: [
        {
          outcome: 'triggered',
          reason: '22.72 gt 20.0',
          observed_value: 22.72,
          thresholds: { demo_sst_watch: 20.0 },
          rule_version: '0.0.1-demo',
        },
      ],
    })
  }
  if (path.startsWith('/alerts/alert-1')) {
    return json({ id: 'alert-1', severity: 'warning', status: 'OPEN', is_decision: false })
  }
  if (path.endsWith('/brief')) return json({ threshold_status: 'DEMO / NON-SCIENTIFIC', signals: [] })
  if (path.endsWith('/evidence')) return json({ supports: [] })
  if (path.endsWith('/options')) {
    return json({
      options: [
        {
          recommendation_id: '0.0.1-demo:continue_monitoring',
          text: 'Continue monitoring with existing public sources',
          epistemic_label: 'RECOMMENDATION',
          is_decision: false,
          source: 'protocol',
        },
      ],
    })
  }
  if (path === '/decisions' && init?.method === 'POST') {
    const body = JSON.parse(String(init.body))
    if (!String(body.justification || '').trim()) {
      return json({ detail: 'justification required' }, 400)
    }
    return json({
      id: 'decision-1',
      actor_id: body.actor_id,
      selected_option: body.selected_option,
      justification: body.justification,
      decided_at: '2026-10-04T12:00:00Z',
      snapshot_id: 'snap-1',
      snapshot_hash: 'abc',
    })
  }
  return json({ detail: `missing mock for ${path}` }, 404)
}

function SeedSession({ value }: { value: MvpSession }) {
  const { setSession } = useSession()
  useEffect(() => {
    setSession(value)
  }, [setSession, value])
  return null
}

function renderAt(path: string, seed?: MvpSession) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <SessionProvider>
        {seed ? <SeedSession value={seed} /> : null}
        <AppShell>
          <Routes>
            <Route path="/" element={<OverviewPage />} />
            <Route path="/spots/:spotId" element={<SpotDetailPage />} />
            <Route path="/alerts/:alertId" element={<AlertDetailPage />} />
            <Route path="/dss/:packageId" element={<DssDetailPage />} />
            <Route path="/decisions/:decisionId" element={<div>Decision recorded</div>} />
          </Routes>
        </AppShell>
      </SessionProvider>
    </MemoryRouter>,
  )
}

describe('BALIZA Visual MVP', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn(mockFetch))
  })

  it('renders Overview and bootstraps DEMO session', async () => {
    const user = userEvent.setup()
    renderAt('/')
    expect(screen.getByText('BALIZA')).toBeInTheDocument()
    expect(screen.getByText('Scientific Decision Support')).toBeInTheDocument()
    expect(screen.getAllByText('DEMO / NON-SCIENTIFIC').length).toBeGreaterThan(0)
    await user.click(screen.getByTestId('bootstrap-btn'))
    expect(await screen.findByText(/Session ready/i)).toBeInTheDocument()
  })

  it('shows Spot detail with external indicators and MERMAID gap honesty', async () => {
    renderAt('/spots/DEMO-CRW-ORIG24-HERITAGE-POINT')
    expect(await screen.findByRole('heading', { name: 'DEMO-CRW-ORIG24-HERITAGE-POINT' })).toBeInTheDocument()
    expect(screen.getAllByText('EXTERNAL INDICATOR').length).toBeGreaterThan(0)
    expect(screen.getByText(/does NOT mean/i)).toBeInTheDocument()
    expect(screen.getByText(/Thermal ground truth: NOT_AVAILABLE/i)).toBeInTheDocument()
    expect(screen.getByText(/Not enabled in MVP/i)).toBeInTheDocument()
  })

  it('shows alert explanation and DEMO threshold warning', async () => {
    renderAt('/alerts/alert-1')
    expect(await screen.findByText('Why this alert exists')).toBeInTheDocument()
    expect(screen.getByText(/Not a scientific bleaching threshold/i)).toBeInTheDocument()
    expect(screen.getByText(/Alert is not a Decision/i)).toBeInTheDocument()
  })

  it('shows DSS options as recommendations and records decision with justification', async () => {
    const user = userEvent.setup()
    renderAt('/dss/pkg-1', session)
    expect(await screen.findByText('Options')).toBeInTheDocument()
    expect(screen.getAllByText('RECOMMENDATION').length).toBeGreaterThan(0)
    expect(screen.getByText(/This is a human decision/i)).toBeInTheDocument()
    const justification = await screen.findByTestId('justification')
    expect(justification).toBeRequired()
    await user.type(justification, 'Human review for Visual MVP demo')
    await user.click(await screen.findByTestId('record-decision'))
    expect(await screen.findByText('Decision recorded')).toBeInTheDocument()
  })

  it('does not auto-create actions from alerts', () => {
    renderAt('/')
    expect(screen.queryByTestId('record-action')).not.toBeInTheDocument()
    expect(screen.getByText(/Decision stays human/i)).toBeInTheDocument()
  })
})
