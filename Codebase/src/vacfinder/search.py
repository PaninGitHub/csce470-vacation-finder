import os

from vacfinder.textproc import clean, tokenize
from vacfinder.bm25 import BM25
from vacfinder.dense import DenseIndex
from vacfinder.hybrid import fuse
from vacfinder.places import load_region

RANKERS = ["BM25", "Dense", "Hybrid"]

class Searcher:
	def __init__(self, final_dir, cache_dir, model):
		self.final_dir = final_dir
		self.cache_dir = cache_dir
		self.model = model

		# Filled in by get_places, one region at a time
		self.regions = {}
		self.place_map = {}
		self.place_region = {}
		self.tokens = {}
		self.dense_indexes = {}

	def get_places(self, region):
		# Loads a region file the first time it is asked for
		if region not in self.regions:
			self.regions[region] = load_region(self.final_dir, region)
			for p in self.regions[region]:
				self.place_map[p["id"]] = p
				self.place_region[p["id"]] = region
		return self.regions[region]

	def get_tokens(self, place):
		# Name, categories and reviews all count, tokenized once per place
		if place["id"] not in self.tokens:
			text = place["name"] + " " + " ".join(place["categories"]) + " " + " ".join(place["texts"])
			self.tokens[place["id"]] = tokenize(clean(text))
		return self.tokens[place["id"]]

	def get_dense(self, region):
		# Built the first time a region is needed, later loads come from cache/
		if region not in self.dense_indexes:
			docs = {}
			for p in self.get_places(region):
				docs[p["id"]] = {"texts": p["texts"], "ratings": []}
			cache_path = os.path.join(self.cache_dir, region + "_dense.npz")
			self.dense_indexes[region] = DenseIndex(docs, cache_path=cache_path, model=self.model)
		return self.dense_indexes[region]

	def search(self, query, candidates, ranker="Hybrid", k=20):
		# candidates: list of place dicts. Returns [(place, score)] best first
		if len(candidates) == 0:
			return []

		# With only a place name in the query there is nothing to match, so use the ratings
		query_tokens = tokenize(query)
		if len(query_tokens) == 0:
			ranked = sorted(candidates, key=lambda p: (p["avg_rating"] or 0, p["n_reviews"] or 0), reverse=True)
			return [(p, p["avg_rating"] or 0) for p in ranked[:k]]

		results = []
		if ranker == "BM25":
			results = self.bm25_results(query_tokens, candidates, k)
		elif ranker == "Dense":
			results = self.dense_results(query, candidates, k)
		else:
			bm25_list = self.bm25_results(query_tokens, candidates, 100)
			dense_list = self.dense_results(query, candidates, 100)
			results = fuse([bm25_list, dense_list])[:k]

		return [(self.place_map[gmap_id], score) for gmap_id, score in results]

	def bm25_results(self, query_tokens, candidates, k):
		# IDF is computed over the candidates only
		docs = {}
		for p in candidates:
			docs[p["id"]] = self.get_tokens(p)
		return BM25(docs).search(query_tokens, k=k)

	def dense_results(self, query, candidates, k):
		# Each region has its own index, so score each one and merge the lists
		by_region = {}
		for p in candidates:
			region = self.place_region[p["id"]]
			if region not in by_region:
				by_region[region] = []
			by_region[region].append(p["id"])

		results = []
		for region, ids in by_region.items():
			results += self.get_dense(region).search(query, k=k, candidates=ids)
		results.sort(key=lambda x: x[1], reverse=True)
		return results[:k]

	def best_snippet(self, place, query):
		# Review with the most query words in it, or the closest chunk if none match
		query_tokens = set(tokenize(query))
		best_text = None
		best_count = 0
		for text in place["texts"]:
			count = len(query_tokens & set(tokenize(clean(text))))
			if count > best_count:
				best_count = count
				best_text = text

		if best_text is None:
			dense = self.dense_indexes.get(self.place_region[place["id"]])
			if dense is not None and place["id"] in getattr(dense, "best_chunk", {}):
				best_text = dense.best_chunk[place["id"]]
			elif len(place["texts"]) > 0:
				best_text = place["texts"][0]
			else:
				return ""

		text = clean(best_text)
		if len(text) > 300:
			text = text[:300].rsplit(" ", 1)[0] + "..."
		return text
