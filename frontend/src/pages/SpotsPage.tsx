import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { api, type SpotSummary } from '../api/client'
import { EpistemicChip } from '../components/EpistemicChip'
import { useSession } from '../state/session'

export function SpotsPage() {
  const { session } = useSession()
  const [spots, setSpots] = useState<SpotSummary[]>([])

  useEffect(() => {
    api.listSpots().then((body) => setSpots(body.spots))
  }, [])

  return (
    <section className="panel">
      <h2>Spots</h2>
      <ul className="list">
        {spots.map((spot) => (
          <li key={spot.spot_id}>
            <div className="row">
              <div>
                <strong>
                  <Link to={`/spots/${spot.spot_id}`}>{spot.spot_id}</Link>
                </strong>
                <div className="muted">
                  Location: {spot.latitude}, {spot.longitude} · Spatial precision:{' '}
                  {spot.spatial_precision ?? 'UNKNOWN'} · CRS {spot.crs}
                </div>
                <div className="muted">
                  Alert status: {session?.alert_id ? 'OPEN (DEMO session)' : 'UNKNOWN until session load'}
                </div>
                <div className="muted">Thermal ground truth: NOT_AVAILABLE</div>
              </div>
              <EpistemicChip kind="DATA GAP" />
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}
