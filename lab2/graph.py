import json
from pathlib import Path

from graphviz import Digraph


folder = Path(__file__).parent
data = json.loads(
    (folder / "wikimedia.json").read_text(encoding="utf-8")
)

articles = data["articles"]
titles = {article["title"] for article in articles}

ids = {}
dot = Digraph("Wikimedia")
dot.attr(rankdir="LR", overlap="false", splines="true")
dot.attr(
    "node",
    shape="box",
    style="rounded,filled",
    fillcolor="#E8F4FA"
)

for number, article in enumerate(articles, start=1):
    node_id = f"A{number:02d}"
    ids[article["title"]] = node_id

    dot.node(
        node_id,
        label=article["title"],
        URL=article["url"]
    )

edges = 0

for article in articles:
    source = ids[article["title"]]

    for linked_title in article["links"]:
        if linked_title not in titles:
            continue

        target = ids[linked_title]

        if source != target:
            dot.edge(source, target)
            edges += 1

(folder / "graph.dot").write_text(
    dot.source,
    encoding="utf-8"
)

dot.render(str(folder / "graph"), format="pdf", cleanup=True)
dot.render(str(folder / "graph"), format="svg", cleanup=True)

print(f"Узлов: {len(articles)}")
print(f"Рёбер: {edges}")