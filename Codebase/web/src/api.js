// Address of the backend (uvicorn --app-dir src api.main:app --port 8000, run from Codebase/)
const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Set VITE_RANKER=BM25 to skip loading the embedding model while developing
const RANKER = import.meta.env.VITE_RANKER

async function getJson(path, params = {}) {
  const url = new URL(BASE + path)
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, value)
    }
  }
  const res = await fetch(url)
  if (!res.ok) {
    throw new Error('Request failed with status ' + res.status)
  }
  return res.json()
}

// Lists the states, countries and categories for the filters
export function getOptions() {
  return getJson('/api/options')
}

// params: { q, travel, radius_km, group, per_group, lat, lon, ... }
export function searchPlaces(params) {
  return getJson('/api/search', RANKER ? { ...params, ranker: RANKER } : params)
}
