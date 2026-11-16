import os
import sys
from dotenv import load_dotenv

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from vacfinder.places import list_regions
from vacfinder.search import Searcher

def main():
	load_dotenv(os.path.join(ROOT, ".env"))
	places_dir = os.path.join(ROOT, os.getenv("PLACES_DIR", "../Docs/AI Stuff/Data Trim Plan/final"))

	# Optional: only build the regions named on the command line
	names = sys.argv[1:]
	if len(names) == 0:
		names = list_regions(places_dir)

	# Imports model used for computing embeddings
	from sentence_transformers import SentenceTransformer
	model = SentenceTransformer("all-MiniLM-L6-v2")

	searcher = Searcher(places_dir, os.path.join(ROOT, "cache"), model)

	for name in names:
		print("Building dense index for", name)
		searcher.get_dense(name)

if __name__ == "__main__":
	main()
