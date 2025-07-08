import requests
from typing import Optional
from model_schema import ModelSchema


BASE_MODELSERVER_URL = "https://models.rcsb.org/v1"


class ModelQuery:
    def __init__(self):
        self.base_url = BASE_MODELSERVER_URL
        self.schema = ModelSchema()
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

        # This builds a map like {"full": ["encoding", ...], "ligand": [...], ...}
        self.full_param_map = self.schema.get_param_dict()

    def _exec(self, type: str, entry_id: str, **params):
        """
        Execute the API call based on the type and parameters.
        """
        endpoint = self._get_endpoint_for_type(type)
        url = f"{self.base_url}/{entry_id}/{endpoint}"

        # Prepare the query parameters
        query_params = {key: value for key, value in params.items() if value is not None}

        try:
            response = requests.post(url, json=query_params)  # POST request with JSON payload
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            return response.text

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def _get_endpoint_for_type(self, type: str) -> str:
        """
        Get the correct endpoint based on the query type.
        """
        modelserver_endpoint_map = {
            "full": "full",
            "ligand": "ligand",
            "atoms": "atoms",
            "residue_interaction": "residueInteraction",
            "residue_surroundings": "residueSurroundings",
            "surrounding_ligands": "surroundingLigands",
            "symmetry_mates": "symmetryMates",
            "assembly": "assembly"
        }

        if type not in modelserver_endpoint_map:
            raise ValueError(f"Unknown query type: {type}")

        return modelserver_endpoint_map[type]

    def get_full_structure(
            self,
            entry_id: str,
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = "",
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = "",
            ):
        """
        Get the full structure from the ModelServer.
        """
        return self._exec(
            type="full",
            entry_id=entry_id,
            model_nums=model_nums,
            encoding=encoding,
            copy_all_categories=copy_all_categories,
            data_source=data_source,
            transform=transform,
            download=download,
            filename=filename
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
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = "",
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = "",
            ):

        return self._exec(
            type="ligand",
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
            filename=filename
        )
