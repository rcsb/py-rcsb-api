import logging
import urllib.parse
import re
import time
from typing import Any, Union, List, Dict, Optional, Tuple
import json
import requests
from tqdm import tqdm
from rcsbapi.data import DATA_SCHEMA
from rcsbapi.config import config
from rcsbapi.const import const

logger = logging.getLogger(__name__)


class DataQuery:
    """
    Class for Data API queries.
    """
    def __init__(
        self,
        input_type: str,
        input_ids: Union[List[str], Dict[str, str], Dict[str, List[str]], List[int]],
        return_data_list: List[str],
        add_rcsb_id: bool = True,
        suppress_autocomplete_warning: bool = False
    ):
        """
        Query object for Data API requests.

        Args:
            input_type (str): query input type
                (e.g., "entry", "polymer_entity_instance", etc.)
            input_ids (list or dict): list (or singular dict) of ids for which to request information
                (e.g., ["4HHB", "2LGI"])
            return_data_list (list): list of data to return (field names)
                (e.g., ["rcsb_id", "exptl.method"])
            add_rcsb_id (bool, optional): whether to automatically add <input_type>.rcsb_id to queries. Defaults to True.
        """
        suppress_autocomplete_warning = config.SUPPRESS_AUTOCOMPLETE_WARNING if config.SUPPRESS_AUTOCOMPLETE_WARNING else suppress_autocomplete_warning

        if not isinstance(input_ids, AllStructures):
            if isinstance(input_ids, list):
                if len(input_ids) > config.INPUT_ID_LIMIT:
                    logger.warning("More than %d input_ids. Query will be slower to complete.", config.INPUT_ID_LIMIT)
            if isinstance(input_ids, dict):
                for value in input_ids.values():
                    if len(value) > config.INPUT_ID_LIMIT:
                        logger.warning("More than %d input_ids. Query will be slower to complete.", config.INPUT_ID_LIMIT)

        self._input_type, self._input_ids = self._process_input_ids(input_type, input_ids)
        self._return_data_list = return_data_list
        self._query: Dict[str, Any] = DATA_SCHEMA.construct_query(
            input_type=self._input_type,
            input_ids=self._input_ids,
            return_data_list=return_data_list,
            add_rcsb_id=add_rcsb_id,
            suppress_autocomplete_warning=suppress_autocomplete_warning
        )
        """GraphQL query as a string"""
        self._response: Optional[Dict[str, Any]] = None
        """JSON response to query, will be assigned after executing"""

    def _process_input_ids(self, input_type: str, input_ids: Union[List[str], Dict[str, str], Dict[str, List[str]]]) -> Tuple[str, List[str]]:
        """Convert input_type to plural if possible.
        Set input_ids to be a list of ids.
        If using ALL_STRUCTURES, return the id list corresponding to the input type.

        Args:
            input_type (str): query input type
                (e.g., "entry", "polymer_entity_instance", etc.)
            input_ids (Union[List[str], Dict[str, str], Dict[str, List[str]]]): list/dict of ids to request information for

        Returns:
            Tuple[str, List[str]]: returns a tuple of converted input_type and list of input_ids
        """
        # If input_ids is ALL_STRUCTURES, return appropriate list of ids
        if isinstance(input_ids, AllStructures):
            new_input_ids = input_ids.get_all_ids(input_type)
            return (input_type, new_input_ids)

        # Convert _input_type to plural if applicable
        converted = False
        if DATA_SCHEMA._root_dict[input_type][0]["ofKind"] != "LIST":
            plural_type = const.SINGULAR_TO_PLURAL[input_type]
            if plural_type:
                input_type = plural_type
                converted = True

        # Set _input_ids
        if isinstance(input_ids, dict):
            if converted:
                # If converted and input_ids is a dict, join into PDB id format
                if isinstance(input_ids, dict):
                    join_id = ""
                    for k, v in input_ids.items():
                        assert isinstance(v, str)  # for mypy
                        if k in const.ID_TO_SEPARATOR:
                            join_id += const.ID_TO_SEPARATOR[k] + v
                        else:
                            join_id += v

                    input_ids = [join_id]

            else:
                # If not converted, retrieve id list from dictionary
                input_ids = list(input_ids[DATA_SCHEMA._root_dict[input_type][0]["name"]])

        # Make all input_ids uppercase if applicable
        if isinstance(input_ids[0], str):
            input_ids = [id.upper() for id in input_ids]

        assert isinstance(input_ids, list)
        return (input_type, input_ids)

    def get_input_ids(self) -> List[str]:
        """get input_ids used to make query

        Returns:
            Union[List[str], Dict[str, List[str]], Dict[str, str]]: input id list or dictionary
        """
        return self._input_ids

    def get_input_type(self) -> str:
        """get input_type used to make query

        Returns:
            str: input_type
                (e.g., "entry", "polymer_entity_instance", etc.)
        """
        return self._input_type

    def get_return_data_list(self) -> List[str]:
        """get return_data_list used to make query

        Returns:
            List[str]: return_data_list
                (e.g., ["rcsb_id", "exptl.method"])
        """
        return self._return_data_list

    def get_query(self) -> str:
        """get GraphQL query

        Returns:
            str: query in GraphQL syntax
        """
        assert isinstance(self._query["query"], str)
        return self._query["query"]

    def get_response(self) -> Union[None, Dict[str, Any]]:
        """get JSON response to executed query

        Returns:
            Dict[str, Any]: JSON object
        """
        return self._response

    def get_editor_link(self) -> str:
        """get url to interactive GraphiQL editor

        Returns:
            str: GraphiQL url
        """
        editor_base_link = str(const.DATA_API_ENDPOINT) + "/index.html?query="
        return str(editor_base_link + urllib.parse.quote(str(self._query["query"])))

    def exec(self, batch_size: int = 5000, progress_bar: bool = False) -> Dict[str, Any]:
        """POST a GraphQL query and get response

        Returns:
            Dict[str, Any]: JSON object
        """
        if len(self._input_ids) > batch_size:
            batched_ids: Union[List[List[str]], tqdm] = self._batch_ids(batch_size)
        else:
            batched_ids = [self._input_ids]
        response_json: Dict[str, Any] = {}

        if progress_bar is True:
            batched_ids = tqdm(batched_ids)

        for id_batch in batched_ids:
            query_body = re.sub(r"\[([^]]+)\]", f"{id_batch}".replace("'", '"'), self._query["query"])
            part_response = requests.post(
                headers={"Content-Type": "application/json", "User-Agent": const.USER_AGENT},
                json={"query": query_body},
                url=const.DATA_API_ENDPOINT,
                timeout=config.API_TIMEOUT
            ).json()
            self._parse_gql_error(part_response)
            time.sleep(0.2)
            if not response_json:
                response_json = part_response
            else:
                response_json = self._merge_response(response_json, part_response)

        if "data" in response_json.keys():
            query_response = response_json["data"][self._input_type]
            if query_response is None:
                logger.warning("Input produced no results. Check that input ids are valid")
            if isinstance(query_response, list):
                if len(query_response) == 0:
                    logger.warning("Input produced no results. Check that input ids are valid")
        self._response = response_json
        return response_json

    def _parse_gql_error(self, response_json: Dict[str, Any]) -> None:
        if "errors" in response_json.keys():
            error_msg_list: List[str] = []
            for error_dict in response_json["errors"]:
                error_msg_list.append(error_dict["message"])
                combined_error_msg: str = ""
                for i, error_msg in enumerate(error_msg_list):
                    combined_error_msg += f"{i+1}. {error_msg}\n"
                raise ValueError(f"{combined_error_msg}.\n\nRun <query object name>.get_editor_link() to get a link to GraphiQL editor with query")

    def _batch_ids(self, batch_size: int) -> List[List[str]]:  # assumes that plural types have only one arg, which is true right now
        """split queries with large numbers of input_ids into smaller batches

        Args:
            batch_size (int): max size of batches

        Returns:
            List[List[str]]: nested list where each list is a batch of ids
        """
        batched_ids: List[List[str]] = []
        i = 0
        while i < len(self._input_ids):
            count = 0
            batch_list: List[str] = []
            while count < batch_size and i < len(self._input_ids):
                batch_list.append(self._input_ids[i])
                count += 1
                i += 1
            if len(batch_list) > 0:
                batched_ids.append(batch_list)
        return batched_ids

    def _merge_response(self, merge_into_response: Dict[str, Any], to_merge_response: Dict[str, Any]) -> Dict[str, Any]:
        """merge two JSON responses. Used after batching ids to merge responses from each batch.

        Args:
            merge_into_response (Dict[str, Any])
            to_merge_response (Dict[str, Any])

        Returns:
            Dict : merged JSON response, formatted as if it was one request
        """
        combined_response = merge_into_response
        combined_response["data"][self._input_type] += to_merge_response["data"][self._input_type]
        return combined_response


class AllStructures:
    """Class for representing all structures of different `input_types`
    """
    def __init__(self):
        """initialize AllStructures object
        """
        self.ALL_STRUCTURES = self.reload()

    def reload(self) -> dict[str, List[str]]:
        """Build dictionary of IDs based on endpoints defined in const

        Returns:
            dict[str, List[str]]: ALL_STRUCTURES object
        """
        ALL_STRUCTURES = {}
        for input_type, endpoints in const.INPUT_TYPE_TO_ALL_STRUCTURES_ENDPOINT.items():
            all_ids: List[str] = []
            for endpoint in endpoints:
                response = requests.get(endpoint, timeout=60, headers={"User-Agent": const.USER_AGENT})
                if response.status_code == 200:
                    all_ids.extend(json.loads(response.text))
                else:
                    response.raise_for_status()
                ALL_STRUCTURES[input_type] = all_ids

        return ALL_STRUCTURES

    def get_all_ids(self, input_type: str) -> List[str]:
        """Get all ids of a certain `input_type`

        Args:
            input_type (str): `input_type` string

        Raises:
            ValueError: raise an error if the `input_type` isn't in ALL_STRUCTURES

        Returns:
            List[str]: list of IDS of specified `input_type`
        """
        if input_type in self.ALL_STRUCTURES:
            return self.ALL_STRUCTURES[input_type]
        else:
            raise ValueError(f"ALL_STRUCTURES is not yet available for input_type {input_type}")
