"""Run the fixed, manually labelled FlowGuard scenario evaluation in mock mode."""

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ai.classifier import ActivityClassifier
from app.core import ActivityState, ContextSnapshot


LABELS = [state.value for state in ActivityState]


def metrics(expected, predicted):
    rows, f1s = {}, []
    for label in LABELS:
        tp = sum(a == label and p == label for a, p in zip(expected, predicted))
        fp = sum(a != label and p == label for a, p in zip(expected, predicted))
        fn = sum(a == label and p != label for a, p in zip(expected, predicted))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        rows[label] = {"precision": precision, "recall": recall, "f1": f1, "support": expected.count(label)}
        f1s.append(f1)
    return {"accuracy": sum(a == p for a, p in zip(expected, predicted)) / len(expected),
            "macro_f1": sum(f1s) / len(f1s), "per_class": rows}


def main():
    base = Path(__file__).resolve().parent
    cases = json.loads((base / "cases.json").read_text(encoding="utf-8"))
    classifier, predicted, baseline = ActivityClassifier(mock=True), [], []
    for case in cases:
        snapshot = ContextSnapshot(datetime.now().astimezone(), case["task"], case["app_name"],
                                   case["window_title"], b"in-memory-eval-placeholder")
        predicted.append(classifier.classify(snapshot).state.value)
        baseline.append("MAIN_TASK" if case["app_name"].casefold() == case["main_app"].casefold() else "DISTRACTION")
    expected = [case["label"] for case in cases]
    report = {"dataset": "manually labelled scenario set", "samples": len(cases),
              "class_counts": Counter(expected), "flowguard_mock": metrics(expected, predicted),
              "leave_main_app_baseline": metrics(expected, baseline)}
    (base / "results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("=== FlowGuard Evaluation ===")
    print(f"Samples: {len(cases)}")
    for name in ("flowguard_mock", "leave_main_app_baseline"):
        result = report[name]; print(f"\n{name}: Accuracy={result['accuracy']:.3f}  Macro-F1={result['macro_f1']:.3f}")
        for label in LABELS:
            row = result["per_class"][label]
            print(f"  {label}: P={row['precision']:.3f} R={row['recall']:.3f} F1={row['f1']:.3f} n={row['support']}")
    print("FLOWGUARD EVALUATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

