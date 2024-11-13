from typing import List, Tuple, Literal, Optional, Any
import typing
import re
import os
import time
import multiprocessing
import gzip
import urllib
import json
import requests

from rcsbapi.const import const, file_const
# from rcsbapi.config import config  # TODO: eventually use config to set timeout?

FileType = Literal["mmCIF", "bCIF", "PDB", "PDBML", "FASTA"]


def build_url(pdb_id: str, file_type: str) -> str:
    """build a full url based on a pdb_id and file_type

    Args:
        pdb_id (str): PDB identifier
        file_type (str): Requested file_type

    Returns:
        str: download url for file_type of pdb_id
    """
    full_file_type = make_full_type(pdb_id, file_type)
    file_extension = ""
    if full_file_type in file_const.CONTENT_TYPE_TO_EXTENSION:
        file_extension = file_const.CONTENT_TYPE_TO_EXTENSION[full_file_type]
    file_name = pdb_id.lower()

    # Special case for file types with different endpoints
    if full_file_type in ["FASTA sequence", "ligand mmCIF", "entry bCIF"]:
        return file_const.EXCEPTION_TYPE_TO_BASE_URL[full_file_type]["endpoint"] + file_name + file_extension
    return file_const.FILE_DOWNLOAD_ENDPOINT + file_name + file_extension


def make_full_type(pdb_id: str, file_type: str) -> str:
    """Make a file type into the file type phrase listed within
    the Data API "repository_content_types"
        ex: "mmCIF" --> "entry mmCIF"

    NOTE: This is overly complicated for the current package, but
    this is left in to allow for future development

    Args:
        pdb_id (str): PDB ID to compare to regex
        file_type (str): file_type requested to download
    Raises:
        ValueError: If the PDB ID doesn't match a regex string

    Returns:
        str: full file type as listed in "repository_content_types"
    """
    # NOTE: the order of the regex matches is important
    if file_type == "FASTA" and re.match("|".join(const.DATA_API_INPUT_TYPE_TO_REGEX["entry"]), pdb_id):
        return "FASTA sequence"
    elif re.match("|".join(const.DATA_API_INPUT_TYPE_TO_REGEX["entry"]), pdb_id):
        return "entry " + file_type
    elif re.match("|".join(const.DATA_API_INPUT_TYPE_TO_REGEX["chem_comp"]), pdb_id):
        return "ligand " + file_type
    else:
        raise ValueError(f"{pdb_id} is not a valid entry or ligand PDB ID")


def has_file_type(pdb_id: str, file_type: str):
    """
    Check that the PDB ID has a given file type

    Args:
        pdb_ids (List[str]): PDB identifier
        file_type (str): file type being requested

    Returns:
        Bool: Whether the file type is available or not
    """
    # Make Data API request that returns available file_types
    holdings_query = """
    query getEntry($id: String!) {
    entry(entry_id: $id) {
        rcsb_id
        rcsb_associated_holdings {
        rcsb_repository_holdings_current {
            repository_content_types
        }
        }
    }
    }
    """
    pdb_id_variable = json.dumps({"id": pdb_id.upper()})
    encoded_query = urllib.parse.quote_plus(holdings_query)
    encoded_variable = urllib.parse.quote_plus(pdb_id_variable)
    url = f"{const.DATA_API_ENDPOINT}?query={encoded_query}&variables={encoded_variable}"
    response_json = requests.get(url, timeout=60).json()
    if response_json["data"]["entry"]:
        available_file_types = (
            response_json["data"]
            ["entry"]
            ["rcsb_associated_holdings"]
            ["rcsb_repository_holdings_current"]
            ["repository_content_types"]
        )
        full_file_type = make_full_type(pdb_id, file_type)
        if full_file_type in available_file_types:
            return True
    return False


def make_id_file_tuples(
    id_list: List[str],
    file_type_list: List[FileType],
    download_dir: str,
    compressed: bool,
) -> List[Tuple[str, FileType, str, bool]]:
    """Make tuples of (pdb_id, file_type, download_dir, compressed) which will be passed
    into _download_file while multiprocessing

    Args:
        id_batch (List[str]): Batch of PDB ID
        file_type_list (List[FileType]]): List of file types requested
        download_dir (str): Path to directory where files will be downloaded
        compressed (bool): Whether to decompress downloaded files
            (which are downloaded compressed when possible)

    Returns:
        List[str]: List of (pdb_id, file_type, download_dir, compressed) tuples
    Returns:
        _type_: _description_
    """
    id_file_tuple_list = []
    for file in file_type_list:
        part_list = [(id, file, download_dir, compressed) for id in id_list]
        id_file_tuple_list += part_list
    return id_file_tuple_list


def unzip_gz(input_file: str):
    """unzip a gz file and delete the compressed file

    Args:
        input_file (str): path to input file
    """
    output_file_path = os.path.abspath(input_file).replace(".gz", "")

    with gzip.open(input_file, 'rb') as gz_file:
        with open(output_file_path, 'wb') as output:
            output.write(gz_file.read())
    os.remove(input_file)


def apply_capitalization(file_type_list: List[FileType]) -> List[FileType]:
    """Take in file_type_list and correct capitalization if the file_type matches to a FileType.
    If there isn't a match, leave as-is for error-handling later on.

    Args:
        file_type_list (List[FileType]): List of FileTypes

    Returns:
        List[str]: List of correctly capitalized
    """
    processed_file_type_list = []
    for file_type in file_type_list:
        matched = False
        for correct_file_type in typing.get_args(FileType):
            if file_type.lower() == correct_file_type.lower():
                processed_file_type_list.append(correct_file_type)
                matched = True
                break
        if matched is False:
            processed_file_type_list.append(file_type)
    assert len(file_type_list) == len(processed_file_type_list)
    return processed_file_type_list


def check_file_types(file_type_list: List[FileType]):
    """Check that requested file_types are valid

    Args:
        file_type_list (List[FileType]): List of FileTypes

    Raises:
        ValueError: Unsupported/invalid file_types
    """
    unsupported_types = set()
    for file_type in file_type_list:
        if file_type not in typing.get_args(FileType):
            unsupported_types.add(file_type)

    if unsupported_types:
        error_msg = ""
        if "XML" in unsupported_types:
            error_msg = '\n  Instead of "XML", did you mean "PDBML"?'
        raise ValueError(
            f"Unsupported or invalid file types: {list(unsupported_types)}" +
            f"{error_msg}"
        )


def _download_file(
    pdb_id: str,
    file_type: FileType,
    download_dir: str,
    compressed: bool,
) -> str:
    """Download an individual file

    Args:
        pdb_id (str): PDB identifier
        file_type (str): File type to download
        download_dir (str): Directory to download files into
        compressed (bool): Whether to decompress downloaded files
            (which are downloaded compressed when possible)

    Returns:
        str: If successful, returns empty string. If download fails, returns PDB id
    """
    url = build_url(pdb_id, file_type)
    print(url)
    file_name = os.path.basename(url)

    # Special case for FASTA because url doesn't contain file extension
    if file_type == "FASTA":
        file_name += ".fasta"

    if file_type == "FASTA":
        if not re.match("|".join(const.DATA_API_INPUT_TYPE_TO_REGEX["entry"]), pdb_id):
            return f"{pdb_id}: FASTA files are only available for entries"

    if file_type == "bCIF":
        if not re.match("|".join(const.DATA_API_INPUT_TYPE_TO_REGEX["entry"]), pdb_id):
            return f"{pdb_id}: BinaryCIF files are only available for entries"

    if file_type == "PDB":
        if not has_file_type(pdb_id, file_type):
            return f"{pdb_id}: PDB file type not available"

    response = requests.get(url, stream=True, timeout=60)
    if response.status_code == 200:
        path = os.path.join("..", download_dir, file_name)
        with open(path, 'wb') as f:
            # set chunk_size to 1 MB (1024 * 1024 bytes)
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        if compressed is False:
            unzip_gz(path)  # TODO: Think about efficiency, I think it's slow rn

        # Not in use currently. For enforcing rate limit:
        # with lock:  # ensure atomic increments
        #     request_counter.value += 1
        #     if request_counter.value % 2 == 0:
        #         time.sleep(1.0)

        # For enforcing rate limit
        # download_time = time.time()
        # check_rate_limit(download_time, prev_download_time)

        return ""
    else:
        return f"{pdb_id}: response code {response.status_code}"


def download(
    pdb_ids: List[str],
    file_type_list: List[FileType] = ["mmCIF"],
    download_dir: str = ".",
    compressed: bool = True,
    num_processors: Optional[int] = None,
):
    """Download a list of ids in the formats listed in file_type_list

    Args:
        pdb_ids (List[str]): List of PDB identifiers
        file_type (List[str], optional): List of file types to download. Defaults to ["mmCIF"]
        dir (str, optional): Directory to download files into. Defaults to "."
        compressed (bool, optional): Whether to decompress downloaded files
            (which are downloaded compressed when possible). Defaults to True
        num_processors (int, optional): number of workers to use for multiprocessing

    """
    # Apply correct capitalization to file_types
    file_type_list = apply_capitalization(file_type_list)

    # Check that file_types are supported
    check_file_types(file_type_list)

    # Before trying to download, check that PDB ids are in valid format
    invalid_ids = []
    for pdb_id in pdb_ids:
        if not (
            re.match("|".join(const.DATA_API_INPUT_TYPE_TO_REGEX["entry"]), pdb_id)
            or re.match("|".join(const.DATA_API_INPUT_TYPE_TO_REGEX["chem_comp"]), pdb_id)
        ):
            invalid_ids.append(pdb_id)
    if invalid_ids:
        raise ValueError(f"Invalid PDB Entry IDs: {invalid_ids}")

    if not num_processors:
        cpu_count = os.cpu_count()
        assert isinstance(cpu_count, int)
        num_processors = min((len(pdb_ids) * len(file_type_list)), cpu_count - 1)

    # Not in use currently. Shared counter for tracking number of requests.
    # Context manager needs to contain rest of function?
    # with multiprocessing.Manager() as manager:
        # Used to ensure requests remain below rate limit
        # request_counter = manager.Value("i", 0)
        # lock = manager.Lock()  # for syncing counter across processes
        # prev_download_time = manager.Value("time", time.time())
        # time_lock = manager.Lock()

    # Make tuples of arguments to pass into _download_file(), required for multiprocessing
    id_file_arg_list: List[Tuple[str, FileType, str, bool]] = make_id_file_tuples(
        id_list=pdb_ids,
        file_type_list=file_type_list,
        download_dir=download_dir,
        compressed=compressed
    )

    # Calculate approximate size of each batch of tasks,
    # remaining tasks will be distributed amongst workers
    chunk_size = max(1, len(id_file_arg_list) // num_processors)
    with multiprocessing.Pool(processes=num_processors) as pool:
        error_msg_list = [error_msg for error_msg in pool.starmap(_download_file, id_file_arg_list, chunksize=chunk_size) if error_msg]
    if error_msg_list:
        raise ValueError(
            "Failed Downloads\n    " +
            "\n    ".join(error_msg_list)
        )
