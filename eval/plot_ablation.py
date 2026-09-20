import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results_dir = os.path.join(BASE_DIR, "eval", "results")
ablation_file = os.path.join(results_dir, "ablation", "ablation_results.csv")

if not os.path.exists(ablation_file):
    print("No ablation results found.")
    exit(1)

df = pd.read_csv(ablation_file)

fig, ax1 = plt.subplots(figsize=(10, 6))

color = 'tab:blue'
ax1.set_xlabel('Architecture Variant')
ax1.set_ylabel('F1 / Groundedness Score', color=color)
bars = ax1.bar(df['Ablation Variant'], df['micro_f1'], color=color, alpha=0.7, label='F1 Score')
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Mean Latency (s)', color=color)
line = ax2.plot(df['Ablation Variant'], df['mean_latency_sec'], color=color, marker='o', linewidth=2, label='Latency')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('Ablation Study: Quality vs. Latency')
fig.tight_layout()

out_png = os.path.join(results_dir, "ablation", "ablation_chart.png")
plt.savefig(out_png, dpi=300)
print(f"Saved {out_png}")
