"""Dense (embedding) index over place reviews."""
import hashlib
import os

import numpy as np
from sentence_transformers import SentenceTransformer

from vacfinder.textproc import clean

class DenseIndex:
	def __init__(self, places, chunk_words=150, model_name="all-MiniLM-L6-v2", cache_path=None):
		# places: {gmap_id: {"texts": [...], "ratings": [...]}} from load_places
		# cache_path: optional .npz file to save/load the encoded chunks
		self.model = SentenceTransformer(model_name)

		# Split every place's reviews into chunks, remembering the owner of each chunk
		self.chunks = []
		self.chunk_place = []
		for gmap_id, info in places.items():
			for chunk in self.make_chunks(info["texts"], chunk_words):
				self.chunks.append(chunk)
				self.chunk_place.append(gmap_id)

		# Fingerprint of everything that affects the vectors. If the data, chunk size,
		# or model changes, the fingerprint changes and the cache gets rebuilt
		hasher = hashlib.sha256(f"{model_name}|{chunk_words}".encode("utf-8"))
		for gmap_id, chunk in zip(self.chunk_place, self.chunks):
			hasher.update(f"\n{gmap_id}\t{chunk}".encode("utf-8"))
		fingerprint = hasher.hexdigest()

		# Use the cached vectors if they were built from exactly these chunks
		if cache_path is not None and os.path.exists(cache_path):
			cached = np.load(cache_path)
			if str(cached["fingerprint"]) == fingerprint:
				self.matrix = cached["matrix"]
				return
			print("Embedding cache is out of date, rebuilding...")

		# One row per chunk, 384 numbers each. Normalized, so dot product = cosine similarity
		# This is the slow part: the model runs over every chunk
		self.matrix = self.model.encode(self.chunks, normalize_embeddings=True, show_progress_bar=True)

		if cache_path is not None:
			os.makedirs(os.path.dirname(os.path.abspath(cache_path)), exist_ok=True)
			np.savez(cache_path, matrix=self.matrix, fingerprint=np.array(fingerprint))

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
