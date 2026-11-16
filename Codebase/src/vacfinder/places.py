import gzip
import json
import os

def list_regions(final_dir):
	# A US state counts only if its processed/<name>.status starts with DONE.
	# Country files have no status file, so they need a .stats.json next to them instead
	regions = []
	status_dir = os.path.join(final_dir, "..", "processed")
	# Using os.listdir to handle files paths like "[1] Projects" and is generally more flexible
	for file_name in sorted(os.listdir(final_dir)):
		if not file_name.endswith(".jsonl.gz"):
			continue
		name = file_name[:-len(".jsonl.gz")]

		status_path = os.path.join(status_dir, name + ".status")
		if os.path.exists(status_path):
			with open(status_path) as f:
				if not f.read().startswith("DONE"):
					continue
		elif not os.path.exists(os.path.join(final_dir, name + ".stats.json")):
			continue
		regions.append(name)
	return regions

# Gathers the country code for a specific dataset (ex: "US" <- US State, "IT" <- Italy)
def region_country(final_dir, name):
	with gzip.open(os.path.join(final_dir, name + ".jsonl.gz"), "rt", encoding="utf-8") as f:
		first = f.readline()
	if first == "":
		return None
	return json.loads(first)["country"]

# Since we distinguish states from countries, we can spilt the regions.
def split_regions(final_dir, names):
	states = []
	countries = []
	for name in names:
		if region_country(final_dir, name) == "US":
			states.append(name)
		else:
			countries.append(name)
	return states, countries

# Returns a list of place dicts, one per line of the file
def load_region(final_dir, name):
	places = []
	with gzip.open(os.path.join(final_dir, name + ".jsonl.gz"), "rt", encoding="utf-8") as f:
		for row in f:
			places.append(json.loads(row))
	return places
