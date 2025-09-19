# src/app.py
import streamlit as st
from data_builder import build_dummy_graph
from sparql_service import exec_sparql
from visualizer import graph_to_pyvis, render_pyvis_in_streamlit
from nl2sparql import nl_to_sparql

st.set_page_config(page_title="KG + SPARQL Demo", layout="wide")

DEFAULT_QUERY = """SELECT ?person ?name ?age ?company WHERE {
  ?person a foaf:Person .
  ?person foaf:name ?name .
  OPTIONAL { ?person ex:age ?age . }
  OPTIONAL { ?person ex:worksAt ?company . }
} LIMIT 20
"""

def ensure_graph():
    if "graph" not in st.session_state:
        st.session_state.graph = build_dummy_graph(n_people=6, n_companies=2, seed=42)

def detect_query_type(query: str) -> str:
    q = query.strip().lower()
    if q.startswith("select"):
        return "SELECT"
    elif q.startswith("construct"):
        return "CONSTRUCT"
    elif q.startswith(("insert", "create")):
        return "INSERT"
    elif q.startswith(("delete", "update", "with", "modify")):
        return "DELETE"
    else:
        return "UNKNOWN"

def main():
    st.title("Knowledge Graph with SPARQL Demo")
    ensure_graph()

    with st.sidebar:
        st.header("Graph Config")
        n_people = st.slider("Number of people", 2, 30, 6)
        n_companies = st.slider("Number of companies", 1, 10, 2)
        if st.button("🔄 Rebuild Graph"):
            st.session_state.graph = build_dummy_graph(n_people, n_companies)
            st.success("Graph rebuilt!")

        st.markdown("---")
        st.subheader("Sample SPARQL")
        st.code(DEFAULT_QUERY, language="sparql")

    # NL → SPARQL
    st.subheader("💬 Ask in Natural Language")
    nl_query = st.text_input("Enter question (e.g., 'Show all people older than 30')")
    if st.button("Convert to SPARQL"):
        if nl_query.strip():
            sparql_query = nl_to_sparql(nl_query)
            st.session_state.last_sparql = sparql_query
            st.code(sparql_query, language="sparql")
        else:
            st.warning("Please type a question.")

    # SPARQL editor
    st.subheader("📝 SPARQL Editor")
    query = st.text_area(
        "Enter or edit SPARQL",
        value=st.session_state.get("last_sparql", DEFAULT_QUERY),
        height=200
    )

    query_type = detect_query_type(query)
    auto_execute = query_type == "SELECT"
    execute_clicked = auto_execute or st.button("▶️ Execute Query")

    if execute_clicked:
        if query_type == "DELETE":
            st.warning("⚠️ This will modify the graph!")
            if not st.session_state.get("confirmed_delete", False):
                if st.button("✅ Confirm DELETE/UPDATE"):
                    st.session_state.confirmed_delete = True
                else:
                    st.stop()

        res = exec_sparql(st.session_state.graph, query)
        if query_type == "DELETE":
            st.session_state.confirmed_delete = False

        if "error" in res:
            st.error(res["error"])
        else:
            if "info" in res:
                st.success(res["info"])
            if "rows" in res:
                st.subheader("📊 Current People Data")
                st.dataframe(res["rows"])

    # Graph visualization
    st.subheader("🌐 Graph Visualization")
    if st.button("Visualize Graph"):
        net = graph_to_pyvis(st.session_state.graph, height="700px", width="100%")
        render_pyvis_in_streamlit(net, height=700)

    st.markdown("---")
    st.info(
        "Notes:\n"
        "- SELECT executes automatically.\n"
        "- INSERT/DELETE/UPDATE modifies graph.\n"
        "- Data table is shown after every query.\n"
        "- Graph is only rebuilt on initial load or manual rebuild."
    )

if __name__ == "__main__":
    main()
