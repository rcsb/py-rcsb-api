import requests
from typing import List, Dict
import rustworkx as rx
from rustworkx.visualization import mpl_draw
from rustworkx.visualization import graphviz_draw
import matplotlib.pyplot as plt

pdb_url = 'https://data.rcsb.org/graphql'
node_index_dict: Dict[str, int] = {}  # keys are names, values are indices
edge_index_dict: Dict[str,int] = {}
type_fields_dict: Dict[str, Dict[str, str]] = {}
schema_graph: rx.PyDiGraph = rx.PyDiGraph()


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


root_query = '''
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
'''


def fetch_schema(url) -> Dict[str, str]:
    query = '''
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
    '''
    schema_response = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=url)
    return schema_response.json()


def constructTypeDict(schema, type_fields_dict) -> Dict[str, Dict[str, Dict[str, str]]]:
    all_types_dict = schema['data']['__schema']['types']
    for each_type_dict in all_types_dict:
        type_name = str(each_type_dict['name'])
        fields = each_type_dict['fields']
        field_dict = {}
        if fields is None:
            continue
        else:
            for field in fields:
                field_dict[str(field['name'])] = dict(field['type'])
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
    type_node = makeTypeSubgraph(type_name)  # use a better name
    for field_node in type_node.field_list:
        if field_node.kind == 'SCALAR' or field_node.of_kind == 'SCALAR':
            # print(f"{field_node.name} is SCALAR, LIST, or NON_NULL")
            continue
        else:
            type_name = field_node.type
            if type_name in node_index_dict.keys():
                type_index = node_index_dict[type_name]
                schema_graph.add_edge(parent=field_node.index, child=type_index, edge='draw')
                # print(f"{field_node.name}: {type_name} is already in node_index_dict")
            else:
                # print(f"recurse on {field_node.name} of kind {field_node.kind}, type {type_name}")
                recurseBuildSchema(schema_graph, type_name)
                type_index = node_index_dict[type_name]
                schema_graph.add_edge(parent=field_node.index, child=type_index, edge='draw')  # TODO: change edge value to None


def makeTypeNode(type_name: str) -> TypeNode:
    type_node = TypeNode(type_name)
    index = schema_graph.add_node(type_node)
    node_index_dict[type_name] = index
    type_node.setIndex(index)
    return type_node


def find_kind(field_dict: Dict):
    if field_dict['name'] is not None:
        return field_dict['kind']
    else:
        return find_kind(field_dict['ofType'])


def find_type_name(field_dict: Dict):
    if field_dict['name'] is not None:
        return field_dict['name']
    else:
        return find_type_name(field_dict['ofType'])


def makeFieldNode(parent_type: str, field_name: str) -> FieldNode:
    kind = type_fields_dict[parent_type][field_name]['kind']
    field_type_dict: Dict = type_fields_dict[parent_type][field_name]  # TODO: Mypy is angry
    return_type = find_type_name(field_type_dict)
    field_node = FieldNode(kind, return_type, field_name)
    assert field_node.type is not None  # maybe delete later
    if kind == 'LIST' or kind == 'NON_NULL':  
        of_kind = find_kind(field_type_dict)
        field_node.setofKind(of_kind)
    parent_type_index = node_index_dict[parent_type]
    if field_node.kind == 'SCALAR' or field_node.of_kind == 'SCALAR':
        index = schema_graph.add_child(parent_type_index, field_node, None)
    else:
        index = schema_graph.add_child(parent_type_index, field_node, 'draw')
    node_index_dict[field_name] = index
    field_node.setIndex(index)
    return field_node


# # maybe make this more performant
# def buildSchema(type_fields_dict, node_index_dict):  # iteratively
#     all_type_names = type_fields_dict.keys()
#     for type_name in all_type_names:
#         # print(type_name)
#         field_list = type_fields_dict[type_name].keys()
#         # if the node is already in the graph, retrieve the node. Else, make the node
#         if type_name not in node_index_dict.keys():
#             makeTypeNode(type_name)
#         # type_node_index = type_node.index
#         for field_name in field_list:
#             return_type = type_fields_dict[type_name][field_name]['kind'].upper()
#             # makeFieldNode(type_name, field_name)
#             if return_type == 'SCALAR':
#                 pass
#                 # field_type_name = type_fields_dict[type_name][field_name]['name'] #get the name of scalar type?
#             if return_type == 'OBJECT':
#                 makeFieldNode(type_name, field_name)  # TODO: comment out and uncomment above later
#                 field_type_name = type_fields_dict[type_name][field_name]['name']
#                 if field_type_name not in node_index_dict.keys():
#                     makeTypeNode(field_type_name)
#                 field_type_index = node_index_dict[field_type_name]
#                 field_index = node_index_dict[field_name]
#                 schema_graph.add_edge(field_index, field_type_index, None)
#             if return_type == 'LIST' or return_type == 'NON_NULL':
#                 makeFieldNode(type_name, field_name)   # TODO: comment out and uncomment above later
#                 field_type_name = type_fields_dict[type_name][field_name]['name']    

# VISUALIZATION ONLY
def node_attr(node):
    if type(node) is TypeNode:
        return {'color': 'blue', 'fixedsize': 'True', 'height': '0.2', 'width':'0.2', 'label': f'{node.name}'}
    if type(node) is FieldNode and ((node.kind == 'OBJECT') or (node.of_kind == 'OBJECT')):
        return {'color': 'red', 'fixedsize': 'True', 'height': '0.2', 'width':'0.2', 'label': f'{node.name}'}
    else:
        return {'style': 'invis'}


def edge_attr(edge):
    if edge is None:
        return {'style': 'invis'}
    else:
        return {}

def main():
    schema = fetch_schema(pdb_url)
    constructTypeDict(schema, type_fields_dict)
    # buildSchema(type_fields_dict, node_index_dict)
    recurseBuildSchema(schema_graph, 'Query')
    # mpl_draw(schema_graph, with_labels=True, labels=lambda node: node.name)
    # plt.show()
    # graphviz_draw(schema_graph, filename='graph.png', method='twopi', node_attr_fn=node_attr, edge_attr_fn=edge_attr)
main()