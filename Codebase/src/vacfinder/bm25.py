"""BM25 index over place documents."""
import math
import heapq

class BM25:
	def __init__(self, docs, k1=1.2, b=0.75):
		# docs: {gmap_id: [tokens]}
		if not docs:
			raise ValueError("Can't build index with zero documents")

		self.k1 = k1
		self.b = b
		self.doc_len = {}
		self.postings = {}

		# Count how many times each term shows up in each place
		for gmap_id, tokens in docs.items():
			self.doc_len[gmap_id] = len(tokens)
			for t in tokens:
				if t not in self.postings:
					self.postings[t] = {}
				self.postings[t][gmap_id] = self.postings[t].get(gmap_id, 0) + 1

		self.total_docs = len(docs)
		self.avg_len = sum(self.doc_len.values()) / self.total_docs

	def idf(self, term):
		# Uses smoothed IDF for purposes of project
		df = len(self.postings[term])
		return math.log(1 + (self.total_docs - df + 0.5) / (df + 0.5))

	def search(self, query_tokens, k=10):
		scores = {}

		for term in set(query_tokens):
			if term not in self.postings:
				continue
			idf = self.idf(term)

			# Only visit places that actually contain the term
			for gmap_id, tf in self.postings[term].items():

				# Length normalization
				norm_tf = tf / ((1 - self.b) + self.b * self.doc_len[gmap_id] / self.avg_len)
				cur_score = norm_tf * (self.k1 + 1) / (norm_tf + self.k1) * idf
				scores[gmap_id] = scores.get(gmap_id, 0.0) + cur_score

		# Returns the list of results based on scoring
		return heapq.nlargest(k, scores.items(), key=lambda x: x[1])
