"""Print Precision@K, MAP and NDCG@10 per system and per query type.

Usage: python eval/run_eval.py [judgments.csv]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from metrics import load_judgments, precision_at_k, average_precision, ndcg_at_k

SYSTEMS = ["BM25", "Dense", "Hybrid"]
COLUMNS = ["P@1", "P@5", "P@10", "MAP", "NDCG@10"]

def score_query(ranked, rels):
	return [
		precision_at_k(ranked, rels, 1),
		precision_at_k(ranked, rels, 5),
		precision_at_k(ranked, rels, 10),
		average_precision(ranked, rels, 10),
		ndcg_at_k(ranked, rels, 10),
	]

def average(rows):
	return [sum(r[i] for r in rows) / len(rows) for i in range(len(COLUMNS))]

def print_table(title, scores):
	# scores: {system: [row per query]}
	print()
	print(title)
	print("%-8s" % "system" + "".join("%9s" % c for c in COLUMNS))
	for system in SYSTEMS:
		if len(scores[system]) == 0:
			continue
		print("%-8s" % system + "".join("%9.3f" % v for v in average(scores[system])))

def main():
	path = os.path.join(HERE, "pools", "judgments.csv")
	if len(sys.argv) > 1:
		path = sys.argv[1]

	judged = load_judgments(path)
	with open(os.path.join(HERE, "pools", "rankings.json"), encoding="utf-8") as f:
		rankings = json.load(f)
	with open(os.path.join(HERE, "queries.json"), encoding="utf-8") as f:
		queries = json.load(f)

	# Only queries that have judgments count
	queries = [q for q in queries if q["id"] in judged]
	print(len(queries), "queries with judgments")

	by_type = {}
	overall = {}
	for system in SYSTEMS:
		overall[system] = []
	for q in queries:
		if q["type"] not in by_type:
			by_type[q["type"]] = {}
			for system in SYSTEMS:
				by_type[q["type"]][system] = []
		for system in SYSTEMS:
			ranked = rankings[system].get(q["id"], [])
			row = score_query(ranked, judged[q["id"]])
			overall[system].append(row)
			by_type[q["type"]][system].append(row)

	print_table("All queries", overall)
	for t in sorted(by_type):
		print_table("Type: " + t + " (" + str(len(by_type[t]["BM25"])) + " queries)", by_type[t])

if __name__ == "__main__":
	main()
