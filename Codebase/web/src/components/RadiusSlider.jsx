function RadiusSlider({ radius, setRadius }) {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor="radius" className="text-sm text-gray-600">
        Radius: {radius} km
      </label>
      <input
        id="radius"
        type="range"
        min="1"
        max="200"
        step="1"
        value={radius}
        onChange={(e) => setRadius(Number(e.target.value))}
        className="w-full accent-blue-600"
      />
    </div>
  )
}

export default RadiusSlider
