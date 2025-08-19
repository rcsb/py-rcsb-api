import os
import time
import logging
from typing import Optional, Literal, List
import urllib.parse
import gzip
import httpx
from rcsbapi.const import const
from rcsbapi.config import config

logger = logging.getLogger(__name__)


class ModelQuery:
    """
    Class for querying model data from the RCSB ModelServer.

    Supports various query types such as full structure retrieval, ligand queries,
    atom-level queries, and contextual residue or ligand information. Handles output
    formats, optional file saving, and gzip compression.
    """

    def __init__(
        self,
        encoding: Optional[Literal["cif", "bcif", "sdf", "mol", "mol2"]] = "cif",
        file_directory: Optional[str] = None,
        download: Optional[bool] = False,
        compress_gzip: Optional[bool] = False,
        max_retries: int = None,
        retry_backoff: int = None,
    ):
        """Query object for Model Server API requests.

        Args:
            encoding (str, optional): Default encoding format to use for all requests. Defaults to "cif".
            file_directory (str, optional): Default file directory to use for all requests. Defaults to current working directory.
            download (bool, optional): Default download flag to use for all requests. Defaults to False.
            compress_gzip (bool, optional): Default setting for GZIP compression to use for all requests. Defaults to False.
            max_retries (int, optional): Default number of max retries to perform for all requests. Defaults to `config.MAX_RETRIES`.
            retry_backoff (int, optional): Default retry backoff delay to wait between failed requets. Defaults to `config.RETRY_BACKOFF`.
        """
        self.base_url = const.MODELSERVER_API_BASE_URL
        self.modelserver_endpoint_map = {
            "full": "full",
            "ligand": "ligand",
            "atoms": "atoms",
            "residue_interaction": "residueInteraction",
            "residue_surroundings": "residueSurroundings",
            "surrounding_ligands": "surroundingLigands",
            "symmetry_mates": "symmetryMates",
            "assembly": "assembly"
        }
        self._params_to_exclude_from_url = ["compress_gzip", "file_directory"]
        self.encoding = encoding
        self.file_directory = file_directory
        self.download = download
        self.compress_gzip = compress_gzip

        # Request retry and rate limit settings
        self._max_retries = max_retries if max_retries else config.MAX_RETRIES
        self._retry_backoff = retry_backoff if retry_backoff else config.RETRY_BACKOFF
        self._last_request_time = time.monotonic()
        self._request_count = 0
        self._request_limit_time_interval = 10  # request rate limits are applied over 10s window
        self._requests_per_window_limit = config.MODEL_API_REQUESTS_PER_SECOND * self._request_limit_time_interval

    def _exec(self, query_type: str, entry_id: str, **kwargs):
        """
        Execute the API request based on the query type and provided parameters.

        Args:
            query_type (str): The type of model query to perform.
            entry_id (str): The entry ID to query.
            **kwargs: Optional query parameters.

        Returns:
            Union[str, bytes, None]: File content if not downloaded, file path if downloaded,
            or None if an error occurred.
        """
        endpoint = self._get_endpoint_for_type(query_type)
        url = f"{self.base_url}/{entry_id}/{endpoint}"

        if "model_nums" in kwargs and kwargs["model_nums"] is not None:
            kwargs["model_nums"] = ",".join(str(num) for num in kwargs["model_nums"])

        # Prepare the query parameters
        query_params = {key: value for key, value in kwargs.items() if key not in self._params_to_exclude_from_url and value is not None}

        encoded_params = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote_plus)
        full_url = f"{url}?{encoded_params}"

        try:
            response = self._submit_request(full_url)

            # Get encoding type (defaults to CIF if not provided)
            encoding = query_params.get("encoding", "CIF").upper()

            # Handle response based on encoding type
            if encoding == "BCIF":
                file_content = response.content
                file_extension = "bcif"
            elif encoding == "SDF":
                file_content = response.text
                file_extension = "sdf"
            elif encoding == "MOL":
                file_content = response.text
                file_extension = "mol"
            elif encoding == "MOL2":
                file_content = response.text
                file_extension = "mol2"
            else:
                file_content = response.text
                file_extension = "cif"

            filename = kwargs.get("filename")
            file_directory = kwargs.get("file_directory")

            if filename and file_directory:
                file_path = os.path.abspath(os.path.join(file_directory, filename))
                os.makedirs(file_directory, exist_ok=True)

            elif kwargs.get("download") and file_directory:
                os.makedirs(file_directory, exist_ok=True)

                if query_type == "assembly" and "name" in kwargs and kwargs["name"] is not None:
                    file_name = f"{entry_id}_{query_type}-{kwargs['name']}.{file_extension}"
                else:
                    file_name = f"{entry_id}_{query_type}.{file_extension}"

                file_path = os.path.abspath(os.path.join(file_directory, file_name))

            elif kwargs.get("download") and filename:
                file_path = os.path.abspath(os.path.join(os.getcwd(), filename))

            elif kwargs.get("download"):
                if query_type == "assembly" and "name" in kwargs and kwargs["name"] is not None:
                    file_name = f"{entry_id}_{query_type}-{kwargs['name']}.{file_extension}"
                else:
                    file_name = f"{entry_id}_{query_type}.{file_extension}"
                file_path = os.path.abspath(os.path.join(os.getcwd(), file_name))

            else:
                return file_content

            if kwargs.get("compress_gzip", False):
                if not file_path.lower().endswith(".gz"):
                    # Update path to include .gz suffix
                    file_path += ".gz"

                # Compress the content before saving
                if encoding == "BCIF":
                    with gzip.open(file_path, "wb") as file:
                        file.write(file_content)
                else:
                    with gzip.open(file_path, "wb") as file:
                        file.write(file_content.encode('utf-8'))
            else:
                # Write without compression
                if encoding == "BCIF":
                    with open(file_path, "wb") as file:
                        file.write(file_content)
                else:
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(file_content)

            # Return the file path of the downloaded file
            return file_path

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error("Request error: %r", e)
            return None

    def _get_endpoint_for_type(self, query_type: str) -> str:
        """
        Get the API endpoint string for a given query type.

        Args:
            query_type (str): Query type to map.

        Returns:
            str: Corresponding endpoint string.

        Raises:
            ValueError: If query type is invalid.
        """
        if query_type not in self.modelserver_endpoint_map:
            raise ValueError(f"Unknown query type: {query_type}")

        return self.modelserver_endpoint_map[query_type]

    def _submit_request(self, url):
        """Submit a single request, with retry behavior and rate limiting.
        """
        retry_backoff = self._retry_backoff
        for attempt in range(1, self._max_retries + 1):
            try:
                # First check if request rate-limit reached
                self._rate_limiter()
                #
                # Now perform the actual request
                response = httpx.get(url, timeout=config.API_TIMEOUT, headers={"Content-Type": "application/json", "User-Agent": const.USER_AGENT})
                response.raise_for_status()  # Raise an error for bad responses
                #
                if response.status_code == httpx.codes.OK:
                    return response
                elif response.status_code == httpx.codes.NO_CONTENT:
                    return None
                else:
                    raise httpx.HTTPStatusError(
                        f"Unexpected status: {response.status_code}",
                        request=response.request,
                        response=response
                    )
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                if attempt == self._max_retries:
                    logger.error(
                        "Final retry attempt %r failed with exception:\n    %r\n"
                        "Check query and parameters. If issue persists, try reducing 'config.MODEL_API_REQUESTS_PER_SECOND'.",
                        attempt,
                        e
                    )
                    raise
                logger.debug("Attempt %r failed: %r. Retrying in %r seconds...", attempt, e, self._retry_backoff)
                time.sleep(retry_backoff)
                retry_backoff *= 2  # exponential backoff

    def _rate_limiter(self):
        """Check if request rate-limit has been reached, and if so, sleep until it can be reset.
        """
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed >= self._request_limit_time_interval:
            self._last_request_time = now
            self._request_count = 0
        if self._request_count >= self._requests_per_window_limit:
            sleep_time = self._request_limit_time_interval - elapsed
            if sleep_time > 0:
                logger.info(
                    "Request rate limit reached (%r requests/ %r seconds). Sleeping for %.1f seconds...",
                    self._requests_per_window_limit,
                    self._request_limit_time_interval,
                    sleep_time
                )
                time.sleep(sleep_time)
            self._last_request_time = time.monotonic()
            self._request_count = 0
        self._request_count += 1

    def get_multiple_structures(
        self,
        entry_ids: List[str],
        query_type: Literal["full", "ligand", "atoms", "residue_interaction", "residue_surroundings", "surrounding_ligands", "symmetry_mates", "assembly"],
        **kwargs
    ):
        """
        Fetch multiple structures at once based on a list of entry_ids.

        Args:
            entry_ids (List[str]): List of structure IDs to query.
            query_type (str): The type of query to execute (e.g., "full", "ligand", etc.).
            **kwargs: Additional query parameters to pass to the API.

        Returns:
            dict: A dictionary with entry IDs as keys and the corresponding responses as values.
        """
        results = {}
        for entry_id in entry_ids:
            try:
                result = self._exec(query_type, entry_id, **kwargs)
                results[entry_id] = result
            except Exception as e:
                results[entry_id] = f"Error occurred: {str(e)}"
        return results

    def get_full_structure(
        self,
        entry_id: str,
        model_nums: Optional[List[int]] = None,
        encoding: Optional[Literal["cif", "bcif"]] = None,
        copy_all_categories: Optional[bool] = False,
        data_source: Optional[str] = None,
        transform: Optional[str] = None,
        download: Optional[bool] = None,
        filename: Optional[str] = None,
        file_directory: Optional[str] = None,
        compress_gzip: Optional[bool] = None,
    ):
        """
        Retrieve the full atomic model of a specified entry from the ModelServer.

        Parameters:
            entry_id (str): The PDB ID of the structure to retrieve.
            model_nums (Optional[List[int]]): List of model numbers to include (if multiple models exist).
            encoding (Optional[Literal["cif", "bcif"]]): Format of the returned file (default is "cif").
            copy_all_categories (Optional[bool]): If True, copies all data categories; otherwise, uses minimal.
            data_source (Optional[str]): Optional data source name.
            transform (Optional[str]): Transformation matrix to apply to coordinates.
            download (Optional[bool]): If True, downloads and saves the file to disk.
            filename (Optional[str]): Custom filename to use if downloading.
            file_directory (Optional[str]): Directory where file will be saved.
            compress_gzip (Optional[bool]): If True, compress the output file using GZIP.
        """
        encoding = encoding if encoding else self.encoding
        file_directory = file_directory if file_directory else self.file_directory
        download = download if download is not None else self.download
        compress_gzip = compress_gzip if compress_gzip is not None else self.compress_gzip
        return self._exec(
            query_type="full",
            entry_id=entry_id,
            model_nums=model_nums,
            encoding=encoding,
            copy_all_categories=copy_all_categories,
            data_source=data_source,
            transform=transform,
            download=download,
            filename=filename,
            file_directory=file_directory,
            compress_gzip=compress_gzip,
        )

    def get_ligand(
        self,
        entry_id: str,
        label_entity_id: Optional[str] = None,
        label_asym_id: Optional[str] = None,
        auth_asym_id: Optional[str] = None,
        label_comp_id: Optional[str] = None,
        auth_comp_id: Optional[str] = None,
        label_seq_id: Optional[int] = None,
        auth_seq_id: Optional[int] = None,
        pdbx_PDB_ins_code: Optional[str] = None,
        label_atom_id: Optional[str] = None,
        auth_atom_id: Optional[str] = None,
        type_symbol: Optional[str] = None,
        model_nums: Optional[List[int]] = None,
        encoding: Optional[Literal["cif", "sdf", "mol", "mol2", "bcif"]] = None,
        copy_all_categories: Optional[bool] = False,
        data_source: Optional[str] = None,
        transform: Optional[str] = None,
        download: Optional[bool] = None,
        filename: Optional[str] = None,
        file_directory: Optional[str] = None,
        compress_gzip: Optional[bool] = None,
    ):
        """
        Retrieves ligand-related information, including components and interactions.

        Parameters:
            entry_id (str): The PDB ID of the structure.
            label_entity_id (str, optional): Entity identifier using label nomenclature.
            label_asym_id (str, optional): Asymmetric unit ID using label nomenclature.
            auth_asym_id (str, optional): Asymmetric unit ID using author-provided nomenclature.
            label_comp_id (str, optional): Ligand component ID using label nomenclature.
            auth_comp_id (str, optional): Ligand component ID using author nomenclature.
            label_seq_id (int, optional): Residue sequence number (label nomenclature).
            auth_seq_id (int, optional): Residue sequence number (author nomenclature).
            pdbx_PDB_ins_code (str, optional): Insertion code for distinguishing alternate residue IDs.
            label_atom_id (str, optional): Atom name using label nomenclature.
            auth_atom_id (str, optional): Atom name using author nomenclature.
            type_symbol (str, optional): Atomic element symbol (e.g., "C", "N", "O").
            model_nums (List[int], optional): Specific model numbers to retrieve.
            encoding (str, optional): Output format, one of: "cif", "sdf", "mol", "mol2", "bcif".
            copy_all_categories (bool, optional): Whether to include all data categories in the output.
            data_source (str, optional): Source of the structure data.
            transform (str, optional): Transformation ID for biological assemblies or specific views.
            download (bool, optional): If True, save the result to disk.
            filename (str, optional): Custom filename for saving the output.
            file_directory (str, optional): Directory path to save the output file.
            compress_gzip (bool, optional): If True, compress the file using gzip.
        """
        encoding = encoding if encoding is not None else self.encoding
        file_directory = file_directory if file_directory else self.file_directory
        download = download if download is not None else self.download
        compress_gzip = compress_gzip if compress_gzip is not None else self.compress_gzip
        return self._exec(
            query_type="ligand",
            entry_id=entry_id,
            label_entity_id=label_entity_id,
            label_asym_id=label_asym_id,
            auth_asym_id=auth_asym_id,
            label_comp_id=label_comp_id,
            auth_comp_id=auth_comp_id,
            label_seq_id=label_seq_id,
            auth_seq_id=auth_seq_id,
            pdbx_PDB_ins_code=pdbx_PDB_ins_code,
            label_atom_id=label_atom_id,
            auth_atom_id=auth_atom_id,
            type_symbol=type_symbol,
            model_nums=model_nums,
            encoding=encoding,
            copy_all_categories=copy_all_categories,
            data_source=data_source,
            transform=transform,
            download=download,
            filename=filename,
            file_directory=file_directory,
            compress_gzip=compress_gzip,
        )

    def get_atoms(
        self,
        entry_id: str,
        label_entity_id: Optional[str] = None,
        label_asym_id: Optional[str] = None,
        auth_asym_id: Optional[str] = None,
        label_comp_id: Optional[str] = None,
        auth_comp_id: Optional[str] = None,
        label_seq_id: Optional[int] = None,
        auth_seq_id: Optional[int] = None,
        pdbx_PDB_ins_code: Optional[str] = None,
        label_atom_id: Optional[str] = None,
        auth_atom_id: Optional[str] = None,
        type_symbol: Optional[str] = None,
        model_nums: Optional[List[int]] = None,
        encoding: Optional[Literal["cif", "bcif"]] = None,
        copy_all_categories: Optional[bool] = False,
        data_source: Optional[str] = None,
        transform: Optional[str] = None,
        download: Optional[bool] = None,
        filename: Optional[str] = None,
        file_directory: Optional[str] = None,
        compress_gzip: Optional[bool] = None,
    ):
        """
        Fetches atom-level details.
        """
        encoding = encoding if encoding is not None else self.encoding
        file_directory = file_directory if file_directory else self.file_directory
        download = download if download is not None else self.download
        compress_gzip = compress_gzip if compress_gzip is not None else self.compress_gzip
        return self._exec(
            query_type="atoms",
            entry_id=entry_id,
            label_entity_id=label_entity_id,
            label_asym_id=label_asym_id,
            auth_asym_id=auth_asym_id,
            label_comp_id=label_comp_id,
            auth_comp_id=auth_comp_id,
            label_seq_id=label_seq_id,
            auth_seq_id=auth_seq_id,
            pdbx_PDB_ins_code=pdbx_PDB_ins_code,
            label_atom_id=label_atom_id,
            auth_atom_id=auth_atom_id,
            type_symbol=type_symbol,
            model_nums=model_nums,
            encoding=encoding,
            copy_all_categories=copy_all_categories,
            data_source=data_source,
            transform=transform,
            download=download,
            filename=filename,
            file_directory=file_directory,
            compress_gzip=compress_gzip,
        )

    def get_residue_interaction(
        self,
        entry_id: str,
        label_entity_id: Optional[str] = None,
        label_asym_id: Optional[str] = None,
        auth_asym_id: Optional[str] = None,
        label_comp_id: Optional[str] = None,
        auth_comp_id: Optional[str] = None,
        label_seq_id: Optional[int] = None,
        auth_seq_id: Optional[int] = None,
        pdbx_PDB_ins_code: Optional[str] = None,
        label_atom_id: Optional[str] = None,
        auth_atom_id: Optional[str] = None,
        type_symbol: Optional[str] = None,
        radius: Optional[float] = 5.0,
        assembly_name: Optional[str] = None,
        model_nums: Optional[List[int]] = None,
        encoding: Optional[Literal["cif", "bcif"]] = None,
        copy_all_categories: Optional[bool] = False,
        data_source: Optional[str] = None,
        transform: Optional[str] = None,
        download: Optional[bool] = None,
        filename: Optional[str] = None,
        file_directory: Optional[str] = None,
        compress_gzip: Optional[bool] = None,
    ):
        """
        Retrieves data on interactions between residues.
        """
        encoding = encoding if encoding is not None else self.encoding
        file_directory = file_directory if file_directory else self.file_directory
        download = download if download is not None else self.download
        compress_gzip = compress_gzip if compress_gzip is not None else self.compress_gzip
        return self._exec(
            query_type="residue_interaction",
            entry_id=entry_id,
            label_entity_id=label_entity_id,
            label_asym_id=label_asym_id,
            auth_asym_id=auth_asym_id,
            label_comp_id=label_comp_id,
            auth_comp_id=auth_comp_id,
            label_seq_id=label_seq_id,
            auth_seq_id=auth_seq_id,
            pdbx_PDB_ins_code=pdbx_PDB_ins_code,
            label_atom_id=label_atom_id,
            auth_atom_id=auth_atom_id,
            type_symbol=type_symbol,
            radius=radius,
            assembly_name=assembly_name,
            model_nums=model_nums,
            encoding=encoding,
            copy_all_categories=copy_all_categories,
            data_source=data_source,
            transform=transform,
            download=download,
            filename=filename,
            file_directory=file_directory,
            compress_gzip=compress_gzip,
        )

    def get_residue_surroundings(
        self,
        entry_id: str,
        label_entity_id: Optional[str] = None,
        label_asym_id: Optional[str] = None,
        auth_asym_id: Optional[str] = None,
        label_comp_id: Optional[str] = None,
        auth_comp_id: Optional[str] = None,
        label_seq_id: Optional[int] = None,
        auth_seq_id: Optional[int] = None,
        pdbx_PDB_ins_code: Optional[str] = None,
        label_atom_id: Optional[str] = None,
        auth_atom_id: Optional[str] = None,
        type_symbol: Optional[str] = None,
        radius: Optional[float] = 5.0,
        assembly_name: Optional[str] = None,
        model_nums: Optional[List[int]] = None,
        encoding: Optional[Literal["cif", "bcif"]] = None,
        copy_all_categories: Optional[bool] = False,
        data_source: Optional[str] = None,
        transform: Optional[str] = None,
        download: Optional[bool] = None,
        filename: Optional[str] = None,
        file_directory: Optional[str] = None,
        compress_gzip: Optional[bool] = None,
    ):
        """
        Provides information about residues surrounding a given structure.
        """
        encoding = encoding if encoding is not None else self.encoding
        file_directory = file_directory if file_directory else self.file_directory
        download = download if download is not None else self.download
        compress_gzip = compress_gzip if compress_gzip is not None else self.compress_gzip
        return self._exec(
            query_type="residue_surroundings",
            entry_id=entry_id,
            label_entity_id=label_entity_id,
            label_asym_id=label_asym_id,
            auth_asym_id=auth_asym_id,
            label_comp_id=label_comp_id,
            auth_comp_id=auth_comp_id,
            label_seq_id=label_seq_id,
            auth_seq_id=auth_seq_id,
            pdbx_PDB_ins_code=pdbx_PDB_ins_code,
            label_atom_id=label_atom_id,
            auth_atom_id=auth_atom_id,
            type_symbol=type_symbol,
            radius=radius,
            assembly_name=assembly_name,
            model_nums=model_nums,
            encoding=encoding,
            copy_all_categories=copy_all_categories,
            data_source=data_source,
            transform=transform,
            download=download,
            filename=filename,
            file_directory=file_directory,
            compress_gzip=compress_gzip,
        )

    def get_surrounding_ligands(
        self,
        entry_id: str,
        label_entity_id: Optional[str] = None,
        label_asym_id: Optional[str] = None,
        auth_asym_id: Optional[str] = None,
        label_comp_id: Optional[str] = None,
        auth_comp_id: Optional[str] = None,
        label_seq_id: Optional[int] = None,
        auth_seq_id: Optional[int] = None,
        pdbx_PDB_ins_code: Optional[str] = None,
        label_atom_id: Optional[str] = None,
        auth_atom_id: Optional[str] = None,
        type_symbol: Optional[str] = None,
        omit_water: Optional[bool] = False,
        radius: Optional[float] = 5.0,
        assembly_name: Optional[str] = None,
        model_nums: Optional[List[int]] = None,
        encoding: Optional[Literal["cif", "bcif"]] = None,
        copy_all_categories: Optional[bool] = False,
        data_source: Optional[str] = None,
        transform: Optional[str] = None,
        download: Optional[bool] = None,
        filename: Optional[str] = None,
        file_directory: Optional[str] = None,
        compress_gzip: Optional[bool] = None,
    ):
        """
        Provides information about ligands surrounding a given structure.
        """
        encoding = encoding if encoding is not None else self.encoding
        file_directory = file_directory if file_directory else self.file_directory
        download = download if download is not None else self.download
        compress_gzip = compress_gzip if compress_gzip is not None else self.compress_gzip
        return self._exec(
            query_type="surrounding_ligands",
            entry_id=entry_id,
            radius=radius,
            label_entity_id=label_entity_id,
            label_asym_id=label_asym_id,
            auth_asym_id=auth_asym_id,
            label_comp_id=label_comp_id,
            auth_comp_id=auth_comp_id,
            label_seq_id=label_seq_id,
            auth_seq_id=auth_seq_id,
            pdbx_PDB_ins_code=pdbx_PDB_ins_code,
            label_atom_id=label_atom_id,
            auth_atom_id=auth_atom_id,
            type_symbol=type_symbol,
            omit_water=omit_water,
            assembly_name=assembly_name,
            model_nums=model_nums,
            encoding=encoding,
            copy_all_categories=copy_all_categories,
            data_source=data_source,
            transform=transform,
            download=download,
            filename=filename,
            file_directory=file_directory,
            compress_gzip=compress_gzip,
        )

    def get_symmetry_mates(
        self,
        entry_id: str,
        radius: Optional[float] = 5.0,
        model_nums: Optional[List[int]] = None,
        encoding: Optional[Literal["cif", "bcif"]] = None,
        copy_all_categories: Optional[bool] = False,
        data_source: Optional[str] = None,
        transform: Optional[str] = None,
        download: Optional[bool] = None,
        filename: Optional[str] = None,
        file_directory: Optional[str] = None,
        compress_gzip: Optional[bool] = None,
    ):
        """
        Retrieves symmetry-related data.
        """
        encoding = encoding if encoding is not None else self.encoding
        file_directory = file_directory if file_directory else self.file_directory
        download = download if download is not None else self.download
        compress_gzip = compress_gzip if compress_gzip is not None else self.compress_gzip
        return self._exec(
            query_type="symmetry_mates",
            entry_id=entry_id,
            radius=radius,
            model_nums=model_nums,
            encoding=encoding,
            copy_all_categories=copy_all_categories,
            data_source=data_source,
            transform=transform,
            download=download,
            filename=filename,
            file_directory=file_directory,
            compress_gzip=compress_gzip,
        )

    def get_assembly(
        self,
        entry_id: str,
        name: Optional[str] = "1",
        model_nums: Optional[List[int]] = None,
        encoding: Optional[Literal["cif", "bcif"]] = None,
        copy_all_categories: Optional[bool] = False,
        data_source: Optional[str] = None,
        transform: Optional[str] = None,
        download: Optional[bool] = None,
        filename: Optional[str] = None,
        file_directory: Optional[str] = None,
        compress_gzip: Optional[bool] = None,
    ):
        """
        Fetches information about molecular assemblies.
        """
        encoding = encoding if encoding is not None else self.encoding
        file_directory = file_directory if file_directory else self.file_directory
        download = download if download is not None else self.download
        compress_gzip = compress_gzip if compress_gzip is not None else self.compress_gzip
        return self._exec(
            query_type="assembly",
            entry_id=entry_id,
            name=name,
            model_nums=model_nums,
            encoding=encoding,
            copy_all_categories=copy_all_categories,
            data_source=data_source,
            transform=transform,
            download=download,
            filename=filename,
            file_directory=file_directory,
            compress_gzip=compress_gzip,
        )
