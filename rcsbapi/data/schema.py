import re
import logging
from typing import List, Dict, Union
import requests
import networkx as nx
import json
import os

use_networkx = False
try:
    import rustworkx as rx
    logging.info("Using  rustworkx")
except ImportError:
    use_networkx = True

pdbUrl = "https://data.rcsb.org/graphql"


class FieldNode:

    def __init__(self, kind, node_type, name):
        self.name = name
        self.redundant = False
        self.kind = kind
        self.of_kind = None
        self.type = node_type
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

    def set_index(self, index):
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
        self.seen_names = set()
        self.name_description_dict = {}
        self.field_names_list = []
        self.root_introspection = self.request_root_types(pdb_url)
        self.root_dict = {}
        self.schema = self.fetch_schema(self.pdb_url)
        self.extract_name_description(self.schema)

        if use_networkx:
            self.schema_graph = nx.DiGraph()
        else:
            self.schema_graph = rx.PyDiGraph()

        self.construct_root_dict(self.pdb_url)
        self.construct_type_dict(self.schema, self.type_fields_dict)
        self.construct_name_list()
        self.recurse_build_schema(self.schema_graph, "Query")
        self.apply_weights(["CoreAssembly"], 2)

    def request_root_types(self, pdb_url) -> Dict:
        root_query = """
        query IntrospectionQuery{
        __schema{
            queryType{
            fields{
                name
                args{
                name
                description
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
        response = requests.post(headers={"Content-Type": "application/graphql"}, data=root_query, url=pdb_url, timeout=10)
        return response.json()

    def construct_root_dict(self, url: str) -> Dict[str, str]:
        response = self.root_introspection
        root_fields_list = response["data"]["__schema"]["queryType"]["fields"]
        for name_arg_dict in root_fields_list:
            root_name = name_arg_dict["name"]
            arg_dict_list = name_arg_dict["args"]
            for arg_dict in arg_dict_list:
                arg_name = arg_dict["name"]
                arg_description = arg_dict["description"]
                arg_kind = arg_dict["type"]["ofType"]["kind"]
                arg_type = self.find_type_name(arg_dict["type"]["ofType"])
                if root_name not in self.root_dict.keys():
                    self.root_dict[root_name] = []
                self.root_dict[root_name].append({"name": arg_name, "description": arg_description, "kind": arg_kind, "type": arg_type})
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
        schema_response = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=url, timeout=10)
        if schema_response.status_code == 200:
            return schema_response.json()
        else:
            logging.info("Loading data schema from file")
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_file_path = os.path.join(current_dir, '../', 'resources', 'data_api_schema.json')
            with open(json_file_path, 'r', encoding="utf-8") as schema_file:
                return json.load(schema_file)

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
            if "__" not in type_name:  # doesn't look through dunder methods because those are not added to the schema
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
                        schema_graph.add_edge(field_node.index, type_index, weight=1)
                    else:
                        schema_graph.add_edge(parent=field_node.index, child=type_index, edge=1)
                else:
                    self.recurse_build_schema(schema_graph, type_name)
                    type_index = self.node_index_dict[type_name]
                    if self.use_networkx:
                        schema_graph.add_edge(field_node.index, type_index, weight=1)
                    else:
                        schema_graph.add_edge(parent=field_node.index, child=type_index, edge=1)

    def apply_weights(self, root_type_list, weight):  # applies weight in all edges from a root TypeNode to FieldNodes
        for root_type in root_type_list:
            node_idx = self.node_index_dict[root_type]
            if use_networkx is False:
                out_edge_list = self.schema_graph.incident_edges(node_idx)
                for edge_idx in out_edge_list:
                    self.schema_graph.update_edge_by_index(edge_idx, weight)
            else:
                out_edge_list = self.schema_graph.edges(node_idx)
                nx.set_edge_attributes(self.schema_graph, {edge_tuple: {"weight": weight} for edge_tuple in out_edge_list})

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
            self.schema_graph.add_edge(parent_type_index, index, weight=1)
        else:
            if field_node.kind == "SCALAR" or field_node.of_kind == "SCALAR":
                index = self.schema_graph.add_child(parent_type_index, field_node, 1)
            else:
                index = self.schema_graph.add_child(parent_type_index, field_node, 1)
        if self.field_names_list.count(field_name) > 1:
            field_node.redundant = True
            self.node_index_dict[f"{parent_type}.{field_name}"] = index
        else:
            self.node_index_dict[field_name] = index
        field_node.set_index(index)
        return field_node

    def verify_unique_field(self, return_data_name):
        node_index_names = list(self.node_index_dict.keys())
        split_data_name = return_data_name.split(".")
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
                    if name.split(".")[1].lower() == return_data_name:
                        valid_field_list.append(name)
        return valid_field_list

    def get_input_id_dict(self, input_type):
        if input_type not in self.root_dict.keys():
            raise ValueError("Not a valid input_type, no available input_id dictionary")
        root_dict_entry = self.root_dict[input_type]
        input_dict = {}
        for arg in root_dict_entry:
            name = arg["name"]
            description = arg["description"]
            if (len(root_dict_entry) == 1) and root_dict_entry[0]["name"] == "entry_id":
                description = "ID"
            input_dict[name] = description
        return input_dict

    def recurse_fields(self, fields, field_map, indent=2):
        query_str = ""
        for field, value in fields.items():
            mapped_path = field_map.get(field, [field])
            mapped_path = mapped_path[:mapped_path.index(field) + 1]  # Only take the path up to the field itself
            for idx, subfield in enumerate(mapped_path):
                query_str += " " * indent + subfield
                if idx < len(mapped_path) - 1 or (isinstance(value, list) and value):
                    query_str += "{\n"
                else:
                    query_str += "\n"
                indent += 2 if idx == 0 else 0
            if isinstance(value, list):
                if value:  # Only recurse if the list is not empty
                    for item in value:
                        if isinstance(item, dict):
                            query_str += self.recurse_fields(item, field_map, indent + 2)
                        else:
                            query_str += " " * (indent + 2) + item + "\n"
            else:
                query_str += " " * (indent + 2) + value + "\n"
            for idx, subfield in enumerate(mapped_path):
                if idx < len(mapped_path) - 1 or (isinstance(value, list) and value):
                    query_str += " " * indent + "}\n"
        return query_str

    def construct_query(self, input_ids: Union[Dict[str, str], List[str]], input_type: str, return_data_list: List[str]):
        if not (isinstance(input_ids, dict) or isinstance(input_ids, list)):
            raise ValueError("input_ids must be dictionary or list")
        if input_type not in self.root_dict.keys():
            raise ValueError(f"Unknown input type: {input_type}")
        for return_field in return_data_list:
            if self.verify_unique_field(return_field) is True:
                continue
            if self.verify_unique_field(return_field) is False:
                raise ValueError(
                    f"\"{return_field}\" exists, but is not a unique field, must specify further. To find valid fields with this name, run: get_unique_fields(\"{return_field}\")")
        if use_networkx:

            return self.__construct_query_networkx(input_ids, input_type, return_data_list)
        else:
            return self.__construct_query_rustworkx(input_ids, input_type, return_data_list)

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

    def extract_name_description(self, schema_part, parent_name=""):
        if isinstance(schema_part, dict):
            if 'name' in schema_part and 'description' in schema_part:
                name = schema_part['name']
                description = schema_part['description']
                if name in self.seen_names:
                    if parent_name:
                        name = f"{parent_name}.{name}"
                else:
                    self.seen_names.add(name)
                self.name_description_dict[name] = description
            for key, value in schema_part.items():
                new_parent_name = schema_part['name'] if key == 'fields' else parent_name
                self.extract_name_description(value, new_parent_name)
        elif isinstance(schema_part, list):
            for item in schema_part:
                self.extract_name_description(item, parent_name)

    def find_field_names(self, search_string):
        if not isinstance(search_string, str):
            raise ValueError(f"Please input a string instead of {type(search_string)}")
        field_names = [key for key in self.name_description_dict if search_string.lower() in key.lower()]
        if not field_names:
            raise ValueError(f"No fields found matching '{search_string}'")
        name_description = {name: self.name_description_dict[name] for name in field_names if name in self.name_description_dict}
        return name_description

    def regex_checks(self, input_dict, input_ids, attr_list, input_type):
        plural_types = [key for key, value in self.root_dict.items() for item in value if item["kind"] == "LIST"]
        entities = ["polymer_entities", "branched_entities", "nonpolymer_entities", "nonpolymer_entity", "polymer_entity", "branched_entity"]
        instances = [
            "polymer_entity_instances",
            "branched_entity_instances",
            "nonpolymer_entity_instances",
            "polymer_entity_instance",
            "nonpolymer_entity_instance",
            "branched_entity_instance"
        ]

        for single_id in input_ids:
            if re.match(r"^(MA|AF)_.*_[0-9]+$", single_id) and input_type in entities:
                attr_name = [single_id["name"] for single_id in attr_list]
                if len(input_ids) == 1:
                    input_dict["entry_id"] = str(re.findall(r"^[^_]*_[^_]*", input_ids[0])[0])
                    input_dict["entity_id"] = str(re.findall(r"^(?:[^_]*_){2}(.*)", input_ids[0])[0])
            elif (re.match(r"^(MA|AF)_.*\.[A-Z]$", single_id) or re.match(r"^[1-9][A-Z]{3}\.[A-Z]$", single_id)) and input_type in instances:
                attr_name = [single_id["name"] for single_id in attr_list]
                if len(input_ids) == 1:
                    input_dict["entry_id"] = str(re.findall(r"^[^.]+", input_ids[0])[0])
                    input_dict["asym_id"] = str(re.findall(r"(?<=\.).*", input_ids[0])[0])
            elif (re.match(r"^(MA|AF)_.*-[0-9]+$", single_id) or re.match(r"^[1-9][A-Z]{3}-[0-9]+$", single_id)) and input_type in ["assemblies", "assembly"]:
                attr_name = [single_id["name"] for single_id in attr_list]
                if len(input_ids) == 1:
                    input_dict["entry_id"] = str(re.findall(r"^[^-]+", input_ids[0])[0])
                    input_dict["assembly_id"] = str(re.findall(r"[^-]+$", input_ids[0])[0])
            elif (re.match(r"^(MA|AF)_.*-[0-9]+\.[0-9]+$", single_id) or re.match(r"^[1-9][A-Z]{3}-[0-9]+\.[0-9]+$", single_id)) and input_type in ["interfaces", "interface"]:
                attr_name = [single_id["name"] for single_id in attr_list]
                if len(input_ids) == 1:
                    input_dict["entry_id"] = str(re.findall(r"^[^-]+", input_ids[0])[0])
                    input_dict["assembly_id"] = str(re.findall(r"-(.*)\.", input_ids[0])[0])
                    input_dict["interface_id"] = str(re.findall(r"[^.]+$", input_ids[0])[0])
            elif (re.match(r"^(MA|AF)_[A-Za-z0-9]*$", single_id) or re.match(r"^[A-Z0-9]{4}$", single_id)) and input_type in ["entries", "entry"]:
                attr_name = [single_id["name"] for single_id in attr_list]
                if len(input_ids) == 1:
                    input_dict["entry_id"] = str(input_ids[0])
            elif re.match(r"^\d{1}[A-Za-z]{3}_\d{1}$", single_id) and input_type in entities:
                attr_name = [single_id["name"] for single_id in attr_list]
                if len(input_ids) == 1:
                    input_dict["entry_id"] = str(re.findall(r"^[^_]+", input_ids[0])[0])
                    input_dict["entity_id"] = str(re.findall(r"[^_]+$", input_ids[0])[0])
            else:
                raise ValueError(f"Invalid ID format for {input_type}: {single_id}")
            for attr in attr_name:
                # print("attr: ", attr)
                if attr not in input_dict:
                    input_dict[attr] = []
                if input_type in plural_types:
                    input_dict[attr].append(single_id)
        return input_dict

    def __construct_query_networkx(self, input_ids: Union[Dict[str, str], List[str]], input_type: str, return_data_list: List[str]):  # incomplete function
        input_ids = [input_ids] if isinstance(input_ids, str) else input_ids
        # query_name = input_type
        # attr_list = self.root_dict[input_type]
        # attr_name = [id["name"] for id in attr_list]
        # field_names = {}
        # start_node_index = None
        for node in self.schema_graph.nodes():
            node_data = self.schema_graph.nodes[node]
            if node_data.get("name") == input_type:
                # start_node_index = node_data.get("index")
                # start_node_name = node_data.get("name")
                # start_node_type = node_data.get("type")
                break
        target_node_indices = []
        for return_data in return_data_list:
            for node, node_data in self.schema_graph.nodes(data=True):
                if isinstance(node_data, dict) and node_data.get("name") == return_data:
                    target_node_indices.append(node_data.get("index"))
                    break
        # all_paths = {target_node: nx.shortest_path(self.schema_graph, start_node_index, target_node) for target_node in target_node_indices}
        query = "query"
        return query

    def __construct_query_rustworkx(self, input_ids: Union[Dict[str, str], List[str]], input_type: str, return_data_list: List[str]):
        # return_data_name = [name.split('.')[-1] for name in return_data_list]
        attr_list = self.root_dict[input_type]
        attr_name = [id["name"] for id in attr_list]
        unknown_return_list = [item for item in return_data_list if item not in self.node_index_dict]
        if unknown_return_list:
            raise ValueError(f"Unknown item in return_data_list: {unknown_return_list}")
        input_dict = {}
        if isinstance(input_ids, Dict):
            input_dict = input_ids
            if not all(key in attr_name for key in input_dict.keys()):
                raise ValueError(f"Input IDs keys do not match attribute names: {input_dict.keys()} vs {attr_name}")
            missing_keys = [key_arg for key_arg in attr_name if key_arg not in input_dict]
            if len(missing_keys) > 0:
                raise ValueError(f"Missing input_id dictionary keys: {missing_keys}. Find input_id keys and descriptions by running SCHEMA.get_input_id_dict(\"{input_type}\")")
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
            input_dict = self.regex_checks(input_dict, input_ids, attr_list, input_type)

        field_names = {}

        start_node_index = None
        for node in self.schema_graph.node_indices():
            node_data = self.schema_graph[node]
            if node_data.name == input_type:
                start_node_index = node_data.index
                # start_node_name = node_data.name
                # sart_node_type = node_data.type
                break

        target_node_indices = []
        for return_data in return_data_list:
            node_index = self.node_index_dict[return_data]
            node_data = self.schema_graph[node_index]
            if isinstance(node_data, FieldNode):
                target_node_indices.append(node_data.index)

        # Get all shortest paths from the start node to each target node
        all_paths = {target_node: rx.digraph_all_shortest_paths(self.schema_graph, start_node_index, target_node, weight_fn=lambda edge: edge) for target_node in target_node_indices}
        for return_data in return_data_list:
            if any(not value for value in all_paths.values()):
                raise ValueError(f"You can't access {return_data} from input type {input_type}")
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

        for i, attr in enumerate(attr_name):
            if isinstance(input_dict[attr], list):
                query += attr + ': ["' + '", "'.join(input_dict[attr]) + '"]'
            else:
                query += attr + ': "' + input_dict[attr] + '"'
            if i < len(attr_name) - 1:
                query += ", "
        query += ") {\n"
        query += self.recurse_fields(final_fields, field_names)
        query += " " + "}\n}\n"
        return query
