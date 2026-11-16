# Offline evaluation

Compares BM25, Dense and Hybrid on 36 queries (`queries.json`, 5 types: keyword, vibe, paraphrase, constraint, multi). It uses the US states Hawaii, Alaska, Nevada, Utah and Colorado. Each query names a place, and like the app it searches places within 25 km of it (or the whole state).

## 1. Make the pool

From `Codebase/`, with `PLACES_DIR` set (in `.env` or the environment):

```bash
python eval/pool.py
```

Runs every query through `Searcher` (the same code as the app), takes the top 10 of each ranker, and joins them. This writes:

- `eval/pools/judgments_template.csv`: one row per (query, place) to judge
- `eval/pools/rankings.json`: the top 10 of each system per query

The first run embeds the five states, so it is slow and needs the embedding model.

## 2. Judge

Copy the template to `eval/pools/judgments.csv` and fill the `relevance` column for every row. Read the place name, group and city, and look the place up if needed. Judge it as an answer to the query text:

- 0: not relevant (wrong thing, wrong place, or nothing to do with the query)
- 1: partly relevant (right area or category, but only part of what was asked)
- 2: highly relevant (a good answer to the whole query)

Rows with an empty relevance are ignored. A place that is not in the file counts as 0.

## 3. Results

```bash
python eval/run_eval.py                       # reads eval/pools/judgments.csv
python eval/run_eval.py other_judgments.csv   # or give a file
```

Prints P@1, P@5, P@10, MAP and NDCG@10 for each system, for all queries and then per query type. Precision and MAP count a place as relevant if it got 1 or 2. NDCG uses the 0/1/2 grades. Both only know about judged places, so the pool has to be fully judged first.

The metric tests are in `tests/test_metrics.py`.
