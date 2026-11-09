from vacfinder.bm25 import BM25
from vacfinder.data import load_places

def test_groups_by_place():
	places = load_places("tests/fixtures/mini.jsonl")
	print(places.keys())
	assert len(places) == 6

def test_ranks_by_term_frequency():
	docs = {"A": ["pool", "beach"], "B": ["bar", "music"], "C": ["pool", "pool", "pool"]}
	index = BM25(docs)
	results = index.search(["pool"])
	assert [g for g, s in results] == ["C", "A"]

def test_unknown_term():
	index = BM25({"A": ["pool"]})
	assert index.search(["zzz"]) == []
