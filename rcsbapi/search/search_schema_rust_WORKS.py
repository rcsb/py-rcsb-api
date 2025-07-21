import json
from rustworkx import PyDiGraph, descendants
import networkx as nx
import matplotlib.pyplot as plt
from rustworkx import bfs_successors
from rich import print as rprint

LEAF_TYPES = {"string", "number", "integer", "date", "boolean"}

def add_attribute_nodes(graph, parent_index, attributes, prefix=""):
    for attr_name, attr_data in attributes.items():
        full_name = f"{prefix}.{attr_name}" if prefix else attr_name
        attr_type = attr_data.get("type")

        if attr_type in LEAF_TYPES:
            metadata = {
                "name": full_name,
                "type": attr_type,
                "description": attr_data.get("description"),
                "rcsb_search_context": attr_data.get("rcsb_search_context"),
                "rcsb_full_text_priority": attr_data.get("rcsb_full_text_priority"),
                "rcsb_units": attr_data.get("rcsb_units"),
            }
            child_index = graph.add_node(metadata)
            # if "annotation_lineage" in full_name or "chem_comp_annotation" in full_name:
            #     print("HERE LEAF", child_index, full_name, metadata)
            graph.add_edge(parent_index, child_index, None)

        elif attr_type == "object" and "properties" in attr_data:
            metadata = {
                "name": full_name,
                "type": "object",
                "description": attr_data.get("description")
            }
            intermediate_index = graph.add_node(metadata)
            # if "annotation_lineage" in full_name or "chem_comp_annotation" in full_name:
            #     print("HERE ARRAY", intermediate_index, full_name, metadata)
            graph.add_edge(parent_index, intermediate_index, None)
            add_attribute_nodes(graph, intermediate_index, attr_data["properties"], prefix=full_name)

        elif attr_type == "array" and isinstance(attr_data.get("items"), dict):
            # handle array of objects
            metadata = {
                "name": full_name,
                "type": "array",
                "description": attr_data.get("description")
            }
            intermediate_index = graph.add_node(metadata)
            # if "annotation_lineage" in full_name or "chem_comp_annotation" in full_name:
            #     print("HERE ARRAY", intermediate_index, full_name, metadata)
            graph.add_edge(parent_index, intermediate_index, None)
            items = attr_data["items"]
            if items.get("type") == "object" and "properties" in items:
                add_attribute_nodes(graph, intermediate_index, items["properties"], prefix=full_name)
            elif items.get("type") in LEAF_TYPES:
                # array of primitives
                metadata = {
                    "name": f"{full_name}[]",
                    "type": items.get("type"),
                    "description": items.get("description"),
                }
                child_index = graph.add_node(metadata)
                graph.add_edge(intermediate_index, child_index, None)


def build_graph_from_schema(schema):
    graph = PyDiGraph()
    root_properties = schema.get("properties", {})

    for category_name, category_info in root_properties.items():
        root_metadata = {
            "name": category_name,
            "type": category_info.get("type", "object"),
            "description": category_info.get("description")
        }
        root_index = graph.add_node(root_metadata)

        if category_info.get("type") == "object" and "properties" in category_info:
            add_attribute_nodes(graph, root_index, category_info["properties"], prefix=category_name)
        elif category_info.get("type") == "array":
            items = category_info.get("items", {})
            if items.get("type") == "object" and "properties" in items:
                add_attribute_nodes(graph, root_index, items["properties"], prefix=category_name)

    return graph


def rustworkx_to_networkx(rust_graph):
    G = nx.DiGraph()
    for i, node in enumerate(rust_graph.nodes()):
        G.add_node(i, **node)
    for edge in rust_graph.edge_list():
        G.add_edge(edge[0], edge[1])
    return G

def visualize_graph(nx_graph, max_nodes=50):
    # Only draw a subset of nodes for clarity if too large
    if len(nx_graph.nodes) > max_nodes:
        print(f"Graph too large to visualize ({len(nx_graph.nodes)} nodes). Truncating to {max_nodes}.")
        nx_graph = nx.subgraph(nx_graph, list(nx_graph.nodes)[:max_nodes])

    pos = nx.spring_layout(nx_graph, seed=42)  # Layout for positioning
    labels = {i: data.get("name", "") for i, data in nx_graph.nodes(data=True)}
    plt.figure(figsize=(15, 12))
    nx.draw(nx_graph, pos, labels=labels, with_labels=True, node_color="lightblue", edge_color="gray", node_size=800, font_size=8)
    plt.title("Schema Graph (subset)")
    plt.show()



def find_node_index_by_name(graph, name):
    for i, data in enumerate(graph.nodes()):
        if data.get("name") == name:
            return i
    return None

def get_node_data(graph, index):
    node_data = graph[index]
    # print(index, node_data["name"], node_data["type"], node_data.get("description"))
    print(index, node_data)
    return node_data


def print_descendants(graph, root_name):
    root_index = find_node_index_by_name(graph, root_name)
    # print(root_name, root_index)
    if root_index is None:
        print(f"Node '{root_name}' not found.")
        return

    print(f"Descendants of node '{root_name}' (index {root_index}):")
    children_indexes = descendants(graph, root_index)
    for ci in children_indexes:
        get_node_data(graph, ci)


    # for x, child_nodes in bfs_successors(graph, root_index):
    #     # rprint(x)
    #     rprint(x, child_nodes)
    #     for child_node in child_nodes:
    #         child_name = 
    #         node_data = graph[child_index]  # child_index is guaranteed to be an int
    #         print(f"- {node_data.get('name')} (type: {node_data.get('type')})")



if __name__ == "__main__":
    import pathlib
    import pprint

    # Load the schema file
    path = pathlib.Path("/Users/dennispiehl/rcsb/py-rcsb-api/rcsbapi/search/resources/structure_schema_jul8.json")
    with path.open("r", encoding="utf-8") as f:
        schema = json.load(f)

    # Build the graph
    graph = build_graph_from_schema(schema)

    # # Print out a few nodes for inspection
    # x = 0
    # for i, node in enumerate(graph.nodes()):
    #     print(f"Node {i}:")
    #     pprint.pprint(node)
    #     x += 1
    #     if x == 10:
    #         break

    # rx_graph = build_graph_from_schema(schema)
    # nx_graph = rustworkx_to_networkx(graph)
    # visualize_graph(nx_graph)
    print_descendants(graph, "rcsb_chem_comp_annotation")

    rprint(dir(graph))
