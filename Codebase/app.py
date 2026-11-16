import os
import sys
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))

from vacfinder.geo import load_gazetteer, find_loc, radius_search
from vacfinder.places import list_regions, split_regions
from vacfinder.search import Searcher, RANKERS
from vacfinder.travel import TRAVEL_MODES, entries_for_mode, is_misfit, other_mode, does_rating_qualify, rating_line

GROUP_NAMES = {
	"LODGING": "Lodging",
	"THINGS_TO_DO": "Things to do",
	"FOOD_DRINK": "Food and drink",
	"SHOPPING": "Shopping",
}

load_dotenv(os.path.join(ROOT, ".env"))
PLACES_DIR = os.path.join(ROOT, os.getenv("PLACES_DIR", "../Docs/AI Stuff/Data Trim Plan/final"))

st.set_page_config(page_title="Vacation Finder", layout="wide")


@st.cache_resource
def load_searcher():
	from sentence_transformers import SentenceTransformer
	model = SentenceTransformer("all-MiniLM-L6-v2")
	return Searcher(PLACES_DIR, os.path.join(ROOT, "cache"), model)


@st.cache_resource
def load_entries():
	return load_gazetteer(PLACES_DIR)


@st.cache_resource
def load_regions():
	# Returns (US states, countries) that have a finished file
	return split_regions(PLACES_DIR, list_regions(PLACES_DIR))


def switch_mode(mode):
	st.session_state["mode"] = mode


def get_candidates(searcher, location, radius_km, region_names):
	# Places near the named location, or every place in it if the name is a state or country
	all_places = []
	for name in region_names:
		all_places += searcher.get_places(name)

	if location["kind"] in ["state", "country"]:
		return [(None, p) for p in all_places]
	return radius_search(all_places, location["lat"], location["lon"], radius_km)


def show_card(searcher, place, distance, query):
	with st.container(border=True):
		st.subheader(place["name"])
		category = ", ".join(place["categories"][:2])
		st.caption(GROUP_NAMES.get(place["group"], place["group"]) + " | " + category)
		if place["address"]:
			st.write(place["address"])

		line = rating_line(place, distance)
		if line != "":
			st.write(line)

		snippet = searcher.best_snippet(place, query)
		if snippet != "":
			st.markdown("> " + snippet.replace("\n", " "))



def main():
	st.title("Vacation Finder")
	st.write("Search places by what their reviews say. Try a place name plus what you want to do.")

	available = list_regions(PLACES_DIR)
	if len(available) == 0:
		st.error("No places found in " + PLACES_DIR + ". Check PLACES_DIR in .env.")
		return

	states, countries = load_regions()

	# Sidebar
	st.sidebar.header("Filters")
	ranker = st.sidebar.radio("Ranker", RANKERS, index=2)
	radius_km = st.sidebar.slider("Radius (km)", 1, 200, 25)
	groups = st.sidebar.multiselect("Category", list(GROUP_NAMES.keys()), format_func=lambda g: GROUP_NAMES[g])
	min_rating = st.sidebar.slider("Minimum rating", 0.0, 5.0, 0.0, 0.5)

	mode = st.sidebar.radio("Where are you travelling", TRAVEL_MODES, index=2, key="mode")
	state = "All states"
	picked = []
	if mode == "International":
		picked = st.sidebar.multiselect("Country", countries)
	else:
		state = st.sidebar.selectbox("State", ["All states"] + states, format_func=lambda s: s.replace("_", " "))

	query = st.text_input("Search", placeholder="beach resort in Waikiki, temples in Kyoto, pizza in Florence, ...")
	if query.strip() == "":
		st.info("Type a query above to get started.")
		return

	searcher = load_searcher()
	entries = load_entries()

	# Only look for place names that fit the travel choice first
	location, rest = find_loc(query, entries_for_mode(entries, mode))
	other, other_rest = find_loc(query, entries)
	if is_misfit(location, other, mode):
		new_mode = other_mode(other["country"])
		st.warning(other["name"] + " is in " + other["region"] + ", which does not fit \"" + mode + "\".")
		st.button("Switch to " + new_mode, on_click=switch_mode, args=(new_mode,))
		return

	# No place name in the query: fall back to the state or country selector
	if location is None:
		names = picked
		if mode != "International" and state != "All states":
			names = [state]
		if len(names) == 0:
			st.warning("I could not find a place name in that query. Add a city or area to it, or pick a state or country in the sidebar.")
			return
		st.write("No place name found, searching all of " + ", ".join(names).replace("_", " ") + ".")
		found = []
		for name in names:
			found += [(None, p) for p in searcher.get_places(name)]
		rest = query
	else:
		# Search the state or country of the place name, unless the sidebar picks a state
		region = location["region"].replace(" ", "_")
		if location["country"] == "US" and state != "All states":
			region = state
		if region not in available:
			st.warning("Found " + location["name"] + ", but " + region.replace("_", " ") + " is not loaded yet.")
			return
		if len(picked) > 0 and region not in picked:
			st.warning(location["name"] + " is in " + location["region"] + ", which is not in your country filter.")
			return

		found = get_candidates(searcher, location, radius_km, [region])
		if location["kind"] in ["state", "country"]:
			st.write("Searching all of " + location["name"] + " for: " + (rest or "(anything)"))
		else:
			st.write("Searching within " + str(radius_km) + " km of " + location["name"] + ", " + location["region"] + " for: " + (rest or "(anything)"))

	# Sidebar filters
	found = [(d, p) for d, p in found if (len(groups) == 0 or p["group"] in groups)]
	found = [(d, p) for d, p in found if does_rating_qualify(p, min_rating)]

	if len(found) == 0:
		st.warning("No places match. Try a bigger radius or fewer filters.")
		return

	distance_map = {}
	for d, p in found:
		distance_map[p["id"]] = d

	with st.spinner("Ranking " + str(len(found)) + " places (the first search in a state builds its index)..."):
		results = searcher.search(rest, [p for d, p in found], ranker=ranker, k=20)

	if len(results) == 0:
		st.warning("None of the " + str(len(found)) + " nearby places mention that. Try different words or the Dense ranker.")
		return

	st.caption(str(len(found)) + " places in range, showing the top " + str(len(results)) + " (" + ranker + ")")
	left, right = st.columns([3, 2])
	with left:
		for place, score in results:
			show_card(searcher, place, distance_map[place["id"]], rest)
	with right:
		points = pd.DataFrame([{"lat": p["lat"], "lon": p["lon"]} for p, s in results])
		st.map(points, zoom=None)


main()
