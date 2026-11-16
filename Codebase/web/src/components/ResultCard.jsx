const CHIP_COLORS = {
  LODGING: 'bg-blue-100 text-blue-800',
  THINGS_TO_DO: 'bg-green-100 text-green-800',
  FOOD_DRINK: 'bg-orange-100 text-orange-800',
  SHOPPING: 'bg-purple-100 text-purple-800',
}

function ResultCard({ place }) {
  const chip = 'rounded-full px-2 py-0.5 text-xs '
  const hasRating = place.avg_rating != null

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="font-semibold">{place.name}</h3>
      <div className="mt-1 flex flex-wrap gap-1">
        <span className={chip + (CHIP_COLORS[place.group] || 'bg-gray-100 text-gray-800')}>
          {place.group_label}
        </span>
        {place.categories.slice(0, 2).map((category) => (
          <span key={category} className={chip + 'bg-gray-100 text-gray-700'}>
            {category}
          </span>
        ))}
      </div>
      {place.address && <p className="mt-2 text-sm text-gray-600">{place.address}</p>}
      <p className="mt-1 text-sm text-gray-600">
        {hasRating && (
          <span>
            {place.avg_rating.toFixed(1)}
            {place.n_reviews != null && ' (' + place.n_reviews + ' reviews)'}
          </span>
        )}
        {place.price_text && <span>{hasRating ? ' · ' : ''}{place.price_text}</span>}
        {place.distance_km != null && (
          <span>{hasRating || place.price_text ? ' · ' : ''}{place.distance_km} km away</span>
        )}
      </p>
      {place.snippet && <p className="mt-2 text-sm italic text-gray-500">“{place.snippet}”</p>}
    </div>
  )
}

export default ResultCard
