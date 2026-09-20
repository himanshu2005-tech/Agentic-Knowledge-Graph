import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results_dir = os.path.join(BASE_DIR, "eval", "results")
ext_file = os.path.join(results_dir, "extraction", "extraction_results.csv")

if not os.path.exists(ext_file):
    print("No extraction results found.")
    exit(1)

df = pd.read_csv(ext_file)

plt.figure(figsize=(10, 6))
# Filter out 0 scores for a cleaner histogram if they just failed due to API errors
non_zero = df[df['f1'] > 0]
if non_zero.empty:
    plt.text(0.5, 0.5, "No Non-Zero F1 Scores\n(Check API Keys)", ha='center', va='center', fontsize=14)
else:
    plt.hist(non_zero['f1'], bins=5, color='green', edgecolor='black', alpha=0.7)

plt.title('Distribution of Triplet Extraction F1 Scores (Non-Zero)')
plt.xlabel('F1 Score')
plt.ylabel('Frequency (Number of Queries)')
plt.grid(axis='y', linestyle='--', alpha=0.7)

out_png = os.path.join(results_dir, "extraction", "extraction_f1_chart.png")
plt.savefig(out_png, dpi=300)
print(f"Saved {out_png}")
