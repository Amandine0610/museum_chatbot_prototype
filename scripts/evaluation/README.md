# Intent routing evaluation

- **`intent_test_set.csv`** — **30** labelled queries (**10 English, 10 French, 10 Kinyarwanda**), same intent types mirrored across languages where possible. Each row: `query`, `language` (`en`/`fr`/`rw`), `museum_id`, `expected_route` (must match `get_core_fact_route_key` in `app.py`).
- **`evaluate_intent.py`** — Loads `app.py`, predicts the route for each row, prints match table and overall accuracy. If `scikit-learn` is installed, prints `classification_report`.

## Run

From the **repository root** (`Rwanda_museums_chatbot/`):

```bash
python scripts/evaluation/evaluate_intent.py
```

Optional:

```bash
pip install scikit-learn
```

## Adding more queries

Duplicate rows in the CSV. For a full capstone-style set (e.g. 40 per language), extend this file and keep `expected_route` aligned with the keys returned by `resolve_core_fact` in `app.py` (e.g. `hours`, `kamwe`, `location`, `history`, `unrouted`, …).
