function MapView({ results }) {
  const located = results.filter((place) => place.lat != null && place.lon != null).length

  return (
    <div className="flex h-40 flex-col items-center justify-center rounded border border-dashed border-gray-400 bg-gray-200 text-sm text-gray-600">
      <p>Map coming later</p>
      <p className="text-xs text-gray-500">{located} places have coordinates</p>
    </div>
  )
}

export default MapView
