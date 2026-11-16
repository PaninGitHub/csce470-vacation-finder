from vacfinder.textproc import clean, tokenize

CAFE = "(Translated by Google) Lovely little cafe with fresh coffee and friendly staff here.\n\n(Original)\nとても素敵なカフェです。"

def test_clean_translation():
	assert clean(CAFE) == "Lovely little cafe with fresh coffee and friendly staff here."

def test_clean_no_wrapper():
	assert clean("Great  beach") == "Great beach"

def test_clean_whitespace():
	assert clean("  a \n\n b\t c  ") == "a b c"

def test_clean_empty():
	assert clean("") == ""

def test_tokenize_cafe():
	assert tokenize(clean(CAFE)) == ["lovely", "little", "cafe", "fresh", "coffee", "friendly", "staff", "here"]

def test_tokenize_lowercase():
	assert tokenize("Beach BAR") == ["beach", "bar"]

def test_tokenize_stopwords():
	assert tokenize("the pool and the beach") == ["pool", "beach"]

def test_tokenize_digits_apostrophes():
	assert tokenize("Open 24 hours, don't miss it") == ["open", "24", "hours", "don't", "miss"]

def test_tokenize_empty():
	assert tokenize("") == []
	assert tokenize("the of and") == []
