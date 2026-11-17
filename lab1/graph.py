import csv
from itertools import combinations
from pathlib import Path

from graphviz import Digraph


N = 2

with open("terms.csv", encoding="utf-8-sig") as file:
    resources = list(csv.DictReader(file))

for resource in resources:
    resource["terms_set"] = set(resource["terms"].split("; "))

edges = []

for first, second in combinations(resources, 2):
    common = first["terms_set"] & second["terms_set"]

    if len(common) >= N:
        edges.append({
            "source": first["id"],
            "target": second["id"],
            "weight": len(common),
            "common_terms": "; ".join(sorted(common)),
        })

dot = Digraph("MetallurgyResources")
dot.attr(rankdir="LR", overlap="false", splines="true")
dot.attr("node", shape="box", style="rounded,filled", fillcolor="#E8F4FA")

for resource in resources:
    dot.node(
        resource["id"],
        label=resource["id"],
        tooltip=resource["title"],
        URL=resource["url"],
    )

for edge in edges:
    dot.edge(
        edge["source"],
        edge["target"],
        label=str(edge["weight"]),
    )

Path("graph.dot").write_text(dot.source, encoding="utf-8")

with open("edges.csv", "w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["source", "target", "weight", "common_terms"],
    )
    writer.writeheader()
    writer.writerows(edges)

dot.render("graph", format="pdf", cleanup=True)
dot.render("graph", format="svg", cleanup=True)

print(f"Готово: {len(resources)} узлов, {len(edges)} рёбер")