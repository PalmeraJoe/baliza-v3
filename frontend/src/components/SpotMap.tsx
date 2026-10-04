import { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

type Props = {
  latitude: number
  longitude: number
  label: string
  precisionNote: string
}

export function SpotMap({ latitude, longitude, label, precisionNote }: Props) {
  const ref = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!ref.current) return
    const map = L.map(ref.current, {
      zoomControl: true,
      attributionControl: true,
    }).setView([latitude, longitude], 6)

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap',
      maxZoom: 18,
    }).addTo(map)

    const marker = L.circleMarker([latitude, longitude], {
      radius: 8,
      color: '#1f6f78',
      fillColor: '#1f6f78',
      fillOpacity: 0.85,
      weight: 2,
    }).addTo(map)

    marker.bindPopup(
      `<strong>${label}</strong><br/>lat ${latitude}, lon ${longitude}<br/><em>${precisionNote}</em>`,
    )

    return () => {
      map.remove()
    }
  }, [latitude, longitude, label, precisionNote])

  return <div className="map-frame" ref={ref} data-testid="spot-map" aria-label="Spot map" />
}
