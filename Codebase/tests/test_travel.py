from vacfinder.geo import find_loc, country_entries, normalize
from vacfinder.travel import entries_for_mode, is_misfit, other_mode, is_right_mode, does_rating_qualify, rating_line

def make_place(city, region, country, i, lat=0.0, lon=0.0):
	return {"id": city + str(i), "city": city, "region": region, "country": country, "lat": lat, "lon": lon}

ITALY = (
	[make_place("Florence", "Italy", "IT", i, 43.77, 11.25) for i in range(3)]
	+ [make_place("Rome", "Italy", "IT", i, 41.9, 12.5) for i in range(4)]
	+ [make_place("Tiny Village", "Italy", "IT", 0, 40.0, 10.0)]
)
JAPAN = [make_place("Kyōto", "Japan", "JP", i, 35.0, 135.7) for i in range(3)]

US_ENTRIES = [
	{"name": "Florence", "key": "florence", "kind": "city", "region": "Alabama", "country": "US", "lat": 34.8, "lon": -87.6, "n_places": 55},
	{"name": "Hawaii", "key": "hawaii", "kind": "state", "region": "Hawaii", "country": "US", "lat": 20.8, "lon": -156.3, "n_places": 2000},
	{"name": "Waikiki", "key": "waikiki", "kind": "area", "region": "Hawaii", "country": "US", "lat": 21.28, "lon": -157.83, "n_places": 0},
]
ENTRIES = US_ENTRIES + country_entries(ITALY) + country_entries(JAPAN)

WIKI = {"source": "wikivoyage", "avg_rating": None, "n_reviews": None, "price_text": None}
GOOGLE = {"source": "google", "avg_rating": 4.26, "n_reviews": 120, "price_text": None}

def test_country_entries():
	names = [e["name"] for e in country_entries(ITALY)]
	assert "Italy" in names
	assert "Florence" in names
	# Fewer than 3 places is not enough for a city entry
	assert "Tiny Village" not in names

def test_country_entries_empty():
	assert country_entries([]) == []

def test_normalize_accents():
	assert normalize("Kyōto") == "kyoto"
	assert normalize("São Paulo") == "sao paulo"

def test_find_country():
	entry, rest = find_loc("wine tours in Italy", ENTRIES)
	assert entry["kind"] == "country"
	assert entry["country"] == "IT"
	assert rest == "wine tours in"

def test_find_city_with_accent():
	entry, rest = find_loc("temples in kyoto", ENTRIES)
	assert entry["name"] == "Kyōto"
	assert entry["country"] == "JP"

def test_biggest_city_wins():
	# Florence, Italy has 3 places here, Florence, Alabama has 55, so Anywhere finds Alabama
	entry, rest = find_loc("pizza in Florence", ENTRIES)
	assert entry["region"] == "Alabama"

def test_mode_picks_florence():
	intl = entries_for_mode(ENTRIES, "International")
	entry, rest = find_loc("pizza in Florence", intl)
	assert entry["region"] == "Italy"
	us = entries_for_mode(ENTRIES, "Domestic (US)")
	entry, rest = find_loc("pizza in Florence", us)
	assert entry["region"] == "Alabama"

def test_domestic_has_no_countries():
	us = entries_for_mode(ENTRIES, "Domestic (US)")
	assert len(us) == 3
	assert all(e["country"] == "US" for e in us)
	entry, rest = find_loc("wine in Italy", us)
	assert entry is None

def test_international_has_no_us():
	intl = entries_for_mode(ENTRIES, "International")
	assert all(e["country"] != "US" for e in intl)
	entry, rest = find_loc("snorkeling in Waikiki", intl)
	assert entry is None

def test_anywhere_keeps_all():
	assert len(entries_for_mode(ENTRIES, "Anywhere")) == len(ENTRIES)

def test_wrong_mode_offers_other():
	# Italy does not fit Domestic, so the app offers to switch to International
	entry, rest = find_loc("wine in Italy", entries_for_mode(ENTRIES, "Domestic (US)"))
	assert entry is None
	other, rest = find_loc("wine in Italy", ENTRIES)
	assert other_mode(other["country"]) == "International"
	assert other_mode("US") == "Domestic (US)"
	assert is_right_mode("IT", "International")
	assert not is_right_mode("IT", "Domestic (US)")

def test_misfit_new_mexico():
	# "Mexico" fits International, but the longer name "New Mexico" is the one the user typed
	mexico = {"key": "mexico", "country": "MX"}
	new_mexico = {"key": "new mexico", "country": "US"}
	assert is_misfit(mexico, new_mexico, "International")
	assert not is_misfit(mexico, mexico, "International")
	assert not is_misfit(new_mexico, new_mexico, "Domestic (US)")
	assert not is_misfit(None, None, "International")
	assert not is_misfit(mexico, new_mexico, "Anywhere")

def test_misfit_same_name_uses_mode():
	# Florence exists in both; International picks Italy without a warning
	alabama = ENTRIES[0]
	italy = [e for e in ENTRIES if e["region"] == "Italy" and e["name"] == "Florence"][0]
	assert not is_misfit(italy, alabama, "International")

def test_card_null_rating():
	line = rating_line(WIKI, None)
	assert line == ""
	assert "*" not in line
	assert "reviews" not in line

def test_card_price_text():
	place = dict(WIKI, price_text="EUR 10")
	assert rating_line(place, 2.34) == "Price: EUR 10  |  2.3 km away"

def test_card_with_rating():
	assert rating_line(GOOGLE, None) == "* 4.3 (120 reviews)"

def test_card_google_no_rating():
	place = dict(GOOGLE, avg_rating=None, n_reviews=None)
	assert rating_line(place, None) == "No rating yet"


def test_min_rating_keeps_unrated_wikivoyage():
	assert does_rating_qualify(WIKI, 4.0)
	assert does_rating_qualify(GOOGLE, 4.0)
	assert not does_rating_qualify(GOOGLE, 4.5)
	assert not does_rating_qualify(dict(GOOGLE, avg_rating=None), 4.0)
