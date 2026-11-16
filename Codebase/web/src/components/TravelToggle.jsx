const CHOICES = [
  { value: 'domestic', label: 'US-Only' },
  { value: 'international', label: 'International' },
  { value: 'anywhere', label: 'Both' },
]

function TravelToggle({ travel, setTravel }) {
  return (
    <div className="flex gap-2">
      {CHOICES.map((choice) => (
        <button
          key={choice.value}
          type="button"
          onClick={() => setTravel(choice.value)}
          className={
            'flex-1 rounded border px-3 py-2 text-sm font-medium ' +
            (travel === choice.value
              ? 'border-blue-600 bg-blue-600 text-white'
              : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50')
          }
        >
          {choice.label}
        </button>
      ))}
    </div>
  )
}

export default TravelToggle
