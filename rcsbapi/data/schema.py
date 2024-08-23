import re
import logging
from typing import List, Dict, Union, Any, Optional
import json
import os
import requests
import networkx as nx
from graphql import validate, parse, build_client_schema

use_networkx: bool = False
try:
    import rustworkx as rx

    logging.info("Using  rustworkx")
except ImportError:
    use_networkx = True

PDB_URL: str = "https://data.rcsb.org/graphql"


class FieldNode:

    def __init__(self, kind, node_type, name, description) -> None:
        self.name: str = name
        self.description: str = description
        self.redundant: bool = False
        self.kind: str = kind
        self.of_kind: str = ""
        self.type: str = node_type
        self.index: Optional[int] = None

    def __str__(self) -> str:
        return f"Field Object name: {self.name}, Kind: {self.kind}, Type: {self.type}, Index if set: {self.index}, Description: {self.description}"

    def set_index(self, index: int) -> None:
        self.index = index

    def set_of_kind(self, of_kind: str) -> None:
        self.of_kind = of_kind


class TypeNode:

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.index: Optional[int] = None
        self.field_list: Optional[List[FieldNode]] = None

    def set_index(self, index) -> None:
        self.index = index

    def set_field_list(self, field_list: List[FieldNode]) -> None:
        self.field_list = field_list


class Schema:
    """
    GraphQL schema defining available fields, types, and how they are connected.
    """
    def __init__(self) -> None:
        """
        GraphQL schema defining available fields, types, and how they are connected.
        """
        self.pdb_url: str = PDB_URL
        self.use_networkx: bool = use_networkx
        self.type_to_idx_dict: Dict[str, int] = {}
        self.field_to_idx_dict: Dict[str, List[int]] = {}
        """Dict where keys are field names and values are lists of indices. Indices of redundant fields are appended to the list under the field name. (ex: {id: [[43, 116, 317...]})"""
        self.seen_names: set[str] = set()
        self.root_introspection = self.request_root_types(PDB_URL)
        self.schema: Dict = self.fetch_schema(self.pdb_url)
        self.client_schema = build_client_schema(self.schema["data"])

        if use_networkx:
            self.schema_graph = nx.DiGraph()
        else:
            self.schema_graph = rx.PyDiGraph()

        self.type_fields_dict: Dict[str, Dict] = self.construct_type_dict()
        self.field_names_list = self.construct_name_list()
        self.root_dict: Dict[str, List[Dict[str, str]]] = self.construct_root_dict(self.pdb_url)
        self.schema_graph = self.recurse_build_schema(self.schema_graph, "Query")
        self.dot_field_to_idx_dict: Dict[str, int] = self.make_dot_field_to_idx()
        """Dict where keys are field names and values are indices. Redundant field names are represented as <parent_field_name>.<field_name> (ex: {entry.id: 1452})"""
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

    def construct_root_dict(self, url: str) -> Dict[str, List[Dict[str, str]]]:
        response = self.root_introspection
        root_dict: Dict[str, List[Dict[str, str]]] = {}
        root_fields_list = response["data"]["__schema"]["queryType"]["fields"]
        for name_arg_dict in root_fields_list:
            root_name = name_arg_dict["name"]
            arg_dict_list = name_arg_dict["args"]
            for arg_dict in arg_dict_list:
                arg_name = arg_dict["name"]
                arg_description = arg_dict["description"]
                arg_kind = arg_dict["type"]["ofType"]["kind"]
                arg_type = self.find_type_name(arg_dict["type"]["ofType"])
                if root_name not in root_dict.keys():
                    root_dict[root_name] = []
                root_dict[root_name].append({"name": arg_name, "description": arg_description, "kind": arg_kind, "type": arg_type})
        return root_dict

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
            json_file_path = os.path.join(current_dir, "../", "resources", "data_api_schema.json")
            with open(json_file_path, "r", encoding="utf-8") as schema_file:
                return json.load(schema_file)

    def construct_type_dict(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        all_types_dict: Dict = self.schema["data"]["__schema"]["types"]
        type_fields_dict = {}
        for each_type_dict in all_types_dict:
            type_name = str(each_type_dict["name"])
            fields = each_type_dict["fields"]
            field_dict = {}
            if fields is not None:
                for field in fields:
                    field_dict[str(field["name"])] = dict(field["type"])
            type_fields_dict[type_name] = field_dict
        return type_fields_dict

    def construct_name_list(self) -> List[str]:
        field_names_list = []
        for type_name, field_dict in self.type_fields_dict.items():
            if "__" not in type_name:  # doesn't look through dunder methods because those are not added to the schema
                for field_name in field_dict.keys():
                    field_names_list.append(field_name)
        return field_names_list

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

    def recurse_build_schema(self, schema_graph: Union[nx.DiGraph, rx.PyDiGraph], type_name: str) -> Union[nx.DiGraph, rx.PyDiGraph]:
        type_node = self.make_type_subgraph(type_name)
        for field_node in type_node.field_list:
            if field_node.kind == "SCALAR" or field_node.of_kind == "SCALAR":
                continue
            else:
                type_name = field_node.type
                if type_name in self.type_to_idx_dict:
                    type_index = self.type_to_idx_dict[type_name]
                if type_name in self.type_to_idx_dict:
                    type_index = self.type_to_idx_dict[type_name]
                if type_name in self.type_to_idx_dict.keys():
                    type_index = self.type_to_idx_dict[type_name]
                    if use_networkx:
                        schema_graph.add_edge(field_node.index, type_index, 1)
                    else:
                        schema_graph.add_edge(field_node.index, type_index, 1)
                else:
                    self.recurse_build_schema(schema_graph, type_name)
                    type_index = self.type_to_idx_dict[type_name]
                    if self.use_networkx:
                        schema_graph.add_edge(field_node.index, type_index, 1)
                    else:
                        schema_graph.add_edge(field_node.index, type_index, 1)
        return schema_graph

    def apply_weights(self, root_type_list: List[str], weight: int) -> None:  # applies weight in all edges from a root TypeNode to FieldNodes
        for root_type in root_type_list:
            node_idx = self.type_to_idx_dict[root_type]
            if use_networkx is False:
                assert isinstance(self.schema_graph, rx.PyDiGraph)
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
        self.type_to_idx_dict[type_name] = index
        type_node.set_index(index)
        return type_node

    def find_kind(self, field_dict: Dict) -> str:
        if field_dict["name"] is not None:
            return field_dict["kind"]
        else:
            return self.find_kind(field_dict["ofType"])

    def find_type_name(self, field_dict: Dict) -> str:
        if field_dict["name"] is not None:
            return field_dict["name"]
        else:
            return self.find_type_name(field_dict["ofType"])

    def find_description(self, type_name: str, field_name: str) -> str:
        for type_dict in self.schema["data"]["__schema"]["types"]:
            if type_dict["name"] == type_name:
                for field in type_dict["fields"]:
                    if field["name"] == field_name:
                        return field["description"]
        return ""

    def make_field_node(self, parent_type: str, field_name: str) -> FieldNode:
        kind = self.type_fields_dict[parent_type][field_name]["kind"]
        field_type_dict: Dict = self.type_fields_dict[parent_type][field_name]
        return_type = self.find_type_name(field_type_dict)
        description = self.find_description(parent_type, field_name)
        field_node = FieldNode(kind, return_type, field_name, description)
        assert field_node.type is not None
        if kind == "LIST" or kind == "NON_NULL":
            of_kind = self.find_kind(field_type_dict)
            field_node.set_of_kind(of_kind)
        parent_type_index = self.type_to_idx_dict[parent_type]
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
        field_node.set_index(index)

        if field_name not in self.field_to_idx_dict.keys():
            self.field_to_idx_dict[field_name] = [field_node.index]
        else:
            self.field_to_idx_dict[field_name].append(field_node.index)

        return field_node

    def make_dot_field_to_idx(self) -> Dict[str, int]:
        dot_field_to_idx: Dict[str, int] = {}
        for node in self.schema_graph.nodes():
            if isinstance(node, FieldNode):
                parent_list = list(self.schema_graph.predecessor_indices(node.index))
                assert len(parent_list) == 1
                parent_type_index = parent_list[0]
                if self.schema_graph[parent_type_index].name == "Query":
                    dot_field_to_idx[f"Query.{node.name}"] = node.index
                if node.redundant is True:
                    predecessor_fields = self.schema_graph.predecessors(parent_type_index)
                    for pred_field in predecessor_fields:
                        if f"{pred_field.name}.{node.name}" not in dot_field_to_idx.keys():
                            dot_field_to_idx[f"{pred_field.name}.{node.name}"] = node.index
                else:
                    dot_field_to_idx[node.name] = node.index
        return dot_field_to_idx

    def get_unique_fields(self, return_data_name: str) -> List[str]:
        return_data_name = return_data_name.lower()
        valid_field_list: List[str] = []
        for name, idx in self.dot_field_to_idx_dict.items():
            if isinstance(self.schema_graph[idx], FieldNode):
                if self.schema_graph[idx].redundant is True:
                    if name.split(".")[1].lower() == return_data_name:
                        valid_field_list.append(name)
        return valid_field_list

    def get_input_id_dict(self, input_type: str) -> Dict[str, str]:
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

    def recurse_fields(self, fields: Dict[Any, Any], field_map: Dict[Any, Any], indent=2) -> None:
        # print(f"fields: {fields}")
        # print(f"field_map: {field_map}")
        query_str = ""
        for target_idx, idx_path in fields.items():
            # print(f"idx_path: {idx_path}")
            mapped_path = field_map.get(target_idx, [target_idx])
            mapped_path = mapped_path[: mapped_path.index(target_idx) + 1]  # Only take the path up to the field itself
            for idx, subfield in enumerate(mapped_path):
                query_str += " " * indent + self.idx_to_name(subfield)
                if idx < len(mapped_path) - 1 or (isinstance(idx_path, list) and idx_path):
                    query_str += "{\n"
                else:
                    query_str += "\n"
                indent += 2 if idx == 0 else 0
            if isinstance(idx_path, list):
                if idx_path:  # Only recurse if the list is not empty
                    for item in idx_path:
                        if isinstance(item, dict):
                            query_str += self.recurse_fields(item, field_map, indent + 2)
                        else:
                            query_str += " " * (indent + 2) + self.idx_to_name(item) + "\n"
            else:
                query_str += " " * (indent + 2) + idx_path + "\n"
            for idx, subfield in enumerate(mapped_path):
                if idx < len(mapped_path) - 1 or (isinstance(idx_path, list) and idx_path):
                    query_str += " " * indent + "}\n"
        return query_str

    def get_descendant_fields(self, node_idx: int, visited=None) -> Union[List[Union[str, Dict]], Union[str, Dict]]:
        if visited is None:
            visited = set()

        result: List[Union[str, Dict]] = []
        children_idx = list(self.schema_graph.neighbors(node_idx))

        for idx in children_idx:
            if idx in visited:
                continue
            visited.add(idx)

            child_data = self.schema_graph[idx]
            if isinstance(child_data, FieldNode):
                child_descendants = self.get_descendant_fields(idx, visited)
                if child_descendants:
                    result.append({child_data.index: child_descendants})
                else:
                    result.append(child_data.index)
            elif isinstance(child_data, TypeNode):
                type_descendants = self.get_descendant_fields(idx, visited)
                if type_descendants:
                    result.extend(type_descendants)
                else:
                    result.append(child_data.index)
        # print(f"get_descendant_fields: {result}")
        return result

    def find_field_names(self, search_string: str) -> List[str]:
        """find field names that fully or partially match the search string

        Args:
            search_string (str): string to search field names for

        Raises:
            ValueError: thrown when a type other than string is passed in for search_string
            ValueError: thrown when no fields match search_string

        Returns:
            List[str]: list of matching field names
        """
        if not isinstance(search_string, str):
            raise ValueError(f"Please input a string instead of {type(search_string)}")
        field_names = [key for key in self.field_to_idx_dict if search_string.lower() in key.lower()]
        if not field_names:
            raise ValueError(f"No fields found matching '{search_string}'")
        return field_names

    def regex_checks(self, input_dict: Dict, input_ids: List[str], attr_list: List[Dict], input_type: str) -> Union[Dict[str, str], Dict[str, List[str]]]:
        plural_types = [key for key, value in self.root_dict.items() for item in value if item["kind"] == "LIST"]
        entities = ["polymer_entities", "branched_entities", "nonpolymer_entities", "nonpolymer_entity", "polymer_entity", "branched_entity"]
        instances = [
            "polymer_entity_instances",
            "branched_entity_instances",
            "nonpolymer_entity_instances",
            "polymer_entity_instance",
            "nonpolymer_entity_instance",
            "branched_entity_instance",
        ]

        for single_id in input_ids:
            if re.match(r"^(MA|AF)_.*_[0-9]+$", single_id) and input_type in entities:
                if len(input_ids) == 1:
                    input_dict["entry_id"] = str(re.findall(r"^[^_]*_[^_]*", input_ids[0])[0])
                    input_dict["entity_id"] = str(re.findall(r"^(?:[^_]*_){2}(.*)", input_ids[0])[0])
            elif (re.match(r"^(MA|AF)_.*\.[A-Z]$", single_id) or re.match(r"^[A-Z0-9]{4}\.[A-Z]$", single_id)) and input_type in instances:
                if len(input_ids) == 1:
                    input_dict["entry_id"] = str(re.findall(r"^[^.]+", input_ids[0])[0])
                    input_dict["asym_id"] = str(re.findall(r"(?<=\.).*", input_ids[0])[0])
            elif (re.match(r"^(MA|AF)_.*-[0-9]+$", single_id) or re.match(r"^[A-Z0-9]{4}-[0-9]+$", single_id)) and input_type in ["assemblies", "assembly"]:
                if len(input_ids) == 1:
                    input_dict["entry_id"] = str(re.findall(r"^[^-]+", input_ids[0])[0])
                    input_dict["assembly_id"] = str(re.findall(r"[^-]+$", input_ids[0])[0])
            elif (re.match(r"^(MA|AF)_.*-[0-9]+\.[0-9]+$", single_id) or re.match(r"^[A-Z0-9]{4}-[0-9]+\.[0-9]+$", single_id)) and input_type in ["interfaces", "interface"]:
                if len(input_ids) == 1:
                    input_dict["entry_id"] = str(re.findall(r"^[^-]+", input_ids[0])[0])
                    input_dict["assembly_id"] = str(re.findall(r"-(.*)\.", input_ids[0])[0])
                    input_dict["interface_id"] = str(re.findall(r"[^.]+$", input_ids[0])[0])
            elif (re.match(r"^(MA|AF)_[A-Za-z0-9]*$", single_id) or re.match(r"^[A-Z0-9]{4}$", single_id)) and input_type in ["entries", "entry"]:
                if len(input_ids) == 1:
                    input_dict["entry_id"] = str(input_ids[0])
            elif re.match(r"^[A-Z0-9]{4}_[0-9]+$", single_id) and input_type in entities:
                if len(input_ids) == 1:
                    input_dict["entry_id"] = str(re.findall(r"^[^_]+", input_ids[0])[0])
                    input_dict["entity_id"] = str(re.findall(r"[^_]+$", input_ids[0])[0])
            elif input_type == "chem_comp" or input_type == "chem_comps":
                if len(input_ids) == 1:
                    input_dict["comp_id"] = str(re.findall(r"^[^_]+", input_ids[0])[0])
            elif input_type == "entry_group" or input_type == "entry_groups":
                if len(input_ids) == 1:
                    input_dict["group_id"] = str(input_ids[0])
            elif input_type == "polymer_entity_group" or input_type == "polymer_entity_groups":
                if len(input_ids) == 1:
                    input_dict["group_id"] = str(input_ids[0])
            # regex for uniprot: https://www.uniprot.org/help/accession_numbers
            elif re.match(r"[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}", single_id) and (input_type == "uniprot"):
                if len(input_ids) == 1:
                    input_dict["uniprot_id"] = str(input_ids[0])
                else:
                    raise ValueError("Uniprot IDs must be searched one at a time")
            elif input_type == "pubmed":
                if len(input_ids) == 1:
                    input_dict["pubmed_id"] = str(input_ids[0])
                else:
                    raise ValueError("Pubmed IDs must be searched one at a time")
            elif input_type == "group provenance":
                if len(input_ids) == 1:
                    input_dict["group_provenance_id"] = str(input_ids[0])
                else:
                    raise ValueError("Group provenance IDs must be searched one at a time")
            else:
                raise ValueError(f"Invalid ID format for {input_type}: {single_id}")
            if input_type in plural_types:
                input_dict = {}
                attr = attr_list[0]["name"]
                input_dict[attr] = input_ids
        return input_dict

    def construct_query(self, input_type: str, input_ids: Union[List[str], Dict[str, str], Dict[str, List[str]]], return_data_list: List[str], add_rcsb_id=True) -> str:
        if not (isinstance(input_ids, dict) or isinstance(input_ids, list)):
            raise ValueError("input_ids must be dictionary or list")
        if input_type not in self.root_dict.keys():
            raise ValueError(f"Unknown input type: {input_type}")
        input_type_idx: int = self.dot_field_to_idx_dict[f"Query.{input_type}"]
        if isinstance(input_ids, List) and (len(input_ids) > 1):
            if self.schema_graph[input_type_idx].kind == "OBJECT":
                raise ValueError(f"Entered multiple input_ids, but input_type is not a plural type. Try making \"{input_type}\" plural")
        unknown_return_list: List[str] = []
        for field in return_data_list:
            if "." in field:
                separate_fields = field.split(".")
                for sep_field in separate_fields:
                    if sep_field not in self.field_names_list:
                        unknown_return_list.append(sep_field)
            else:
                if field not in self.field_names_list:
                    unknown_return_list.append(field)
        if unknown_return_list:
            raise ValueError(f"Unknown item in return_data_list: {unknown_return_list}")
        for return_field in return_data_list:
            if ("." not in return_field) and (self.field_names_list.count(return_field) > 1):
                path_list = self.find_paths(input_type, return_field)
                path_msg = "  " + "\n  ".join(path_list[:10])
                if len(path_list) > 10:
                    len_path = 10
                else:
                    len_path = len(path_list)
                raise ValueError(
                    f'"{return_field}" exists, but is not a unique field, must specify further.\n'
                    f"{len_path} of {len(path_list)} possible paths:\n"
                    f"{path_msg}\n\n"
                    f"For all paths run:\n"
                    f"  from rcsbapi.data import Schema\n"
                    f"  schema = Schema()\n"
                    f'  schema.get_unique_fields("{return_field}")'
                )
        if use_networkx:
            query = self._construct_query_networkx(input_type=input_type, input_ids=input_ids, return_data_list=return_data_list)
        else:
            query = self._construct_query_rustworkx(input_type=input_type, input_ids=input_ids, return_data_list=return_data_list, add_rcsb_id=add_rcsb_id)
        validation_error_list = validate(self.client_schema, parse(query))
        if not validation_error_list:
            return query
        else:
            raise ValueError(validation_error_list)

    def _construct_query_networkx(self, input_type: str, input_ids: Union[Dict[str, str], List[str]], return_data_list: List[str]):  # incomplete function
        query = ""
        return query

    def _construct_query_rustworkx(self, input_ids: Union[List[str], Dict[str, str], Dict[str, List[str]]], input_type: str, return_data_list: List[str], add_rcsb_id: bool = True) -> str:
        """Construct a query in GraphQL syntax using a rustworkx graph.

        Args:
            input_ids (Union[List[str], Dict[str, str], Dict[str, List[str]]]): identifing information for the specific entry, chemical component, etc to query
            input_type (str): specifies where you are starting your query. These are specific fields like "entry" or "polymer_entity_instance".
            return_data_list (List[str]): requested data, can be field name(s) or dot-separated field names
                ex: "cluster_id" or "exptl.method"
            add_rcsb_id (bool): automatically request rcsb_id at the top of the query. Default is True.

        Raises:
            ValueError: input_ids dictionary keys don't match the input_type given
            ValueError: input_ids dictionary keys missing
            ValueError: input_ids dictionary value should be a string, but another type was passed in
            ValueError: field in return_data_list exists, but is a redundant name and needs to be further specified
            ValueError: path in return_data_list exists, but is a redundant and needs to be further specified

        Returns:
            str: query in GraphQL syntax
        """
        attr_list = self.root_dict[input_type]
        attr_name = [id["name"] for id in attr_list]

        # check formatting of input_ids
        input_dict: Union[Dict[str, str], Dict[str, List[str]]] = {}

        if isinstance(input_ids, Dict):
            input_dict = input_ids
            if not all(key in attr_name for key in input_dict.keys()):
                raise ValueError(f"Input IDs keys do not match: {input_dict.keys()} vs {attr_name}")
            missing_keys = [key_arg for key_arg in attr_name if key_arg not in input_dict]
            if len(missing_keys) > 0:
                raise ValueError(
                    f"Missing input_id dictionary keys: {missing_keys}. Find input_id keys and descriptions by running:\n"
                    f"  from rcsbapi.data import Schema\n"
                    f"  schema = Schema()\n"
                    f'  schema.get_input_id_dict("{input_type}")'
                )
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

        start_node_index = self.dot_field_to_idx_dict[f"Query.{input_type}"]

        #if rcsb_id isn't requested, add it to the query for more readable query results
        if (f"{input_type}.rcsb_id" not in return_data_list) and (add_rcsb_id is True):
            return_data_list.insert(0, f"{input_type}.rcsb_id")

        all_paths: Dict[int, List[List[int]]] = {}

        for field in return_data_list:
            if "." in field:
                # generate list of all possible paths to the final requested field. Try to find matching sequence to user input.
                path_list = field.split(".")
                possible_paths = self.find_paths(input_type, path_list[-1])
                matching_paths: List[str] = []
                for path in possible_paths:
                    possible_paths_list = path.split(".")
                    possible_paths_list.insert(0, str(input_type))
                    for i in range(len(possible_paths_list)):
                        if possible_paths_list[i:i + len(path_list)] == path_list:
                            matching_paths.append(".".join(possible_paths_list))

                idx_paths: List[List[int]] = []
                if len(matching_paths) > 0:
                    for path in matching_paths:
                        idx_paths.extend(self.parse_dot_path(path))
                    idx_paths = self.compare_paths(start_node_index, idx_paths)

                if len(idx_paths) > 1:
                    path_choice_msg = ""
                    for name_path in matching_paths:
                        path_choice_msg += "  " + name_path + "\n"
                    raise ValueError(
                        f'"{field}" not specific enough. Use one or more of these paths in return_data_list argument:\n'
                        f"{path_choice_msg}\n"
                    )

                # if path isn't in possible_paths_list, try using the graph to validate the path. Allows for queries with loops and paths that have repeated nodes.
                if len(matching_paths) == 0:
                    possible_dot_paths: List[List[int]] = self.parse_dot_path(field)  # throws an error if path is invalid
                    shortest_full_paths: List[List[int]] = self.compare_paths(start_node_index, possible_dot_paths)
                    assert len(shortest_full_paths) != 0
                    if len(shortest_full_paths) > 1:
                        shortest_name_paths = [".".join([self.idx_to_name(idx) for idx in path if isinstance(self.schema_graph[idx], FieldNode)]) for path in shortest_full_paths]
                        shortest_name_paths.sort()
                        path_choice_msg = ""
                        for name_path in shortest_name_paths:
                            path_choice_msg += "  " + name_path + "\n"
                        raise ValueError(
                            "Given path not specific enough. Use one or more of these paths in return_data_list argument:\n"
                            f"{path_choice_msg}\n"
                            "Please note that this list may not be complete. "
                            "If looking for a different path, you can search the interactive editor's documentation explorer: https://data.rcsb.org/graphql/index.html"
                        )
                    idx_paths = shortest_full_paths
                
                final_idx: int = idx_paths[0][-1]
                all_paths[final_idx] = idx_paths

            # if no dots and the node name is unique in schema_graph
            else:
                node_idx = self.dot_field_to_idx_dict[field]
                paths = rx.digraph_all_shortest_paths(self.schema_graph, start_node_index, node_idx, weight_fn=lambda edge: edge)
                unique_paths = {tuple(path) for path in paths}
                unique_paths_list: List[List[int]] = [list(unique_path) for unique_path in unique_paths]
                all_paths[node_idx] = unique_paths_list

        for return_data in return_data_list:
            if any(not value for value in all_paths.values()):
                raise ValueError(f'You can\'t access "{return_data}" from input type {input_type}')

        final_fields = {}
        for target_idx in all_paths.keys():
            final_fields[target_idx] = self.get_descendant_fields(target_idx)

        field_names: Dict[Any, Any] = {}
        paths: Dict[Any, Any] = {}

        for target_idx, paths_list in all_paths.items():
            node_data = self.schema_graph[target_idx]
            if isinstance(node_data, FieldNode):
                field_names[target_idx] = []
                paths[target_idx] = []
            for each_path in paths_list:
                skip_first = True
                path = [node_idx for node_idx in each_path if isinstance(self.schema_graph[node_idx], FieldNode)][1:]
                paths[target_idx].append(path)
                for node_idx in each_path:
                    node_data = self.schema_graph[node_idx]
                    if isinstance(node_data, FieldNode):
                        if skip_first:
                            skip_first = False
                            continue
                        field_names[target_idx].append(node_idx)
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

    def find_idx_path(self, dot_path: List[str], idx_list: List[int], node_idx: int) -> List[int]:
        """function that recursively finds a list of indices that matches a list of field names.

        Args:
            dot_path (List[str]): list of field names to find index matches for
            idx_list (List[int]): list of matching indices, appended to as matches are found during recursion
            node_idx (int): index to be searched for a child node matching the next field name

        Returns:
            List[int]: a list of indices matching the given dot_path. If no path is found, an empty list is returned.
        """
        if len(dot_path) == 0:
            idx_list.append(node_idx)
            return idx_list
        if (self.schema_graph[node_idx].kind == "SCALAR") or (self.schema_graph[node_idx].of_kind == "SCALAR"):
            return self.find_idx_path(dot_path[1:], idx_list, node_idx)
        else:
            type_node = list(self.schema_graph.successor_indices(node_idx))[0]
            field_nodes = self.schema_graph.successor_indices(type_node)
            for field_idx in field_nodes:
                if self.schema_graph[field_idx].name == dot_path[0]:
                    idx_list.append(node_idx)
                    return self.find_idx_path(dot_path[1:], idx_list, field_idx)
                else:
                    continue
            return []

    def parse_dot_path(self, dot_path: str) -> List[List[int]]:
        """Parse dot-separated field names into lists of matching node indices
                ex: "prd.chem_comp.id" --> [[57, 81, 116], [610, 81, 116], [858, 81, 116]]

        Args:
            dot_path (str): dot-separated field names given in return_data_list
                ex: "exptl.method" or "prd.chem_comp.id"

        Raises:
            ValueError: thrown if no path matches dot_path

        Returns:
            List[List[int]]: list of paths where each path is a list of FieldNode indices matching the given dot_path
        """
        path_list = dot_path.split(".")
        node_matches: List[int] = self.field_to_idx_dict[path_list[0]]
        idx_path_list: List[List[int]] = []
        for node_idx in node_matches:
            found_path: List[int] = []
            found_path = self.find_idx_path(path_list[1:], found_path, node_idx)
            if len(found_path) == len(path_list):
                idx_path_list.append(found_path)
        if len(idx_path_list) == 0:
            raise ValueError(f"return_data_list path is not valid: {dot_path}")
        return idx_path_list

    def compare_paths(self, start_node_index: int, dot_paths: List[List[int]]) -> List[List[int]]:
        """Compare length of paths from the starting node to dot notation paths, returning the shortest paths

        Args:
            start_node_index (int): the index of query's input_type
                ex: input_type entry --> 20
            dot_paths (List[List[int]]):  a list of paths where each path is a list of node indices matching a dot notation string

        Raises:
            ValueError: thrown when there is no path from the input_type node to the return data nodes.

        Returns:
            List[List[int]]: list of shortest paths from the input_type node index to the index of the final field given in dot notation.
                ex: input_type "entry" and "exptl.method" would return a list of shortest path(s) with indices from "entry" to "method".
        """
        all_paths: List[List[int]] = []
        assembly_node_idxs = list(self.field_to_idx_dict["assemblies"])
        assembly_node_idxs.remove(self.dot_field_to_idx_dict["Query.assemblies"])  # nodes named "assemblies" except the root "assemblies"
        for path in dot_paths:
            first_path_idx = path[0]
            if start_node_index == first_path_idx:
                unique_paths_list: List[List[int]] = [path]
            else:
                paths = rx.digraph_all_shortest_paths(self.schema_graph, start_node_index, first_path_idx, weight_fn=lambda edge: edge)
                unique_paths = {tuple(path) for path in paths}
                unique_paths_list = [list(unique_path) for unique_path in unique_paths]
                if len(unique_paths_list) == 0:
                    unique_paths_list = []
                else:
                    for unique_path in unique_paths_list:
                        unique_path += path[1:]
            all_paths.extend(unique_paths_list)
        if len(all_paths) == 0:
            raise ValueError(f"Can't access \"{'.'.join(self.idx_path_to_name_path(dot_paths[0]))}\" from given input_type {self.schema_graph[start_node_index].name}")
        shortest_path_len = len(min(all_paths, key=len))
        shortest_paths = [path for path in all_paths if len(path) == shortest_path_len]
        shortest_paths = self._weigh_assemblies(shortest_paths, assembly_node_idxs)
        return shortest_paths
    
    def _weigh_assemblies(self, paths: List[List[int]], assembly_node_idxs: List[int]) -> List[List[int]]:
        """remove paths containing "assemblies" that are otherwise equivalent. Mimics weighing assembly edges in the rest of query construction

        Args:
            paths (List[List[int]]): list of paths where each path is a list of indices from a root node to a requested field.
            assembly_node_idxs (List[int]): list of indices of nodes named "assemblies" (root node excluded)

        Returns:
            List[List[int]]: List with weight applied (no "assemblies" path if there is an equivalent path present)
        """
        for path in paths:
            for assemblies_idx in assembly_node_idxs:
                if assemblies_idx in path:
                    path_no_assemblies = [field for field in path if field != assemblies_idx]
                    for compare_path in paths:
                        if compare_path == path:
                            continue
                        name_compare_path = self.idx_path_to_name_path(compare_path)
                        if (len(compare_path) == len(path)) and all(self.idx_to_name(field) in name_compare_path for field in path_no_assemblies):
                            paths.remove(path)
        return paths

    def idx_to_name(self, idx: int) -> str:
        """Given an index, return the associated node's name

        Args:
            idx (int): index of a node

        Returns:
            str: name of node
        """
        return self.schema_graph[idx].name

    def idx_path_to_name_path(self, idx_path: List[int]) -> List[str]:
        """Take a path of graph indices and return a path of field names

        Args:
            idx_path (List[int]): List of node indices (can be both TypeNodes and FieldNodes)

        Returns:
            List[str]: List of field names, removing TypeNodes.
        """
        name_path: List[str] = []
        for idx in idx_path:
            if isinstance(self.schema_graph[idx], FieldNode):
                name_path.append(self.schema_graph[idx].name)
        return name_path

    def find_paths(self, input_type: str, return_data_name: str) -> List[str]:
        """Find path from input_type to any nodes matching return_data_name

        Args:
            input_type (str): name of an input_type (ex: entry, polymer_entity_instance)
            return_data_name (str): name of one field, can be a redundant name

        Returns:
            List[str]: list of paths to nodes with names that match return_data_name
        """
        paths: List[List[int]] = []
        input_type_idx: int = self.dot_field_to_idx_dict[f"Query.{input_type}"]
        for possible_idx in self.field_to_idx_dict[return_data_name]:
            paths_to_idx = rx.all_simple_paths(self.schema_graph, input_type_idx, possible_idx)
            paths.extend(paths_to_idx)
        name_paths: List[List[str]] = []
        for path in paths:
            name_paths.append(self.idx_path_to_name_path(path))
        dot_paths: List[str] = [".".join(name_path[1:]) for name_path in name_paths]
        dot_paths.sort()
        return dot_paths
