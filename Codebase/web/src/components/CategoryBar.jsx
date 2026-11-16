const TABS = [
  { value: '', label: 'All' },
  { value: 'LODGING', label: 'Lodging' },
  { value: 'THINGS_TO_DO', label: 'Activities' },
  { value: 'FOOD_DRINK', label: 'Dining' },
  { value: 'SHOPPING', label: 'Shopping' },
]

function CategoryBar({ group, setGroup, results }) {
  function count(value) {
    return value ? results.filter((place) => place.group === value).length : results.length
  }

  return (
    <div className="flex flex-wrap gap-1 border-b border-gray-300">
      {TABS.map((tab) => (
        <button
          key={tab.value}
          type="button"
          onClick={() => setGroup(tab.value)}
          className={
            '-mb-px border-b-2 px-3 py-2 text-sm font-medium ' +
            (group === tab.value
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-600 hover:text-gray-900')
          }
        >
          {tab.label} <span className="text-xs text-gray-500">({count(tab.value)})</span>
        </button>
      ))}
    </div>
  )
}

export default CategoryBar
