from pyvis.network import Network


def visualize(G, output_file="knowledge_graph.html"):
    """
    Visualize the tree graph using pyvis with full drag-and-drop functionality for nodes.
    Differentiate node types with distinct colors or appearances.
    """
    net = Network(notebook=True, directed=True, height="600px", width="100%")

    # Define styles for different node types
    node_styles = {
        "project_title": {"background": "#FFD700", "border": "#DAA520"},  # Gold
        "core_concept": {"background": "#87CEEB", "border": "#4682B4"},  # Light Blue
        "seminal_paper": {
            "background": "#87CEEB",
            "border": "#4682B4",
        },  # Light Blue (same as core concepts)
        "foundational_topic": {
            "background": "#87CEEB",
            "border": "#4682B4",
        },  # Light Blue (same as core concepts)
        "default": {"background": "white", "border": "black"},  # Default
    }

    for node, data in G.nodes(data=True):
        node_type = data.get("group", "default")  # Use 'group' to determine type
        style = node_styles.get(node_type, node_styles["default"])
        net.add_node(
            node,
            title=data.get("metadata", ""),
            label=node,
            group=node_type,  # Assign group for filtering
            color=style,  # Apply color based on type
        )

    for source, target in G.edges():
        net.add_edge(source, target)

    # Disable hierarchical layout and enable physics for free movement in all directions
    net.set_options(
        """
        {
          "layout": {
            "hierarchical": {
              "enabled": false,
              "direction": "UD",
              "sortMethod": "directed",
              "nodeSpacing": 200, 
              "treeSpacing": 300 
            }
          },
          "nodes": {
            "font": {
              "multi": true,
              "size": 20
            },
            "size": 25,
            "shape": "box",
            "widthConstraint": {
              "maximum": 200
            }
          },
          "interaction": {
            "hover": true,
            "dragNodes": true,
            "selectConnectedEdges": false
          },
          "physics": {
            "enabled": true,
            "stabilization": {
              "enabled": true
            },
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
              "gravitationalConstant": -100,
              "centralGravity": 0.01,
              "springLength": 200,
              "springConstant": 0.05
            },
            "minVelocity": 0.75
          }
        }
        """
    )

    net.show(output_file)
