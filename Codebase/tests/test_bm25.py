import pytest

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

def test_repeated_query_word_counts_once():
	index = BM25({"A": ["pool", "beach"], "B": ["bar"]})
	assert index.search(["pool", "pool", "pool"]) == index.search(["pool"])

def test_empty_token_document():
	# A has no tokens, it just never matches
	index = BM25({"A": [], "B": ["pool"]})
	assert [g for g, s in index.search(["pool"])] == ["B"]

def test_all_documents_empty():
	index = BM25({"A": [], "B": []})
	assert index.search(["pool"]) == []

def test_empty_query():
	assert BM25({"A": ["pool"]}).search([]) == []

def test_known_and_unknown_terms():
	index = BM25({"A": ["pool"], "B": ["bar"]})
	assert [g for g, s in index.search(["pool", "zzz"])] == ["A"]

def test_k_limits_results():
	index = BM25({"A": ["pool"], "B": ["pool"], "C": ["pool"]})
	assert len(index.search(["pool"], k=2)) == 2

def test_more_matching_terms_wins():
	index = BM25({"A": ["pool", "beach"], "B": ["pool", "bar"], "C": ["pool", "pool"]})
	assert index.search(["pool", "beach"])[0][0] == "A"

def test_no_documents():
	with pytest.raises(ValueError):
		BM25({})
