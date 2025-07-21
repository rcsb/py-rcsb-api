import json
from rustworkx import PyDiGraph, descendants
import networkx as nx
import matplotlib.pyplot as plt
from rustworkx import bfs_successors
from rich import print as rprint


LEAF_TYPES = {"string", "number", "integer", "date", "boolean"}


def add_attribute_nodes(graph, parent_index, attributes, prefix="", service=None):
    for attr_name, attr_data in attributes.items():
        full_name = f"{prefix}.{attr_name}" if prefix else attr_name
        attr_type = attr_data.get("type")

        if attr_type in LEAF_TYPES:
            metadata = {
                "name": full_name,
                "type": attr_type,
                "description": attr_data.get("description"),
                "rcsb_search_context": attr_data.get("rcsb_search_context"),
                "rcsb_units": attr_data.get("rcsb_units"),
                "service": [service]
            }
            prexisting, prexisting_root_attribute_idx, graph = check_and_update_preexisting_nodes(graph, full_name, service, metadata)
            if prexisting:
                child_index = prexisting_root_attribute_idx
            else:
                child_index = graph.add_node(metadata)
                graph.add_edge(parent_index, child_index, None)

        elif attr_type == "object" and "properties" in attr_data:
            metadata = {
                "name": full_name,
                "type": "object",
                "description": attr_data.get("description"),
                "service": [service],
            }
            prexisting, prexisting_root_attribute_idx, graph = check_and_update_preexisting_nodes(graph, full_name, service, metadata)
            if prexisting:
                intermediate_index = prexisting_root_attribute_idx
            else:
                intermediate_index = graph.add_node(metadata)
                graph.add_edge(parent_index, intermediate_index, None)
            add_attribute_nodes(graph, intermediate_index, attr_data["properties"], prefix=full_name, service=service)

        elif attr_type == "array" and isinstance(attr_data.get("items"), dict):
            # handle array of objects
            metadata = {
                "name": full_name,
                "type": "array",
                "description": attr_data.get("description"),
                "service": [service],
            }
            prexisting, prexisting_root_attribute_idx, graph = check_and_update_preexisting_nodes(graph, full_name, service, metadata)
            if prexisting:
                intermediate_index = prexisting_root_attribute_idx
            else:
                intermediate_index = graph.add_node(metadata)
                # if "annotation_lineage" in full_name or "chem_comp_annotation" in full_name:
                #     print("HERE ARRAY", intermediate_index, full_name, metadata)
                graph.add_edge(parent_index, intermediate_index, None)
            items = attr_data["items"]
            if items.get("type") == "object" and "properties" in items:
                add_attribute_nodes(graph, intermediate_index, items["properties"], prefix=full_name, service=service)
            elif items.get("type") in LEAF_TYPES:
                # array of primitives
                metadata = {
                    "name": f"{full_name}[]",
                    "type": items.get("type"),
                    "description": items.get("description"),
                    "service": [service],
                }
                prexisting, prexisting_root_attribute_idx, graph = check_and_update_preexisting_nodes(graph, full_name, service, metadata)
                if prexisting:
                    child_index = prexisting_root_attribute_idx
                else:
                    child_index = graph.add_node(metadata)
                    graph.add_edge(intermediate_index, child_index, None)


def build_graph_from_schema(schema, schema_type=None, graph=None):
    if not graph:
        graph = PyDiGraph()
    root_properties = schema.get("properties", {})

    for category_name, category_info in root_properties.items():
        root_metadata = {
            "name": category_name,
            "type": category_info.get("type", "object"),
            "rcsb_search_context": category_info.get("rcsb_search_context"),
            "description": category_info.get("description"),  # leave as string and only make a list if the two descriptions are different
            "service": [schema_type]  # always leave this as a list, so can just check if len(list) == 2 or not.
        }
        # rprint("root_metadata", root_metadata)
        # How about instead of updating the same node, you create separate nodes for each service?
        prexisting, prexisting_root_attribute_idx, graph = check_and_update_preexisting_nodes(graph, category_name, schema_type, root_metadata)
        if prexisting:
            root_index = prexisting_root_attribute_idx
        else:
            root_index = graph.add_node(root_metadata)
        # print("category_name, root_index", category_name, root_index)

        if category_info.get("type") == "object" and "properties" in category_info:
            add_attribute_nodes(graph, root_index, category_info["properties"], prefix=category_name, service=schema_type)
        elif category_info.get("type") == "array":
            items = category_info.get("items", {})
            if items.get("type") == "object" and "properties" in items:
                add_attribute_nodes(graph, root_index, items["properties"], prefix=category_name, service=schema_type)

    return graph

def check_and_update_preexisting_nodes(graph, name, schema_type, incoming_node_metadata):
    prexisting_root_attribute_idx = find_node_index_by_name(graph, name)
    if prexisting_root_attribute_idx:
        # update the node with extended serviceType and descriptions
        # print("HERE")
        # rprint(get_node_data(graph, prexisting_root_attribute_idx, data_key_list=["service", "description"]))
        prexisting_node_data_to_append = get_node_data(graph, prexisting_root_attribute_idx, data_key_list=["service", "description"])
        prexisting_node_data_to_append["service"].append(schema_type)
        if incoming_node_metadata["description"] != prexisting_node_data_to_append["description"]:
            prexisting_node_data_to_append["description"] = [prexisting_node_data_to_append["description"], incoming_node_metadata["description"]]
        # rprint(get_node_data(graph, prexisting_root_attribute_idx, data_key_list=["service", "description"]))
        # print("END HERE")
        return True, prexisting_root_attribute_idx, graph
    return False, None, graph


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
    ## TODO: This can be sped up by creating a mapping dictionary up front and then referring to it here
    for i in graph.node_indices():
        if graph[i]["name"] == name:
            return i
    return None

def get_node_data(graph, index, data_key_list=None, return_index=False):
    node_data = graph[index]
    # print(index, node_data["name"], node_data["type"], node_data.get("description"))
    if data_key_list:
        node_data_return = {k: node_data[k] for k in data_key_list}
    else:
        node_data_return = node_data
    #
    if return_index:
        node_data_return.update({"node_index": index})
    return node_data_return


def get_descendants(graph, root_name, names_only=False):
    root_index = find_node_index_by_name(graph, root_name)
    # print(root_name, root_index)
    if root_index is None:
        print(f"Node '{root_name}' not found.")
        return

    print(f"Descendants of node '{root_name}' (index {root_index}):")
    children_indexes = descendants(graph, root_index)
    if names_only:
        desc_list = sorted([get_node_data(graph, ci, data_key_list=["name"]).get("name") for ci in children_indexes], key=len)
    else:
        desc_list = [get_node_data(graph, ci) for ci in children_indexes]
    # rprint(desc_list)
    return desc_list


def construct_complete_schema_graph_object():
    import pathlib
    import pprint
    import requests

    schema_files = {
        "text": "https://search.rcsb.org/rcsbsearch/v2/metadata/schema",
        "text_chem": "https://search.rcsb.org/rcsbsearch/v2/metadata/chemical/schema"
    }
    #
    graph = None
    #
    for service, schema_file in schema_files.items():
        print(f"Processing {service} schema - {schema_file}")
        response = requests.get(schema_file)
        response.raise_for_status()  # will raise an error if request fails
        raw_schema_data = response.json()

        # Build the graph
        graph = build_graph_from_schema(raw_schema_data, service, graph)

    return graph


def delete_unsearchable_leaf_nodes(graph):
    to_remove = []

    for node_index in range(graph.num_nodes()):
        node_data = graph[node_index]

        # Skip if node has outgoing edges (i.e., not a leaf)
        if graph.out_degree(node_index) > 0:
            continue

        # Check if "rcsb_search_context" is missing or None
        if node_data.get("rcsb_search_context") is None:
            if node_data["name"] == "rcsb_ligand_neighbors.ligand_asym_id":
            # if node_data["name"] == "rcsb_ligand_neighbors.comp_id":
                print("deleting node", node_data)

            to_remove.append(node_index)

    # Remove nodes in reverse order to preserve indices during deletion
    for idx in sorted(to_remove, reverse=True):
        # rprint(idx, get_node_data(graph, idx))
        # print(graph[idx]["name"])
        if graph[idx]["name"] == "rcsb_ligand_neighbors.ligand_asym_id":
            print("deleting node", graph[idx])
        graph.remove_node(idx)

    print(f"Removed {len(to_remove)} unsearchable leaf node attributes")
    print(f"Total number of searchable nodes retained in graph: {graph.num_nodes()}")



def count_nodes_with_service_text_and_chem(graph):
    count = 0
    for node_data in graph.nodes():
        if node_data.get("service") == ['text', 'text_chem']:
            count += 1
    print(f"Found {count} node(s) with service = ['text', 'text_chem']")
    return count



if __name__ == "__main__":

    graph = construct_complete_schema_graph_object()

    # rx_graph = build_graph_from_schema(schema)
    # nx_graph = rustworkx_to_networkx(graph)
    # visualize_graph(nx_graph)
    descL = get_descendants(graph, "rcsb_chem_comp_annotation")
    # rprint(sorted(descL, key=lambda x: len(x["name"])))

    descL = get_descendants(graph, "rcsb_ligand_neighbors")
    rprint(sorted(descL, key=lambda x: len(x["name"])))

    delete_unsearchable_leaf_nodes(graph)

    # ** !!! IMPORTANT: graph.node_indices() retains the original index of each node—when you do graph[idx], it does NOT grab the ith element, but grabs the node originally indexed with that index!
    print(find_node_index_by_name(graph, "pdbx_struct_assembly"))
    # rprint(graph[35])

    # exit()
    print(find_node_index_by_name(graph, "rcsb_ligand_neighbors.ligand_asym_id"))
    print(graph[279])

    descL = get_descendants(graph, "rcsb_ligand_neighbors")
    rprint(sorted(descL, key=lambda x: len(x["name"])))

    count = count_nodes_with_service_text_and_chem(graph)

    print(type(graph.nodes()[0]))
