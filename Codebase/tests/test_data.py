import json

from vacfinder.data import load_places

PATH = "tests/fixtures/mini.jsonl"

def test_place_count():
	assert len(load_places(PATH)) == 6

def test_kept_texts():
	places = load_places(PATH)
	assert len(places["pool_resort"]["texts"]) == 2
	assert places["pool_resort"]["ratings"] == [5, 4, 5, 3]

def test_no_text_place():
	place = load_places(PATH)["no_text_place"]
	assert place["texts"] == []
	assert place["ratings"] == [1, 4]

def test_short_and_null_keep_rating():
	# "Nice pool" is too short and one text is null, but all four ratings stay
	place = load_places(PATH)["pool_resort"]
	assert "Nice pool" not in place["texts"]
	assert len(place["ratings"]) == 4

def test_texts_are_raw():
	# Cleaning happens later, the loader keeps the original text
	place = load_places(PATH)["cafe"]
	assert "(Translated by Google)" in place["texts"][0]

def test_min_words(tmp_path):
	path = tmp_path / "r.jsonl"
	path.write_text(json.dumps({"gmap_id": "x", "rating": 5, "text": "one two three"}) + "\n")
	assert load_places(str(path), min_words=3)["x"]["texts"] == ["one two three"]
	assert load_places(str(path), min_words=4)["x"]["texts"] == []

def test_missing_text_key(tmp_path):
	path = tmp_path / "r.jsonl"
	path.write_text(json.dumps({"gmap_id": "x", "rating": 2}) + "\n")
	place = load_places(str(path))["x"]
	assert place["texts"] == []
	assert place["ratings"] == [2]
