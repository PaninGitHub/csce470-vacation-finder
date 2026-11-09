This Vacation Finder will take in a query and then rank using BM25 and an embedding.

To load it, install the requirements in `requirements.txt` for the .venv, then load the .venv folder as source.

For the .env, put the path of the review data relative to the codebase root directory

## Setup
From the `Codebase/` folder:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Or '.venv\Scripts\activate' on windows
pip install -r requirements.txt
cp .env.example .env             # Or 'copy .env.example .env' on Windows
```

The default `.env` uses the small sample in `sample_data/`, so no download is needed.

## Run

```bash
python scripts/demo.py "glacier cruise"
```

Results show place IDs, since names come from metadata we haven't added yet.

## Test

```bash
pytest -v
```
