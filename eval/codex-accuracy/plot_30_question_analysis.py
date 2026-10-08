from __future__ import annotations

import ast
import csv
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "eval" / "results" / "accuracy" / "comparative_answers.csv"
OUTPUT = Path(__file__).resolve().parent
MODELS = {
    "Cloud 70B": "Cloud_70B_Answer",
    "Raw Local 3B": "Local_3B_Answer",
    "3B + Knowledge Graph": "Hybrid_Answer",
}
COLORS = ["#5B8FF9", "#F6BD16", "#5AD8A6"]


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def expected_values(value: str) -> list[str]:
    if value.startswith("["):
        parsed = ast.literal_eval(value)
        return [str(item) for item in parsed]
    return [value]


def is_correct(expected: str, answer: str) -> bool:
    normalized_answer = normalize(answer)
    return all(normalize(item) in normalized_answer for item in expected_values(expected))


def category(index: int) -> str:
    if index < 24:
        return "Languages"
    if index < 28:
        return "Sorting"
    return "Graph algorithms"


def save_figure(name: str) -> None:
    plt.tight_layout()
    plt.savefig(OUTPUT / name, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with INPUT.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 30:
        raise ValueError(f"Expected 30 evaluation rows, found {len(rows)}")

    matrix = np.array([
        [is_correct(row["Expected_Answer"], row[column]) for row in rows]
        for column in MODELS.values()
    ], dtype=int)
    totals = matrix.sum(axis=1)
    percentages = totals / len(rows) * 100

    plt.figure(figsize=(9, 5.6))
    bars = plt.bar(MODELS.keys(), percentages, color=COLORS, width=0.62)
    for bar, count, percent in zip(bars, totals, percentages):
        plt.text(bar.get_x() + bar.get_width() / 2, percent + 2, f"{count}/30\n{percent:.1f}%",
                 ha="center", fontweight="bold")
    plt.title("Accuracy Across 30 Questions")
    plt.ylabel("Normalized answer-match accuracy (%)")
    plt.ylim(0, 108)
    plt.grid(axis="y", alpha=0.25)
    save_figure("01_overall_accuracy.png")

    plt.figure(figsize=(13, 3.8))
    plt.imshow(matrix, cmap=plt.matplotlib.colors.ListedColormap(["#F25F5C", "#43AA8B"]), aspect="auto", vmin=0, vmax=1)
    plt.yticks(range(len(MODELS)), MODELS.keys())
    plt.xticks(range(30), range(1, 31))
    plt.xlabel("Question number")
    plt.title("Per-Question Correctness (green = correct, red = incorrect)")
    for y in range(matrix.shape[0]):
        for x in range(matrix.shape[1]):
            plt.text(x, y, "✓" if matrix[y, x] else "×", ha="center", va="center", color="white", fontsize=8)
    save_figure("02_question_heatmap.png")

    plt.figure(figsize=(10, 5.6))
    x = np.arange(1, 31)
    for label, values, color in zip(MODELS, matrix, COLORS):
        plt.plot(x, np.cumsum(values) / x * 100, label=label, color=color, linewidth=2.3)
    plt.title("Running Accuracy Across the Evaluation")
    plt.xlabel("Questions evaluated")
    plt.ylabel("Cumulative accuracy (%)")
    plt.xlim(1, 30)
    plt.ylim(0, 105)
    plt.grid(alpha=0.25)
    plt.legend(loc="lower left")
    save_figure("03_cumulative_accuracy.png")

    categories = ["Languages", "Sorting", "Graph algorithms"]
    category_indices = [[i for i in range(30) if category(i) == name] for name in categories]
    category_scores = np.array([
        [matrix[m, indices].mean() * 100 for indices in category_indices]
        for m in range(len(MODELS))
    ])
    x = np.arange(len(categories))
    width = 0.24
    plt.figure(figsize=(10, 5.6))
    for model_index, (label, color) in enumerate(zip(MODELS, COLORS)):
        bars = plt.bar(x + (model_index - 1) * width, category_scores[model_index], width, label=label, color=color)
        for bar in bars:
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                     f"{bar.get_height():.0f}%", ha="center", fontsize=8)
    plt.xticks(x, ["Languages\n(n=24)", "Sorting\n(n=4)", "Graph algorithms\n(n=2)"])
    plt.ylabel("Accuracy (%)")
    plt.title("Accuracy by Question Category")
    plt.ylim(0, 110)
    plt.grid(axis="y", alpha=0.25)
    plt.legend(loc="lower left")
    save_figure("04_category_accuracy.png")

    with (OUTPUT / "scored_results.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["question_id", "category", "question", *MODELS.keys()])
        for index, row in enumerate(rows):
            writer.writerow([index + 1, category(index), row["Question"], *matrix[:, index].tolist()])

    print(f"Created four charts and scored_results.csv in {OUTPUT}")


if __name__ == "__main__":
    main()
