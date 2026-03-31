#!/usr/bin/env python3
"""
Evaluate keyword / curated-fact routing against a labelled CSV.

Run from repository root:
    python scripts/evaluation/evaluate_intent.py

Uses the same logic as production: app.get_core_fact_route_key (resolve_core_fact).
Optional: pip install scikit-learn for classification_report output.
"""
from __future__ import annotations

import csv
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

from app import get_core_fact_route_key  # noqa: E402


def main():
    csv_path = os.path.join(os.path.dirname(__file__), "intent_test_set.csv")
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)

    y_true = []
    y_pred = []
    print(f"Loaded {len(rows)} test cases from intent_test_set.csv\n")
    print(f"{'Language':<6} {'Museum':<7} {'Expected':<18} {'Predicted':<18} OK")
    print("-" * 70)

    for r in rows:
        q = r["query"].strip()
        lang = r["language"].strip()
        mid = str(int(r["museum_id"]))  # normalise "3" not "03"
        exp = r["expected_route"].strip()
        pred = get_core_fact_route_key(q, mid, lang)
        y_true.append(exp)
        y_pred.append(pred)
        ok = "yes" if pred == exp else "NO"
        print(f"{lang:<6} {mid:<7} {exp:<18} {pred:<18} {ok}")

    print("-" * 70)
    correct = sum(1 for a, b in zip(y_true, y_pred) if a == b)
    print(f"Accuracy: {correct}/{len(rows)} = {100.0 * correct / len(rows):.1f}%")

    try:
        from sklearn.metrics import classification_report

        print("\n sklearn.metrics.classification_report (macro averages):\n")
        print(
            classification_report(
                y_true, y_pred, zero_division=0, digits=3
            )
        )
    except ImportError:
        print(
            "\nInstall scikit-learn for precision/recall/F1: pip install scikit-learn"
        )


if __name__ == "__main__":
    main()
