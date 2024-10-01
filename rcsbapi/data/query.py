import logging
import urllib.parse
import re
import time
from typing import Any, Union, List, Dict, Optional
import requests
from rcsbapi.data import SCHEMA
from .constants import ApiSettings, SINGULAR_TO_PLURAL, ID_TO_SEPARATOR

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format="[%(levelname)s]: %(message)s")


class Query:
    """
    class for Data API queries.
    """
    def __init__(self, input_type: str, input_ids: Union[List[str], Dict[str, str], Dict[str, List[str]]], return_data_list: List[str], add_rcsb_id: bool = True):
        """
        Args:
            input_type (str): query input type
                ex: "entry", "polymer_entity_instance", etc
            input_ids (Union[List[str], Dict[str, str], Dict[str, List[str]]]): list of ids to request information for
            return_data_list (List[str]): list of data to return (field names)
                ex: ["rcsb_id", "exptl.method"]
        """
        input_id_limit = 200
        if isinstance(input_ids, list):
            if len(input_ids) > input_id_limit:
                logging.warning("More than %d input_ids. For a more readable response, reduce number of ids.", input_id_limit)
        if isinstance(input_ids, dict):
            for value in input_ids.values():
                if len(value) > input_id_limit:
                    logging.warning("More than %d input_ids. For a more readable response, reduce number of ids.", input_id_limit)

        self._plural_input = False
        """boolean indicating whether input type is plural or not (ex: "entry" vs "entries")"""
        if SCHEMA.root_dict[input_type][0]["kind"] == "LIST":
            self._plural_input = True
            if isinstance(input_ids, dict):
                assert isinstance(input_ids, dict)  # mypy
                self._input_ids_list: List[str] = input_ids[SCHEMA.root_dict[input_type][0]["name"]]

        self._input_type = input_type
        # automatically turn singular input_types into plural for more flexibility in number of ids
        if self._plural_input is False:
            plural_type = SINGULAR_TO_PLURAL[input_type]
            if plural_type:
                self._input_type = plural_type
                self._plural_input = True

                # if input_ids is a dict, join into PDB id format
                if isinstance(input_ids, dict):
                    join_id = ""
                    for k, v in input_ids.items():
                        assert isinstance(v, str)  # for mypy
                        if k in ID_TO_SEPARATOR:
                            join_id += ID_TO_SEPARATOR[k] + v
                        else:
                            join_id += v

                    input_ids = [join_id]

        self._input_ids = input_ids
        if isinstance(self._input_ids, list):
            self._input_ids_list = self._input_ids
        self._return_data_list = return_data_list
        self._query = SCHEMA.construct_query(input_type=self._input_type, input_ids=self._input_ids, return_data_list=return_data_list, add_rcsb_id=add_rcsb_id)
        """GraphQL query as a string"""
        self._response: Optional[Dict[str, Any]] = None

    def get_input_ids(self) -> Union[List[str], Dict[str, List[str]], Dict[str, str]]:
        """get input_ids used to make query

        Returns:
            Union[List[str], Dict[str, List[str]], Dict[str, str]]: input id list or dictionary
        """
        return self._input_ids

    def get_input_type(self) -> str:
        """get input_type used to make query

        Returns:
            str: input_type
                ex: "entry", "polymer_entity_instance", etc
        """
        return self._input_type

    def get_return_data_list(self) -> List[str]:
        """get return_data_list used to make query

        Returns:
            List[str]: return_data_list 
                ex: ["rcsb_id", "exptl.method"]
        """
        return self._return_data_list

    def get_query(self) -> str:
        """get GraphQL query

        Returns:
            str: query in GraphQL syntax
        """
        return self._query

    def get_input_ids_list(self) -> Union[str, List[str], None]:
        try:
            return self._input_ids_list
        except AttributeError:
            return None

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
        editor_base_link = str(ApiSettings.API_ENDPOINT.value) + "/index.html?query="
        return editor_base_link + urllib.parse.quote(self._query)

    def exec(self) -> Dict[str, Any]:
        """POST a GraphQL query and get response

        Returns:
            Dict[str, Any]: JSON object
        """
        batch_size = 50
        if (self._plural_input is True) and (len(self._input_ids_list) > batch_size):
            batched_ids = self.batch_ids(batch_size)
            response_json: Dict[str, Any] = {}
            # count = 0
            for id_batch in batched_ids:
                query = re.sub(r"\[([^]]+)\]", f"{id_batch}".replace("'", '"'), self._query)
                part_response = requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=ApiSettings.API_ENDPOINT.value, timeout=ApiSettings.TIMEOUT).json()
                self.parse_gql_error(part_response)
                time.sleep(0.2)
                if not response_json:
                    response_json = part_response
                else:
                    response_json = self.merge_response(response_json, part_response)
        else:
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=self._query, url=ApiSettings.API_ENDPOINT.value, timeout=10).json()
            self.parse_gql_error(response_json)
        if "data" in response_json.keys():
            query_response = response_json["data"][self._input_type]
            if query_response is None:
                logging.warning("Input produced no results. Check that input ids are valid")
            if isinstance(query_response, list):
                if len(query_response) == 0:
                    logging.warning("Input produced no results. Check that input ids are valid")
        self._response = response_json
        return response_json

    def parse_gql_error(self, response_json: Dict[str, Any]):
        if "errors" in response_json.keys():
            error_msg_list: list[str] = []
            for error_dict in response_json["errors"]:
                error_msg_list.append(error_dict["message"])
                combined_error_msg: str = ""
                for i, error_msg in enumerate(error_msg_list):
                    combined_error_msg += f"{i+1}. {error_msg}\n"
                raise ValueError(f"{combined_error_msg}. Run <query object name>.get_editor_link() to get a link to GraphiQL editor with query")

    def batch_ids(self, batch_size: int) -> List[List[str]]:  # assumes that plural types have only one arg, which is true right now
        """split queries with large numbers of input_ids into smaller batches

        Args:
            batch_size (int): max size of batches

        Returns:
            List[List[str]]: nested list where each list is a batch of ids
        """
        batched_ids: List[List[str]] = []
        i = 0
        while i < len(self._input_ids_list):
            count = 0
            batch_list: List[str] = []
            while count < batch_size and i < len(self._input_ids_list):
                batch_list.append(self._input_ids_list[i])
                count += 1
                i += 1
            if len(batch_list) > 0:
                batched_ids.append(batch_list)
        return batched_ids

    def merge_response(self, merge_into_response: Dict[str, Any], to_merge_response: Dict[str, Any]):
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
