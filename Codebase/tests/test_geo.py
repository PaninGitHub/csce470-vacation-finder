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

PLACES = [
	{"name": "Temple", "key": "temple", "kind": "city", "region": "Texas", "country": "US", "lat": 31.1, "lon": -97.4, "n_places": 62},
	{"name": "Kyoto", "key": "kyoto", "kind": "city", "region": "Japan", "country": "JP", "lat": 35.0, "lon": 135.7, "n_places": 300},
	{"name": "Japan", "key": "japan", "kind": "country", "region": "Japan", "country": "JP", "lat": 36.0, "lon": 138.0, "n_places": 5000},
	{"name": "New York", "key": "new york", "kind": "city", "region": "New York", "country": "US", "lat": 40.75, "lon": -73.98, "n_places": 1180},
	{"name": "New York", "key": "new york", "kind": "state", "region": "New York", "country": "US", "lat": 41.7, "lon": -74.0, "n_places": 20000},
	{"name": "Italy", "key": "italy", "kind": "city", "region": "Texas", "country": "US", "lat": 32.2, "lon": -96.9, "n_places": 8},
	{"name": "Italy", "key": "italy", "kind": "country", "region": "Italy", "country": "IT", "lat": 41.9, "lon": 12.5, "n_places": 4000},
	{"name": "Texas", "key": "texas", "kind": "state", "region": "Texas", "country": "US", "lat": 30.7, "lon": -97.1, "n_places": 22000},
	{"name": "California", "key": "california", "kind": "city", "region": "Maryland", "country": "US", "lat": 38.3, "lon": -76.5, "n_places": 22},
	{"name": "California", "key": "california", "kind": "state", "region": "California", "country": "US", "lat": 36.7, "lon": -119.4, "n_places": 31000},
]

def test_place_after_in_beats_town_word():
	# "temple" is a town in Texas, but the query is about Kyoto
	entry, rest = find_loc("temple in Kyoto", PLACES)
	assert entry["name"] == "Kyoto"
	assert rest == "temple in"

def test_place_after_in_beats_town_word_with_country():
	entry, rest = find_loc("temple Kyoto Japan", PLACES)
	assert entry["name"] == "Kyoto"

def test_town_word_alone_still_matches():
	entry, rest = find_loc("temple in Temple", PLACES)
	assert entry["name"] == "Temple"

def test_city_beats_state_of_same_name():
	entry, rest = find_loc("pizza in New York", PLACES)
	assert entry["kind"] == "city"
	assert rest == "pizza in"

def test_state_word_picks_state():
	entry, rest = find_loc("pizza in New York state", PLACES)
	assert entry["kind"] == "state"

def test_city_with_state_picks_city():
	entry, rest = find_loc("pasta in Italy, Texas", PLACES)
	assert entry["kind"] == "city"
	assert entry["region"] == "Texas"
	assert rest == "pasta in"

def test_italy_alone_is_country():
	entry, rest = find_loc("pasta in Italy", PLACES)
	assert entry["kind"] == "country"

def test_small_town_does_not_beat_state():
	# California, Maryland is a tiny town, so "California" still means the state
	entry, rest = find_loc("hotels in California", PLACES)
	assert entry["kind"] == "state"
	assert entry["region"] == "California"
