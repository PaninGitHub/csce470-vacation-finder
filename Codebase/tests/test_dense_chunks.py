from vacfinder.dense import DenseIndex

def words(n, word="w"):
	return " ".join([word] * n)

def test_never_over_limit():
	texts = [words(40), words(70), words(5), words(130), words(30)]
	for chunk in DenseIndex.make_chunks(texts, 50):
		assert len(chunk.split()) <= 50

def test_long_review_is_split():
	chunks = DenseIndex.make_chunks([words(120)], 50)
	assert [len(c.split()) for c in chunks] == [50, 50, 20]

def test_short_reviews_stay_together():
	chunks = DenseIndex.make_chunks([words(10, "a"), words(10, "b")], 50)
	assert chunks == [words(10, "a") + " " + words(10, "b")]

def test_whole_review_moves_to_next_chunk():
	# 30 + 30 does not fit in 50, so the second review starts a new chunk
	chunks = DenseIndex.make_chunks([words(30, "a"), words(30, "b")], 50)
	assert chunks == [words(30, "a"), words(30, "b")]

def test_leftover_is_last_chunk():
	chunks = DenseIndex.make_chunks([words(30, "a"), words(30, "b"), words(10, "c")], 50)
	assert chunks[-1] == words(30, "b") + " " + words(10, "c")

def test_long_review_flushes_current():
	chunks = DenseIndex.make_chunks([words(10, "a"), words(60, "b")], 50)
	assert chunks[0] == words(10, "a")
	assert len(chunks) == 3

def test_exact_limit():
	assert len(DenseIndex.make_chunks([words(50)], 50)) == 1

def test_cleans_text():
	chunks = DenseIndex.make_chunks(["(Translated by Google) nice\n\nbeach (Original) 海"], 50)
	assert chunks == ["nice beach"]

def test_no_texts():
	assert DenseIndex.make_chunks([], 50) == []
