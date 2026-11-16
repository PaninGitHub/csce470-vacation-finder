function SearchBar({ query, setQuery, onSearch, loading }) {
  function handleSubmit(e) {
    e.preventDefault()
    onSearch()
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="e.g. sushi in Honolulu"
        className="min-w-0 flex-1 rounded border border-gray-300 bg-white px-3 py-2 focus:border-blue-600 focus:outline-none"
      />
      <button
        type="submit"
        disabled={loading}
        className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
      >
        Search
      </button>
    </form>
  )
}

export default SearchBar
