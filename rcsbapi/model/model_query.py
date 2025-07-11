import os
from typing import Optional
import urllib.parse
import gzip
import requests
# from model_schema import ModelSchema


BASE_MODELSERVER_URL = "https://models.rcsb.org/v1"


class ModelQuery:
    def __init__(self):
        self.base_url = BASE_MODELSERVER_URL
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
        self._params_to_exclude_from_url = ['compress_gzip', 'file_directory']

    def _exec(self, query_type: str, entry_id: str, **kwargs):
        """
        Execute the API call based on the query_type and parameters, including handling different encoding types.
        """
        endpoint = self._get_endpoint_for_type(query_type)
        url = f"{self.base_url}/{entry_id}/{endpoint}"

        # Prepare the query parameters
        query_params = {key: value for key, value in kwargs.items() if key not in self._params_to_exclude_from_url and value is not None}

        encoded_params = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote_plus)
        full_url = f"{url}?{encoded_params}"

        try:
            response = requests.get(full_url, timeout=30)  # Use the constructed URL
            response.raise_for_status()  # Raise an error for bad responses

            # Get encoding type (defaults to CIF if not provided)
            encoding = query_params.get('encoding', 'CIF').upper()

            # Handle response based on encoding type
            if encoding == 'BCIF':
                file_content = response.content
                file_extension = 'bcif'
            elif encoding == 'SDF':
                file_content = response.text
                file_extension = 'sdf'
            elif encoding == 'MOL':
                file_content = response.text
                file_extension = 'mol'
            elif encoding == 'MOL2':
                file_content = response.text
                file_extension = 'mol2'
            else:
                file_content = response.text
                file_extension = 'cif'

            filename = query_params.get('filename')
            file_directory = query_params.get('file_directory')

            if filename and file_directory:
                file_path = os.path.join(file_directory, filename)
            elif query_params.get('download') and filename:
                file_path = os.path.join(os.getcwd(), filename)
            elif query_params.get('download'):
                file_path = os.path.join(os.getcwd(), f"{entry_id}_{query_type}.{file_extension}")
            else:
                return file_content

            if kwargs.get('compress_gzip', False):
                # Compress the content before saving
                if encoding == 'BCIF':
                    with gzip.open(file_path + '.gz', 'wb') as file:
                        file.write(file_content)
                else:
                    with gzip.open(file_path + '.gz', 'w') as file:
                        file.write(file_content)
            else:
                # Write without compression
                if encoding == 'BCIF':
                    with open(file_path, 'wb') as file:
                        file.write(file_content)
                else:
                    with open(file_path, 'w') as file:
                        file.write(file_content)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def _get_endpoint_for_type(self, query_type: str) -> str:
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

        if query_type not in modelserver_endpoint_map:
            raise ValueError(f"Unknown query type: {query_type}")

        return modelserver_endpoint_map[query_type]

    def get_full_structure(
            self,
            entry_id: str,
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = None,
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = None,
            file_directory: Optional[str] = None,
            compress_gzip: Optional[bool] = False,
            ):
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
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = None,
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = None,
            file_directory: Optional[str] = None,
            compress_gzip: Optional[bool] = False,
            ):

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
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = None,
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = None,
            file_directory: Optional[str] = None,
            compress_gzip: Optional[bool] = False,
            ):
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
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = None,
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = None,
            file_directory: Optional[str] = None,
            compress_gzip: Optional[bool] = False,
            ):
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
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = None,
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = None,
            file_directory: Optional[str] = None,
            compress_gzip: Optional[bool] = False,
            ):
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
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = None,
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = None,
            file_directory: Optional[str] = None,
            compress_gzip: Optional[bool] = False,
            ):

        return self._exec(
            query_type="surrounding_ligands",
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
            filename=filename,
            file_directory=file_directory,
            compress_gzip=compress_gzip,
        )

    def get_symmetry_mates(
            self,
            entry_id: str,
            radius: Optional[float] = 5.0,
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = None,
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = None,
            file_directory: Optional[str] = None,
            compress_gzip: Optional[bool] = False,
            ):

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
            model_nums: Optional[str] = None,
            encoding: Optional[str] = "cif",
            copy_all_categories: Optional[bool] = False,
            data_source: Optional[str] = None,
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = None,
            file_directory: Optional[str] = None,
            compress_gzip: Optional[bool] = False,
            ):

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
