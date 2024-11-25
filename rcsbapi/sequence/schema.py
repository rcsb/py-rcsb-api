import logging
import json
from typing import List, Dict, Union, Any, Optional
import os
import requests
from graphql import build_client_schema
import rustworkx as rx

from rcsbapi.const import seq_const
from rcsbapi.config import config

use_networkx: bool = False
# Below section and parts of code involving networkx are commented out
# May implement graph construction through networkx at a later point
# try:
#     import rustworkx as rx

#     logging.info("Using  rustworkx")
# except ImportError:
#     use_networkx = True

logger = logging.getLogger(__name__)


class FieldNode:
    """
    Node representing GraphQL field
        name (str): field name
        description (str): field description
        redundant (bool): whether field name is redundant in schema
        kind (str): "LIST", "SCALAR, or "OBJECT"
        of_kind (str): If "LIST", whether list of "SCALAR" or "OBJECT"
        type (str): GraphQL schema type (ex: CoreEntry)
        index (int): graph index
    """

    def __init__(self, kind: str, node_type: str, name: str, description: str):
        """Initialize FieldNodes

        Args:
            kind (str): GraphQL kind, can be "OBJECT", "SCALAR", "LIST"
            node_type (str): If applicable, the GraphQL type returned by the field
            name (str): Name of field
            description (str): Description of field
        """
        self.name: str = name
        self.description: str = description
        self.redundant: bool = False
        self.kind: str = kind
        self.of_kind: str = ""
        self.type: str = node_type
        self.index: Optional[int] = None

    def __str__(self) -> str:
        return f"Field Object name: {self.name}, Kind: {self.kind}, Type: {self.type}, Index if set: {self.index}, Description: {self.description}"

    def set_index(self, index: int):
        """set index that is associated with the FieldNode

        Args:
            index (int): index of node in schema_graph
        """
        self.index = index

    def set_of_kind(self, of_kind: str):
        """Only applicable if kind is LIST. Describes the GraphQL kind of the list (OBJECT, SCALAR)

        Args:
            of_kind (str): GraphQL kind of the list returned by a node (a LIST can be "of_kind" OBJECT)
        """
        self.of_kind = of_kind


class TypeNode:
    """
    Class for nodes representing GraphQL Types in the schema graph.
    """

    def __init__(self, name: str):
        """Initialize TypeNodes

        Args:
            name (str): name of GraphQL type (ex: CoreEntry)
        """
        self.name = name
        self.index: Optional[int] = None
        self.field_list: List[FieldNode] = []

    def set_index(self, index: int):
        """set index that is associated with the TypeNode

        Args:
            index (int): index of node in schema_graph
        """
        self.index = index

    def set_field_list(self, field_list: List[FieldNode]):
        """List of FieldNodes associated with the GraphQL type

        Args:
            field_list (Union[None, List[FieldNode]]): list of FieldNodes
        """
        self.field_list = field_list


class SeqSchema:
    """
    GraphQL schema defining available fields, types, and how they are connected.
    """

    def __init__(self) -> None:
        """
        GraphQL schema defining available fields, types, and how they are connected.
        """
        self.pdb_url: str = seq_const.API_ENDPOINT + "/graphql"
        self.timeout: int = config.DATA_API_TIMEOUT  # TODO: change?
        self.schema: Dict = self.fetch_schema()
        """JSON resulting from full introspection of the GraphQL schema"""

        self._use_networkx: bool = use_networkx
        # if use_networkx:
        #     self._schema_graph = nx.DiGraph()
        #     """NetworkX graph representing the GraphQL schema"""
        # else:
        #     self._schema_graph = rx.PyDiGraph()
        #     """rustworkx graph representing the GraphQL schema"""

        self._type_to_idx_dict: Dict[str, int] = {}
        self._field_to_idx_dict: Dict[str, List[int]] = {}
        """Dict where keys are field names and values are lists of indices.
        Indices of redundant fields are appended to the list under the field name. (ex: {id: [[43, 116, 317...]})"""
        self._root_introspection = self._request_root_types()
        """Request root types of the GraphQL schema and their required arguments"""
        self._client_schema = build_client_schema(self.schema["data"])
        """GraphQLSchema object from graphql package, used for query validation"""
        self._type_fields_dict: Dict[str, Dict] = self._construct_type_dict()
        """Dict where keys are type names and the values are their associated fields"""
        self._field_names_list = self._construct_name_list()
        """list of all field names"""
        self._root_dict: Dict[str, List[Dict[str, str]]] = self._construct_root_dict()
        self._schema_graph: rx.PyDiGraph = rx.PyDiGraph()
        self._schema_graph = self._recurse_build_schema(self._schema_graph, "Query")
        self._root_to_idx: Dict[str, int] = self._make_root_to_idx()
        self._field_names_list = self._construct_name_list()
        """Dict where keys are field names and values are indices. Redundant field names are represented as <parent_field_name>.<field_name> (ex: {entry.id: 1452})"""

    def _request_root_types(self) -> Dict:
        """Make an introspection query to get information about schema's root types

        Returns:
            Dict: JSON response of introspection request
        """
        root_query = {"query": """query IntrospectionQuery{ __schema{ queryType{ fields{ name args
        { name description type{ kind ofType{ name kind ofType{ inputFields {name type { kind ofType { name kind ofType { ofType { kind name ofType {kind name}} } } } }
        kind name ofType{name kind} } } } } } } } }"""}
        response = requests.post(headers={"Content-Type": "application/json"}, json=root_query, url=self.pdb_url, timeout=self.timeout)
        return response.json()

    def _construct_root_dict(self) -> Dict[str, List[Dict[str, str]]]:
        """Build a dictionary to organize information about schema root types.

        Returns:
            Dict[str, List[Dict]]: Dict where keys are the type names.
            Values are lists of dictionaries with information about arguments.

            ex: {"alignments": [{'name': 'from', 'description': 'Query sequence database'...}, ...], ...}
        """
        response = self._root_introspection
        root_dict: Dict[str, List[Dict[str, str]]] = {}
        root_fields_list = response["data"]["__schema"]["queryType"]["fields"]
        for name_arg_dict in root_fields_list:
            root_name = name_arg_dict["name"]
            arg_dict_list = name_arg_dict["args"]
            for arg_dict in arg_dict_list:
                arg_name = arg_dict["name"]
                arg_description = arg_dict["description"]
                arg_kind = arg_dict["type"]["kind"]
                arg_of_kind = ""
                arg_of_type = ""
                if arg_kind == "LIST" or arg_kind == "NON_NULL":
                    arg_of_kind = arg_dict["type"]["ofType"]["kind"]
                    arg_of_type = self._find_type_name(arg_dict["type"]["ofType"])
                input_fields = ""
                if ("ofType" in arg_dict["type"]["ofType"]) and (arg_dict["type"]["ofType"]["ofType"] is not None):
                    if ("inputFields" in arg_dict["type"]["ofType"]["ofType"]) and (arg_dict["type"]["ofType"]["ofType"]["inputFields"] is not None):
                        input_fields = arg_dict["type"]["ofType"]["ofType"]["inputFields"]
                if root_name not in root_dict:
                    root_dict[root_name] = []
                root_dict[root_name].append({
                    "name": arg_name,
                    "description": arg_description,
                    "kind": arg_kind,
                    "of_kind": arg_of_kind,
                    "of_type": arg_of_type,
                    "input_fields": input_fields
                })
        return root_dict

    def fetch_schema(self) -> Dict:
        """Make an introspection query to get full Data API query.
        Can also be found in resources folder as "data_api_schema.json"

        Returns:
            Dict: JSON response of introspection request
        """
        query = {
            "query": """query IntrospectionQuery { __schema
            { queryType { name } types { kind name description fields(includeDeprecated: true)
            { name description args { name description type { kind name ofType { kind name ofType
            { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType
            { kind name } } } } } } } } defaultValue } type { kind name ofType { kind name ofType { kind name
            ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name } } } } } } } }
            isDeprecated deprecationReason } inputFields { name description type { kind name ofType
            { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType
            { kind name ofType { kind name } } } } } } } } defaultValue } interfaces { kind name ofType
            { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType
            { kind name } } } } } } } } enumValues(includeDeprecated: true) { name description isDeprecated deprecationReason }
            possibleTypes { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType
            { kind name ofType { kind name ofType { kind name } } } } } } } } } directives { name description locations args
            { name description type { kind name ofType { kind name ofType { kind name ofType { kind name ofType
            { kind name ofType { kind name ofType { kind name ofType { kind name } } } } } } } } defaultValue } } }}"""
        }
        schema_response = requests.post(headers={"Content-Type": "application/json"}, json=query, url=self.pdb_url, timeout=self.timeout)
        if schema_response.status_code == 200:
            return schema_response.json()
        logger.info("Loading data schema from file")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(current_dir, "resources", "seq_api_schema.json")
        with open(json_file_path, "r", encoding="utf-8") as schema_file:
            return json.load(schema_file)

    def _construct_type_dict(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Construct dictionary of GraphQL types and their associated fields.

        Args:
            schema (Dict): GraphQL schema

        Returns:
            Dict[str, Dict[str, Dict[str, str]]]: Dict where keys are GraphQL types and values are lists of field names
        """
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

    def _construct_name_list(self) -> List[str]:
        """construct a list of all field names in the schema.
        Used to determine whether a redundant field and if a field is known.

        Returns:
            List[str]: list of all fields
        """
        field_names_list = []
        for type_name, field_dict in self._type_fields_dict.items():
            if "__" in type_name:
                continue
            for field_name in field_dict.keys():
                field_names_list.append(field_name)
        return field_names_list

    def make_type_subgraph(self, type_name: str) -> TypeNode:
        """Make a subgraph of only one type and its associated fields

        Args:
            type_name (str): name of the type for which to construct subgraph

        Returns:
            TypeNode: returns TypeNode constructed from type_name
        """
        field_name_list = self._type_fields_dict[type_name].keys()
        field_node_list = []
        type_node = self._make_type_node(type_name)
        for field_name in field_name_list:
            parent_type_name = type_name
            field_node = self._make_field_node(parent_type_name, field_name)
            field_node_list.append(field_node)
        type_node.set_field_list(field_node_list)
        return type_node

    def _recurse_build_schema(self, schema_graph: rx.PyDiGraph, type_name: str) -> rx.PyDiGraph:
        """Build the API schema by iterating through the fields of the given type
        and building subgraphs for each one recursively until a scalar (leaf) is reached

        Args:
            schema_graph (rx.PyDiGraph): graph object to build into
            type_name (str): name of type whose fields will be iterated through

        Returns:
            rx.PyDiGraph: returns complete schema graph object
        """
        type_node = self.make_type_subgraph(type_name)
        for field_node in type_node.field_list:
            assert isinstance(field_node.index, int)  # for mypy
            if field_node.kind == "SCALAR" or field_node.of_kind == "SCALAR":
                continue
            else:
                type_name = field_node.type
                if type_name in self._type_to_idx_dict:
                    type_index = self._type_to_idx_dict[type_name]
                    if use_networkx:
                        schema_graph.add_edge(field_node.index, type_index, 1)
                    else:
                        schema_graph.add_edge(field_node.index, type_index, 1)
                else:
                    self._recurse_build_schema(schema_graph, type_name)
                    type_index = self._type_to_idx_dict[type_name]
                    # if self._use_networkx:
                    #     schema_graph.add_edge(field_node.index, type_index, 1)
                    if self._use_networkx is False:
                        schema_graph.add_edge(field_node.index, type_index, 1)
        return schema_graph

    # def _apply_weights(self, root_type_list: List[str], weight: int) -> None:
    #     """applies weight to all edges from a root TypeNode to FieldNodes

    #     Args:
    #         root_type_list (List[str]): list of root fields to apply weights to
    #             ex: "CoreEntry", "CoreAssembly"
    #         weight (int): integer weight to apply to edges from specified type(s)
    #     """
    #     for root_type in root_type_list:
    #         node_idx = self._type_to_idx_dict[root_type]
    #         if use_networkx is False:
    #             assert isinstance(self._schema_graph, rx.PyDiGraph)
    #             out_edge_list = self._schema_graph.incident_edges(node_idx)
    #             for edge_idx in out_edge_list:
    #                 self._schema_graph.update_edge_by_index(edge_idx, weight)
    #         # else:
    #         #     out_edge_list = self._schema_graph.edges(node_idx)
    #         #     nx.set_edge_attributes(
    #         #         self._schema_graph,
    #         #         {edge_tuple: {"weight": weight} for edge_tuple in out_edge_list}
    #         #     )

    def _make_type_node(self, type_name: str) -> TypeNode:
        type_node = TypeNode(type_name)
        # if self._use_networkx:
        #     index = len(self._schema_graph.nodes)
        #     self._schema_graph.add_node(index, type_node=type_node)
        # if self._use_networkx is False:
        index = self._schema_graph.add_node(type_node)
        self._type_to_idx_dict[type_name] = index
        type_node.set_index(index)
        return type_node

    def _find_kind(self, field_dict: Dict) -> str:
        if field_dict["name"] is not None:
            return field_dict["kind"]
        return self._find_kind(field_dict["ofType"])

    def _find_type_name(self, field_dict: Dict) -> str:
        if field_dict:
            if field_dict["name"] is not None:
                return field_dict["name"]
            return self._find_type_name(field_dict["ofType"])
        return ""

    def _find_description(self, type_name: str, field_name: str) -> str:
        for type_dict in self.schema["data"]["__schema"]["types"]:
            if type_dict["name"] == type_name:
                for field in type_dict["fields"]:
                    if field["name"] == field_name:
                        return field["description"]
        return ""

    def _make_field_node(self, parent_type: str, field_name: str) -> FieldNode:
        kind = self._type_fields_dict[parent_type][field_name]["kind"]
        field_type_dict: Dict = self._type_fields_dict[parent_type][field_name]
        return_type = self._find_type_name(field_type_dict)
        description = self._find_description(parent_type, field_name)
        field_node = FieldNode(kind, return_type, field_name, description)
        assert field_node.type is not None
        if kind == "LIST" or kind == "NON_NULL":
            of_kind = self._find_kind(field_type_dict)
            field_node.set_of_kind(of_kind)
        parent_type_index = self._type_to_idx_dict[parent_type]
        # if self._use_networkx:
        #     index = len(self._schema_graph.nodes
        #     self._schema_graph.add_node(index, field_node=field_node)
        #     self._schema_graph.add_edge(parent_type_index, index, weight=1)
        # if self._use_networkx is False:
        if field_node.kind == "SCALAR" or field_node.of_kind == "SCALAR":
            index = self._schema_graph.add_child(parent_type_index, field_node, 1)
        else:
            index = self._schema_graph.add_child(parent_type_index, field_node, 1)
        if self._field_names_list.count(field_name) > 1:
            field_node.redundant = True
        field_node.set_index(index)

        assert isinstance(field_node.index, int)  # for mypy
        if field_name not in self._field_to_idx_dict:
            self._field_to_idx_dict[field_name] = [field_node.index]
        else:
            self._field_to_idx_dict[field_name].append(field_node.index)

        return field_node

    def _make_root_to_idx(self) -> Dict[str, int]:
        root_to_idx: Dict[str, int] = {}
        # Assumes 0 is the index for root Query node.
        # Remains true as long as graph building starts from there
        for root_node in self._schema_graph.successors(0):
            root_to_idx[root_node.name] = root_node.index
        return root_to_idx

    def get_input_id_dict(self, input_type: str) -> Dict[str, str]:
        if input_type not in self._root_dict.keys():
            raise ValueError("Not a valid input_type, no available input_id dictionary")
        root_dict_entry = self._root_dict[input_type]
        input_dict = {}
        for arg in root_dict_entry:
            name = arg["name"]
            description = arg["description"]
            if (len(root_dict_entry) == 1) and root_dict_entry[0]["name"] == "entry_id":
                description = "ID"
            input_dict[name] = description
        return input_dict

    def _recurse_fields(self, fields: Dict[Any, Any], field_map: Dict[Any, Any]) -> str:
        query_str = ""
        for target_idx, idx_path in fields.items():
            mapped_path = field_map.get(target_idx, [target_idx])
            mapped_path = mapped_path[: mapped_path.index(target_idx) + 1]  # Only take the path up to the field itself
            for idx, subfield in enumerate(mapped_path):
                query_str += " " + self._idx_to_name(subfield)
                if idx < len(mapped_path) - 1 or (isinstance(idx_path, list) and idx_path):
                    query_str += "{ "
                else:
                    query_str += " "
            if isinstance(idx_path, list):
                if idx_path:  # Only recurse if the list is not empty
                    for item in idx_path:
                        if isinstance(item, dict):
                            query_str += self._recurse_fields(item, field_map)
                        else:
                            query_str += " " + self._idx_to_name(item)
            else:
                query_str += " " + idx_path
            for idx, subfield in enumerate(mapped_path):
                if idx < len(mapped_path) - 1 or (isinstance(idx_path, list) and idx_path):
                    query_str += " " + "} "
        return query_str

    def _get_descendant_fields(self, node_idx: int, field_name: str, visited=None) -> List[Union[int, Dict]]:
        if visited is None:
            visited = set()

        result: List[Union[int, Dict]] = []
        children_idx = list(self._schema_graph.neighbors(node_idx))

        for idx in children_idx:
            if idx in visited:
                raise ValueError(f"{field_name} in return_data_list is too general, unable to autocomplete query.\n" "Please request a more specific field.")

            visited.add(idx)
            child_data = self._schema_graph[idx]
            assert isinstance(child_data.index, int)  # for mypy

            if isinstance(child_data, FieldNode):
                child_descendants = self._get_descendant_fields(idx, field_name, visited)
                # If further subfields append as dictionary. ex: {field index: [subfield1, subfield2, ...]}
                if child_descendants:
                    result.append({child_data.index: child_descendants})
                # If scalar, append index
                else:
                    result.append(child_data.index)
            elif isinstance(child_data, TypeNode):
                type_descendants = self._get_descendant_fields(idx, field_name, visited)
                # If further subfields, append the list of descendants (indices and index dicts)
                if type_descendants:
                    result.extend(type_descendants)
                # Skips appending if no further subfields (ENUMS)
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
        field_names = [key for key in self._field_to_idx_dict if search_string.lower() in key.lower()]
        if not field_names:
            raise ValueError(f"No fields found matching '{search_string}'")
        return field_names

    def construct_query(
        self,
        query_type: str,
        query_args: Union[Dict[str, str], Dict[str, list]],
        return_data_list: List[str],
        suppress_autocomplete_warning=False
    ) -> Dict:
        unknown_return_list: List[str] = []
        for field in return_data_list:
            if "." in field:
                separate_fields = field.split(".")
                for sep_field in separate_fields:
                    if sep_field not in self._field_names_list:
                        unknown_return_list.append(sep_field)
            else:
                if field not in self._field_names_list:
                    unknown_return_list.append(field)
        if unknown_return_list:
            raise ValueError(f"Unknown item in return_data_list: {unknown_return_list}")
        # if use_networkx:
        #     query = self._construct_query_networkx(
        #         input_type=input_type,
        #         input_ids=input_ids,
        #         return_data_list=return_data_list,
        #         suppress_autocomplete_warning=suppress_autocomplete_warning
        #     )
        # else:
            # query = self._construct_query_rustworkx(
            #     input_type=input_type,
            #     input_ids=input_ids,
            #     return_data_list=return_data_list,
            #     add_rcsb_id=add_rcsb_id,
            #     suppress_autocomplete_warning=suppress_autocomplete_warning
            # )
        query = self._construct_query_rustworkx(
            query_type=query_type,
            query_args=query_args,
            return_data_list=return_data_list,
            suppress_autocomplete_warning=suppress_autocomplete_warning
        )
        return query

    # def _construct_query_networkx(
    #     self,
    #     input_type: str,
    #     input_ids: Union[Dict[str, str], List[str]],
    #     return_data_list: List[str],
    #     add_rcsb_id: bool,
    #     suppress_autocomplete_warning: bool
    # ):  # Incomplete function
    #     query = ""
    #     return query

    def _construct_query_rustworkx(
        self,
        query_type: str,
        query_args: Union[Dict[str, str], Dict[str, list]],
        return_data_list: List[str],
        suppress_autocomplete_warning: bool = False,
    ) -> Dict:
        """Construct a GraphQL query as JSON using a rustworkx graph.

        Args:
            input_ids (Union[List[str], Dict[str, str], Dict[str, List[str]]]): identifying information for the specific entry, chemical component, etc to query
            input_type (str): specifies where you are starting your query. These are specific fields like "entry" or "polymer_entity_instance".
            return_data_list (List[str]): requested data, can be field name(s) or dot-separated field names
                ex: "cluster_id" or "exptl.method"

        Raises:
            ValueError: input_ids dictionary keys don't match the input_type given
            ValueError: input_ids dictionary keys missing
            ValueError: input_ids dictionary value should be a string, but another type was passed in
            ValueError: field in return_data_list exists, but is a redundant name and needs to be further specified
            ValueError: path in return_data_list exists, but is a redundant and needs to be further specified

        Returns:
            str: query in GraphQL syntax
        """
        arg_list = self._root_dict[query_type]
        # arg_name_list = [id["name"] for id in arg_list]  # might need to revert back to this

        # # Check formatting of input_ids
        # input_dict: Union[Dict[str, str], Dict[str, List[str]]] = {}

        # if isinstance(input_ids, Dict):
        #     input_dict = input_ids
        #     if not all(key in arg_name_list for key in input_dict.keys()):
        #         raise ValueError(f"Input IDs keys do not match: {input_dict.keys()} vs {arg_name_list}")
        #     missing_keys = [key_arg for key_arg in arg_name_list if key_arg not in input_dict]
        #     if len(missing_keys) > 0:
        #         raise ValueError(
        #             f"Missing input_id dictionary keys: {missing_keys}. Find input_id keys and descriptions by running:\n"
        #             f"  from rcsbapi.data import Schema\n"
        #             f"  schema = Schema()\n"
        #             f'  schema.get_input_id_dict("{input_type}")'
        #         )
        #     attr_kind = {attr["name"]: attr["kind"] for attr in attr_list}
        #     for key, value in input_dict.items():
        #         if attr_kind[key] == "SCALAR":
        #             if not isinstance(value, str):
        #                 raise ValueError(f"Input ID for {key} should be a single string")
        #         elif attr_kind[key] == "LIST":
        #             if not isinstance(value, list):
        #                 raise ValueError(f"Input ID for {key} should be a list of strings")
        #             if not all(isinstance(item, str) for item in value):
        #                 raise ValueError(f"Input ID for {key} should be a list of strings")

        start_node_index = self._root_to_idx[query_type]

        return_data_paths: Dict[int, List[List[int]]] = {}
        complete_path: int = 0

        for field in return_data_list:
            # Generate list of all possible paths to the final requested field. Try to find matching sequence to user input.
            path_list = field.split(".")
            possible_paths = self.find_paths(query_type, path_list[-1])
            matching_paths: List[str] = []
            for path in possible_paths:
                possible_path_list = path.split(".")
                possible_path_list.insert(0, str(query_type))

                # If there is an exact path match,
                # the path is fully specified and other possible_paths can be removed and loop can stop.
                # Iterate complete path, so warning can be raised if autocompletion is used
                path_list_with_input = [query_type] + path_list
                if (possible_path_list == path_list) or (possible_path_list == path_list_with_input):
                    matching_paths = [".".join(possible_path_list)]
                    complete_path += 1
                    break
                # Else, check for matching path segments.
                else:
                    for i in range(len(possible_path_list)):
                        if possible_path_list[i: i + len(path_list)] == path_list:
                            matching_paths.append(".".join(possible_path_list))

            idx_paths: List[List[int]] = []
            if len(matching_paths) > 0:
                for path in matching_paths:
                    idx_paths.extend(self._parse_dot_path(path))

            # remove paths not beginning with input_type
            full_idx_paths: List[List[int]] = list(idx_paths)
            input_type_idx = self._root_to_idx[query_type]
            for path in idx_paths:
                if path[0] != input_type_idx:
                    full_idx_paths.remove(path)
            idx_paths = full_idx_paths

            if len(idx_paths) > 1:
                # Print error message that doesn't include input_type at beginning
                # But keep input_type in matching_paths for query construction reasons
                path_choice_msg = "  " + "\n  ".join([".".join(path.split(".")[1:]) for path in matching_paths[:10]])
                if len(matching_paths) > 10:
                    len_path = 10
                else:
                    len_path = len(matching_paths)

                if len(matching_paths) > 10:
                    raise ValueError(
                        f'Given path "{field}" not specific enough. Use one or more of these paths in return_data_list argument:\n\n'
                        f"{len_path} of {len(matching_paths)} possible paths:\n"
                        f"{path_choice_msg}"
                        f"\n  ...\n\n"
                        f"For all paths run:\n"
                        f"  from rcsbapi.data import Schema\n"
                        f"  schema = Schema()\n"
                        f'  schema.find_paths("{query_type}", "{path_list[-1]}")'
                    )

                raise ValueError(
                    f'Given path  "{field}" not specific enough. Use one or more of these paths in return_data_list argument:\n\n'
                    f"{len_path} of {len(matching_paths)} possible paths:\n"
                    f"{path_choice_msg}"
                )

            # If path isn't in possible_paths_list, try using the graph to validate the path. Allows for queries with loops and paths that have repeated nodes.
            if len(idx_paths) == 0:
                possible_dot_paths: List[List[int]] = self._parse_dot_path(field)  # Throws an error if path is invalid
                shortest_full_paths: List[List[int]] = self._compare_paths(start_node_index, possible_dot_paths)
                assert len(shortest_full_paths) != 0
                if len(shortest_full_paths) > 1:
                    shortest_name_paths = [".".join([self._idx_to_name(idx) for idx in path[1:] if isinstance(self._schema_graph[idx], FieldNode)]) for path in shortest_full_paths]
                    shortest_name_paths.sort()
                    path_choice_msg = ""
                    for name_path in shortest_name_paths:
                        path_choice_msg += "  " + name_path + "\n"
                    raise ValueError(
                        "Given path not specific enough. Use one or more of these paths in return_data_list argument:\n\n"
                        f"{path_choice_msg}\n"
                        "Please note that this list may not be complete. "
                        "If looking for a different path, you can search the interactive editor's documentation explorer: https://data.rcsb.org/graphql/index.html"
                    )
                idx_paths = shortest_full_paths
            final_idx: int = idx_paths[0][-1]
            return_data_paths[final_idx] = idx_paths

        if (complete_path != len(return_data_list)) and (suppress_autocomplete_warning is False):
            info_list = []
            for path in return_data_paths.values():
                assert len(path) == 1
                info_list.append(".".join(self._idx_path_to_name_path(path[0][1:])))

            path_msg = "".join(f'\n        "{item}",' for item in info_list)
            logger.warning(
                "\n"
                "Some paths are being autocompleted based on the current API. If this code is meant for long-term use, use the set of fully-specified paths below:\n"
                "    ["
                "%s\n"
                "    ]", path_msg
            )

        for return_data in return_data_list:
            if any(not value for value in return_data_paths.values()):
                raise ValueError(f'You can\'t access "{return_data}" from input type {query_type}')

        final_fields = {}
        for target_idx in return_data_paths.keys():
            final_fields[target_idx] = self._get_descendant_fields(node_idx=target_idx, field_name=self._schema_graph[target_idx].name)

        field_names: Dict[Any, Any] = {}
        paths: Dict[Any, Any] = {}

        for target_idx, paths_list in return_data_paths.items():
            node_data = self._schema_graph[target_idx]
            if isinstance(node_data, FieldNode):
                field_names[target_idx] = []
                paths[target_idx] = []
            for each_path in paths_list:
                skip_first = True
                path = [node_idx for node_idx in each_path if isinstance(self._schema_graph[node_idx], FieldNode)][1:]
                paths[target_idx].append(path)
                for node_idx in each_path:
                    node_data = self._schema_graph[node_idx]
                    if isinstance(node_data, FieldNode):
                        if skip_first:
                            skip_first = False
                            continue
                        field_names[target_idx].append(node_idx)

        query = "query { " + query_type + "("

        num_arg_added = 0
        for arg_dict in arg_list:
            arg_name = arg_dict["name"]
            # If arg not in query_args, assume it's an optional (checking done earlier)
            if arg_name not in query_args:
                continue
            query += self.format_args(arg_dict, query_args[arg_name])
            num_arg_added += 1
            if num_arg_added < (len(query_args) - 1):
                query += ", "

        query += ") { "
        query += self._recurse_fields(final_fields, field_names)
        query += " } }"
        json_query = {"query": f"{query}"}
        return json_query

    def format_args(self, arg_dict: Union[Dict[str, list], Dict[str, str]], input_value: Union[str, List[str]]) -> str:
        """Add double quotes or omit quotes around a single GraphQL argument

        Args:
            arg_dict (Dict[str, str]): dictionary with information about the argument
            input_value (str): input value of the argument

        Returns:
            str: returns input value formatted with quotes, no quotes, or as a list
        """
        format_arg = ""
        if arg_dict["kind"] == "LIST" or arg_dict["of_kind"] == "LIST":
            if arg_dict["of_type"] == "String":
                # Add double quotes around each item
                format_arg += f'{arg_dict["name"]}: {str(input_value).replace("'", '"')}'
            else:
                # Remove single quotes if not string
                format_arg += f'{arg_dict["name"]}: {str(input_value).replace("'", "")}'
        elif arg_dict["of_type"] == "String":
            # If arg type is string, add double quotes around value
            format_arg += f'{arg_dict["name"]}: "{input_value}"'
        else:
            assert isinstance(input_value, str)
            format_arg += f"{arg_dict["name"]}: {input_value}"
        return format_arg

    def _find_idx_path(self, dot_path: List[str], idx_list: List[int], node_idx: int) -> List[int]:
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
        if (self._schema_graph[node_idx].kind == "SCALAR") or (self._schema_graph[node_idx].of_kind == "SCALAR"):
            return self._find_idx_path(dot_path[1:], idx_list, node_idx)
        else:
            type_node = list(self._schema_graph.successor_indices(node_idx))[0]
            field_nodes = self._schema_graph.successor_indices(type_node)
            for field_idx in field_nodes:
                if self._schema_graph[field_idx].name == dot_path[0]:
                    idx_list.append(node_idx)
                    return self._find_idx_path(dot_path[1:], idx_list, field_idx)
                else:
                    continue
            return []

    def _parse_dot_path(self, dot_path: str) -> List[List[int]]:
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
        node_matches: List[int] = self._field_to_idx_dict[path_list[0]]
        idx_path_list: List[List[int]] = []
        for node_idx in node_matches:
            found_path: List[int] = []
            found_path = self._find_idx_path(path_list[1:], found_path, node_idx)
            if len(found_path) == len(path_list):
                idx_path_list.append(found_path)
        if len(idx_path_list) == 0:
            raise ValueError(f"return_data_list path is not valid: {dot_path}")

        return idx_path_list

    def _compare_paths(self, start_node_index: int, dot_paths: List[List[int]]) -> List[List[int]]:
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

        for path in dot_paths:
            first_path_idx = path[0]
            if start_node_index == first_path_idx:
                unique_paths_list: List[List[int]] = [path]
            else:
                paths = rx.digraph_all_shortest_paths(self._schema_graph, start_node_index, first_path_idx, weight_fn=lambda edge: edge)
                unique_paths = {tuple(path) for path in paths}
                unique_paths_list = [list(unique_path) for unique_path in unique_paths]
                if len(unique_paths_list) == 0:
                    unique_paths_list = []
                else:
                    for unique_path in unique_paths_list:
                        unique_path += path[1:]
            all_paths.extend(unique_paths_list)
        if len(all_paths) == 0:
            raise ValueError(f"Can't access \"{'.'.join(self._idx_path_to_name_path(dot_paths[0]))}\" from given input_type {self._schema_graph[start_node_index].name}")
        shortest_path_len = len(min(all_paths, key=len))
        shortest_paths = [path for path in all_paths if len(path) == shortest_path_len]
        return shortest_paths

    def _weigh_assemblies(self, paths: List[List[int]], assembly_node_idxs: List[int]) -> List[List[int]]:
        """remove paths containing "assemblies" if there are shorter or equal length paths available.
        Mimics weighing assembly edges in the rest of query construction.

        Args:
            paths (List[List[int]]): list of paths where each path is a list of indices from a root node to a requested field.
            assembly_node_idxs (List[int]): list of indices of nodes named "assemblies" (root node excluded)

        Returns:
            List[List[int]]: List with weight applied (no "assemblies" path if there is an equivalent path present)
        """
        remove_paths: set = set()

        for path in paths:
            for assemblies_idx in assembly_node_idxs:
                if assemblies_idx in path:
                    for compare_path in paths:
                        if compare_path == path:
                            continue
                        name_compare_path = self._idx_path_to_name_path(compare_path)
                        # If there are shorter or equal length paths without "assemblies", filter out
                        if (
                            (len(compare_path) <= len(path))
                            and ("assemblies" not in name_compare_path)
                            and (compare_path[-1] == path[-1])
                        ):
                            remove_paths.add(tuple(path))

        for path in remove_paths:
            paths.remove(list(path))

        return paths

    def _idx_to_name(self, idx: int) -> str:
        """Given an index, return the associated node's name

        Args:
            idx (int): index of a node

        Returns:
            str: name of node
        """
        return self._schema_graph[idx].name

    def _idx_path_to_name_path(self, idx_path: List[int]) -> List[str]:
        """Take a path of graph indices and return a path of field names

        Args:
            idx_path (List[int]): List of node indices (can be both TypeNodes and FieldNodes)

        Returns:
            List[str]: List of field names, removing TypeNodes.
        """
        name_path: List[str] = []
        for idx in idx_path:
            if isinstance(self._schema_graph[idx], FieldNode):
                name_path.append(self._schema_graph[idx].name)
        return name_path

    def find_paths(self, input_type: str, return_data_name: str, descriptions: bool = False) -> Union[List[str], Dict]:
        """Find path from input_type to any nodes matching return_data_name

        Args:
            input_type (str): name of an input_type (ex: entry, polymer_entity_instance)
            return_data_name (str): name of one field, can be a redundant name
            description (bool, optional): whether to include descriptions for the final field of each path. Default is False.

        Returns:
            Union[List[str], Dict]
                List[str]: list of paths to nodes with names that match return_data_name
                Dict: if description is True, a dictionary with paths as keys and descriptions as values is returned.
        """
        paths: List[List[int]] = []
        input_type_idx: int = self._root_to_idx[input_type]
        for possible_idx in self._field_to_idx_dict[return_data_name]:
            paths_to_idx = rx.all_simple_paths(self._schema_graph, input_type_idx, possible_idx)
            paths.extend(paths_to_idx)
        dot_paths: List[str] = []
        description_dict: Dict[str, str] = {}
        for path in paths:
            name_path = self._idx_path_to_name_path(path)
            dot_path = ".".join(name_path[1:])
            dot_paths.append(dot_path)
            if descriptions:
                final_field_idx = path[-1]
                description = self._schema_graph[final_field_idx].description
                if description is None:
                    description = ""
                description_dict[dot_path] = description.replace("\n", " ")

        if descriptions:
            return description_dict
        dot_paths.sort()
        return dot_paths

    def read_enum(self, type_name: str) -> List[str]:
        """parse given type name into a list of enumeration values

        Args:
            type_name (str): GraphQL type name
        """
        for type_dict in self.schema["data"]["__schema"]["types"]:
            if type_dict["name"] == type_name:
                enum_values = []
                for value in type_dict["enumValues"]:
                    enum_values.append(value["name"])
        return enum_values

    def check_typing(self, query_type: str, enum_types, args: Dict[str, Any]):
        """Check that arguments match typing specified in schema

        Args:
            query_type (str): Name of query field (annotations, alignments, etc)
            enum_types (Enum): Enum class of GraphQL types that are enumerations.
                Values are lists of valid strings corresponding to enumerations
            kwargs**: key word arguments corresponding to query-specific arguments
        """
        error_list = []
        arg_dict_list = self._root_dict[query_type]
        for arg_dict in arg_dict_list:
            arg_type = arg_dict["of_type"]
            arg_name = arg_dict["name"]

            if arg_name not in args:
                continue

            if arg_dict["kind"] == "NON_NULL":
                if arg_dict["of_kind"] == "ENUM":
                    if args[arg_name] not in enum_types[arg_type].value:
                        error_list.append(
                            f"Invalid value '{args[arg_name]}' for '{arg_name}': valid values are {enum_types[arg_type].value}"
                        )

            if arg_dict["kind"] == "LIST":
                if not isinstance(args[arg_name], list):
                    error_list.append(
                        f"'{arg_name}' must be a list"
                    )

            # List of ENUMs
            if arg_dict["kind"] == "NON_NULL":
                if arg_dict["of_kind"] == "LIST":
                    mismatch_type = [item for item in args[arg_name] if item not in enum_types[arg_type].value]
                    if mismatch_type:
                        raise ValueError(
                            f"Invalid value(s) {mismatch_type} for '{arg_name}': valid values are {enum_types[arg_type].value}"
                        )

        if error_list:
            raise ValueError(
                "\n" + "  " +
                "\n  ".join(error_list)
            )
