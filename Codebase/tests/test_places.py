import gzip
import json

from vacfinder.places import list_regions, load_region, split_regions

def make_region(tmp_path, name, status, country="US"):
	final = tmp_path / "final"
	processed = tmp_path / "processed"
	final.mkdir(parents=True, exist_ok=True)
	processed.mkdir(parents=True, exist_ok=True)
	with gzip.open(final / (name + ".jsonl.gz"), "wt", encoding="utf-8") as f:
		f.write(json.dumps({"id": "a", "name": "A", "country": country}) + "\n")
		f.write(json.dumps({"id": "b", "name": "B", "country": country}) + "\n")
	if status is not None:
		(processed / (name + ".status")).write_text(status)
	return str(final)

def test_only_done_regions(tmp_path):
	make_region(tmp_path, "Utah", "DONE 13:11:29 raw deleted")
	make_region(tmp_path, "Iowa", "RUNNING")
	final = make_region(tmp_path, "Texas", None)
	assert list_regions(final) == ["Utah"]

def test_country_needs_stats_file(tmp_path):
	# Country files have no status file, a .stats.json marks them as finished
	final = make_region(tmp_path, "Italy", None)
	assert list_regions(final) == []
	(tmp_path / "final" / "Italy.stats.json").write_text("{}")
	assert list_regions(final) == ["Italy"]

def test_split_regions(tmp_path):
	final = make_region(tmp_path, "Utah", "DONE", country="US")
	make_region(tmp_path, "Italy", None, country="IT")
	assert split_regions(final, ["Italy", "Utah"]) == (["Utah"], ["Italy"])

def test_load_region(tmp_path):
	final = make_region(tmp_path, "Utah", "DONE")
	places = load_region(final, "Utah")
	assert [p["id"] for p in places] == ["a", "b"]

def test_brackets_in_folder_name(tmp_path):
	# glob treats [1] as a character class, so this used to find nothing
	make_region(tmp_path / "[1] Projects", "Utah", "DONE")
	assert list_regions(str(tmp_path / "[1] Projects" / "final")) == ["Utah"]
