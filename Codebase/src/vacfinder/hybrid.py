from vacfinder.textproc import tokenize

def fuse(result_lists, k=60):
	fused = {}
	for results in result_lists:
		# Only rank matters, so og scoresare ignored
		for rank, (gmap_id, _) in enumerate(results, 1):
			fused[gmap_id] = fused.get(gmap_id, 0.0) + 1 / (k + rank)

	return sorted(fused.items(), key=lambda x: x[1], reverse=True)

def hybrid_search(bm25_index, dense_index, query, k=10, pool=100):
	bm25_results = bm25_index.search(tokenize(query), k=pool)
	dense_results = dense_index.search(query, k=pool)
	return fuse([bm25_results, dense_results])[:k]
