import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"


def ok(path):
	try:
		urllib.request.urlopen(BASE + path, timeout=8)
		return True
	except urllib.error.HTTPError as e:
		return e.code if e.code == 404 else False
	except Exception:
		return False


# Prefer /api/health; fall back to /api/options if the route does not exist yet
r = ok("/api/health")
if r == 404:
	r = ok("/api/options")
sys.exit(0 if r is True else 1)
