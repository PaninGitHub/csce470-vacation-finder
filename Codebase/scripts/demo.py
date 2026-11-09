import os
import sys
from dotenv import load_dotenv

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

# Import these after, as we need to run the above code first
from vacfinder.data import load_places
from vacfinder.textproc import clean, tokenize
from vacfinder.bm25 import BM25

def build_docs(places):
	docs = {}

	# Build and filter out the vectors for each doc
	for gmap_id, info in places.items():
		if len(info["texts"]) == 0:
			continue
		big_text = clean(" ".join(info["texts"]))
		docs[gmap_id] = tokenize(big_text)
	return docs

def take_first_snippet(texts, query_tokens):
	# First review that contains a query word, cut to 150 characters
	for text in texts:
		if any(t in tokenize(text) for t in query_tokens):
			return clean(text)[:250]
	return None


def main():
	# Corrects if not enough args
	if len(sys.argv) < 2:
		print('Incorrec arguments. Do this: python scripts/demo.py {query}')
		return
	query = sys.argv[1]

	load_dotenv()
	path = os.getenv("REVIEWS_PATH")
	if path is None:
		print("Set REVIEWS_PATH in the .env file")
		return
	path = os.path.join(ROOT, path)

	print("Loading reviews...")
	places = load_places(path)
	docs = build_docs(places)

	print("Building indices for the following docs. Amt: ", len(docs))
	index = BM25(docs)

	query_tokens = tokenize(query)
	results = index.search(query_tokens, k=5)

	if len(results) == 0:
		print("No results for:", query)
		return

	print("\nTop results for:", query)
	for rank, (gmap_id, score) in enumerate(results, 1):
		info = places[gmap_id]
		avg_rating = sum(info["ratings"]) / len(info["ratings"])
		print(rank, gmap_id, "score:", round(score, 2),"; avg rating:", round(avg_rating, 2), "; amt of reviews:", len(info["ratings"]))
		snippet = take_first_snippet(info["texts"], query_tokens)
		if snippet:
			print("Review Snippet: ", snippet)


if __name__ == "__main__":
	main()
