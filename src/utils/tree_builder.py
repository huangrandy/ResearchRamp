import networkx as nx


def build_tree_graph(
    project_title,
    core_concepts,
    pruned_selected_papers,
    foundational_topics,
):
    """
    Build a tree graph representing the relationships between the project title, core concepts,
    selected papers, and foundational topics.
    """
    G = nx.DiGraph()

    # Add the project title as the root node
    G.add_node(project_title, group="project_title", metadata="Project Title")

    # Add core concepts as children of the project title
    for concept in core_concepts:
        G.add_node(concept, group="core_concept", metadata="Core Concept")
        G.add_edge(project_title, concept)

        # Add selected papers as children of core concepts
        for paper in pruned_selected_papers.get(concept, []):
            # paper_metadata_entry = paper_metadata.get(paper, {})
            G.add_node(
                paper,
                group="seminal_paper",
                metadata=f"Seminal Paper",
            )
            G.add_edge(concept, paper)

            # Add foundational topics as children of selected papers
            for topic in foundational_topics.get(paper, []):
                G.add_node(
                    topic["topic"],
                    group="foundational_topic",
                    metadata=f"Foundational Topic\nResource: {topic.get('resource', 'No resource available')}",
                )
                G.add_edge(paper, topic["topic"])

    return G
