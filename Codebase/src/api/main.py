import os
import sys
import threading
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))

from vacfinder.geo import load_gazetteer, find_loc, find_distance_sphere, radius_search
from vacfinder.places import list_regions, split_regions
from vacfinder.search import Searcher, RANKERS
from vacfinder.textproc import tokenize
from vacfinder.travel import TRAVEL_MODES, entries_for_mode, is_misfit, other_mode, does_rating_qualify, rating_line

# Groups for different types of places
GROUPS = {
	"LODGING": "Lodging",
	"THINGS_TO_DO": "Activities",
	"FOOD_DRINK": "Dining",
	"SHOPPING": "Shopping"
}

# Type of travel to be used
TRAVEL = {
	"domestic": TRAVEL_MODES[0],
	"international": TRAVEL_MODES[1],
	"anywhere": TRAVEL_MODES[2]
}

load_dotenv(os.path.join(ROOT, ".env"))

# Local dev origins plus any comma-separated ones in CORS_ORIGINS
ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
ORIGINS += [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip() != ""]

app = FastAPI(title = "Vacation Finder API")
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
	allow_methods=["GET"],
	allow_headers=["*"],
)

# Loads embedding on first encode. This makes sure BM25 searches don't touch the torch library
class EmbeddingModel:
	def __init__(self):
		self.model = None

	def encode(self, *args, **kwargs):
		if self.model is None:
			from sentence_transformers import SentenceTransformer
			self.model = SentenceTransformer("all-MiniLM-L6-v2")
		return self.model.encode(*args, **kwargs)

# One shared model, so the warm-up and the searches use the same one
EMBEDDER = EmbeddingModel()

# Loads the embedding model in the background at startup s.t. the first dense/hybrid search isn't slow
# Set WARMUP=0 to skip. Any failure (torch not installed, etc.) is ignored
def warm_model():
	try:
		EMBEDDER.encode(["warm up"])
	except Exception:
		pass

@app.on_event("startup")
def start_warmup():
	if os.getenv("WARMUP", "1") == "0":
		return
	threading.Thread(target=warm_model, daemon=True).start()

class Context:
	def __init__(self, places_dir, cache_dir, model):
		self.places_dir = places_dir
		self.available = list_regions(places_dir)
		self.states, self.countries = split_regions(places_dir, self.available)
		self.entries = load_gazetteer(places_dir)
		self.searcher = Searcher(places_dir, cache_dir, model)

@lru_cache(maxsize=1) # Least Recently Used cache.
def get_context():
	places_dir = os.path.join(ROOT, os.getenv("PLACES_DIR", "../Docs/AI Stuff/Data Trim Plan/final"))
	cache_dir = os.path.join(ROOT, os.getenv("CACHE_DIR", "cache"))
	return Context(places_dir, cache_dir, EMBEDDER)


def empty_reply(note, location=None, suggest=None):
	return {"results": [], "location": location, "total": 0, "note": note, "suggest_travel": suggest}


def location_json(entry):
	return {
		"name": entry["name"], "region": entry["region"], "country": entry["country"],
		"kind": entry["kind"], "lat": entry["lat"], "lon": entry["lon"],
	}

# Gathers places within raidus of the named location, or every place in it if the name is a state or country
def get_candidates(searcher, entry, radius_km, region):
	places = searcher.get_places(region)
	if entry["kind"] in ["state", "country"]:
		return [(None, p) for p in places]
	return radius_search(places, entry["lat"], entry["lon"], radius_km)

def place_json(searcher, place, distance, query):
	return {
		"id": place["id"],
		"name": place["name"],
		"group": place["group"],
		"group_label": GROUPS.get(place["group"], place["group"]),
		"categories": place["categories"][:2],
		"address": place["address"] or "",
		"avg_rating": place["avg_rating"],
		"n_reviews": place["n_reviews"],
		"price_text": place.get("price_text"),
		"distance_km": None if distance is None else round(distance, 1),
		"info_line": rating_line(place, distance),
		"snippet": searcher.best_snippet(place, query),
		"lat": place["lat"],
		"lon": place["lon"],
	}


def pick_region(ctx, entry, state, country):
	region = entry["region"].replace(" ", "_")
	if entry["country"] == "US" and state != "":
		region = state
	if region not in ctx.available:
		return None, "Found " + entry["name"] + ", but " + region.replace("_", " ") + " is not loaded yet."
	if country != "" and region != country:
		return None, entry["name"] + " is in " + entry["region"] + ", which is not the country you picked."
	return region, ""


# Answers without loading any data, for Docker and tunnel health checks
@app.get("/api/health")
def health():
	return {"status": "ok"}


@app.get("/api/options")
def options(ctx: Context = Depends(get_context)):
	return {
		"states": ctx.states,
		"countries": ctx.countries,
		"groups": [{"value": k, "label": v} for k, v in GROUPS.items()],
		"rankers": RANKERS,
		"travel": list(TRAVEL.keys()),
	}


@app.get("/api/search")
def search(
	q: str = "",
	radius_km: float = Query(25, gt=0, le=500),
	ranker: Literal["BM25", "Dense", "Hybrid"] = "Hybrid",
	travel: Literal["domestic", "international", "anywhere"] = "anywhere",
	group: str = "",
	min_rating: float = Query(0, ge=0, le=5),
	country: str = "",
	state: str = "",
	k: int = Query(20, ge=1, le=50),
	per_group: int = Query(0, ge=0, le=20),
	lat: float | None = None,
	lon: float | None = None,
	ctx: Context = Depends(get_context),
):
	mode = TRAVEL[travel]
	# Checks if coordinates are given and in range
	is_coord_valid = lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180
	if q.strip() == "" and not is_coord_valid:
		return empty_reply("Type a query to get started.")

	# Only look for place names that fit the travel choice first
	entry, rest = find_loc(q, entries_for_mode(ctx.entries, mode))
	other, other_rest = find_loc(q, ctx.entries)
	if is_coord_valid:
		# Search around the point. The nearest city gives it a region and country
		near = min([e for e in ctx.entries if e["kind"] == "city"], key=lambda e: find_distance_sphere(lat, lon, e["lat"], e["lon"]))
		entry = {"name": "Your location", "key": "", "kind": "point", "region": near["region"], "country": near["country"], "lat": lat, "lon": lon, "n_places": 0}
		rest, other = q, near
	if is_misfit(entry, other, mode, len(other_rest) < len(rest)):
		note = other["name"] + " is in " + other["region"] + ", which does not fit \"" + mode + "\"."
		return empty_reply(note, suggest=other_mode(other["country"]).split(" ")[0].lower())

	# If no place name in the query, fall back to the state or country choice
	if entry is None:
		name = country if mode == "International" else state
		if name == "" or name not in ctx.available:
			return empty_reply("I could not find a place name in that query. Add a city or area to it, or pick a state or country.")
		found = [(None, p) for p in ctx.searcher.get_places(name)]
		rest = q
		location = None
	else:
		picked = country if mode == "International" else ""
		state_pick = state if mode != "International" else ""
		region, note = pick_region(ctx, entry, state_pick, picked)
		if region is None:
			return empty_reply(note, location_json(entry))
		found = get_candidates(ctx.searcher, entry, radius_km, region)
		location = location_json(entry)

	groups = [g for g in group.split(",") if g != ""]
	found = [(d, p) for d, p in found if len(groups) == 0 or p["group"] in groups]
	found = [(d, p) for d, p in found if does_rating_qualify(p, min_rating)]
	if len(found) == 0:
		return empty_reply("No places match. Try a bigger radius or fewer filters.", location)

	distance_map = {p["id"]: d for d, p in found}
	results = ctx.searcher.search(rest, [p for d, p in found], ranker=ranker, k=200 if per_group > 0 else k)
	if len(results) == 0:
		return empty_reply("None of the " + str(len(found)) + " nearby places mention that. Try different words or the Dense ranker.", location)

	# Drop repeats of the same name and address, keeping the best ranked
	seen = set()
	unique = []
	for p, s in results:
		key = (p["name"], p["address"])
		if key not in seen:
			seen.add(key)
			unique.append((p, s))
	results = unique

	# Keep the best per_group places of each group, in rank order.
	if per_group > 0:
		counts = {}
		kept = []
		for p, s in results:
			counts[p["group"]] = counts.get(p["group"], 0) + 1
			if counts[p["group"]] <= per_group:
				kept.append((p, s))
		results = kept

	# Warn when no place mentions any query word
	note = ""
	query_tokens = set(tokenize(rest))
	if query_tokens and not any(query_tokens & set(ctx.searcher.get_tokens(p)) for d, p in found):
		note = "No place mentions those words. Showing the closest matches."

	return {
		"results": [place_json(ctx.searcher, p, distance_map[p["id"]], rest) for p, s in results],
		"location": location,
		"total": len(found),
		"note": note,
		"suggest_travel": None,
	}
