from vacfinder.bm25 import BM25

def test_ranks_by_term_frequency():
	docs = {"A": ["pool", "beach"], "B": ["bar", "music"], "C": ["pool", "pool", "pool"]}
	index = BM25(docs)
	results = index.search(["pool"])
	assert [g for g, s in results] == ["C", "A"]

def test_unknown_term():
	index = BM25({"A": ["pool"]})
	assert index.search(["zzz"]) == []
