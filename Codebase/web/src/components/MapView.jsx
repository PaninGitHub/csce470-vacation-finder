import { useEffect } from 'react'
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

// Vite does not resolve Leaflet's default icon paths, so set them here
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
})

// MapContainer ignores center changes, so fit the view to the markers instead
// The coordinates come in as a JSON string so unrelated re-renders do not re-fit
function FitBounds({ pointsKey }) {
  const map = useMap()

  useEffect(() => {
    map.fitBounds(JSON.parse(pointsKey), { padding: [30, 30], maxZoom: 14 })
  }, [map, pointsKey])

  return null
}

function MapView({ results }) {
  const located = results.filter((place) => place.lat != null && place.lon != null)

  if (located.length === 0) {
    return (
      <div className="flex h-80 items-center justify-center rounded border border-dashed border-gray-400 bg-gray-200 text-sm text-gray-600">
        <p>No places to show on the map</p>
      </div>
    )
  }

  const points = located.map((place) => [place.lat, place.lon])

  return (
    <MapContainer
      center={points[0]}
      zoom={10}
      className="z-0 h-80 rounded border border-gray-300"
    >
      <TileLayer
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      {located.map((place) => (
        <Marker key={place.id} position={[place.lat, place.lon]}>
          <Popup>
            <strong>{place.name}</strong>
            <br />
            {place.group_label}
          </Popup>
        </Marker>
      ))}
      <FitBounds pointsKey={JSON.stringify(points)} />
    </MapContainer>
  )
}

export default MapView
