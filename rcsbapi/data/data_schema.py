"""Fetching and Parsing API's GraphQL schema."""

from __future__ import annotations
from typing import Any, List, Dict, Union
import re

from rcsbapi.const import const
from rcsbapi.config import config
from rcsbapi.graphql_schema import GQLSchema, SchemaEnum


class DataAPIEnums(SchemaEnum):
    pass


class DataSchema(GQLSchema):
    def __init__(self) -> None:
        super().__init__(
            endpoint=const.DATA_API_ENDPOINT,
            timeout=config.API_TIMEOUT,
            fallback_file=const.DATA_API_SCHEMA_FILENAME,
            # remove paths containing "assemblies" if there are shorter or equal length paths available.
            weigh_nodes=["assemblies"]
        )

    # pylint: disable=arguments-differ
    def construct_query(  # type: ignore[override]
        self,
        input_type: str,
        input_ids: Union[List[str], Dict[str, str], Dict[str, List[str]]],
        return_data_list: List[str],
        add_rcsb_id: bool = True,
        suppress_autocomplete_warning: bool = False
    ) -> Dict[str, Any]:
        """Construct a GraphQL query in JSON format

        Args:
            input_ids (Union[List[str], Dict[str, str], Dict[str, List[str]]]): identifying information for the specific entry, chemical component, etc to query
            input_type (str): specifies where you are starting your query. These are specific fields like "entry" or "polymer_entity_instance".
            return_data_list (List[str]): requested data, can be field name(s) or dot-separated field names
                ex: "cluster_id" or "exptl.method"
            add_rcsb_id (bool): automatically request rcsb_id at the top of the query. Default is True.
            suppress_autocomplete_warning (bool, optional): Whether to suppress warning when
                autocompletion of paths is used. Defaults to False.

        Returns:
            Dict[str, Any]: dictionary of format - {"query": <query in GraphQL syntax>}
        """
        suppress_autocomplete_warning = config.SUPPRESS_AUTOCOMPLETE_WARNING if config.SUPPRESS_AUTOCOMPLETE_WARNING else suppress_autocomplete_warning

        # Do basic type-checking and validation of input_ids and input_type
        if not (isinstance(input_ids, dict) or isinstance(input_ids, list)):
            raise ValueError("input_ids must be dictionary or list")
        input_type_idx: int = self._root_to_idx[input_type]
        if isinstance(input_ids, List) and (len(input_ids) > 1):
            # Below object will be a FieldNode, so mypy error overridden
            if self._schema_graph[input_type_idx].kind == "OBJECT":  # type: ignore[union-attr]
                raise ValueError(f'Entered multiple input_ids, but input_type is not a plural type. Try making "{input_type}" plural')
        if input_type not in self._root_dict:
            raise ValueError(f"Unknown input type: {input_type}")

        # Check for invalid fields in `return_data_list`
        self._check_return_list(return_data_list)

        query_args = self._construct_query_args(input_ids=input_ids, input_type=input_type)

        # Validate query_args, throw ValueError if there's a problem
        self._check_input_ids(query_args=query_args, input_type=input_type)
        self._check_typing(query_type=input_type, enum_types=DataAPIEnums, args=query_args)
        return self._construct_query_rustworkx(
            query_type=input_type,
            query_args=query_args,
            return_data_list=return_data_list,
            add_rcsb_id=add_rcsb_id,
            suppress_autocomplete_warning=suppress_autocomplete_warning,
        )

    def _construct_query_args(self, input_ids: Union[List[str], Dict[str, str], Dict[str, List[str]]], input_type: str) -> Union[Dict[str, str], Dict[str, List[str]]]:
        """Identify how to divide given id and divide the input id that has been passed in into the appropriate graphql format"""
        # If user passes in dictionary of args, validate keys and format
        if isinstance(input_ids, dict):
            # Will throw error if invalid typing, missing keys etc
            return input_ids

        plural_types = [key for key, value in self._root_dict.items() for item in value if item["ofKind"] == "LIST"]
        entities = ["polymer_entities", "branched_entities", "nonpolymer_entities", "nonpolymer_entity", "polymer_entity", "branched_entity"]
        instances = [
            "polymer_entity_instances",
            "branched_entity_instances",
            "nonpolymer_entity_instances",
            "polymer_entity_instance",
            "nonpolymer_entity_instance",
            "branched_entity_instance",
        ]
        input_dict: Dict[str, Any] = {}

        for single_id in input_ids:
            # Should be catching almost everything since most input_types will be converted to plural input_types automatically
            if input_type in plural_types:
                attr_list = self._root_dict[input_type]
                attr = attr_list[0]["name"]
                input_dict[attr] = input_ids
            elif (input_type in entities) and re.match("|".join(const.DATA_API_INPUT_TYPE_TO_REGEX["entity"]), single_id):
                if len(input_ids) == 1:
                    input_dict["entry_id"] = str(re.findall(r"^[^_]+", input_ids[0])[0])
                    input_dict["entity_id"] = str(re.findall(r"[^_]+$", input_ids[0])[0])
            elif (input_type in instances) and re.match("|".join(const.DATA_API_INPUT_TYPE_TO_REGEX["instance"]), single_id):
                if len(input_ids) == 1:
                    input_dict["entry_id"] = str(re.findall(r"^[^.]+", input_ids[0])[0])
                    input_dict["asym_id"] = str(re.findall(r"(?<=\.).*", input_ids[0])[0])
            elif (input_type in ["assemblies", "assembly"]) and re.match("|".join(const.DATA_API_INPUT_TYPE_TO_REGEX["assembly"]), single_id):
                if len(input_ids) == 1:
                    input_dict["entry_id"] = str(re.findall(r"^[^-]+", input_ids[0])[0])
                    input_dict["assembly_id"] = str(re.findall(r"[^-]+$", input_ids[0])[0])
            elif (input_type in ["interfaces", "interface"]) and re.match("|".join(const.DATA_API_INPUT_TYPE_TO_REGEX["interface"]), single_id):
                if len(input_ids) == 1:
                    input_dict["entry_id"] = str(re.findall(r"^[^-]+", input_ids[0])[0])
                    input_dict["assembly_id"] = str(re.findall(r"-(.*)\.", input_ids[0])[0])
                    input_dict["interface_id"] = str(re.findall(r"[^.]+$", input_ids[0])[0])
            elif (input_type in ["entries", "entry"]) and re.match("|".join(const.DATA_API_INPUT_TYPE_TO_REGEX["entry"]), single_id):
                if len(input_ids) == 1:
                    input_dict["entry_id"] = str(input_ids[0])
            elif input_type in ["chem_comp", "chem_comps"]:
                if len(input_ids) == 1:
                    input_dict["comp_id"] = str(re.findall(r"^[^_]+", input_ids[0])[0])
            elif input_type in ["entry_group", "entry_groups"]:
                if len(input_ids) == 1:
                    input_dict["group_id"] = str(input_ids[0])
            elif input_type in ["polymer_entity_group", "polymer_entity_groups"]:
                if len(input_ids) == 1:
                    input_dict["group_id"] = str(input_ids[0])
            elif (input_type == "uniprot") and re.match("|".join(const.DATA_API_INPUT_TYPE_TO_REGEX["uniprot"]), single_id):
                if len(input_ids) == 1:
                    input_dict["uniprot_id"] = str(input_ids[0])
                else:
                    raise ValueError("Uniprot IDs must be searched one at a time")
            elif input_type == "pubmed":
                if len(input_ids) == 1:
                    input_dict["pubmed_id"] = input_ids[0]
                else:
                    raise ValueError("Pubmed IDs must be searched one at a time")
            elif input_type == "group provenance":
                if len(input_ids) == 1:
                    input_dict["group_provenance_id"] = str(input_ids[0])
                else:
                    raise ValueError("Group provenance IDs must be searched one at a time")
            else:
                raise ValueError(f"Invalid ID format for {input_type}: {single_id}")
        return input_dict

    def _construct_query_rustworkx(
        self,
        query_type: str,
        query_args: Dict[str, Any],
        return_data_list: List[str],
        add_rcsb_id: bool = True,
        suppress_autocomplete_warning: bool = False
    ) -> Dict[str, Any]:
        return super()._construct_query_rustworkx(
            query_type=query_type,
            query_args=query_args,
            return_data_list=return_data_list,
            add_rcsb_id=add_rcsb_id,
            suppress_autocomplete_warning=suppress_autocomplete_warning,
        )

    def _check_input_ids(self, query_args: Dict[str, Any], input_type: str) -> None:
        arg_dict_list = self._root_dict[input_type]
        attr_names = [id["name"] for id in arg_dict_list]

        # Check that keys match required keys
        if not all(key in attr_names for key in query_args.keys()):
            raise ValueError(f"Input IDs keys do not match: {query_args.keys()} vs {attr_names}")
        missing_keys = [key_arg for key_arg in attr_names if key_arg not in query_args]
        if len(missing_keys) > 0:
            raise ValueError(
                f"Missing input_id dictionary keys: {missing_keys}. Find input_id keys and descriptions by running:\n"
                f"  from rcsbapi.data import DataSchema\n"
                f"  schema = DataSchema()\n"
                f'  schema.get_input_id_dict("{input_type}")'
            )

    def find_field_names(self, search_string: str) -> list[str]:
        """Find field names that fully or partially match the search string.

        Args:
            search_string (str): string to search field names for

        Raises:
            ValueError: thrown when a type other than string is passed in for search_string
            ValueError: thrown when no fields match search_string

        Returns:
            list[str]: list of matching field names
        """
        return super().find_field_names(search_string)

    def fetch_schema(self) -> Dict[str, Any]:
        """Get the JSON schema defining the Data API. Fallback to local file if necessary.

        Returns:
            Dict[str, Any]: JSON schema for Data API
        """
        return super()._abstract_fetch_schema(const.DATA_API_SCHEMA_FILENAME)
