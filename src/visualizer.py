# src/visualizer.py
from pyvis.network import Network
from rdflib import URIRef, BNode
import tempfile
import os

def _short(uri):
    s = str(uri)
    if "#" in s:
        return s.split("#")[-1]
    if "/" in s.rstrip("/"):
        return s.rstrip("/").split("/")[-1]
    return s

def graph_to_pyvis(graph, height="600px", width="100%"):
    net = Network(height=height, width=width, directed=True)
    added = set()
    literal_counter = 0
    for s, p, o in graph:
        s_id = str(s)
        if s_id not in added:
            net.add_node(s_id, label=_short(s))
            added.add(s_id)
        if isinstance(o, (URIRef, BNode)):
            o_id = str(o)
            if o_id not in added:
                net.add_node(o_id, label=_short(o))
                added.add(o_id)
            net.add_edge(s_id, o_id, title=_short(p))
        else:
            lit_id = f"lit_{literal_counter}"
            net.add_node(lit_id, label=str(o), shape="box")
            net.add_edge(s_id, lit_id, title=_short(p))
            literal_counter += 1
    return net

def render_pyvis_in_streamlit(net, height=600):
    from streamlit import components
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        path = tmp.name
    net.write_html(path)
    html = open(path, "r", encoding="utf-8").read()
    components.v1.html(html, height=height, scrolling=True)
    try:
        os.remove(path)
    except OSError:
        pass
