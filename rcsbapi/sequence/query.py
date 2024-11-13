from typing import Dict, Literal, List, Any, Optional
from types import MappingProxyType
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields, is_dataclass
import requests

from rcsbapi.const import seq_const
from rcsbapi.config import config
from rcsbapi.sequence import COORD_SCHEMA

# pylint: disable=useless-parent-delegation
# This should be dynamically populated at some point
SequenceReference = Literal["NCBI_GENOME", "NCBI_PROTEIN", "PDB_ENTITY", "PDB_INSTANCE", "UNIPROT"]
FieldName = Literal["TARGET_ID", "TYPE"]
OperationType = Literal["CONTAINS", "EQUALS"]
AnnotationReference = Literal["PDB_ENTITY", "PDB_INSTANCE", "PDB_INTERFACE", "UNIPROT"]


@dataclass(frozen=True)
class Query(ABC):
    """Base class for all query types"""

    @abstractmethod
    def to_dict(self) -> Dict:
        """Get dictionary represented query and attributes, skips values of None"""
        request_dict: Dict = {}
        for field in fields(self):
            field_name = field.name
            field_value = getattr(self, field_name)
            field_name = field_name.replace("_", "")
            if field_value:
                if is_dataclass(field_value):
                    field_value = field_value.to_dict()
                request_dict[field_name] = field_value
        return request_dict

    @abstractmethod
    def exec(self) -> Dict:
        """execute query and return JSON response"""

    def _parse_gql_error(self, response_json: Dict[str, Any]):
        if "error" in response_json.keys():
            raise requests.HTTPError(
                f"Status code {response_json["status"]} {response_json["error"]}:\n"
                f"  Run <query object name>.get_editor_link() to get a link to GraphiQL editor with query"
            )

    def get_editor_link(self):  # TODO
        pass


@dataclass(frozen=True)
class alignments(Query):
    """
    sequence alignments
        from_ (SequenceReference): From which query sequence database
        to (SequenceReference): To which query sequence database
        queryId (str): Database sequence identifier
        return_data_list (List[str]): requested data fields
        range (Optional, List[])
    """
    from_: SequenceReference  # python keyword:( Is this the best way?
    to: SequenceReference
    queryId: str
    return_data_list: List[str]
    range: Optional[List[int]] = None
    suppress_autocomplete_warning: bool = False
    _query: MappingProxyType = MappingProxyType({})

    def to_dict(self) -> Dict:
        return super().to_dict()

    def __post_init__(self):
        query = COORD_SCHEMA.construct_query(
            query_type="alignments",
            query_args=self.to_dict(),
            return_data_list=self.return_data_list,
            suppress_autocomplete_warning=self.suppress_autocomplete_warning,
        )
        object.__setattr__(
            self,
            "_query",
            query,
        )

    def exec(self) -> Dict:
        response_json = requests.post(
            json=dict(self._query),
            url=seq_const.API_ENDPOINT,
            timeout=config.DATA_API_TIMEOUT
        ).json()
        self._parse_gql_error(response_json)
        return response_json


@dataclass(frozen=True)
class annotations(Query):
    queryId: str
    sources: List[AnnotationReference]
    reference: SequenceReference
    return_data_list: List[str]
    filters: Optional["AnnotationFilterInput"] = None
    range: Optional[List[int]] = None
    suppress_autocomplete_warning: bool = False
    _query: MappingProxyType = MappingProxyType({})

    def to_dict(self) -> Dict:
        return super().to_dict()

    def __post_init__(self):
        query = COORD_SCHEMA.construct_query(
            query_type="annotations",
            query_args=self.to_dict(),
            return_data_list=self.return_data_list,
            suppress_autocomplete_warning=self.suppress_autocomplete_warning,
        )
        object.__setattr__(
            self,
            "_query",
            query,
        )
        print(query)

    def exec(self) -> Dict:
        response_json = requests.post(
            json=dict(self._query),
            url=seq_const.API_ENDPOINT,
            timeout=config.DATA_API_TIMEOUT
        ).json()
        self._parse_gql_error(response_json)
        return response_json


@dataclass(frozen=True)
class AnnotationFilterInput:
    field: FieldName
    operation: OperationType
    source: AnnotationReference
    values: List[str]

    def to_dict(self) -> Dict:
        return {
            "field": self.field,
            "operation": self.operation,
            "source": self.source,
            "values": self.values,
        }

    def to_string(self) -> Dict:
        pass
