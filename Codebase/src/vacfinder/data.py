"""Load raw Google Local reviews and group them into one record per place."""
import json

#Returns {gmap_id: {"texts": [...], "ratings": [...]}}.
def load_places(path, min_words=5):
	doc_map = {}

	with open(path, encoding="utf-8") as f:
		for row in f:
			# Load JSON
			r = json.loads(row)
			place = r["gmap_id"]

			# Format doc_map
			if place not in doc_map:
				doc_map[place] = {"texts": [], "ratings": []}
			doc_map[place]["ratings"].append(r["rating"])

			# Check for empty/short text:
			text = r.get("text")
			if text is None:
				continue
			if(len(text.split()) < min_words):
				continue

			# Keep the raw text
			doc_map[place]["texts"].append(text)

	return doc_map
