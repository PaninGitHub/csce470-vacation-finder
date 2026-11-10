# Vacation Finder

Search engine for vacation spots. Type a query like "glacier cruise" and get places ranked by how well their reviews match. CSCE 470 project by Dinidu Samaranayake and Oliver Hankins.

Currently implemented: loading reviews, text cleaning, BM25 ranking, dense (embedding) ranking with caching, hybrid ranking (BM25 and dense combined with reciprocal rank fusion), and a command-line demo that prints all three rankings. Place names and the UI are not done yet.

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
python scripts/demo.py "glacier cruise"
```

Prints the top 5 places from BM25, from the dense embeddings, and from the hybrid of the two. Results show place IDs, since names come from metadata we haven't added yet. The first run on a dataset embeds all reviews and is slower; later runs reuse the saved vectors in `cache/`.

## Test

```bash
pytest -v
```

## Data

Reviews come from the UCSD McAuley Lab Google Local dataset:
https://mcauleylab.ucsd.edu/public_datasets/gdrive/googlelocal/

`sample_data/sample_alaska.jsonl` is a small excerpt (40 places, reviewer info removed). To use a full file, download and unzip it (for example `review-Alaska_10.json.gz`) and set `REVIEWS_PATH` in `.env`.
