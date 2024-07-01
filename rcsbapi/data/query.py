from rcsbapi.data import schema
import requests
import logging
import time
import urllib.parse
from typing import Any, Union, List, Dict

PDB_URL = "https://data.rcsb.org/graphql"
SCHEMA = schema.Schema(PDB_URL)
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format="[%(levelname)s]: %(message)s")

class Query:

    def __init__(self, input_ids: Union[str,List[str],Dict[Any, Any]], input_type: str, return_data_list: List[str]):  # TODO: will edit when dicts and strings for input are supported
        if len(input_ids) > 300:
            raise ValueError("Too many input_ids. Reduce to less than 300.")
        self.input_ids = input_ids
        self.input_type = input_type
        self.return_data_list = return_data_list
        self.query = SCHEMA.construct_query(input_ids, input_type, return_data_list)
        self.plural_input = False
        if SCHEMA.root_dict[self.input_type][0]["kind"] == "LIST":
            self.plural_input = True
            if isinstance(input_ids, dict):
                self.input_ids_list: List[str] = input_ids[SCHEMA.root_dict[self.input_type][0]["name"]]
            if isinstance(input_ids, list):
                self.input_ids_list = input_ids
        self.response = self.post_query()  # TODO: should this be upon initialization or must be called explicitly?

    def get_input_ids(self):
        return self.input_ids

    def get_input_type(self):
        return self.input_type

    def get_return_data_list(self):
        return self.return_data_list

    def get_query(self):
        return self.query

    def get_editor_link(self):
        editor_base_link = PDB_URL + "/index.html?query="
        return editor_base_link + urllib.parse.quote(self.query)

    def post_query(self):
        batch_size = 50
        if (self.plural_input is True) and (len(self.input_ids_list) > batch_size):
            batched_ids = self.batch_ids(batch_size)
            response_json = {}
            count = 0
            for id_batch in batched_ids:
                query = SCHEMA.construct_query(id_batch, self.input_type, self.return_data_list)  #could be more efficient by subbing in just id_batch
                part_response =  requests.post(headers={"Content-Type": "application/graphql"}, data=query, url=PDB_URL).json()
                self.parse_gql_error(part_response)
                time.sleep(0.2)
                if not response_json:
                    response_json = part_response
                else:
                    response_json = self.merge_response(response_json, part_response)
        else:
            response_json = requests.post(headers={"Content-Type": "application/graphql"}, data=self.query, url=PDB_URL).json()
            self.parse_gql_error(response_json)
        if "data" in response_json.keys():
            query_response = response_json["data"][self.input_type]
            if query_response is None:
                logging.warning("Input produced no results. Check that input ids are valid")
            if isinstance(query_response, list):
                if len(query_response) == 0:
                   logging.warning("Input produced no results. Check that input ids are valid")        
        return response_json
            # parse_response(response_json)
            # fields_list = 

    def parse_gql_error(self, response_json):
        if "errors" in response_json.keys():
            error_msg_list = []
            for error_dict in response_json["errors"]:
                error_msg_list.append(error_dict["message"])
                combined_error_msg = ""
                for i in range(len(error_msg_list)):
                    combined_error_msg += f"{i+1}. {error_msg_list[i]}"
                    raise ValueError(f"{combined_error_msg}.\n Run <query object name>.get_editor_link() to get a link to GraphiQL editor with query")

    #TODO: change to use list of input ids?
    def batch_ids(self, batch_size) -> List[Dict[str, List[str]]]: # assumes that plural types have only one arg, which is true right now
        id_name = SCHEMA.root_dict[self.input_type][0]["name"]
        batched_ids: List[Dict[str, List[str]]] = []
        i = 0
        while i < len(self.input_ids_list):
            count = 0
            batch_list: Dict[str, List[str]] = {id_name: []}
            while count < batch_size and i < len(self.input_ids_list):
                batch_list[id_name].append(self.input_ids_list[i])
                count += 1
                i += 1
            if len(batch_list) > 0:
                batched_ids.append(batch_list)
        return batched_ids

    def merge_response(self, merge_into_response, to_merge_response):
        combined_response = merge_into_response
        combined_response["data"][self.input_type] += to_merge_response["data"][self.input_type]
        return combined_response
        
    def get(self, key: str):
        pass

def editor_to_query(url:str):
    editor_base_link = PDB_URL + "/index.html?query="
    str_query = urllib.parse.unquote(url.replace(editor_base_link, ""))
    return str_query    