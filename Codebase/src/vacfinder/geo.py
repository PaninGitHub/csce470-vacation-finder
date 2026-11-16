import json
import math
import os
import re
import statistics
import unicodedata

from vacfinder.places import list_regions, split_regions, load_region

MIN_PLACES_PER_CITY = 3

# Lowercase accents and punctuation for normalization
def normalize(name):
	name = unicodedata.normalize("NFKD", name.lower())
	name = "".join(c for c in name if not unicodedata.combining(c))
	name = re.sub(r"[^a-z0-9 ]", " ", name)
	return " ".join(name.split())

# Puts the coordinates of countries and cities if it meets MIN_PLACES_PER_CITY by finding centroid
def country_entries(places):
	if len(places) == 0:
		return []
	entries = []
	cities = {}
	for p in places:
		if p["city"]:
			if p["city"] not in cities:
				cities[p["city"]] = []
			cities[p["city"]].append((p["lat"], p["lon"]))

	for city, points in cities.items():
		if len(points) < MIN_PLACES_PER_CITY:
			continue
		lat = statistics.median(p[0] for p in points)
		lon = statistics.median(p[1] for p in points)
		entries.append({
			"name": city, "key": normalize(city), "kind": "city", "region": places[0]["region"],
			"country": places[0]["country"], "lat": lat, "lon": lon, "n_places": len(points),
		})
	lat = statistics.median(p[0] for p in [(p["lat"], p["lon"]) for p in places])
	lon = statistics.median(p[1] for p in [(p["lat"], p["lon"]) for p in places])
	entries.append({
		"name": places[0]["region"], "key": normalize(places[0]["region"]), "kind": "country", "region": places[0]["region"],
		"country": places[0]["country"], "lat": lat, "lon": lon, "n_places": len(places),
	})
	return entries

def load_gazetteer(final_dir):
	with open(os.path.join(final_dir, "gazetteer.json"), encoding="utf-8") as f:
		entries = [e for e in json.load(f) if e["country"] == "US"]

	states, countries = split_regions(final_dir, list_regions(final_dir))
	for name in countries:
		entries += country_entries(load_region(final_dir, name))

	alias_path = os.path.join(final_dir, "aliases.json")
	if os.path.exists(alias_path):
		with open(alias_path, encoding="utf-8") as f:
			entries += list(json.load(f).values())
	return entries

def find_loc(query, entries):
	text = " " + normalize(query) + " "
	best = None
	for e in entries:
		if e["kind"] == "state" and len(e["key"]) == 2:
			continue
		if " " + e["key"] + " " not in text:
			continue

		if best is None:
			best = e
		elif (e["kind"] == "area", len(e["key"]), e["n_places"]) > (best["kind"] == "area", len(best["key"]), best["n_places"]):
			best = e

	if best is None:
		return None, query

	rest = text.replace(" " + best["key"] + " ", " ", 1)
	return best, " ".join(rest.split())

def find_distance_sphere(lat1, lon1, lat2, lon2):
	r = 6371.0
	p1 = math.radians(lat1)
	p2 = math.radians(lat2)
	dp = p2 - p1
	dl = math.radians(lon2 - lon1)
	a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
	return 2 * r * math.asin(math.sqrt(a))

def radius_search(places, lat, lon, km):
	dlat = km / 111.0
	dlon = km / (111.0 * max(math.cos(math.radians(lat)), 0.01))

	found = []
	for p in places:
		if abs(p["lat"] - lat) > dlat or abs(p["lon"] - lon) > dlon:
			continue
		d = find_distance_sphere(lat, lon, p["lat"], p["lon"])
		if d <= km:
			found.append((d, p))

	found.sort(key=lambda x: x[0])
	return found
