import os
import requests
from typing import Optional

# Constants (can be moved to a separate const.py if desired)
BASE_MODELSERVER_URL = "https://models.rcsb.org/v1"

# Endpoint mapping for model types
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


class ModelQuery:
    def __init__(self):
        self.base_url = BASE_MODELSERVER_URL

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
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = "",
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = "",
            ):

        return self._exec(
            type="atoms",
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
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = "",
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = "",
            ):
        return self._exec(
            type="residue_interaction",
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
            filename=filename
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
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = "",
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = "",
            ):
        return self._exec(
            type="residue_surroundings",
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
            filename=filename
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
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = "",
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = "",
            ):

        return self._exec(
            type="surrounding_ligands",
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
            omit_water=omit_water,
            assembly_name=assembly_name,
            model_nums=model_nums,
            encoding=encoding,
            copy_all_categories=copy_all_categories,
            data_source=data_source,
            transform=transform,
            download=download,
            filename=filename
        )

    def get_symmetry_mates(
            self,
            entry_id: str,
            radius: Optional[float] = 5.0,
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = "",
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = "",
            ):

        return self._exec(
            type="symmetry_mates",
            entry_id=entry_id,
            radius=radius,
            model_nums=model_nums,
            encoding=encoding,
            copy_all_categories=copy_all_categories,
            data_source=data_source,
            transform=transform,
            download=download,
            filename=filename
        )

    def get_assembly(
            self,
            entry_id: str,
            name: Optional[str] = "1",
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = "",
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = "",
            ):

        return self._exec(
            type="assembly",
            entry_id=entry_id,
            name=name,
            model_nums=model_nums,
            encoding=encoding,
            copy_all_categories=copy_all_categories,
            data_source=data_source,
            transform=transform,
            download=download,
            filename=filename
        )

    def _exec(self, type, entry_id=None, **params):
        endpoint = modelserver_endpoint_map.get(type)
        if not endpoint:
            raise ValueError(f"Unsupported type: {type}")

        if not entry_id:
            entry_id = params.get("entry_id")

        if not entry_id:
            raise ValueError("entry_id is required")

        url = os.path.join(self.base_url, entry_id, endpoint)
        clean_params = {k: v for k, v in params.items() if v is not None and k != "type"}

        response = requests.get(url, params=clean_params)
        response.raise_for_status()
        return response.content
