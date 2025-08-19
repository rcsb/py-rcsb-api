import time
import logging
from typing import Dict, List, Any, Optional, Union
from types import MappingProxyType
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from dataclasses import field as dcfield
import urllib.parse
import httpx

from rcsbapi.const import const
from rcsbapi.config import config
from rcsbapi.sequence import SEQ_SCHEMA
from rcsbapi.graphql_schema import SchemaEnum

logger = logging.getLogger(__name__)


class SeqEnums(SchemaEnum):
    # While it makes more sense to have this in seq_schema, it's here to avoid a circular import error
    SequenceReference = SEQ_SCHEMA._read_enum("SequenceReference")
    FieldName = SEQ_SCHEMA._read_enum("FieldName")
    OperationType = SEQ_SCHEMA._read_enum("OperationType")
    AnnotationReference = SEQ_SCHEMA._read_enum("AnnotationReference")
    GroupReference = SEQ_SCHEMA._read_enum("GroupReference")


@dataclass(frozen=True)
class SeqQuery(ABC):
    """Base class for all query types"""
    argument_name_map = {
        "db_from": "from",
        "db_to": "to",
        "query_id": "queryId",
        "group_id": "groupId"
    }

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Get dictionary representation of query and attributes, skips values of None. Skips return_data_list"""
        request_dict: Dict[str, Any] = {}
        for field in fields(self):
            field_name = field.name
            if field_name == "return_data_list":
                continue
            field_value = getattr(self, field_name)
            if field_value:
                # Create an exception for AnnotationFilterInput
                if (
                    isinstance(field_value, list)
                    and all(isinstance(item, AnnotationFilterInput) for item in field_value)
                ):
                    field_value = [filter.to_string() for filter in field_value]

                output_key = self.argument_name_map.get(field_name, field_name)
                request_dict[output_key] = field_value

        return request_dict

    def get_query(self) -> MappingProxyType:
        assert hasattr(self, "_query")
        return self._query  # type: ignore

    def construct_query(self, query_type: str) -> Dict[str, Any]:
        """type check based on the GraphQL schema, then construct the GraphQL query"""
        # Assert attributes exists for mypy.
        # Can't be defined in SeqQuery class because
        # attributes without defaults must be defined before those with defaults.
        # Inherited attributes are placed before non-inherited attributes.
        # Possible workaround is making the attributes keyword-only, but I decided against it for now.
        # Issue: https://github.com/python-attrs/attrs/issues/38
        assert hasattr(self, "return_data_list"), \
            f"{self.__class__.__name__} must define 'return_data_list' attribute."
        assert hasattr(self, "suppress_autocomplete_warning"), \
            f"{self.__class__.__name__} must define 'suppress_autocomplete_warning' attribute."

        SEQ_SCHEMA._check_typing(
            query_type=query_type,
            enum_types=SeqEnums,
            args=self.to_dict(),
        )

        query = SEQ_SCHEMA.construct_query(
            query_type=query_type,
            query_args=self.to_dict(),
            return_data_list=self.return_data_list,
            suppress_autocomplete_warning=self.suppress_autocomplete_warning,
        )

        return query

    def exec(self, max_retries: int = None, retry_backoff: int = None) -> Dict[str, Any]:
        """Execute given query and return JSON response.

        Args:
            max_retries (int, optional): maximum number of retries to attempt for each individual sub-request (in case of timeouts or errors). Defaults to `config.MAX_RETRIES`.
            retry_backoff (int, optional): delay in seconds to wait for each retry. Defaults to `config.RETRY_BACKOFF`.

        Returns:
            Dict[str, Any]: JSON object containing the query result
        """
        # Assert attribute exists for mypy
        assert hasattr(self, "_query"), \
            f"{self.__class__.__name__} must define '_query' attribute."

        # Request retry and rate limit settings
        max_retries = max_retries if max_retries else config.MAX_RETRIES
        retry_backoff = retry_backoff if retry_backoff else config.RETRY_BACKOFF

        response_json = self._submit_request(max_retries, retry_backoff)

        return dict(response_json)

    def _submit_request(self, max_retries, retry_backoff):
        """Submit a single request, with retry behavior.
        """
        for attempt in range(1, max_retries + 1):
            try:
                response = httpx.post(
                    url=const.SEQUENCE_API_GRAPHQL_ENDPOINT,
                    json=dict(self._query),
                    timeout=config.API_TIMEOUT,
                    headers={"Content-Type": "application/json", "User-Agent": const.USER_AGENT}
                )
                response.raise_for_status()  # Raise an error for bad responses
                response_json = response.json()
                self._parse_gql_error(response_json)
                #
                if response.status_code == httpx.codes.OK:
                    return response_json
                elif response.status_code == httpx.codes.NO_CONTENT:
                    return None
                else:
                    raise httpx.HTTPStatusError(
                        f"Unexpected status: {response.status_code}",
                        request=response.request,
                        response=response
                    )
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if attempt == max_retries:
                    logger.error(
                        "Final retry attempt %r failed with exception:\n    %r\n"
                        "Check query and parameters.",
                        attempt,
                        e
                    )
                    raise
                logger.debug("Attempt %r failed: %r. Retrying in %r seconds...", attempt, e, self._retry_backoff)
                time.sleep(retry_backoff)
                retry_backoff *= 2  # exponential backoff

    def get_editor_link(self) -> str:
        """Get link to GraphiQL editor with given query populated"""
        editor_base_link = str(const.SEQUENCE_API_ENDPOINT) + "/graphiql" + "/index.html?query="
        assert hasattr(self, "_query")  # for mypy
        return editor_base_link + urllib.parse.quote(str(self._query["query"]))

    def _parse_gql_error(self, response_json: Dict[str, Any]) -> None:
        """Look through responses to see if there are errors. If so, throw an HTTP error, """
        if "errors" in response_json.keys():
            error = response_json["errors"][0]
            raise Exception(
                f'\n{error["message"]}\n'
                f"Run <query object name>.get_editor_link() to get a link to GraphiQL editor with query"
            )


@dataclass(frozen=True)
class Alignments(SeqQuery):
    """
    Get sequence alignments.

    Args:
        db_from (str): From which query sequence database
        db_to (str): To which query sequence database
        query_id (str): Sequence identifier specified in `db_from`
        return_data_list (List[str]): Fields to request data for
        range (Optional, List[]): Optional integer list to filter annotations that fall in a particular region
        suppress_autocomplete_warning (bool, optional): Suppress warning message about field path autocompletion. Defaults to False.
        data_list_args (Optional[Dict[str, Dict[str, Union[int, str]]]]): Optional dictionary specifying field-level arguments for entries in `return_data_list`.
            The key must match fields in `return_data_list`. Values currently include "offset" and "first"

    Attrs:
        _query (MappingProxyType[str, Any]): Attribute for storing GraphQL query
    """
    db_from: str
    db_to: str
    query_id: str
    return_data_list: List[str]
    range: Optional[List[int]] = None
    suppress_autocomplete_warning: bool = False
    data_list_args: Optional[Dict[str, Dict[str, Union[int, str]]]] = None
    _query: MappingProxyType = dcfield(default_factory=lambda: MappingProxyType({}))

    def to_dict(self) -> Dict[str, Any]:
        return super().to_dict()

    def __post_init__(self) -> None:
        query = super().construct_query("alignments")
        object.__setattr__(self, "_query", query)


@dataclass(frozen=True)
class Annotations(SeqQuery):
    """
    Get sequence annotations.

    Args:
        query_id (str): Database sequence identifier
        sources (List[str]): List defining the annotation collections to be requested
        reference (SequenceReference): Query sequence database
        return_data_list (List[str]): Requested data fields
        filters (List["AnnotationFilterInput"], optional): Select what annotations will be retrieved
        range: (List[int], optional): Optional integer list to filter annotations to a particular region
        suppress_autocomplete_warning (bool, optional): Suppress warning message about field path autocompletion. Defaults to False.

    Attrs:
        _query (MappingProxyType[str, Any]): Attribute for storing GraphQL query
    """
    query_id: str
    sources: List[str]
    reference: str
    return_data_list: List[str]
    filters: Optional[List["AnnotationFilterInput"]] = None
    range: Optional[List[int]] = None
    suppress_autocomplete_warning: bool = False
    _query: MappingProxyType = dcfield(default_factory=lambda: MappingProxyType({}))

    def to_dict(self) -> Dict[str, Any]:
        return super().to_dict()

    def __post_init__(self) -> None:
        query = super().construct_query("annotations")
        object.__setattr__(self, "_query", query)


@dataclass(frozen=True)
class GroupAlignments(SeqQuery):
    """
    Get alignments for structures in groups

    Args:
        group_id (str): Database sequence identifier for group
        return_data_list (List[str]): Requested data fields
        filter (List[str], optional): Optional string list of allowed identifiers for group members
        suppress_autocomplete_warning (bool, optional): Suppress warning message about field path autocompletion. Defaults to False.
        data_list_args (Optional[Dict[str, Dict[str, Union[int, str]]]]): Optional dictionary specifying field-level arguments for entries in `return_data_list`.
            The key must match fields in `return_data_list`. Values currently include "offset" and "first"

    Attrs:
        _query (MappingProxyType[str, Any]): Attribute for storing GraphQL query
    """
    group: str
    group_id: str
    return_data_list: List[str]
    filter: Optional[List[str]] = None
    suppress_autocomplete_warning: bool = False
    data_list_args: Optional[Dict[str, Dict[str, Union[int, str]]]] = None
    _query: MappingProxyType = dcfield(default_factory=lambda: MappingProxyType({}))

    def to_dict(self) -> Dict[str, Any]:
        return super().to_dict()

    def __post_init__(self) -> None:
        query = super().construct_query("group_alignments")
        object.__setattr__(self, "_query", query)


@dataclass(frozen=True)
class GroupAnnotations(SeqQuery):
    """
    Get annotations for sequences in groups.

    Args:
        group (GroupReference): Query sequence database
        group_id (str): Database sequence identifier for group
        sources (List[AnnotationReference]): List defining the annotation collections to be requested
        return_data_list (List[str]): Requested data fields
        filters (List[AnnotationFilterInput]): Optional annotation filter by type or target identifier
        suppress_autocomplete_warning (bool, optional): Suppress warning message about field path autocompletion. Defaults to False.

    Attrs:
        _query (MappingProxyType[str, Any]): Attribute for storing GraphQL query
    """
    group: str
    group_id: str
    sources: List[str]
    return_data_list: List[str]
    filters: Optional[List["AnnotationFilterInput"]] = None
    suppress_autocomplete_warning: bool = False
    _query: MappingProxyType = dcfield(default_factory=lambda: MappingProxyType({}))

    def to_dict(self) -> Dict[str, Any]:
        return super().to_dict()

    def __post_init__(self) -> None:
        query = super().construct_query("group_annotations")
        object.__setattr__(self, "_query", query)


@dataclass(frozen=True)
class GroupAnnotationsSummary(SeqQuery):
    """
    Get a summary of positional annotations for a group of sequences.

    Args:
        group (GroupReference): Query sequence database
        group_id (str): Database sequence identifier for group
        sources (List[AnnotationReference]): List defining the annotation collections to be requested
        return_data_list (List[str]): Request data fields
        filters (List[AnnotationFilterInput], optional): Optional annotation filter by type or target identifier
        suppress_autocomplete_warning (bool, optional): Suppress warning message about field path autocompletion. Defaults to False.

    Attrs:
        _query (MappingProxyType[str, Any]): Attribute for storing GraphQL query
    """
    group: str
    group_id: str
    sources: List[str]
    return_data_list: List[str]
    filters: Optional[List["AnnotationFilterInput"]] = None
    suppress_autocomplete_warning: bool = False
    _query: MappingProxyType = dcfield(default_factory=lambda: MappingProxyType({}))

    def to_dict(self) -> Dict[str, Any]:
        return super().to_dict()

    def __post_init__(self) -> None:
        query = super().construct_query("group_annotations_summary")
        object.__setattr__(self, "_query", query)


class AnnotationFilterInput:
    """
    Filter used to select which annotations will be retrieved.
    """

    def __init__(
        self,
        field: str,
        operation: str,
        values: List[str],
        source: Optional[str] = None,
    ):
        """
        Args:
            field (FieldName): Defines the field to be compared
            operation (OperationType): Defines the comparison method
            values (List[str]): List of allowed values
            source (AnnotationReference, optional): Only features with the same annotation collections will be filtered
        """
        self.field = field
        self.operation = operation
        self.values = values
        self.source = source

    def to_string(self) -> str:
        """Generate string to insert in GraphQL query based on GraphQL schema"""

        input_field_specs: List[Any] = []
        for arg_dict in SEQ_SCHEMA._root_dict["annotations"]:
            if arg_dict["name"] == "filters":
                input_field_specs = arg_dict["inputFields"]
        assert len(input_field_specs) > 0, '"filters" key not found in arg_dict'

        args = set()
        for input_field in input_field_specs:
            field_name = input_field["name"]
            if getattr(self, field_name) is None:
                continue
            if (
                (input_field["type"]["ofType"] is not None)
                and (input_field["type"]["ofType"]["kind"] == "LIST")
            ):
                if input_field["type"]["ofType"]["ofType"]["ofType"]["name"] == "String":
                    # If type is string, add list with double quotes around each item
                    args.add("{}: {}".format(field_name, str(getattr(self, field_name)).replace("'", '"')))
                else:
                    # If type isn't string, remove single quotes
                    args.add("{}: {}".format(field_name, str(getattr(self, field_name)).replace("'", "")))
            elif (
                (input_field["type"]["kind"] == "ENUM")
                or (input_field["type"]["ofType"]["kind"] == "ENUM")
            ):
                # If type is ENUM, remove single quotes
                args.add("{}: {}".format(field_name, str(getattr(self, field_name)).replace("'", "")))
            else:
                raise NotImplementedError("Unsupported type in schema dictionary")
        str_filter = str(args).replace("'", "")
        return str_filter
