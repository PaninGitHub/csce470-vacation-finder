from vacfinder.hybrid import fuse

def test_both_list():
	bm25 = [("B", 9.0), ("A", 5.0), ("C", 1.0)]
	dense = [("D", 0.9), ("B", 0.8), ("E", 0.1)]
	results = fuse([bm25, dense])
	assert results[0][0] == "B"

def test_either_list():
	results = fuse([[("A", 1.0)], [("B", 1.0)]])
	assert {g for g, s in results} == {"A", "B"}

def test_empty_lists():
	assert fuse([[], []]) == []
