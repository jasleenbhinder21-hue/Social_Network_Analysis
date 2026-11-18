
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Social Network Analysis",
    page_icon="🌐",
    layout="wide"
)

# ---------------- SAMPLE DATA ----------------

edges = [
    ("Alice", "Bob"),
    ("Alice", "Charlie"),
    ("Bob", "Charlie"),
    ("Bob", "David"),
    ("Charlie", "David"),
    ("David", "Emma"),
    ("Emma", "Frank"),
    ("Frank", "Grace"),
    ("Grace", "Emma"),
    ("Alice", "Emma"),
    ("David", "Frank"),
    ("George", "Helen"),
    ("Helen", "Ian"),
    ("George", "Ian"),
    ("Ian", "Jack"),
    ("Jack", "George")
]

# ---------------- GRAPH INITIALIZATION ----------------

if "graph" not in st.session_state:
    G = nx.Graph()
    G.add_edges_from(edges)
    st.session_state.graph = G

G = st.session_state.graph

# ---------------- SIDEBAR ----------------

st.sidebar.title("🌐 Social Network Analysis")

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Network Graph",
        "Add Connection",
        "Dataset Upload",
        "Centrality Analysis",
        "Community Detection",
        "Graph Statistics"
    ]
)

st.sidebar.divider()
st.sidebar.info("Graph Theory Based Project")

# ---------------- COMMON METRICS ----------------

total_users = G.number_of_nodes()
total_edges = G.number_of_edges()
density = nx.density(G)

degrees = dict(G.degree())

# ---------------- OVERVIEW ----------------

if page == "Overview":

    st.title("🌐 Social Network Analysis Dashboard")

    st.caption(
        "Analyzing social relationships using Graph Theory"
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Users", total_users)
    col2.metric("Connections", total_edges)
    col3.metric("Network Density", round(density, 3))

    col4.metric(
        "Communities",
        len(list(
            nx.community.greedy_modularity_communities(G)
        )) if total_edges > 0 else total_users
    )

    st.divider()

    st.subheader("Social Network Visualization")

    if total_users > 0:

        fig, ax = plt.subplots(figsize=(11, 7))
        pos = nx.spring_layout(G, seed=42)

        nx.draw(
            G,
            pos,
            with_labels=True,
            node_color="skyblue",
            node_size=1800,
            font_size=10,
            font_weight="bold",
            edge_color="gray",
            ax=ax
        )

        st.pyplot(fig)
        plt.close(fig)

    st.success("Dashboard is running successfully!")

# ---------------- NETWORK GRAPH ----------------

elif page == "Network Graph":

    st.title("Network Graph Visualization")

    if total_users > 0:

        fig, ax = plt.subplots(figsize=(11, 7))
        pos = nx.spring_layout(G, seed=42)

        nx.draw(
            G,
            pos,
            with_labels=True,
            node_color="lightgreen",
            node_size=1800,
            font_size=10,
            edge_color="gray",
            ax=ax
        )

        st.pyplot(fig)
        plt.close(fig)

    else:
        st.warning("No users available in the graph.")

# ---------------- ADD CONNECTION ----------------

elif page == "Add Connection":

    st.title("Add New Connection")

    with st.form("connection_form"):

        user1 = st.text_input("Enter First User")
        user2 = st.text_input("Enter Second User")

        submit = st.form_submit_button("Add Connection")

        if submit:

            user1 = user1.strip()
            user2 = user2.strip()

            if user1 and user2 and user1 != user2:

                if G.has_edge(user1, user2):
                    st.warning("Connection already exists.")

                else:
                    G.add_edge(user1, user2)
                    st.session_state.graph = G
                    st.success("Connection added successfully!")

            else:
                st.error("Please enter two different user names.")

# ---------------- DATASET UPLOAD ----------------

elif page == "Dataset Upload":

    st.title("Upload Social Network Dataset")

    st.write(
        "Upload a CSV file containing two columns: "
        "User1 and User2."
    )

    uploaded_file = st.file_uploader(
        "Choose CSV File",
        type=["csv"]
    )

    if uploaded_file is not None:

        try:
            df = pd.read_csv(uploaded_file)

            st.subheader("Dataset Preview")
            st.dataframe(df, use_container_width=True)

            required_columns = {"User1", "User2"}

            if required_columns.issubset(df.columns):

                if st.button("Create Network Graph"):

                    new_graph = nx.from_pandas_edgelist(
                        df,
                        source="User1",
                        target="User2"
                    )

                    st.session_state.graph = new_graph

                    st.success(
                        "Dataset successfully converted into graph!"
                    )

                    st.rerun()

            else:
                st.error(
                    "CSV must contain User1 and User2 columns."
                )

        except Exception as e:
            st.error(f"Unable to read dataset: {e}")

# ---------------- CENTRALITY ANALYSIS ----------------

elif page == "Centrality Analysis":

    st.title("Centrality Analysis")

    if total_users > 0:

        degree_centrality = nx.degree_centrality(G)

        betweenness = nx.betweenness_centrality(G)

        closeness = nx.closeness_centrality(G)

        df = pd.DataFrame({
            "User": list(G.nodes()),

            "Degree": [
                degrees[n] for n in G.nodes()
            ],

            "Degree Centrality": [
                degree_centrality[n] for n in G.nodes()
            ],

            "Betweenness Centrality": [
                betweenness[n] for n in G.nodes()
            ],

            "Closeness Centrality": [
                closeness[n] for n in G.nodes()
            ]
        })

        st.subheader("Centrality Results")

        st.dataframe(
            df.round(3),
            use_container_width=True
        )

        st.subheader("Degree Comparison")

        st.bar_chart(
            df.set_index("User")["Degree"]
        )

        most_connected = max(
            degrees,
            key=degrees.get
        )

        st.success(
            f"Most Connected User: {most_connected}"
        )

    else:
        st.warning("No users available.")

# ---------------- COMMUNITY DETECTION ----------------

elif page == "Community Detection":

    st.title("Community Detection")

    if total_edges > 0:

        communities = list(
            nx.community.greedy_modularity_communities(G)
        )

        for i, community in enumerate(communities, 1):

            st.write(
                f"Community {i}: {', '.join(sorted(community))}"
            )

        fig, ax = plt.subplots(figsize=(11, 7))

        pos = nx.spring_layout(G, seed=42)

        colors = {}
        palette = plt.cm.Set2.colors

        for i, community in enumerate(communities):

            for node in community:
                colors[node] = palette[i % len(palette)]

        nx.draw(
            G,
            pos,
            with_labels=True,
            node_color=[colors[n] for n in G.nodes()],
            node_size=1800,
            font_size=10,
            font_weight="bold",
            edge_color="gray",
            ax=ax
        )

        st.pyplot(fig)
        plt.close(fig)

    else:
        st.info("Add connections to detect communities.")

# ---------------- GRAPH STATISTICS ----------------

elif page == "Graph Statistics":

    st.title("Graph Statistics")

    st.metric("Total Nodes", total_users)
    st.metric("Total Edges", total_edges)
    st.metric("Network Density", round(density, 3))

    if total_users > 0:

        average_degree = (
            sum(degrees.values()) / total_users
        )

        st.metric(
            "Average Degree",
            round(average_degree, 2)
        )

        st.subheader("User-wise Connections")

        df = pd.DataFrame({
            "User": list(G.nodes()),
            "Connections": [
                degrees[n] for n in G.nodes()
            ]
        })

        st.dataframe(df, use_container_width=True)

    st.subheader("Connection Dataset")

    connection_df = pd.DataFrame(
        list(G.edges()),
        columns=["User1", "User2"]
    )

    st.dataframe(connection_df, use_container_width=True)

    st.download_button(
        "Download Dataset CSV",
        connection_df.to_csv(index=False),
        file_name="social_network_dataset.csv",
        mime="text/csv"
    )
