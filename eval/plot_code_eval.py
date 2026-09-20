import os
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results_dir = os.path.join(BASE_DIR, "eval", "results")

# Data from the master evaluation run
labels = ['Passed', 'Failed']
sizes = [3, 1]
colors = ['#4CAF50', '#F44336']
explode = (0.1, 0)  # explode the Passed slice

plt.figure(figsize=(8, 6))
plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
        shadow=True, startangle=140, textprops={'fontsize': 14})
plt.title('Code Vault Interpreter Execution Pass Rate (N=4)', fontsize=16)

os.makedirs(results_dir, exist_ok=True)
out_png = os.path.join(results_dir, "code_eval", "code_pass_rate_chart.png")
plt.savefig(out_png, dpi=300)
print(f"Saved {out_png}")
