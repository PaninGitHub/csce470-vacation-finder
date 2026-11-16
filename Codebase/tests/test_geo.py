from vacfinder.geo import find_loc, find_distance_sphere, radius_search

ENTRIES = [
	{"name": "Honolulu", "key": "honolulu", "kind": "city", "region": "Hawaii", "country": "US", "lat": 21.3, "lon": -157.85, "n_places": 500},
	{"name": "Waikiki", "key": "waikiki", "kind": "area", "region": "Hawaii", "country": "US", "lat": 21.28, "lon": -157.83, "n_places": 0},
	{"name": "Hawaii", "key": "hawaii", "kind": "state", "region": "Hawaii", "country": "US", "lat": 20.8, "lon": -156.3, "n_places": 2000},
	{"name": "Oregon", "key": "or", "kind": "state", "region": "Oregon", "country": "US", "lat": 44.0, "lon": -120.5, "n_places": 2000},
]

def test_find_in_sentence():
	entry, rest = find_loc("beach resort in Waikiki", ENTRIES)
	assert entry["name"] == "Waikiki"
	assert rest == "beach resort in"

def test_area_beats_city():
	entry, rest = find_loc("waikiki honolulu sushi", ENTRIES)
	assert entry["name"] == "Waikiki"

def test_no_place_name():
	entry, rest = find_loc("quiet cabin with a hot tub", ENTRIES)
	assert entry is None
	assert rest == "quiet cabin with a hot tub"

def test_two_letter_code_ignored():
	# "or" is a normal word, not Oregon
	entry, rest = find_loc("hiking or kayaking", ENTRIES)
	assert entry is None

def test_haversine():
	# Honolulu to Waikiki is a few km
	assert 2 < find_distance_sphere(21.3, -157.85, 21.28, -157.83) < 4
	assert find_distance_sphere(10.0, 10.0, 10.0, 10.0) == 0

def test_radius_filter():
	places = [
		{"name": "near", "lat": 21.29, "lon": -157.84},
		{"name": "mid", "lat": 21.4, "lon": -157.85},
		{"name": "far", "lat": 20.8, "lon": -156.3},
	]
	found = radius_search(places, 21.28, -157.83, 25)
	assert [p["name"] for d, p in found] == ["near", "mid"]
	assert found[0][0] < found[1][0]

def test_radius_zero_results():
	places = [{"name": "far", "lat": 20.8, "lon": -156.3}]
	assert radius_search(places, 21.28, -157.83, 25) == []

def test_empty_places():
	assert radius_search([], 21.28, -157.83, 25) == []

def test_place_on_center():
	places = [{"name": "here", "lat": 21.28, "lon": -157.83}]
	found = radius_search(places, 21.28, -157.83, 1)
	assert found[0][0] == 0

def test_query_is_only_place_name():
	entry, rest = find_loc("Waikiki", ENTRIES)
	assert entry["name"] == "Waikiki"
	assert rest == ""

def test_punctuation_in_query():
	entry, rest = find_loc("sushi, in Honolulu!", ENTRIES)
	assert entry["name"] == "Honolulu"
	assert rest == "sushi in"

def test_no_entries():
	assert find_loc("beach", []) == (None, "beach")
