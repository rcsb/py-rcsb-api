import requests
from typing import List, Dict, Union
import logging
import re

use_networkx = False
try:
    import rustworkx as rx  
    logging.info("Using  rustworkx")
except ImportError:
    use_networkx = True

if use_networkx is True:
    try:
        import networkx as nx
        logging.info("Using  networkx")
    except ImportError:
        print("Error: Neither rustworkx nor networkx is installed.")
        exit(1)

pdb_url = "https://data.rcsb.org/graphql"

class FieldNode:

    def __init__(self, kind, type, name):
        self.name = name
        self.redundant = False
        self.kind = kind
        self.of_kind = None
        self.type = type
        self.index = None

    def __str__(self):
        return f"Field Object name: {self.name}, Kind: {self.kind}, Type: {self.type}, Index if set: {self.index}"

    def set_index(self, index: int):
        self.index = index

    def set_of_kind(self, of_kind: str):
        self.of_kind = of_kind


class TypeNode:

    def __init__(self, name: str):
        self.name = name
        self.index = None
        self.field_list = None

    def set_index(self, index: int):
        self.index = index

    def set_field_list(self, field_list: List[FieldNode]):
        self.field_list = field_list


class Schema:
    def __init__(self, pdb_url):
        self.pdb_url = pdb_url
        self.use_networkx = use_networkx
        self.schema_graph = None
        self.node_index_dict = {}
        self.edge_index_dict = {}
        self.type_fields_dict = {}
        self.field_names_list = []
        self.root_introspection = self.request_root_types(pdb_url)
        self.root_dict = {}
        self.schema = self.fetch_schema(self.pdb_url)

        if use_networkx:
            self.schema_graph = nx.DiGraph()
        else:
            self.schema_graph = rx.PyDiGraph()

        self.construct_root_dict(self.pdb_url)
        self.construct_type_dict(self.schema, self.type_fields_dict)
        self.construct_name_list()
        self.recurse_build_schema(self.schema_graph, "Query")

    def request_root_types(self, pdb_url) -> Dict:
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
        response = requests.post(headers={"Content-Type": "application/graphql"}, data=root_query, url=pdb_url)
        return response.json()

    def construct_root_dict(self, url: str) -> Dict[str, str]:
        response = self.root_introspection
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

    def construct_type_dict(self, schema, type_fields_dict) -> Dict[str, Dict[str, Dict[str, str]]]:
        all_types_dict = schema["data"]["__schema"]["types"]
        for each_type_dict in all_types_dict:
            type_name = str(each_type_dict["name"])
            fields = each_type_dict["fields"]
            field_dict = {}
            if fields is not None:
                for field in fields:
                    field_dict[str(field["name"])] = dict(field["type"])
            type_fields_dict[type_name] = field_dict
        return type_fields_dict

    def construct_name_list(self):
        for type_name in self.type_fields_dict.keys():
            if '__' not in type_name:  # doesn't look through dunder methods because those are not added to the schema
                for field_name in self.type_fields_dict[type_name].keys():
                    self.field_names_list.append(field_name)

    def make_type_subgraph(self, type_name) -> TypeNode:
        field_name_list = self.type_fields_dict[type_name].keys()
        field_node_list = []
        type_node = self.make_type_node(type_name)
        for field_name in field_name_list:
            parent_type_name = type_name
            field_node = self.make_field_node(parent_type_name, field_name)
            field_node_list.append(field_node)
        type_node.set_field_list(field_node_list)
        return type_node

    def recurse_build_schema(self, schema_graph, type_name):
        type_node = self.make_type_subgraph(type_name)
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
                    self.recurse_build_schema(schema_graph, type_name)
                    type_index = self.node_index_dict[type_name]
                    if self.use_networkx:
                        schema_graph.add_edge(field_node.index, type_index)
                    else:
                        schema_graph.add_edge(parent=field_node.index, child=type_index, edge="draw")  # TODO: change edge value to None

    def make_type_node(self, type_name: str) -> TypeNode:
        type_node = TypeNode(type_name)
        if self.use_networkx:
            index = len(self.schema_graph.nodes)
            self.schema_graph.add_node(index, type_node=type_node)
        else:
            index = self.schema_graph.add_node(type_node)
        self.node_index_dict[type_name] = index
        type_node.set_index(index)
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

    def make_field_node(self, parent_type: str, field_name: str) -> FieldNode:
        kind = self.type_fields_dict[parent_type][field_name]["kind"]
        field_type_dict: Dict = self.type_fields_dict[parent_type][field_name] 
        return_type = self.find_type_name(field_type_dict)
        field_node = FieldNode(kind, return_type, field_name)
        assert field_node.type is not None
        if kind == "LIST" or kind == "NON_NULL":
            of_kind = self.find_kind(field_type_dict)
            field_node.set_of_kind(of_kind)
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
        if self.field_names_list.count(field_name) > 1:
            field_node.redundant = True
            self.node_index_dict[f"{parent_type}.{field_name}"] = index
        else:
            self.node_index_dict[field_name] = index
        field_node.set_index(index)
        return field_node

    def verify_unique_field(self, return_data_name):
        node_index_names = list(self.node_index_dict.keys())
        split_data_name = return_data_name.split('.')
        if len(split_data_name) == 1:
            field_name = split_data_name[0]
            name_count = self.field_names_list.count(field_name)
        else: 
            name_count = node_index_names.count(return_data_name)
        if name_count == 1:
            return True
        if name_count > 1:
            return False
        if name_count == 0:
            return None

    def get_unique_fields(self, return_data_name) -> List[str]:
        return_data_name = return_data_name.lower()
        valid_field_list: List[str] = []
        for name, idx in self.node_index_dict.items():
            if isinstance(self.schema_graph[idx], FieldNode):
                if self.schema_graph[idx].redundant is True:
                    if name.split('.')[1].lower() == return_data_name:
                        valid_field_list.append(name)
        return valid_field_list

    def construct_query(self, input_type, return_data_list, input_ids: Union[Dict[str, str], List[str]]):
        for return_field in return_data_list:
            if self.verify_unique_field(return_field) is True:
                continue
            if self.verify_unique_field(return_field) is False:
                raise ValueError(f"Not a unique field, must specify further. To find valid fields with this name, run: get_unique_fields({return_field})") # TODO: write this function
        if input_type not in self.root_dict.keys():
            raise ValueError(f"Unknown input type: {input_type}")
        if use_networkx:

            return self.___construct_query_networkx(input_type, return_data_list, input_ids)
        else:
            return self.___construct_query_rustworkx(input_type, return_data_list, input_ids)

    def get_descendant_fields(self, schema_graph, node, visited=None):
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
                child_descendants = self.get_descendant_fields(schema_graph, child, visited)
                if child_descendants:
                    result.append({child_data.name: child_descendants})
                else:
                    result.append(child_data.name)
            elif isinstance(child_data, TypeNode):
                type_descendants = self.get_descendant_fields(schema_graph, child, visited)
                if type_descendants:
                    result.extend(type_descendants)
                else:
                    result.append(child_data.name)

        if len(result) == 1:
            return result[0]
        return result

    def __construct_query_networkx(self, input_type, return_data_list, input_ids: Dict[str, str] = None, id_list=None):  # incomplete function
        input_ids = [input_ids] if isinstance(input_ids, str) else input_ids
        query_name = input_type
        attr_list = self.root_dict[input_type]
        attr_name = [id["name"] for id in attr_list]
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

    def __construct_query_rustworkx(self, input_type, return_data_list, input_ids: Union[Dict[str, str], List[str]]):
        return_data_name = [name.split('.')[-1] for name in return_data_list]
        attr_list = self.root_dict[input_type]
        attr_name = [id["name"] for id in attr_list]
        if not all(item in self.node_index_dict.keys() for item in return_data_list):
            raise ValueError(f"Unknown item in return_data_list: {', '.join([str(item) for item in return_data_list if item not in self.node_index_dict.keys()])}")
        input_dict = {}
        if isinstance(input_ids, Dict):
            input_dict = input_ids
            if not all(key in attr_name for key in input_dict.keys()):
                raise ValueError(f"Input IDs keys do not match attribute names: {input_dict.keys()} vs {attr_name}")
            attr_kind = {attr["name"]: attr["kind"] for attr in attr_list}
            for key, value in input_dict.items():
                if attr_kind[key] == "SCALAR":
                    if not isinstance(value, str):
                        raise ValueError(f"Input ID for {key} should be a single string")
                elif attr_kind[key] == "LIST":
                    if not isinstance(value, list):
                        raise ValueError(f"Input ID for {key} should be a list of strings")
                    if not all(isinstance(item, str) for item in value):
                        raise ValueError(f"Input ID for {key} should be a list of strings")
 
        if isinstance(input_ids, List):
            plural_types = [key for key, value in self.root_dict.items() 
                for item in value 
                    if item['kind'] == 'LIST']
            
            entities = ["polymer_entities", "branched_entities", "nonpolymer_entities", "nonpolymer_entity", "polymer_entity", "branched_entity"]
            instances = ["polymer_entity_instances", "branched_entity_instances", "nonpolymer_entity_instances", "polymer_entity_instance","nonpolymer_entity_instance", "branched_entity_instance"]

            for id in input_ids:
                if (re.match(r'^(MA|AF)_.*_[0-9]+$', id) and input_type in entities):
                    attr_name = [id["name"] for id in attr_list]
                    if len(input_ids) == 1: 
                        input_dict["entry_id"] = str(re.findall(r'^[^_]*_[^_]*', input_ids[0])[0])
                        input_dict["entity_id"] = str(re.findall(r'^(?:[^_]*_){2}(.*)', input_ids[0])[0])
                elif ((re.match(r'^(MA|AF)_.*\.[A-Z]$', id) or re.match(r'^[1-9][A-Z]{3}\.[A-Z]$', id)) and input_type in instances):
                    attr_name = [id["name"] for id in attr_list]
                    if len(input_ids) == 1: 
                        input_dict["entry_id"] = str(re.findall(r'^[^.]+', input_ids[0])[0])
                        input_dict["asym_id"] = str(re.findall(r'(?<=\.).*', input_ids[0])[0])
                elif ((re.match(r'^(MA|AF)_.*-[0-9]+$', id) or re.match(r'^[1-9][A-Z]{3}-[0-9]+$', id)) and input_type in ["assemblies", "assembly"]):
                    attr_name = [id["name"] for id in attr_list]
                    if len(input_ids) == 1: 
                        input_dict["entry_id"] = str(re.findall( r'[^-]*', input_ids[0])[0])
                        input_dict["assembly_id"] = str(re.findall(r'[^-]+$', input_ids[0])[0])
                elif ((re.match(r'^(MA|AF)_.*-[0-9]+\.[0-9]+$', id) or re.match(r'^[1-9][A-Z]{3}-[0-9]+\.[0-9]+$', id)) and input_type in ["interfaces", "interface"]):
                    attr_name = [id["name"] for id in attr_list]
                    if len(input_ids) == 1: 
                        input_dict["entry_id"] = str(re.findall( r'[^-]*', input_ids[0])[0])
                        input_dict["assembly_id"] = str(re.findall(r'-(.*)\.', input_ids[0])[0])
                        input_dict["interface_id"] = str(re.findall(r'[^.]+$', input_ids[0])[0])
                elif ((re.match(r'^(MA|AF)_.*$', id) or re.match(r'^[1-9][A-Z]{3}$', id)) and input_type in ["entries", "entry"]):
                    attr_name = [id["name"] for id in attr_list]
                    if len(input_ids) == 1:
                        input_dict["entry_id"] = str(input_ids[0])
                elif (re.match(r'^[1-9][A-Z]{3}_[0-9]+$', id) and input_type in entities):
                    attr_name = [id["name"] for id in attr_list]
                    if len(input_ids) == 1:
                        input_dict["entry_id"] = str(re.findall( r'[^_]*', input_ids[0])[0])
                        input_dict["entity_id"] = str(re.findall(r'[^_]+$', input_ids[0])[0])
                else:
                    raise ValueError(f"Invalid ID format: {id}")
                for attr in attr_name:
                    # print("attr: ", attr)
                    if attr not in input_dict:
                        input_dict[attr] = []
                    if input_type in plural_types:
                        input_dict[attr].append(id)
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
            node_index = self.node_index_dict[return_data]
            node_data = self.schema_graph[node_index]
            if isinstance(node_data, FieldNode):
                target_node_indices.append(node_data.index)

        # Get all shortest paths from the start node to each target node
        all_paths = {target_node: rx.digraph_all_shortest_paths(self.schema_graph, start_node_index, target_node) for target_node in target_node_indices}
        if any(not value for value in all_paths.values()):
            raise ValueError(f"The return data requested does not match the input type {input_type}")
        final_fields = {}

        for target_node in target_node_indices:
            target_data = self.schema_graph[target_node]
            if isinstance(target_data, FieldNode):
                final_fields[target_data.name] = self.get_descendant_fields(self.schema_graph, target_node)

        # print(final_fields)

        for target_node in target_node_indices:
            node_data = self.schema_graph[target_node]
            if isinstance(node_data, FieldNode):
                target_node_name = node_data.name
                field_names[target_node_name] = []
            for each_path in all_paths[target_node]:
                skip_first = True
                for node in each_path:
                    node_data = self.schema_graph[node]
                    if isinstance(node_data, FieldNode):
                        if skip_first:
                            skip_first = False
                            continue
                        field_node_name = node_data.name
                        field_names[target_node_name].append(field_node_name)
        query = "{ " + input_type + "("
        opened_brackets = 1
        closed_brackets = 0

        for i, attr in enumerate(attr_name):
            if isinstance(input_dict[attr], list):
                query += attr + ": [\"" + "\", \"".join(input_dict[attr]) + "\"]"
            else:
                query += attr + ": \"" + input_dict[attr] + "\""
            if i < len(attr_name) - 1:
                query += ", "
        query += ") {\n"
        opened_brackets += 1

        for field, field_info in field_names.items():
            if field in field_info:
                query += "  " + field_info[0] 
                if len(field_info) > 1 or final_fields[field]:
                    query += " {\n"
                    opened_brackets += 1
                for subfield in field_info[1:]:
                    if subfield != field:
                        query += "    " + subfield + " {\n"
                        opened_brackets += 1
                    else:
                        query += "    " + subfield 
                        if final_fields[subfield]:
                            query += " {\n"
                            opened_brackets += 1
                        break
                if field in final_fields:
                    for final_field in final_fields[field]:
                        if isinstance(final_field, dict):
                            for key, value in final_field.items():
                                query += "      " + key + " {\n"
                                opened_brackets += 1
                                for v in value:
                                    query += "        " + v + "\n"
                                query += "      }\n"
                                closed_brackets += 1
                        else:
                            query += "     " + final_field + "\n"
                if final_fields[field]: 
                    query += "  }\n"
                    closed_brackets += 1
            else:
                query += "  " + field + " {\n"
                opened_brackets += 1
                query += "  }\n"
                closed_brackets += 1

        while opened_brackets > closed_brackets:
            query += "}"
            closed_brackets += 1

        return query

# def main():
#     schema = fetch_schema(pdb_url)
#     if use_networkx:
#         construct_root_dict(pdb_url)
#     construct_type_dict(schema, type_fields_dict)
#     recurse_build_schema(schema_graph, "Query")
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
