import io
import json
import tempfile
import os

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx
import numpy as np
import pandas as pd
import streamlit as st

from alignmentfreegraph import AlignmentFreeGraph

# ──────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Alignment-Free Sequence to Graph",
    page_icon="🧬",
    layout="wide",
)

# ──────────────────────────────────────────────
# Session state initialisation
# ──────────────────────────────────────────────
if "afg" not in st.session_state:
    st.session_state.afg = None
if "connection_error" not in st.session_state:
    st.session_state.connection_error = None


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
def is_valid_color(color_str: str) -> bool:
    try:
        mcolors.to_rgba(color_str)
        return True
    except ValueError:
        return False


def random_hex_color(existing: set) -> str:
    while True:
        r, g, b = np.random.randint(0, 256, 3)
        hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
        if hex_color not in existing:
            return hex_color


def build_graph_figure(afg: AlignmentFreeGraph) -> plt.Figure:
    graph = afg.get_networkx_di_graph()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_axis_off()

    if len(graph.nodes) == 0:
        ax.text(0.5, 0.5, "Empty graph", ha="center", va="center", fontsize=14)
        return fig

    pos = nx.spring_layout(graph, seed=42)

    nx.draw_networkx_nodes(
        graph, pos, node_size=1000, node_color="skyblue",
        node_shape="o", alpha=0.8, ax=ax,
    )
    nx.draw_networkx_labels(
        graph, pos,
        labels=nx.get_node_attributes(graph, "name"),
        font_weight="bold", font_size=14, font_color="black", ax=ax,
    )
    # node id labels below the main label
    id_labels = {node: f"\n\n\n{node}" for node in graph.nodes}
    nx.draw_networkx_labels(graph, pos, labels=id_labels, font_color="gray", font_size=9, ax=ax)

    used_colors: set = set()
    color_map: dict = {}

    for edge in graph.edges:
        rad = -0.2
        for color_name in graph.edges[edge]["label"].split("+"):
            if is_valid_color(color_name):
                edge_color = color_name
            else:
                if color_name not in color_map:
                    color_map[color_name] = random_hex_color(used_colors)
                    used_colors.add(color_map[color_name])
                edge_color = color_map[color_name]

            nx.draw_networkx_edges(
                graph, pos, edgelist=[edge],
                connectionstyle=f"arc3,rad={rad}",
                arrows=True, arrowsize=20, width=2,
                edge_color=edge_color, ax=ax,
            )
            rad = -rad if rad < 0 else -(rad + 0.2)

    fig.tight_layout()
    return fig


def connect(location, db_name, username, password, config_dict=None):
    try:
        afg = AlignmentFreeGraph(
            location=location or None,
            db_name=db_name or None,
            username=username or None,
            password=password or None,
            configuration=config_dict or None,
        )
        st.session_state.afg = afg
        st.session_state.connection_error = None
    except Exception as e:
        st.session_state.afg = None
        st.session_state.connection_error = str(e)


# ──────────────────────────────────────────────
# Sidebar — connection
# ──────────────────────────────────────────────
with st.sidebar:
    st.title("🔌 Connection")

    config_file = st.file_uploader("Load credentials.json", type=["json"])
    config_dict = None
    if config_file is not None:
        raw = json.load(config_file)
        config_dict = raw.get("neo4j", raw)

    with st.form("connection_form"):
        location = st.text_input("Location", placeholder="bolt://localhost:7687")
        db_name = st.text_input("Database name", placeholder="neo4j")
        username = st.text_input("Username", placeholder="neo4j")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Connect")
        if submitted:
            connect(location, db_name, username, password, config_dict)

    if config_dict and not submitted:
        if st.button("Connect with config file"):
            connect(None, None, None, None, config_dict)

    if st.session_state.connection_error:
        st.error(st.session_state.connection_error)
    elif st.session_state.afg is not None:
        st.success("Connected")

    st.divider()

    # ── K parameter ──
    st.subheader("⚙️ K parameter")
    if st.session_state.afg is not None:
        current_k = st.session_state.afg.get_k()
        new_k = st.number_input(
            "k", min_value=1, value=current_k, step=1, key="k_input"
        )
        if new_k != current_k:
            st.session_state.afg.set_k(new_k)
            st.rerun()
    else:
        st.info("Connect to a database first.")

    st.divider()

    # ── Data operations ──
    st.subheader("📂 Load graph")
    upload = st.file_uploader("Upload JSON or GFA file", type=["json", "gfa"])
    if st.button("Load file") and upload is not None and st.session_state.afg is not None:
        suffix = ".json" if upload.name.endswith(".json") else ".gfa"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(upload.read())
            tmp_path = tmp.name
        try:
            if suffix == ".gfa":
                st.session_state.afg.upload_from_gfa(tmp_path)
            else:
                st.session_state.afg.upload_from_json(tmp_path)
            st.success("File loaded successfully.")
            st.rerun()
        except Exception as e:
            st.error(str(e))
        finally:
            os.unlink(tmp_path)

    if st.button("🗑️ Delete all nodes", type="secondary",
                 disabled=st.session_state.afg is None):
        st.session_state.afg.delete_all()
        st.rerun()


# ──────────────────────────────────────────────
# Main area
# ──────────────────────────────────────────────
st.title("🧬 Alignment-Free Sequence to Graph")

if st.session_state.afg is None:
    st.info("Use the sidebar to connect to a Neo4j database.")
    st.stop()

afg: AlignmentFreeGraph = st.session_state.afg

tab_graph, tab_hash, tab_search = st.tabs(["Graph", "K-mer Hashtable", "Sequence Search"])

# ── Tab 1: Graph ──────────────────────────────
with tab_graph:
    col_graph, col_export = st.columns([5, 1])

    with col_graph:
        with st.spinner("Rendering graph…"):
            fig = build_graph_figure(afg)
        st.pyplot(fig, use_container_width=True)

    with col_export:
        st.subheader("Export")
        buf_png = io.BytesIO()
        fig.savefig(buf_png, format="png", bbox_inches="tight")
        st.download_button(
            label="⬇️ PNG",
            data=buf_png.getvalue(),
            file_name="graph.png",
            mime="image/png",
        )

        buf_jpg = io.BytesIO()
        fig.savefig(buf_jpg, format="jpeg", bbox_inches="tight")
        st.download_button(
            label="⬇️ JPEG",
            data=buf_jpg.getvalue(),
            file_name="graph.jpeg",
            mime="image/jpeg",
        )

        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

# ── Tab 2: Hashtable ──────────────────────────
with tab_hash:
    ht_df: pd.DataFrame = afg.get_hashtable_df()

    if ht_df.empty:
        st.info("The hashtable is empty. Load a graph first.")
    else:
        st.dataframe(ht_df, use_container_width=True, hide_index=True)

    st.subheader("Export hashtable")
    export_col1, export_col2, export_col3 = st.columns(3)

    with export_col1:
        csv_bytes = ht_df.to_csv(index=False).encode()
        st.download_button("⬇️ CSV", data=csv_bytes,
                           file_name="hashtable.csv", mime="text/csv")

    with export_col2:
        xlsx_buf = io.BytesIO()
        with pd.ExcelWriter(xlsx_buf, engine="openpyxl") as writer:
            ht_df.to_excel(writer, index=False)
        st.download_button("⬇️ Excel", data=xlsx_buf.getvalue(),
                           file_name="hashtable.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with export_col3:
        json_bytes = json.dumps(afg.get_hashtable(), indent=4).encode()
        st.download_button("⬇️ JSON", data=json_bytes,
                           file_name="hashtable.json", mime="application/json")

# ── Tab 3: Sequence search ────────────────────
with tab_search:
    st.subheader("Search sequence in graph")

    sequence = st.text_input("Sequence (e.g. ACGT)", placeholder="ACGT")

    search_col1, search_col2 = st.columns(2)
    with search_col1:
        if st.button("Search via hashtable", use_container_width=True,
                     disabled=not sequence):
            result = afg.sequence_from_hash(sequence)
            if result:
                st.success(f"Found at nodes: {result}")
            else:
                st.warning("Sequence not found in hashtable.")

    with search_col2:
        if st.button("Search via graph (Cypher)", use_container_width=True,
                     disabled=not sequence):
            result = afg.sequence_from_graph(sequence)
            if result:
                st.success(f"Found at nodes: {result}")
            else:
                st.warning("Sequence not found in graph.")
