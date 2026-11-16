"""Build the pool of places for people to judge.

Runs every query through the same Searcher the app uses, takes the top 10 of
each ranker and joins them. Writes pools/judgments_template.csv and pools/rankings.json.
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from vacfinder.geo import load_gazetteer, find_loc, radius_search
from vacfinder.search import Searcher, RANKERS

TOP_K = 10
RADIUS_KM = 25
STATES = ["Hawaii", "Alaska", "Nevada", "Utah", "Colorado"]

def get_candidates(searcher, entry):
	# Same as the app: every place in the state, or the places within the radius
	region = entry["region"].replace(" ", "_")
	places = searcher.get_places(region)
	if entry["kind"] == "state":
		return places
	found = radius_search(places, entry["lat"], entry["lon"], RADIUS_KM)
	return [p for d, p in found]

def run_query(searcher, entries, query):
	# Returns {ranker: [place ids]} for one query
	entry, rest = find_loc(query["text"], entries)
	if entry is None:
		print("No place name found in", query["id"], query["text"])
		return {}
	candidates = get_candidates(searcher, entry)
	print(query["id"], query["text"], "->", entry["name"], len(candidates), "places, rest:", rest)

	lists = {}
	for ranker in RANKERS:
		results = searcher.search(rest, candidates, ranker=ranker, k=TOP_K)
		lists[ranker] = [p["id"] for p, score in results]
	return lists

def write_template(path, queries, rankings, searcher):
	with open(path, "w", newline="", encoding="utf-8") as f:
		w = csv.writer(f)
		w.writerow(["query_id", "query", "place_id", "place name", "group", "city", "systems", "ranks", "relevance"])

		for q in queries:
			# For each place: which rankers returned it and at what rank
			seen = {}
			for ranker in RANKERS:
				for rank, place_id in enumerate(rankings[ranker].get(q["id"], []), 1):
					if place_id not in seen:
						seen[place_id] = {}
					seen[place_id][ranker] = rank

			# Best rank first, so the likely good ones are at the top of each query
			order = sorted(seen.items(), key=lambda x: (min(x[1].values()), x[0]))
			for place_id, ranks in order:
				p = searcher.place_map[place_id]
				systems = " ".join(r for r in RANKERS if r in ranks)
				rank_text = " ".join(r + ":" + str(ranks[r]) for r in RANKERS if r in ranks)
				w.writerow([q["id"], q["text"], place_id, p["name"], p["group"], p["city"], systems, rank_text, ""])

def main():
	from dotenv import load_dotenv
	from sentence_transformers import SentenceTransformer

	load_dotenv(os.path.join(ROOT, ".env"))
	places_dir = os.path.join(ROOT, os.getenv("PLACES_DIR", "../Docs/AI Stuff/Data Trim Plan/final"))

	with open(os.path.join(HERE, "queries.json"), encoding="utf-8") as f:
		queries = json.load(f)

	model = SentenceTransformer("all-MiniLM-L6-v2")
	searcher = Searcher(places_dir, os.path.join(ROOT, "cache"), model)
	entries = load_gazetteer(places_dir)

	# Load the states up front, so a state outside the list shows up as an error
	for name in STATES:
		searcher.get_places(name)

	rankings = {}
	for ranker in RANKERS:
		rankings[ranker] = {}
	for q in queries:
		lists = run_query(searcher, entries, q)
		for ranker in lists:
			rankings[ranker][q["id"]] = lists[ranker]

	out_dir = os.path.join(HERE, "pools")
	os.makedirs(out_dir, exist_ok=True)
	with open(os.path.join(out_dir, "rankings.json"), "w", encoding="utf-8") as f:
		json.dump(rankings, f, indent=1)
	write_template(os.path.join(out_dir, "judgments_template.csv"), queries, rankings, searcher)

if __name__ == "__main__":
	main()
