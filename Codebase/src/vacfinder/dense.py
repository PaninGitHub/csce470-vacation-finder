"""Dense (embedding) index over place reviews."""
import numpy as np
from sentence_transformers import SentenceTransformer

from vacfinder.textproc import clean

class DenseIndex:
	def __init__(self, places, chunk_words=150, model_name="all-MiniLM-L6-v2"):
		# places: {gmap_id: {"texts": [...], "ratings": [...]}} from load_places
		self.model = SentenceTransformer(model_name)

		# Split every place's reviews into chunks, remembering the owner of each chunk
		self.chunks = []
		self.chunk_place = []
		for gmap_id, info in places.items():
			for chunk in self.make_chunks(info["texts"], chunk_words):
				self.chunks.append(chunk)
				self.chunk_place.append(gmap_id)

		# One row per chunk, 384 numbers each. Normalized, so dot product = cosine similarity
		self.matrix = self.model.encode(self.chunks, normalize_embeddings=True)

	def make_chunks(self, texts, chunk_words):
		# Pack whole reviews into chunks of at most chunk_words words.
		# The model only reads ~256 tokens (~180-200 words), so a chunk must never
		# go over chunk_words or the end of it is silently ignored.
		chunks = []
		cur_words = []
		for text in texts:
			words = clean(text).split()

			# A single review longer than the limit gets split into pieces on its own
			if len(words) > chunk_words:
				if len(cur_words) > 0:
					chunks.append(" ".join(cur_words))
					cur_words = []
				for start in range(0, len(words), chunk_words):
					chunks.append(" ".join(words[start:start + chunk_words]))
				continue

			# Close the current chunk if this review would push it over the limit
			if len(cur_words) + len(words) > chunk_words:
				chunks.append(" ".join(cur_words))
				cur_words = []
			cur_words += words

		# Leftover words become the last chunk
		if len(cur_words) > 0:
			chunks.append(" ".join(cur_words))
		return chunks

	def search(self, query, k=10):
		# Returns [(gmap_id, score), ...] sorted best-first
		q = self.model.encode([query], normalize_embeddings=True)[0]

		# Similarity of the query to every chunk in one go
		sims = self.matrix @ q

		# Group the chunk similarities by place
		place_sims = {}
		for i, sim in enumerate(sims):
			gmap_id = self.chunk_place[i]
			if gmap_id not in place_sims:
				place_sims[gmap_id] = []
			place_sims[gmap_id].append(float(sim))

		# Place score: best chunk, mixed with the average of its top 3 chunks
		scores = {}
		for gmap_id, sim_list in place_sims.items():
			sim_list.sort(reverse=True)
			best = sim_list[0]
			top3_avg = sum(sim_list[:3]) / len(sim_list[:3])
			scores[gmap_id] = 0.6 * best + 0.4 * top3_avg

		ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
		return ranked[:k]
