"""Export report-ready visualizations from data/rag/rag_knowledge.txt."""
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parents[1]
FACT_PATTERN = re.compile(
    r"^\[domain=(?P<domain>[^]]+)]\s*\((?P<subject>[^,]+),\s*(?P<relation>[^,]+),\s*(?P<object>.+)\)\s*$"
)
PALETTE = ("#8DD96A", "#69A7FF", "#F2B95F", "#D78BFF", "#FF7B70", "#50D2C8", "#C8CB62", "#F08EB5")


def read_graph(path: Path) -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = FACT_PATTERN.match(line.strip())
        if not match:
            continue
        item = {key: value.strip() for key, value in match.groupdict().items()}
        graph.add_node(item["subject"])
        graph.add_node(item["object"])
        graph.add_edge(item["subject"], item["object"], relation=item["relation"], domain=item["domain"])
    return graph


def node_domains(graph: nx.MultiDiGraph) -> dict[str, str]:
    result = {}
    for node in graph.nodes:
        domains = [data["domain"] for *_, data in graph.in_edges(node, data=True)]
        domains += [data["domain"] for *_, data in graph.out_edges(node, data=True)]
        result[node] = Counter(domains).most_common(1)[0][0] if domains else "Other"
    return result


def overview(graph: nx.MultiDiGraph, maximum: int) -> nx.MultiDiGraph:
    simple = nx.DiGraph(graph)
    ranks = nx.pagerank(simple)
    degrees = dict(nx.Graph(graph).degree())
    hubs = sorted(graph.nodes, key=lambda node: (degrees[node], ranks[node]), reverse=True)
    selected: set[str] = set()
    # Add hubs together with their strongest immediate neighborhoods. This avoids
    # selecting high-ranked endpoint nodes whose connecting entity is not shown.
    for hub in hubs:
        if len(selected) >= maximum:
            break
        neighborhood = set(graph.predecessors(hub)) | set(graph.successors(hub))
        ordered = sorted(neighborhood, key=lambda node: (degrees[node], ranks[node]), reverse=True)
        if hub not in selected:
            selected.add(hub)
        for node in ordered:
            if len(selected) >= maximum:
                break
            selected.add(node)
    return graph.subgraph(selected).copy()


def export(source: Path, output: Path, mode: str, maximum: int) -> None:
    complete = read_graph(source)
    graph = overview(complete, maximum) if mode == "overview" else complete
    domains = node_domains(graph)
    domain_counts = Counter(data["domain"] for *_, data in graph.edges(data=True))
    domain_order = [name for name, _ in domain_counts.most_common()]
    colors = {name: PALETTE[index % len(PALETTE)] for index, name in enumerate(domain_order)}

    width, height, dpi = ((16, 9, 220) if mode == "overview" else (24, 15, 220))
    figure, axis = plt.subplots(figsize=(width, height), dpi=dpi, facecolor="#0D0E0C")
    axis.set_facecolor("#0D0E0C")
    simple = nx.Graph(graph)
    positions = nx.spring_layout(simple, seed=42, k=1.8 / max(len(graph), 1) ** 0.5, iterations=180)
    degrees = dict(simple.degree())

    nx.draw_networkx_edges(
        graph, positions, ax=axis, edge_color="#A3A996", alpha=0.14 if mode == "full" else 0.24,
        width=0.45 if mode == "full" else 0.8, arrows=False,
    )
    nx.draw_networkx_nodes(
        graph, positions, ax=axis,
        node_color=[colors.get(domains[node], "#AAAAAA") for node in graph.nodes],
        node_size=[18 + min(degrees.get(node, 0), 20) * (7 if mode == "full" else 18) for node in graph.nodes],
        alpha=0.88, linewidths=0.25, edgecolors="#F4F6EA",
    )
    label_count = 42 if mode == "overview" else 85
    labels = {
        node: re.sub(r"(?<=[a-z])(?=[A-Z])", " ", node)
        for node, _ in sorted(degrees.items(), key=lambda item: item[1], reverse=True)[:label_count]
    }
    nx.draw_networkx_labels(
        graph, positions, labels=labels, ax=axis, font_size=5.8 if mode == "full" else 7.2,
        font_color="#EEF0E7", font_family="sans-serif",
        bbox={"facecolor": "#0D0E0C", "edgecolor": "none", "alpha": 0.68, "pad": 0.7},
    )

    title = "Agentic Knowledge Graph — Report Overview" if mode == "overview" else "Agentic Knowledge Graph — Complete Snapshot"
    subtitle = (
        f"Source: {source.name}  •  Complete knowledge base: {complete.number_of_nodes():,} entities, "
        f"{complete.number_of_edges():,} facts  •  Displayed: {graph.number_of_nodes():,} entities, {graph.number_of_edges():,} facts"
    )
    figure.text(0.04, 0.955, title, color="#F1F3E9", fontsize=20, fontweight="bold")
    figure.text(0.04, 0.925, subtitle, color="#969C8E", fontsize=8.5)
    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=colors[name], markersize=7, label=f"{name} ({domain_counts[name]})")
        for name in domain_order[:10]
    ]
    axis.legend(handles=handles, loc="lower left", frameon=False, labelcolor="#C9CDC1", fontsize=7, ncol=2)
    axis.text(0.995, 0.012, "Node size represents visible degree • Color represents dominant domain",
              transform=axis.transAxes, ha="right", color="#777D70", fontsize=7)
    axis.axis("off")
    figure.subplots_adjust(left=0.025, right=0.975, bottom=0.045, top=0.88)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, facecolor=figure.get_facecolor())
    plt.close(figure)
    print(f"Wrote {output} ({output.stat().st_size / 1024:.1f} KB)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT / "data" / "rag" / "rag_knowledge.txt")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=("overview", "full"), default="overview")
    parser.add_argument("--max-nodes", type=int, default=140)
    args = parser.parse_args()
    export(args.source, args.output, args.mode, args.max_nodes)


if __name__ == "__main__":
    main()
