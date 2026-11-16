TRAVEL_MODES = ["Domestic (US)", "International", "Anywhere"]
WIKIVOYAGE_CREDIT = "Source: Wikivoyage (CC BY-SA 4.0)"

# Checks if the country fits the selected mode (domestic vs international)
def is_right_mode(country, mode):
	return country == "US" if mode == "Domestic (US)" else (country != "US" if mode == "International" else True)

def entries_for_mode(entries, mode):
	return [e for e in entries if is_right_mode(e["country"], mode)]

def is_misfit(location, other, mode):
	if other is None or is_right_mode(other["country"], mode):
		return False
	return location is None or len(other["key"]) > len(location["key"])

def other_mode(country):
	return "Domestic (US)" if country == "US" else "International"

def does_rating_qualify(place, min_rating):
	# Wikivoyage places have no rating so it's excempt
	return (place["source"] == "wikivoyage" or min_rating == 0) if place["avg_rating"] is None else place["avg_rating"] >= min_rating

def rating_line(place, distance):
	# Stars and review count only when the place has them
	parts = []
	if place["avg_rating"] is not None:
		line = "* " + str(round(place["avg_rating"], 1))
		if place["n_reviews"]:
			line += " (" + str(place["n_reviews"]) + " reviews)"
		parts.append(line)
	elif place["source"] != "wikivoyage":
		parts.append("No rating yet")

	if place.get("price_text"):
		parts.append("Price: " + place["price_text"])
	if distance is not None:
		parts.append(str(round(distance, 1)) + " km away")
	return "  |  ".join(parts)
