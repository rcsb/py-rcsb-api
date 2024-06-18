import requests
from typing import List, Dict
import networkx as nx
import matplotlib.pyplot as plt
from scipy.io import wavfile
import scipy.io.wavfile
from PIL import Image

# import pygraphviz as pgv
# from networkx.drawing.nx_agraph import write_dot, graphviz_layout, to_agraph

pdb_url = "https://data.rcsb.org/graphql"
node_index_dict: Dict[str, int] = {}  # keys are names, values are indices
edge_index_dict: Dict[str, int] = {}
type_fields_dict: Dict[str, Dict[str, str]] = {}
root_dict: Dict[str, List[Dict[str, str]]] = {}
schema_graph = nx.DiGraph()


class FieldNode:
    def __init__(self, kind, type, name):
        self.name = name
        self.kind = kind
        self.of_kind = None
        self.type = type
        self.index = None

    def __str__(self):
        return f"Field Object name: {self.name}, Kind: {self.kind}, Type: {self.type}, Index if set: {self.index}"

    def setIndex(self, index: int):
        self.index = index

    def setofKind(self, of_kind: str):
        self.of_kind = of_kind


class TypeNode:
    def __init__(self, name: str):
        self.name = name
        self.index = None
        self.field_list = None

    def setIndex(self, index: int):
        self.index = index

    def setFieldList(self, field_list: List[FieldNode]):
        self.field_list = field_list


def find_kind(field_dict: Dict):
    if field_dict["name"] is not None:
        return field_dict["kind"]
    else:
        return find_kind(field_dict["ofType"])


def find_type_name(field_dict: Dict):
    if field_dict["name"] is not None:
        return field_dict["name"]
    else:
        return find_type_name(field_dict["ofType"])


def constructRootDict(url: str) -> Dict[str, str]:
    get_root_query = """
    query IntrospectionQuery{
      __schema{
        queryType{
          fields{
            name
            args{
              name
              type{
                ofType{
                  name
                  kind
                  ofType{
                    kind
                    name
                    ofType{
                      name
                      kind
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    response = requests.post(headers={"Content-Type": "application/graphql"}, data=get_root_query, url=url).json()
    root_fields_list = response["data"]["__schema"]["queryType"]["fields"]
    for name_arg_dict in root_fields_list:
        root_name = name_arg_dict["name"]
        arg_dict_list = name_arg_dict["args"]
        for arg_dict in arg_dict_list:
            arg_name = arg_dict["name"]
            arg_kind = arg_dict["type"]["ofType"]["kind"]
            arg_type = find_type_name(arg_dict["type"]["ofType"])
            if root_name not in root_dict.keys():
                root_dict[root_name] = []
            root_dict[root_name].append({"name": arg_name, "kind": arg_kind, "type": arg_type})
    return root_dict


def fetchSchema(url: str) -> Dict[str, str]:
    query = """
        query IntrospectionQuery {
          __schema {

            queryType { name }
            types {
              ...FullType
            }
            directives {
              name
              description

              locations
              args {
                ...InputValue
              }
            }
          }
        }

        fragment FullType on __Type {
          kind
          name
          description

          fields(includeDeprecated: true) {
            name
            description
            args {
              ...InputValue
            }
            type {
              ...TypeRef
            }
            isDeprecated
            deprecationReason
          }
          inputFields {
            ...InputValue
          }
          interfaces {
            ...TypeRef
          }
          enumValues(includeDeprecated: true) {
            name
            description
            isDeprecated
            deprecationReason
          }
          possibleTypes {
            ...TypeRef
          }
        }

        fragment InputValue on __InputValue {
          name
          description
          type { ...TypeRef }
          defaultValue


        }

        fragment TypeRef on __Type {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                    ofType {
                      kind
                      name
                      ofType {
                        kind
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
    """
    schema_response = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=url)
    return schema_response.json()


def constructTypeDict(schema, type_fields_dict) -> Dict[str, Dict[str, Dict[str, str]]]:
    all_types_dict = schema["data"]["__schema"]["types"]
    for each_type_dict in all_types_dict:
        type_name = str(each_type_dict["name"])
        fields = each_type_dict["fields"]
        field_dict = {}
        if fields is None:
            continue
        else:
            for field in fields:
                field_dict[str(field["name"])] = dict(field["type"])
        type_fields_dict[type_name] = field_dict
    return type_fields_dict


def makeTypeSubgraph(type_name) -> TypeNode:
    field_name_list = type_fields_dict[type_name].keys()
    field_node_list = []
    type_node = makeTypeNode(type_name)
    for field_name in field_name_list:
        parent_type_name = type_name
        field_node = makeFieldNode(parent_type_name, field_name)
        field_node_list.append(field_node)
    type_node.setFieldList(field_node_list)
    return type_node


def recurseBuildSchema(schema_graph, type_name):
    type_node = makeTypeSubgraph(type_name)
    for field_node in type_node.field_list:
        if field_node.kind == "SCALAR" or field_node.of_kind == "SCALAR":
            continue
        else:
            type_name = field_node.type
            if type_name in node_index_dict.keys():
                type_index = node_index_dict[type_name]
                schema_graph.add_edge(field_node.index, type_index)
            else:
                recurseBuildSchema(schema_graph, type_name)
                type_index = node_index_dict[type_name]
                schema_graph.add_edge(field_node.index, type_index)


def makeTypeNode(type_name: str) -> TypeNode:
    type_node = TypeNode(type_name)
    index = len(schema_graph.nodes)
    schema_graph.add_node(index, type_node=type_node)
    node_index_dict[type_name] = index
    type_node.setIndex(index)
    return type_node


def makeFieldNode(parent_type: str, field_name: str) -> FieldNode:
    kind = type_fields_dict[parent_type][field_name]["kind"]
    field_type_dict: Dict[any, any] = type_fields_dict[parent_type][field_name]
    return_type = find_type_name(field_type_dict)
    field_node = FieldNode(kind, return_type, field_name)
    assert field_node.type is not None
    if kind == "LIST" or kind == "NON_NULL":
        of_kind = find_kind(field_type_dict)
        field_node.setofKind(of_kind)
    parent_type_index = node_index_dict[parent_type]
    index = len(schema_graph.nodes)
    schema_graph.add_node(index, field_node=field_node)
    schema_graph.add_edge(parent_type_index, index)
    node_index_dict[field_name] = index
    field_node.setIndex(index)
    return field_node


def node_attr(node):
    if isinstance(node, TypeNode):
        return {"color": "blue", "label": f"{node.name}"}
    if isinstance(node, FieldNode) and ((node.kind == "OBJECT") or (node.of_kind == "OBJECT")):
        return {"color": "red", "label": f"{node.name}"}
    else:
        return {"style": "invis"}


def edge_attr(edge):
    if edge is None:
        return {"style": "invis"}
    else:
        return {}


def main():
    schema = fetchSchema(pdb_url)
    constructRootDict(pdb_url)
    constructTypeDict(schema, type_fields_dict)
    recurseBuildSchema(schema_graph, "Query")

    # Convert to AGraph for Graphviz
    A = to_agraph(schema_graph)

    # Apply node attributes
    for node in schema_graph.nodes(data=True):
        n = A.get_node(node[0])
        attrs = node_attr(node[1].get("type_node", node[1].get("field_node")))
        for attr, value in attrs.items():
            n.attr[attr] = value

    # Apply edge attributes
    for edge in A.edges():
        attrs = edge_attr(edge)
        for attr, value in attrs.items():
            edge.attr[attr] = value

    A.draw("graph.png", prog="dot")

    img = Image.open("graph.png")
    img.show()


main()
