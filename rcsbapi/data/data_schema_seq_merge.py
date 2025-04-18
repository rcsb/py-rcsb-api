"""Fetching and Parsing API's GraphQL schema."""

from __future__ import annotations
import logging
import json
from typing import Any, List, Dict, Union
from pathlib import Path
import requests
from graphql import build_client_schema
import rustworkx as rx

from rcsbapi.const import const
from rcsbapi.config import config
from rcsbapi.graphql_schema import Schema

use_networkx: bool = False
# Below section and parts of code involving networkx are commented out
# May implement graph construction through networkx at a later point
# try:
#     import rustworkx as rx

#     logging.info("Using  rustworkx")
# except ImportError:
#     use_networkx = True

logger = logging.getLogger(__name__)


class DataSchema(Schema):
    def __init__(self) -> None:
        super().__init__(
            endpoint=const.DATA_API_ENDPOINT,
            timeout=config.API_TIMEOUT
        )

    # TODO: document this design decision where the signature of construct_query is variable
    def construct_query(  # type: ignore[override]
        self,
        input_type: str,
        input_ids: Union[List[str], Dict[str, str], Dict[str, List[str]]],
        return_data_list: List[str],
        add_rcsb_id: bool = True,
        suppress_autocomplete_warning: bool = False
    ) -> Dict[str, Any]:

        # Check for invalid fields in `return_data_list`
        super()._check_return_list(return_data_list)

        query_args = construct_query_args(input_ids)

        return super()._construct_query_rustworkx(
            query_type=input_type,
            query_args=query_args,
            return_data_list=return_data_list,
            suppress_autocomplete_warning=suppress_autocomplete_warning
        )

    def construct_query_args(self, input_ids: Union[List[str], Dict[str, str], Dict[str, List[str]]]) -> Union[Dict[str, str], Dict[str, List[str]]]:
        # If user passes in dictionary of args, # TODO: validate
        if isinstance(input_ids, dict):
            return input_ids

        plural_types = [key for key, value in self._root_dict.items() for item in value if item["kind"] == "LIST"]
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
            if (input_type in entities) and re.match("|".join(const.DATA_API_INPUT_TYPE_TO_REGEX["entity"]), single_id):
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
            if input_type in plural_types:
                input_dict = {}
                attr = attr_list[0]["name"]
                input_dict[attr] = input_ids
        return input_dict