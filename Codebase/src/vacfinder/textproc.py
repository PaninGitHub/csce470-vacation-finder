import re

STOPWORDS = {
	"a", "an", "the",
	"and", "but", "or", "for", "nor", "so", "yet",
	"in", "on", "at", "with", "by", "from", "about", "to", "of",
	"i", "you", "he", "she", "it", "we", "they", "me", "him", "her",
	"us", "them", "my", "your", "his", "its", "our", "their",
	"is", "am", "are", "was", "were", "be", "been", "being",
	"have", "has", "had", "do", "does", "did", "can", "will", "should",
}

def clean(text):
	# Remove any original text from foreign languages and only keep the Google ones
	if "(Original)" in text:
		text = text.split("(Original)")[0]
	text = text.replace("(Translated by Google)", "")

	return " ".join(text.split())


def tokenize(text):
	# Lowercase and grab letters and digits
	words = re.findall(r"[a-z0-9']+", text.lower())
	return [w for w in words if w not in STOPWORDS]
