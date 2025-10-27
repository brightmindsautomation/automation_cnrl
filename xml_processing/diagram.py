from graphviz import Digraph

# Define your input connections
connections = [
    ("250LIC4523.FANOUTA.OP[1]", "250FIC4521.PIDA.SP"),
    ("250FI4521.DACA.PV", "250FIC4521.DACA.P1"),
    ("250FIC4521.FANOUTA.OP[1]", "250FX4555A.SELREALA.IN[1]"),
    ("250FIC4521.FANOUTA.OP[1]", "250FX4555A.AUTOMANA.X1"),
    ("250FIC4521.FANOUTA.OP[2]", "250FX4555B.SELREALA.IN[1]"),
    ("250FIC4521.FANOUTA.OP[2]", "250FX4555B.AUTOMANA.X1"),
]

# Create a directed graph
dot = Digraph(format="png")
dot.attr(rankdir="LR", size="8,5")  # left-to-right layout

# Add nodes and edges
for src, dst in connections:
    dot.node(src, src, shape="box", style="rounded,filled", fillcolor="#e6f2ff")
    dot.node(dst, dst, shape="box", style="rounded,filled", fillcolor="#f9e6ff")
    dot.edge(src, dst)

# Save and render
dot.render("pipeline_chart", cleanup=True)
print("Pipeline chart created as pipeline_chart.png")
