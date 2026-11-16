import csv
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from eval.metrics import precision_at_k, average_precision, ndcg_at_k, load_judgments

# a and c are relevant, b is not, d is highly relevant but was not returned
RELS = {"a": 1, "b": 0, "c": 2, "d": 2}
RANKED = ["a", "b", "c", "x"]

def test_precision_at_k():
	# top 1: a is relevant -> 1/1. top 3: a and c -> 2/3
	assert precision_at_k(RANKED, RELS, 1) == 1.0
	assert math.isclose(precision_at_k(RANKED, RELS, 3), 2 / 3)

def test_precision_unjudged_counts_as_not_relevant():
	# x was never judged, so top 4 still has only a and c
	assert precision_at_k(RANKED, RELS, 4) == 0.5

def test_average_precision():
	# hits at rank 1 (1/1) and rank 3 (2/3), three relevant places in total (a, c, d)
	expected = (1 + 2 / 3) / 3
	assert math.isclose(average_precision(RANKED, RELS), expected)

def test_average_precision_no_relevant():
	assert average_precision(["a", "b"], {"a": 0, "b": 0}) == 0.0

def test_ndcg_perfect_order():
	# c and d (2) first, then a (1)
	assert math.isclose(ndcg_at_k(["c", "d", "a", "b"], RELS), 1.0)

def test_ndcg_hand_computed():
	# gains in rank order: 1, 0, 2 -> 1/1 + 0/log2(3) + 2/log2(4) = 2.0
	# ideal order: 2, 2, 1 -> 2/1 + 2/log2(3) + 1/2
	dcg = 2.0
	ideal = 2 + 2 / math.log2(3) + 0.5
	assert math.isclose(ndcg_at_k(RANKED, RELS), dcg / ideal)

def test_ndcg_nothing_relevant():
	assert ndcg_at_k(["a"], {"a": 0}) == 0.0

def test_load_judgments_skips_blank(tmp_path):
	path = tmp_path / "j.csv"
	with open(path, "w", newline="") as f:
		w = csv.writer(f)
		w.writerow(["query_id", "place_id", "relevance"])
		w.writerow(["q01", "a", "2"])
		w.writerow(["q01", "b", ""])
		w.writerow(["q02", "c", "0"])
	judged = load_judgments(str(path))
	assert judged == {"q01": {"a": 2}, "q02": {"c": 0}}
