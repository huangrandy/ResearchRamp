import networkx as nx

def build_tree_graph(project_title, core_concepts, pruned_papers, foundational_topics, paper_metadata):
    """
    Build a tree graph for visualization.
    """
    G = nx.DiGraph()

    # Add root node
    G.add_node(project_title, metadata=f"Project Title: {project_title}", group="root", interactive=True, level=0)

    # Add core concepts as children of the root
    for core_index, core in enumerate(core_concepts):
        G.add_node(core, metadata=f"Core Concept: {core}", group=core, interactive=True, level=1)
        G.add_edge(project_title, core)

        # Add pruned selected papers as children of core concepts
        for paper in pruned_papers.get(core, []):
            metadata = paper_metadata.get(paper, {})
            foundational_topic_names = [
                topic_entry.get("topic", "Unknown Topic") for topic_entry in foundational_topics.get(paper, [])
            ]
            metadata_str = (
                f"Paper: {paper}\n"
                f"Authors: {metadata.get('authors', 'Unknown')}\n"
                f"Year: {metadata.get('year', 'Unknown')}\n"
                f"DOI: {metadata.get('doi', 'N/A')}\n"
                f"URL: {metadata.get('url', 'N/A')}\n"
                f"Foundational Topics: {', '.join(foundational_topic_names) if foundational_topic_names else 'None'}"
            )
            G.add_node(paper, metadata=metadata_str, group=core, interactive=True, level=2)
            G.add_edge(core, paper)

            # Add foundational topics as children of each paper
            for topic_entry in foundational_topics.get(paper, []):
                topic = topic_entry.get("topic", "Unknown Topic")
                resource = topic_entry.get("resource", "No Resource Provided")
                metadata_str = (
                    f"Foundational Topic: {topic}\n"
                    f"Resource: {resource}"
                )
                # Ensure the topic node exists
                if not G.has_node(topic):
                    G.add_node(topic, metadata=metadata_str, group=core, interactive=True, level=3)
                # Add an edge from the paper to the topic
                G.add_edge(paper, topic)

    return G
