"""Ranking metrics for the offline evaluation."""
import csv
import math

def load_judgments(path):
	# Returns {query_id: {place_id: 0/1/2}}. Rows with an empty relevance column are skipped
	judged = {}
	with open(path, newline="", encoding="utf-8") as f:
		for row in csv.DictReader(f):
			rel = row["relevance"].strip()
			if rel == "":
				continue
			if rel not in ("0", "1", "2"):
				raise ValueError("Bad relevance " + rel + " for " + row["place_id"])
			if row["query_id"] not in judged:
				judged[row["query_id"]] = {}
			judged[row["query_id"]][row["place_id"]] = int(rel)
	return judged

def precision_at_k(ranked, rels, k):
	# rels: {place_id: 0/1/2}. A place counts as relevant when it got 1 or 2
	# Places nobody judged count as not relevant
	hits = 0
	for place_id in ranked[:k]:
		if rels.get(place_id, 0) > 0:
			hits += 1
	return hits / k

def average_precision(ranked, rels, k=10):
	# Average of the precision at each relevant place in the top k,
	# divided by all relevant places that were judged for the query
	total_rel = 0
	for r in rels.values():
		if r > 0:
			total_rel += 1
	if total_rel == 0:
		return 0.0

	hits = 0
	score = 0.0
	for i, place_id in enumerate(ranked[:k], 1):
		if rels.get(place_id, 0) > 0:
			hits += 1
			score += hits / i
	return score / total_rel

def dcg(gains):
	# Rank 1 is divided by log2(2), rank 2 by log2(3), and so on
	total = 0.0
	for i, g in enumerate(gains, 1):
		total += g / math.log2(i + 1)
	return total

def ndcg_at_k(ranked, rels, k=10):
	gains = [rels.get(place_id, 0) for place_id in ranked[:k]]
	best = sorted(rels.values(), reverse=True)[:k]
	if dcg(best) == 0:
		return 0.0
	return dcg(gains) / dcg(best)
