import os
import requests
from typing import Optional
from model_schema import ModelSchema
import urllib.parse
import gzip


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
        self.fun_list = ['compress_gzip', 'file_directory']  # TODO: Change Name

        # This builds a map like {"full": ["encoding", ...], "ligand": [...], ...}
        self.full_param_map = self.schema.get_param_dict()

    def _exec(self, query_type: str, entry_id: str, **kwargs):
        """
        Execute the API call based on the query_type and parameters, including handling different encoding types.
        """
        endpoint = self._get_endpoint_for_type(query_type)
        url = f"{self.base_url}/{entry_id}/{endpoint}"

        # Prepare the query parameters
        query_params = {key: value for key, value in kwargs.items() if key not in self.fun_list}

        encoded_params = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote_plus)
        full_url = f"{url}?{encoded_params}"

        try:
            compress_gzip = kwargs.get('compress_gzip', False)

            # If compress_gzip is True, skip downloading the file and only download if compress_gzip is False
            if not compress_gzip:
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

                # Write the content to the appropriate file
                if encoding == 'BCIF':
                    with open(file_path, 'wb') as file:
                        file.write(file_content)
                else:
                    with open(file_path, 'w') as file:
                        file.write(file_content)

            else:
                # If compress_gzip is True, download the file and compress it
                file_content = self._download_and_compress_file(full_url)

                filename = query_params.get('filename')
                file_directory = query_params.get('file_directory')

                if filename and file_directory:
                    file_path = os.path.join(file_directory, filename)
                elif query_params.get('download') and filename:
                    file_path = os.path.join(os.getcwd(), filename)
                elif query_params.get('download'):
                    file_path = os.path.join(os.getcwd(), f"{entry_id}_{query_type}.gz")

                with gzip.open(file_path, 'wb') as f_out:
                    f_out.write(file_content)

            return file_path  # Return the path of the saved file or None if an error occurs

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def _download_and_compress_file(self, url: str) -> bytes:
        """
        Downloads the content from the URL and compresses it using gzip.
        Returns the compressed content as bytes.
        """
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Ensure we got a valid response

        # Gzip compress the file content
        compressed_content = gzip.compress(response.content)
        return compressed_content

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
            data_source: Optional[str] = "",
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = "",
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
            data_source: Optional[str] = "",
            transform: Optional[str] = None,
            download: Optional[bool] = False,
            filename: Optional[str] = "",
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

    # def get_atoms(
    #         self,
    #         entry_id: str,
    #         label_entity_id: Optional[str] = None,
    #         label_asym_id: Optional[str] = None,
    #         auth_asym_id: Optional[str] = None,
    #         label_comp_id: Optional[str] = None,
    #         auth_comp_id: Optional[str] = None,
    #         label_seq_id: Optional[int] = None,
    #         auth_seq_id: Optional[int] = None,
    #         pdbx_PDB_ins_code: Optional[str] = None,
    #         label_atom_id: Optional[str] = None,
    #         auth_atom_id: Optional[str] = None,
    #         type_symbol: Optional[str] = None,
    #         model_nums: Optional[str] = None,
    #         encoding: Optional[str] = "cif",
    #         copy_all_categories: Optional[bool] = False,
    #         data_source: Optional[str] = "",
    #         transform: Optional[str] = None,
    #         download: Optional[bool] = False,
    #         filename: Optional[str] = "",
    #         ):

    #     return self._exec(
    #         type="atoms",
    #         entry_id=entry_id,
    #         label_entity_id=label_entity_id,
    #         label_asym_id=label_asym_id,
    #         auth_asym_id=auth_asym_id,
    #         label_comp_id=label_comp_id,
    #         auth_comp_id=auth_comp_id,
    #         label_seq_id=label_seq_id,
    #         auth_seq_id=auth_seq_id,
    #         pdbx_PDB_ins_code=pdbx_PDB_ins_code,
    #         label_atom_id=label_atom_id,
    #         auth_atom_id=auth_atom_id,
    #         type_symbol=type_symbol,
    #         model_nums=model_nums,
    #         encoding=encoding,
    #         copy_all_categories=copy_all_categories,
    #         data_source=data_source,
    #         transform=transform,
    #         download=download,
    #         filename=filename
    #     )

    # def get_residue_interaction(
    #         self,
    #         entry_id: str,
    #         label_entity_id: Optional[str] = None,
    #         label_asym_id: Optional[str] = None,
    #         auth_asym_id: Optional[str] = None,
    #         label_comp_id: Optional[str] = None,
    #         auth_comp_id: Optional[str] = None,
    #         label_seq_id: Optional[int] = None,
    #         auth_seq_id: Optional[int] = None,
    #         pdbx_PDB_ins_code: Optional[str] = None,
    #         label_atom_id: Optional[str] = None,
    #         auth_atom_id: Optional[str] = None,
    #         type_symbol: Optional[str] = None,
    #         radius: Optional[float] = 5.0,
    #         assembly_name: Optional[str] = None,
    #         model_nums: Optional[str] = None,
    #         encoding: Optional[str] = "cif",
    #         copy_all_categories: Optional[bool] = False,
    #         data_source: Optional[str] = "",
    #         transform: Optional[str] = None,
    #         download: Optional[bool] = False,
    #         filename: Optional[str] = "",
    #         ):
    #     return self._exec(
    #         query_type="residue_interaction",
    #         entry_id=entry_id,
    #         label_entity_id=label_entity_id,
    #         label_asym_id=label_asym_id,
    #         auth_asym_id=auth_asym_id,
    #         label_comp_id=label_comp_id,
    #         auth_comp_id=auth_comp_id,
    #         label_seq_id=label_seq_id,
    #         auth_seq_id=auth_seq_id,
    #         pdbx_PDB_ins_code=pdbx_PDB_ins_code,
    #         label_atom_id=label_atom_id,
    #         auth_atom_id=auth_atom_id,
    #         type_symbol=type_symbol,
    #         radius=radius,
    #         assembly_name=assembly_name,
    #         model_nums=model_nums,
    #         encoding=encoding,
    #         copy_all_categories=copy_all_categories,
    #         data_source=data_source,
    #         transform=transform,
    #         download=download,
    #         filename=filename
    #     )

    # def get_residue_surroundings(
    #         self,
    #         entry_id: str,
    #         label_entity_id: Optional[str] = None,
    #         label_asym_id: Optional[str] = None,
    #         auth_asym_id: Optional[str] = None,
    #         label_comp_id: Optional[str] = None,
    #         auth_comp_id: Optional[str] = None,
    #         label_seq_id: Optional[int] = None,
    #         auth_seq_id: Optional[int] = None,
    #         pdbx_PDB_ins_code: Optional[str] = None,
    #         label_atom_id: Optional[str] = None,
    #         auth_atom_id: Optional[str] = None,
    #         type_symbol: Optional[str] = None,
    #         radius: Optional[float] = 5.0,
    #         assembly_name: Optional[str] = None,
    #         model_nums: Optional[str] = None,
    #         encoding: Optional[str] = "cif",
    #         copy_all_categories: Optional[bool] = False,
    #         data_source: Optional[str] = "",
    #         transform: Optional[str] = None,
    #         download: Optional[bool] = False,
    #         filename: Optional[str] = "",
    #         ):
    #     return self._exec(
    #         query_type="residue_surroundings",
    #         entry_id=entry_id,
    #         label_entity_id=label_entity_id,
    #         label_asym_id=label_asym_id,
    #         auth_asym_id=auth_asym_id,
    #         label_comp_id=label_comp_id,
    #         auth_comp_id=auth_comp_id,
    #         label_seq_id=label_seq_id,
    #         auth_seq_id=auth_seq_id,
    #         pdbx_PDB_ins_code=pdbx_PDB_ins_code,
    #         label_atom_id=label_atom_id,
    #         auth_atom_id=auth_atom_id,
    #         type_symbol=type_symbol,
    #         radius=radius,
    #         assembly_name=assembly_name,
    #         model_nums=model_nums,
    #         encoding=encoding,
    #         copy_all_categories=copy_all_categories,
    #         data_source=data_source,
    #         transform=transform,
    #         download=download,
    #         filename=filename
    #     )

    # def get_surrounding_ligands(
    #         self,
    #         entry_id: str,
    #         label_entity_id: Optional[str] = None,
    #         label_asym_id: Optional[str] = None,
    #         auth_asym_id: Optional[str] = None,
    #         label_comp_id: Optional[str] = None,
    #         auth_comp_id: Optional[str] = None,
    #         label_seq_id: Optional[int] = None,
    #         auth_seq_id: Optional[int] = None,
    #         pdbx_PDB_ins_code: Optional[str] = None,
    #         label_atom_id: Optional[str] = None,
    #         auth_atom_id: Optional[str] = None,
    #         type_symbol: Optional[str] = None,
    #         omit_water: Optional[bool] = False,
    #         radius: Optional[float] = 5.0,
    #         assembly_name: Optional[str] = None,
    #         model_nums: Optional[str] = None,
    #         encoding: Optional[str] = "cif",
    #         copy_all_categories: Optional[bool] = False,
    #         data_source: Optional[str] = "",
    #         transform: Optional[str] = None,
    #         download: Optional[bool] = False,
    #         filename: Optional[str] = "",
    #         ):

    #     return self._exec(
    #         query_type="surrounding_ligands",
    #         entry_id=entry_id,
    #         label_entity_id=label_entity_id,
    #         label_asym_id=label_asym_id,
    #         auth_asym_id=auth_asym_id,
    #         label_comp_id=label_comp_id,
    #         auth_comp_id=auth_comp_id,
    #         label_seq_id=label_seq_id,
    #         auth_seq_id=auth_seq_id,
    #         pdbx_PDB_ins_code=pdbx_PDB_ins_code,
    #         label_atom_id=label_atom_id,
    #         auth_atom_id=auth_atom_id,
    #         type_symbol=type_symbol,
    #         omit_water=omit_water,
    #         assembly_name=assembly_name,
    #         model_nums=model_nums,
    #         encoding=encoding,
    #         copy_all_categories=copy_all_categories,
    #         data_source=data_source,
    #         transform=transform,
    #         download=download,
    #         filename=filename
    #     )

    # def get_symmetry_mates(
    #         self,
    #         entry_id: str,
    #         radius: Optional[float] = 5.0,
    #         model_nums: Optional[str] = None,
    #         encoding: Optional[str] = "cif",
    #         copy_all_categories: Optional[bool] = False,
    #         data_source: Optional[str] = "",
    #         transform: Optional[str] = None,
    #         download: Optional[bool] = False,
    #         filename: Optional[str] = "",
    #         ):

    #     return self._exec(
    #         query_type="symmetry_mates",
    #         entry_id=entry_id,
    #         radius=radius,
    #         model_nums=model_nums,
    #         encoding=encoding,
    #         copy_all_categories=copy_all_categories,
    #         data_source=data_source,
    #         transform=transform,
    #         download=download,
    #         filename=filename
    #     )

    # def get_assembly(
    #         self,
    #         entry_id: str,
    #         name: Optional[str] = "1",
    #         model_nums: Optional[str] = None,
    #         encoding: Optional[str] = "cif",
    #         copy_all_categories: Optional[bool] = False,
    #         data_source: Optional[str] = "",
    #         transform: Optional[str] = None,
    #         download: Optional[bool] = False,
    #         filename: Optional[str] = "",
    #         ):

    #     return self._exec(
    #         query_type="assembly",
    #         entry_id=entry_id,
    #         name=name,
    #         model_nums=model_nums,
    #         encoding=encoding,
    #         copy_all_categories=copy_all_categories,
    #         data_source=data_source,
    #         transform=transform,
    #         download=download,
    #         filename=filename
    #     )
