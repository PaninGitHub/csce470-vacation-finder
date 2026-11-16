import { useState } from 'react'
import TravelToggle from './components/TravelToggle.jsx'
import SearchBar from './components/SearchBar.jsx'
import RadiusSlider from './components/RadiusSlider.jsx'
import MapView from './components/MapView.jsx'
import CategoryBar from './components/CategoryBar.jsx'
import ResultList from './components/ResultList.jsx'
import { searchPlaces } from './api.js'

const PER_GROUP = 10

function App() {
  const [query, setQuery] = useState('')
  const [travel, setTravel] = useState('anywhere')
  const [radius, setRadius] = useState(25) // km
  const [group, setGroup] = useState('')


  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function runSearch(extra = {}) {
    setLoading(true)
    setError('')
    try {
      const params = { q: query, travel, radius_km: radius, per_group: PER_GROUP, ...extra }
      setData(await searchPlaces(params))
    } catch {
      setError('Could not reach the server. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  function switchTravel(value) {
    setTravel(value)
    runSearch({ travel: value })
  }

  const results = data ? data.results : []
  // The tabs only filter what is already loaded
  const shown = group ? results.filter((place) => place.group === group) : results

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900">
      <div className="mx-auto flex max-w-2xl flex-col gap-4 px-4 py-8">
        <h1 className="text-2xl font-semibold">Vacation Finder</h1>
        <TravelToggle travel={travel} setTravel={setTravel} />
        <SearchBar query={query} setQuery={setQuery} onSearch={() => runSearch()} loading={loading} />
        <RadiusSlider radius={radius} setRadius={setRadius} />
        <MapView results={shown} />
        <CategoryBar group={group} setGroup={setGroup} results={results} />
        <ResultList
          results={shown}
          loading={loading}
          error={error}
          data={data}
          onSwitchTravel={switchTravel}
          onNearMe={runSearch}
        />
      </div>
    </div>
  )
}

export default App
