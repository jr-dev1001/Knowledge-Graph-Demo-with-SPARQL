# src/sparql_service.py
from rdflib import Graph

def prefixes_from_graph(graph: Graph) -> str:
    """
    Build PREFIX declarations from graph.bind() calls.
    """
    prefixes = ""
    for prefix, ns in graph.namespaces():
        prefixes += f"PREFIX {prefix}: <{ns}>\n"
    return prefixes


def exec_sparql(graph: Graph, query: str):
    q_lower = query.strip().lower()
    try:
        if q_lower.startswith(("insert", "delete", "update")):
            graph.update(query)
            # return updated table automatically
            select_query = """
            SELECT ?person ?name ?age ?company WHERE {
              ?person a foaf:Person .
              ?person foaf:name ?name .
              OPTIONAL { ?person ex:age ?age . }
              OPTIONAL { ?person ex:worksAt ?company . }
            }
            """
            res_query = graph.query(select_query)
        else:
            res_query = graph.query(query)

        vars_ = [str(v) for v in res_query.vars] if res_query.vars else []
        rows = [
            {str(v): str(row[i]) if row[i] is not None else None for i, v in enumerate(res_query.vars)}
            for row in res_query
        ]
        return {"vars": vars_, "rows": rows, "info": "Query executed."}

    except Exception as e:
        return {"error": str(e)}
