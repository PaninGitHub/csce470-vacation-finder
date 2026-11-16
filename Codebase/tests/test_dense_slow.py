import pytest

from vacfinder.data import load_places
from vacfinder.dense import DenseIndex

# Loads the real embedding model, so it is skipped unless run with -m slow
pytestmark = pytest.mark.slow

def test_quiet_beats_bar():
	places = load_places("tests/fixtures/mini.jsonl")
	index = DenseIndex(places)
	ids = [g for g, s in index.search("serene oceanside hideaway")]
	assert ids.index("quiet_beach") < ids.index("night_bar")

def test_candidates_limit_results():
	places = load_places("tests/fixtures/mini.jsonl")
	index = DenseIndex(places)
	results = index.search("glacier cruise", candidates=["night_bar", "glacier_tour"])
	assert [g for g, s in results][0] == "glacier_tour"
	assert len(results) == 2
