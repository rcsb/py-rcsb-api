import requests
from typing import List, Dict
import matplotlib.pyplot as plt

try:
    use_networkx = False
    import rustworkx as rx
    from rustworkx.visualization import mpl_draw
    from rustworkx.visualization import graphviz_draw
except ImportError:
    use_networkx = True
    try:
        import networkx as nx
        from scipy.io import wavfile
        import scipy.io.wavfile
        from PIL import Image
        import pygraphviz as pgv
        from networkx.drawing.nx_agraph import write_dot, graphviz_layout, to_agraph
    except ImportError:
        print("Error: Neither rustworkx nor networkx is installed.")
        exit(1)


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


class Schema:
    def __init__(self, pdb_url):
        self.pdb_url = pdb_url
        self.use_networkx = use_networkx
        self.schema_graph = None
        self.node_index_dict = {}
        self.edge_index_dict = {}
        self.type_fields_dict = {}
        self.root_dict = {}
        self.schema = self.fetch_schema("https://data.rcsb.org/graphql")

        if use_networkx:
            self.schema_graph = nx.DiGraph()
        else:
            self.schema_graph = rx.PyDiGraph()

        self.constructRootDict(self.pdb_url)
        self.constructTypeDict(self.schema, self.type_fields_dict)
        self.recurseBuildSchema(self.schema_graph, "Query")

    def constructRootDict(self, url: str) -> Dict[str, str]:
        root_query = """
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
        response = requests.post(headers={"Content-Type": "application/graphql"}, data=root_query, url=url).json()
        root_fields_list = response["data"]["__schema"]["queryType"]["fields"]
        for name_arg_dict in root_fields_list:
            root_name = name_arg_dict["name"]
            arg_dict_list = name_arg_dict["args"]
            for arg_dict in arg_dict_list:
                arg_name = arg_dict["name"]
                arg_kind = arg_dict["type"]["ofType"]["kind"]
                arg_type = self.find_type_name(arg_dict["type"]["ofType"])
                if root_name not in self.root_dict.keys():
                    self.root_dict[root_name] = []
                self.root_dict[root_name].append({"name": arg_name, "kind": arg_kind, "type": arg_type})
        return self.root_dict

    def fetch_schema(self, url: str) -> Dict[str, str]:
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

    def constructTypeDict(self, schema, type_fields_dict) -> Dict[str, Dict[str, Dict[str, str]]]:
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

    def makeTypeSubgraph(self, type_name) -> TypeNode:
        field_name_list = self.type_fields_dict[type_name].keys()
        field_node_list = []
        type_node = self.makeTypeNode(type_name)
        for field_name in field_name_list:
            parent_type_name = type_name
            field_node = self.makeFieldNode(parent_type_name, field_name)
            field_node_list.append(field_node)
        type_node.setFieldList(field_node_list)
        return type_node

    def recurseBuildSchema(self, schema_graph, type_name):
        type_node = self.makeTypeSubgraph(type_name)
        for field_node in type_node.field_list:
            if field_node.kind == "SCALAR" or field_node.of_kind == "SCALAR":
                continue
            else:
                type_name = field_node.type
                if type_name in self.node_index_dict.keys():
                    type_index = self.node_index_dict[type_name]
                    if use_networkx:
                        schema_graph.add_edge(field_node.index, type_index)
                    else:
                        schema_graph.add_edge(parent=field_node.index, child=type_index, edge="draw")
                else:
                    self.recurseBuildSchema(schema_graph, type_name)
                    type_index = self.node_index_dict[type_name]
                    if self.use_networkx:
                        schema_graph.add_edge(field_node.index, type_index)
                    else:
                        schema_graph.add_edge(parent=field_node.index, child=type_index, edge="draw")  # TODO: change edge value to None

    def makeTypeNode(self, type_name: str) -> TypeNode:
        type_node = TypeNode(type_name)
        if self.use_networkx:
            index = len(self.schema_graph.nodes)
            self.schema_graph.add_node(index, type_node=type_node)
        else:
            index = self.schema_graph.add_node(type_node)
        self.node_index_dict[type_name] = index
        type_node.setIndex(index)
        return type_node

    def find_kind(self, field_dict: Dict):
        if field_dict["name"] is not None:
            return field_dict["kind"]
        else:
            return self.find_kind(field_dict["ofType"])

    def find_type_name(self, field_dict: Dict):
        if field_dict["name"] is not None:
            return field_dict["name"]
        else:
            return self.find_type_name(field_dict["ofType"])

    def makeFieldNode(self, parent_type: str, field_name: str) -> FieldNode:
        kind = self.type_fields_dict[parent_type][field_name]["kind"]
        field_type_dict: Dict = self.type_fields_dict[parent_type][field_name]  # TODO: Mypy is angry
        return_type = self.find_type_name(field_type_dict)
        field_node = FieldNode(kind, return_type, field_name)
        assert field_node.type is not None
        if kind == "LIST" or kind == "NON_NULL":
            of_kind = self.find_kind(field_type_dict)
            field_node.setofKind(of_kind)
        parent_type_index = self.node_index_dict[parent_type]
        if self.use_networkx:
            index = len(self.schema_graph.nodes)
            self.schema_graph.add_node(index, field_node=field_node)
            self.schema_graph.add_edge(parent_type_index, index)
        else:
            if field_node.kind == "SCALAR" or field_node.of_kind == "SCALAR":
                index = self.schema_graph.add_child(parent_type_index, field_node, None)
            else:
                index = self.schema_graph.add_child(parent_type_index, field_node, "draw")
        self.node_index_dict[field_name] = index
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
    def node_attr(self, node):
        if self.use_networkx:
            if isinstance(node, TypeNode):
                return {"color": "blue", "label": f"{node.name}"}
            if isinstance(node, FieldNode) and ((node.kind == "OBJECT") or (node.of_kind == "OBJECT")):
                return {"color": "red", "label": f"{node.name}"}
            else:
                return {"style": "invis"}
        else:
            if type(node) is TypeNode:
                return {"color": "blue", "fixedsize": "True", "height": "0.2", "width": "0.2", "label": f"{node.name}"}
            if type(node) is FieldNode and ((node.kind == "OBJECT") or (node.of_kind == "OBJECT")):
                return {"color": "red", "fixedsize": "True", "height": "0.2", "width": "0.2", "label": f"{node.name}"}


    def edge_attr(self, edge):
        if edge is None:
            return {"style": "invis"}
        else:
            return {}


    def construct_query(self, input_ids, input_type, return_data_list):
        if use_networkx:
            return self.___construct_query_networkx(input_ids, input_type, return_data_list)
        else:
            return self.___construct_query_rustworkx(input_ids, input_type, return_data_list)

    def ___construct_query_networkx(self, input_ids, input_type, return_data_list): #incomplete function
        if input_type not in self.root_dict.keys():
            raise ValueError(f"Unknown input type: {input_type}")

        input_ids = [input_ids] if isinstance(input_ids, str) else input_ids
        query_name = input_type
        attr_list = self.root_dict[input_type]
        attr_name = attr_name = [id["name"] for id in attr_list]  
        field_names = {}
        start_node_index = None
        for node in self.schema_graph.nodes():
                node_data = self.schema_graph.nodes[node]
                if node_data.get('name') == input_type:
                    start_node_index = node_data.get('index')
                    start_node_name = node_data.get('name')
                    start_node_type = node_data.get('type')
                    break
        target_node_indices = []
        for return_data in return_data_list:
                for node, node_data in self.schema_graph.nodes(data=True):
                    if isinstance(node_data, dict) and node_data.get('name') == return_data:
                        target_node_indices.append(node_data.get('index'))
                        break
        all_paths = {target_node: nx.shortest_path(self.schema_graph, start_node_index, target_node) for target_node in target_node_indices}
        query = "query"
        return query

    def ___construct_query_rustworkx(self, input_ids, input_type, return_data_list):
        if input_type not in self.root_dict.keys():
            raise ValueError(f"Unknown input type: {input_type}")

        input_ids = [input_ids] if isinstance(input_ids, str) else input_ids
        query_name = input_type
        attr_list = self.root_dict[input_type]
        attr_name = attr_name = [id["name"] for id in attr_list]  
        field_names = {}

        start_node_index = None
        for node in self.schema_graph.node_indices():
            node_data = self.schema_graph[node]
            if node_data.name == input_type:
                start_node_index = node_data.index
                start_node_name = node_data.name
                sart_node_type = node_data.type
                break

        target_node_indices = []
        for return_data in return_data_list:
            for node in self.schema_graph.node_indices():
                node_data = self.schema_graph[node]
                if isinstance(node_data, FieldNode) and node_data.name == return_data:
                    target_node_indices.append(node_data.index)
                    break
        # print(target_node_indices)

        # Get all shortest paths from the start node to each target node
        all_paths = {target_node: rx.digraph_all_shortest_paths(self.schema_graph, start_node_index, target_node) for target_node in target_node_indices}
        final_fields = {}

        def get_descendant_fields(schema_graph, node, visited=None):
            if visited is None:
                visited = set()

            result = []
            children = list(schema_graph.neighbors(node))

            for child in children:
                if child in visited:
                    continue
                visited.add(child)

                child_data = schema_graph[child]
                if isinstance(child_data, FieldNode):
                    child_descendants = get_descendant_fields(schema_graph, child, visited)
                    if child_descendants:
                        result.append({child_data.name: child_descendants})
                    else:
                        result.append(child_data.name)
                elif isinstance(child_data, TypeNode):
                    type_descendants = get_descendant_fields(schema_graph, child, visited)
                    if type_descendants:
                        result.extend(type_descendants)
                    else:
                        result.append(child_data.name)

            if len(result) == 1:
                return result[0]
            return result

        for target_node in target_node_indices:
            target_data = self.schema_graph[target_node]
            if isinstance(target_data, FieldNode):
                final_fields[target_data.name] = get_descendant_fields(self.schema_graph, target_node)

        # print(final_fields)

        for target_node in target_node_indices:
            node_data = self.schema_graph[target_node]
            if isinstance(node_data, FieldNode):
                target_node_name = node_data.name
                field_names[target_node_name] = []
            for each_path in all_paths[target_node]:
                for node in each_path:
                    node_data = self.schema_graph[node]
                    if isinstance(node_data, FieldNode) and node_data.name != input_type:
                        field_node_name = node_data.name
                        field_names[target_node_name].append(field_node_name)
        # print(field_names)

        # def create_final_query(final_fields, field_names):
        #     final_query = {}
        #     for key in field_names:
        #         if key in final_fields:
        #             # Find the first matching value in field_names
        #             for value in field_names[key]:
        #                 if value == key:
        #                     final_query[key] = field_names[key][: field_names[key].index(key)] + [{key: final_fields[key]}] + field_names[key][field_names[key].index(key) + 1 :]
        #                     break
        #             else:
        #                 final_query[key] = field_names[key]
        #         else:
        #             final_query[key] = field_names[key]
        #     return final_query

        # final_query = create_final_query(final_fields, field_names)
        # print(final_query)
        # with open('final_query_prettified.txt', 'w') as f:
        #     json.dump(final_query, f, indent=4)

        # root query
        query = "{ " + input_type + "("
        for i, attr in enumerate(attr_name):
            query += attr + ": [\"" + "\", \"".join(input_ids) + "\"]"
            if i < len(attr_name) - 1:
                query += ", "
        query += ") {\n"

        for field, field_info in field_names.items():
            if field in field_info:
                query += "  " + field_info[0] + " {\n"
                for subfield in field_info[1:]:
                    if subfield != field:
                        query += "    " + subfield + " {\n"
                    else:
                        query += "    " + subfield + " {\n"
                        break
                if field in final_fields:
                    for final_field in final_fields[field]:
                        if isinstance(final_field, dict):
                            for key, value in final_field.items():
                                query += "      " + key + " {\n"
                                for v in value:
                                    query += "        " + v + "\n"
                                query += "      }\n"
                        else:
                            query += "      " + final_field + "\n"
                query += "  }\n"
            else:
                query += "  " + field + " {\n"
                query += "  }\n"

        query += "}}"

        return query


# def main():
#     schema = fetch_schema(pdb_url)
#     if use_networkx:
#         constructRootDict(pdb_url)
#     constructTypeDict(schema, type_fields_dict)
#     recurseBuildSchema(schema_graph, "Query")
#     input_ids = ["4HHB", "4HHB"]
#     input_type = "entry"
#     return_data_list = ["exptl", "rcsb_polymer_instance_annotation"]

#     query = construct_query(input_ids, input_type, return_data_list)
#     print("Constructed Query:")
#     print(query)
#     # if use_networkx:
#     #   # Convert to AGraph for Graphviz
#     #   A = to_agraph(schema_graph)

#     #   # Apply node attributes
#     #   for node in schema_graph.nodes(data=True):
#     #       n = A.get_node(node[0])
#     #       attrs = node_attr(node[1].get("type_node", node[1].get("field_node")))
#     #       for attr, value in attrs.items():
#     #           n.attr[attr] = value

#     #   # Apply edge attributes
#     #   for edge in A.edges():
#     #       attrs = edge_attr(edge)
#     #       for attr, value in attrs.items():
#     #           edge.attr[attr] = value

#     #   A.draw("graph.png", prog="dot")

#     #   img = Image.open("graph.png")
#     #   img.show()
#     # else:
#     # buildSchema(type_fields_dict, node_index_dict)
#     # mpl_draw(schema_graph, with_labels=True, labels=lambda node: node.name)
#     # plt.show()
#     # graphviz_draw(schema_graph, filename='graph.png', method='twopi', node_attr_fn=node_attr, edge_attr_fn=edge_attr)
# main()