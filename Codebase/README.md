# Vacation Finder

Search engine for vacation spots. Type a query like "glacier cruise" and get places ranked by how well their reviews match. CSCE 470 project by Dinidu Samaranayake and Oliver Hankins.

Currently implemented: loading reviews, text cleaning, BM25 ranking, dense (embedding) ranking with caching, hybrid ranking (BM25 and dense combined with reciprocal rank fusion), and a command-line demo that prints all three rankings. Also implemented: finding a place name in the query (gazetteer), a radius filter, a FastAPI backend, and a React search UI with a map (a Streamlit version is still in `app.py`).

## Setup

From the `Codebase/` folder:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
```

The default `.env` uses the small sample in `sample_data/`, so no data download is needed. `requirements.txt` installs the CPU-only build of PyTorch, which keeps the download to a few hundred MB. The first run of the demo downloads a ~90 MB embedding model, so it needs an internet connection (the tests do not).

## Run

```bash
python src/vacfinder/demo.py "glacier cruise"
```

Prints the top 5 places from BM25, from the dense embeddings, and from the hybrid of the two. Results show place IDs, since names come from metadata we haven't added yet. The first run on a dataset embeds all reviews and is slower; later runs reuse the saved vectors in `cache/`.

## Web app

The app searches the trimmed place files (one `.jsonl.gz` per state). Set `PLACES_DIR` in `.env` to the `final/` folder (see `.env.example`); only states whose `processed/<State>.status` starts with `DONE` show up, so new states and countries appear without code changes.

```bash
pip install -r requirements.txt
python scripts/build_cache.py Hawaii Nevada      # optional: precompute embeddings (cached in cache/)
streamlit run app.py
```

Then open http://localhost:8501. Type something like "beach resort in Waikiki" or "snorkeling Maui". The place name sets the center of the search, the radius slider limits the candidates, and the rest of the query is ranked with BM25, Dense or Hybrid. If no place name is found, pick a state in the sidebar. The first search in a state is slow if its embeddings are not cached yet.

### React app and API

Run the backend from `Codebase/` and the frontend from `Codebase/web/`, in two terminals:

```bash
uvicorn --app-dir src api.main:app --port 8000
```

```bash
cd web
npm install
npm run dev
```

Then open http://localhost:5173. The backend loads the embedding model in the background when it starts (set `WARMUP=0` to skip that). Run `python scripts/build_cache.py` once first so every region's embeddings are cached, otherwise the first Dense or Hybrid search in a new region takes minutes. `python scripts/bench_search.py Hawaii` prints where search time goes.

## Test

```bash
pytest -v
```

The default run skips the slow dense test, which loads the real embedding model (needs the model downloaded, a few seconds on CPU). To include it, run `pytest -m slow` (only the slow test) or `pytest -m ""` (everything).

## Data

Reviews come from the UCSD McAuley Lab Google Local dataset:
https://mcauleylab.ucsd.edu/public_datasets/gdrive/googlelocal/

`sample_data/sample_alaska.jsonl` is a small excerpt (40 places, reviewer info removed). To use a full file, download and unzip it (for example `review-Alaska_10.json.gz`) and set `REVIEWS_PATH` in `.env`.
