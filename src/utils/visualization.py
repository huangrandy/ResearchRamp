from pyvis.network import Network


def visualize(G, output_file="tree_graph.html"):
    """
    Visualize the tree graph using pyvis with full drag-and-drop functionality for nodes.
    Enable toggling nodes to mark them as "complete" and filtering by group.
    """
    net = Network(notebook=True, directed=True)
    for node, data in G.nodes(data=True):
        net.add_node(
            node,
            title=data.get("metadata", ""),
            label=node,
            group=data.get(
                "group", "default"
            ),  # Assign group for background highlighting
            color={"background": "white", "border": "black"},  # Default color
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
              "treeSpacing": 100
            }
          },
          "nodes": {
            "font": {
              "multi": true,
              "size": 10
            },
            "size": 15,
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
            "enabled": false,
            "stabilization": {
              "enabled": true
            },
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 100,
              "springConstant": 0.08
            },
            "minVelocity": 0.75
          }
        }
        """
    )

    net.show(output_file)
