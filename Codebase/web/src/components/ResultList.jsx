import { useState } from 'react'
import ResultCard from './ResultCard.jsx'

function ResultList({ results, loading, error, data, onSwitchTravel, onNearMe }) {
  const [geoError, setGeoError] = useState('')

  if (loading) return <p className="text-gray-600">Searching...</p>
  if (error) return <p className="text-red-600">{error}</p>
  if (!data) return <p className="text-gray-500">Search for a place to see results.</p>

  if (data.results.length === 0) {
    const vague = !data.location && data.note.includes('place name')

    function listNearMe() {
      setGeoError('')
      if (!navigator.geolocation) {
        setGeoError('Location is not available in this browser.')
        return
      }
      navigator.geolocation.getCurrentPosition(
        (pos) => onNearMe({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
        () => setGeoError('Could not get your location. Allow location access or add a city to your search.'),
      )
    }

    return (
      <div className="rounded-lg border border-gray-200 bg-white p-4 text-sm">
        {vague ? (
          <>
            <p>Add a city or area to your search, or list places near you.</p>
            <button
              type="button"
              onClick={listNearMe}
              className="mt-3 rounded bg-blue-600 px-3 py-2 font-medium text-white hover:bg-blue-700"
            >
              List places near me
            </button>
            {geoError && <p className="mt-2 text-red-600">{geoError}</p>}
          </>
        ) : (
          <p>{data.note || 'No results.'}</p>
        )}
        {data.suggest_travel && (
          <button
            type="button"
            onClick={() => onSwitchTravel(data.suggest_travel)}
            className="mt-3 rounded bg-blue-600 px-3 py-2 font-medium text-white hover:bg-blue-700"
          >
            Switch to {data.suggest_travel === 'international' ? 'International' : 'US-Only'}
          </button>
        )}
      </div>
    )
  }

  if (results.length === 0) return <p className="text-gray-500">No places in this category.</p>

  return (
    <div className="flex flex-col gap-3">
      {data.note && <p className="text-sm text-gray-600">{data.note}</p>}
      {results.map((place) => (
        <ResultCard key={place.id} place={place} />
      ))}
    </div>
  )
}

export default ResultList
