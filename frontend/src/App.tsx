import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { OverviewPage } from './pages/OverviewPage'
import { SpotsPage } from './pages/SpotsPage'
import { SpotDetailPage } from './pages/SpotDetailPage'
import { AlertsPage, AlertDetailPage } from './pages/AlertsPage'
import { DssListPage, DssDetailPage } from './pages/DssPage'
import { DecisionsPage, DecisionDetailPage } from './pages/DecisionsPage'
import { SessionProvider } from './state/session'

export default function App() {
  return (
    <SessionProvider>
      <AppShell>
        <Routes>
          <Route path="/" element={<OverviewPage />} />
          <Route path="/spots" element={<SpotsPage />} />
          <Route path="/spots/:spotId" element={<SpotDetailPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/alerts/:alertId" element={<AlertDetailPage />} />
          <Route path="/dss" element={<DssListPage />} />
          <Route path="/dss/:packageId" element={<DssDetailPage />} />
          <Route path="/decisions" element={<DecisionsPage />} />
          <Route path="/decisions/:decisionId" element={<DecisionDetailPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppShell>
    </SessionProvider>
  )
}
