from vacfinder.geo import find_loc, radius_search
from vacfinder.search import Searcher

def make_place(gmap_id, name, texts, rating=4.0):
	return {
		"id": gmap_id, "name": name, "categories": ["Place"], "texts": texts,
		"avg_rating": rating, "n_reviews": len(texts), "group": "LODGING", "lat": 0.0, "lon": 0.0,
	}

PLACES = [
	make_place("a", "Palm Resort", ["Great snorkeling right off the beach", "Beach was clean and snorkeling gear was free"]),
	make_place("b", "City Hotel", ["Parking was a nightmare downtown", "Room was loud at night"], rating=3.0),
	make_place("c", "Quiet Inn", ["Lovely garden and friendly staff"], rating=4.8),
]

def make_searcher():
	# No model needed, BM25 never touches the dense index
	searcher = Searcher("unused", "unused", None)
	for p in PLACES:
		searcher.place_map[p["id"]] = p
		searcher.place_region[p["id"]] = "Test"
	return searcher

def test_bm25_only_ranks_candidates():
	searcher = make_searcher()
	results = searcher.search("snorkeling beach", [PLACES[1], PLACES[2]], ranker="BM25")
	ids = [p["id"] for p, s in results]
	assert "a" not in ids

def test_bm25_best_first():
	searcher = make_searcher()
	results = searcher.search("snorkeling beach", PLACES, ranker="BM25")
	assert results[0][0]["id"] == "a"

def test_name_only_query_uses_rating():
	searcher = make_searcher()
	results = searcher.search("", PLACES, ranker="BM25")
	assert results[0][0]["id"] == "c"

def test_empty_candidates():
	assert make_searcher().search("beach", [], ranker="BM25") == []

def test_snippet_picks_matching_review():
	searcher = make_searcher()
	snippet = searcher.best_snippet(PLACES[1], "parking")
	assert "Parking" in snippet

def test_only_stopwords_uses_rating():
	searcher = make_searcher()
	results = searcher.search("the in of", PLACES, ranker="BM25")
	assert results[0][0]["id"] == "c"

def test_rating_ties_use_review_count():
	a = make_place("a", "A", ["one review here"], rating=4.0)
	b = make_place("b", "B", ["one", "two"], rating=4.0)
	results = make_searcher().search("", [a, b], ranker="BM25")
	assert [p["id"] for p, s in results] == ["b", "a"]

def test_null_avg_rating():
	# Places with no rating go last and get score 0
	nope = make_place("n", "No Rating", ["nothing yet"], rating=None)
	results = make_searcher().search("", [nope, PLACES[1]], ranker="BM25")
	assert [p["id"] for p, s in results] == ["b", "n"]
	assert results[1][1] == 0

def test_null_n_reviews():
	nope = make_place("n", "No Count", ["nothing yet"], rating=4.0)
	nope["n_reviews"] = None
	results = make_searcher().search("", [nope, PLACES[2]], ranker="BM25")
	assert results[0][0]["id"] == "c"

def test_k_limit_on_rating_path():
	results = make_searcher().search("", PLACES, ranker="BM25", k=2)
	assert len(results) == 2

def test_query_no_match():
	results = make_searcher().search("zzzz", PLACES, ranker="BM25")
	assert results == []

def test_place_without_reviews():
	# Name and categories still count as text
	empty = make_place("e", "Snorkel Shack", [])
	searcher = make_searcher()
	searcher.place_map["e"] = empty
	results = searcher.search("snorkel", [empty, PLACES[1]], ranker="BM25")
	assert [p["id"] for p, s in results] == ["e"]

def test_snippet_no_texts():
	empty = make_place("e", "Empty", [])
	searcher = make_searcher()
	searcher.place_region["e"] = "Test"
	assert searcher.best_snippet(empty, "beach") == ""

def test_snippet_cut_at_300():
	place = make_place("l", "Long", ["word " * 200])
	searcher = make_searcher()
	searcher.place_region["l"] = "Test"
	snippet = searcher.best_snippet(place, "word")
	assert len(snippet) <= 303
	assert snippet.endswith("...")

def test_snippet_cleans_translation():
	place = make_place("t", "T", ["(Translated by Google) Nice beach\n\n(Original)\n良い"])
	searcher = make_searcher()
	searcher.place_region["t"] = "Test"
	assert searcher.best_snippet(place, "beach") == "Nice beach"

def test_place_name_only_query():
	# find_loc strips the name, so the rest is empty and ratings decide
	entries = [{"name": "Waikiki", "key": "waikiki", "kind": "area", "n_places": 0}]
	entry, rest = find_loc("Waikiki", entries)
	assert rest == ""
	results = make_searcher().search(rest, PLACES, ranker="BM25")
	assert results[0][0]["id"] == "c"

def test_no_places_in_radius():
	# The radius filter finds nothing, so the search gets no candidates
	found = radius_search(PLACES, 50.0, 50.0, 10)
	assert found == []
	assert make_searcher().search("beach", [p for d, p in found], ranker="BM25") == []
