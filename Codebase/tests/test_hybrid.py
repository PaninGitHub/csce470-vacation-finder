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

def test_single_list_score():
	assert fuse([[("A", 3.0)]]) == [("A", 1 / 61)]

def test_empty_input():
	assert fuse([]) == []

def test_tie_keeps_first_list_order():
	# A and B are both rank 1 in one list, same score, so A stays ahead
	results = fuse([[("A", 1.0)], [("B", 1.0)]])
	assert [g for g, s in results] == ["A", "B"]

def test_both_lists_beats_one():
	results = fuse([[("A", 1.0), ("B", 0.5)], [("C", 1.0), ("B", 0.5)]])
	assert results[0][0] == "B"

def test_one_list_only_place_kept():
	results = fuse([[("A", 1.0), ("B", 0.5)], [("A", 1.0)]])
	assert [g for g, s in results] == ["A", "B"]

def test_raw_scores_ignored():
	big = fuse([[("A", 1000.0), ("B", 1.0)]])
	small = fuse([[("A", 0.2), ("B", 0.1)]])
	assert big == small
