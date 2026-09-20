# Ablation Study Metrics

This folder contains the systematic removal of pipeline components to prove their individual value.

- **ablation_results.csv**: Quality (F1/Groundedness proxy) versus Latency for 4 configurations.
- **ablation_chart.png**: Dual-axis bar/line chart visualizing the trade-offs.

**Key Metric**: Groundedness drop when 'no_expansion' or 'single_model_70b' is used.