# Quickstart
This is a quickstart guide to interacting with the RCSB PDB [ModelServer Coordinates API](https://models.rcsb.org/) using the *rcsb-api* Python package.

## Installation
Get it from PyPI:

    pip install rcsb-api

Or, download from [GitHub](https://github.com/rcsb/py-rcsb-api)

## Import
To import this module, use:
```python
from rcsbapi.model import ModelQuery
```

## Getting Started
The RCSB [ModelServer API](https://models.rcsb.org/) provides access to molecular structure data (e.g., atomic coordinates) and related information from PDB structures. The Model Server API allows you to extract out specific structural components of a given structure, such as the full structure coordinates or the coordinates of particular chains, ligands, or surrounding/interacting residues or ligands, and more.

The API supports queries for Experimental Structures. (Support for Computed Structure Models (CSMs) is not yet available.)

## Model API Query Construction

### Query Methods

The `ModelQuery` object supports the following types of queries/methods:

| Method                        | Description                                                                                                                                           |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.get_ligand()`               | Retrieve ligand coordinates from a given structure                                                                                                    |
| `.get_atoms()`                | Fetch the coordinates of any part of a given structure (e.g., a particular entity, chain, or ligand)                                                  |
| `.get_residue_interaction()`  | Retrieve the coordinates of all residues and ligands within a specified distance from a given residue or ligand (takes crystal symmetry into account) |
| `.get_residue_surroundings()` | Retrieve the coordinates of all residues and ligands within a specified distance from a given residue or ligand (ignores crystal symmetry)            |
| `.get_surrounding_ligands()`  | Retrieve the coordinates of all ligands within a specified distance from a given residue or ligand (taking crystal symmetry into account)             |
| `.get_assembly()`             | Extract the coordinates of a structural assembly (selected group of instances or “chains”) from an entry                                              |
| `.get_full_structure()`       | Fetch the full structure coordinates for a given entry                                                                                                |
| `.get_symmetry_mates()`       | Compute crystal symmetry mates for a given structure                                                                                                  |
| `.get_multiple_structures()`  | Fetch data for multiple structures                                                                                                                    |

### Query Arguments

The specific set of arguments available depend on the particular `ModelQuery` method being used above. However, in general, most methods will accept the following common arguments:

| Argument              | Description                                                           | Default                                       |
| --------------------- | --------------------------------------------------------------------- | --------------------------------------------- |
| `entry_id`            | Structure identifier (e.g., `"2HHB"`)                                 | —                                             |
| `encoding`            | Response encoding format. Supported values: `"cif"` and `"bcif"`      | `"cif"`                                       |
| `download`            | Whether to download the response to a file                            | `False`                                       |
| `filename`            | Output filename for downloaded data                                   | `None` (auto-generated from query parameters) |
| `file_directory`      | Directory where downloaded files will be saved                        | `None` (current working directory)            |
| `compress_gzip`       | Whether to gzip-compress the downloaded file                          | `False`                                       |
| `copy_all_categories` | Whether to include all metadata categories from the source entry file | `False`                                       |

Depending on the particular method being used and the level of granularity of the structure you want to fetch, one or more of the following can be specified:

| Argument          | Description                                                 | Default | Example                         |
| ----------------- | ----------------------------------------------------------- | ------- | ------------------------------- |
| `label_entity_id` | PDB-assigned entity ID for the structural component         | `None`  | `"1"` (as in entity `4HHB_1`)   |
| `label_asym_id`   | PDB-assigned asymmetric (chain) ID                          | `None`  | `"A"` (as in instance `4HHB.A`) |
| `auth_asym_id`    | Author-assigned asymmetric (chain) ID                       | `None`  | `"A"`                           |
| `label_comp_id`   | PDB-assigned chemical component or ligand ID                | `None`  | `"HEM"`                         |
| `auth_comp_id`    | Author-assigned chemical component or ligand ID             | `None`  | `"HEM"`                         |
| `label_seq_id`    | PDB-assigned sequence number of the residue of interest     | `None`  | `123` (as in residue `A123`)    |
| `auth_seq_id`     | Author-assigned sequence number of the residue of interest  | `None`  | `123`                           |


## Ligand Data

Use the `.get_ligand()` method to fetch ligand-related data (metadata and coordinates) within a given structure.

Note that by default this returns only the first instance of the specified ligand (e.g., if there are 10 `HEM` ligands in the structure, only the first one is returned). If you want a specific instance of the ligand, you can specify `label_asym_id` and/or `label_entity_id`. If you want *all* occurrences of a specific ligand, you should use the `.get_atoms()` [method below](#atoms-data).

```python
from rcsbapi.model import ModelQuery

# Fetch the first occurrence of the `HEM` ligand for entry "4HHB"
query = ModelQuery()
result = query.get_ligand(entry_id="4HHB", label_comp_id="HEM", download=True, filename="4HHB_HEM_ligand.cif", file_directory="model-output")
print(result)
```

| Argument              | Description                                                                |
| --------------------- | -------------------------------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")                                     |
| `label_entity_id`     | The entity label for the ligand                                            |
| `label_asym_id`       | The asymmetric ID for the ligand                                           |
| `auth_asym_id`        | The author asymmetric ID                                                   |
| `label_comp_id`       | The label for the component                                                |
| `auth_comp_id`        | The author component ID                                                    |
| `label_seq_id`        | The label sequence ID                                                      |
| `auth_seq_id`         | The author sequence ID                                                     |
| `pdbx_PDB_ins_code`   | The insertion code (optional)                                              |
| `label_atom_id`       | The label for the atom                                                     |
| `auth_atom_id`        | The author atom ID                                                         |
| `type_symbol`         | The chemical type symbol for the ligand (optional)                         |
| `model_nums`          | The model numbers to fetch (optional)                                      |
| `encoding`            | The encoding format for the response (`cif`, `sdf`, `mol`, `mol2`, `bcif`) |
| `copy_all_categories` | Whether to copy all categories (default: False)                            |
| `data_source`         | Allows to control how the provided data source ID maps to input file (as specified by the server instance config)  (default: None)                     |
| `transform`           | Apply any transformations (optional)                                       |
| `download`            | Whether to download the file (True/False)                                  |
| `filename`            | The name of the file to save                                               |
| `file_directory`      | Directory to save the file                                                 |
| `compress_gzip`       | Whether to compress the file (default: False)                              |

## Atoms Data

Use the `.get_atoms()` method to fetch atom-level data (coordinates and metadata) from a given structure. This can be used to fetch all `atom_site` data for a particular component using `label_comp_id` (e.g., all `HEM` ligands, all water molecules `HOH`, or all `CYS` residues), a given entity, a specific residue in the sequence, and/or a combination of these criteria.

```python
from rcsbapi.model import ModelQuery

# Fetch the metadata and `atom_site` coordinates of ALL occurrence of `HEM` in entry "4HHB"
query = ModelQuery()
result = query.get_atoms(entry_id="4HHB", label_comp_id="HEM", download=True, filename="4HHB_HEM_atoms.cif", file_directory="model-output")
print(result)
```

| Argument              | Description                                          |
| --------------------- | ---------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")               |
| `label_entity_id`     | The entity label for the atom                        |
| `label_asym_id`       | The asymmetric ID for the atom                       |
| `auth_asym_id`        | The author asymmetric ID                             |
| `label_comp_id`       | The label for the component                          |
| `auth_comp_id`        | The author component ID                              |
| `label_seq_id`        | The label sequence ID                                |
| `auth_seq_id`         | The author sequence ID                               |
| `pdbx_PDB_ins_code`   | The insertion code (optional)                        |
| `label_atom_id`       | The label for the atom                               |
| `auth_atom_id`        | The author atom ID                                   |
| `type_symbol`         | The chemical type symbol for the atom                |
| `model_nums`          | The model numbers to fetch (optional)                |
| `encoding`            | The encoding format for the response (`cif`, `bcif`) |
| `copy_all_categories` | Whether to copy all categories (default: False)      |
| `data_source`         | Allows to control how the provided data source ID maps to input file (as specified by the server instance config)  (default: None)                     |
| `transform`           | Apply any transformations (optional)                 |
| `download`            | Whether to download the file (True/False)            |
| `filename`            | The name of the file to save                         |
| `file_directory`      | Directory to save the file                           |
| `compress_gzip`       | Whether to compress the file (default: False)        |


## Residue Interaction

Use the `.get_residue_interaction()` method to fetch data (metadata and coordinates) on the surrounding residues and ligands of a given ligand or residue. If you only provide the `label_comp_id`, the server will return the interaction data for *all* occurrences of the component. This method takes crystal symmetry into account (returned data includes `_molstar_atom_site_operator_mapping`).

```python
from rcsbapi.model import ModelQuery

# Fetch surrounding residues for ALL `HEM` ligands in entry "4HHB"
query = ModelQuery()
result = query.get_residue_interaction(entry_id="4HHB", label_comp_id="HEM", radius=5.0, download=True, file_directory="model-output")
print(result)

# Fetch surrounding residues for `HEM` chain `E` in entry "4HHB"
query = ModelQuery()
result = query.get_residue_interaction(
    entry_id="4HHB",
    label_comp_id="HEM",
    label_asym_id="E",
    radius=5.0,
    download=True,
    filename="4HHB_HEM_E_residue_interaction.cif",
    file_directory="model-output"
)
print(result)
```

| Argument              | Description                                                   |
| --------------------- | ------------------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")                        |
| `label_entity_id`     | The entity label for the residue interaction                  |
| `label_asym_id`       | The asymmetric ID for the residue interaction                 |
| `auth_asym_id`        | The author asymmetric ID                                      |
| `label_comp_id`       | The label for the component                                   |
| `auth_comp_id`        | The author component ID                                       |
| `label_seq_id`        | The label sequence ID                                         |
| `auth_seq_id`         | The author sequence ID                                        |
| `pdbx_PDB_ins_code`   | The insertion code (optional)                                 |
| `label_atom_id`       | The label for the atom                                        |
| `auth_atom_id`        | The author atom ID                                            |
| `type_symbol`         | The chemical type symbol for the residue                      |
| `radius`              | The interaction radius for residue interaction (default: 5.0) |
| `assembly_name`       | The assembly name (optional)                                  |
| `model_nums`          | The model numbers to fetch (optional)                         |
| `encoding`            | The encoding format for the response (`cif`, `bcif`)          |
| `copy_all_categories` | Whether to copy all categories (default: False)               |
| `data_source`         | Allows to control how the provided data source ID maps to input file (as specified by the server instance config)  (default: None)                     |
| `transform`           | Apply any transformations (optional)                          |
| `download`            | Whether to download the file (True/False)                     |
| `filename`            | The name of the file to save                                  |
| `file_directory`      | Directory to save the file                                    |
| `compress_gzip`       | Whether to compress the file (default: False)                 |


## Residue Surroundings

Use the `.get_residue_surroundings()` method to fetch data (metadata and coordinates) on the surrounding residues and ligands of a given ligand or residue. If you only provide the `label_comp_id`, the server will return the interaction data for *all* occurrences of the component. Similar to [Residue Interaction](#residue-interaction), but doesn't take crystal symmetry into account (returned data does *not* include `_molstar_atom_site_operator_mapping`).

```python
from rcsbapi.model import ModelQuery

# Fetch surrounding residues for `HEM` chain `E` in entry "4HHB"
query = ModelQuery()
result = query.get_residue_surroundings(
    entry_id="4HHB",
    label_comp_id="HEM",
    label_asym_id="E",
    radius=5.0,
    download=True,
    filename="4HHB_HEM_E_residue_surroundings.cif",
    file_directory="model-output"
)
print(result)
```

| Argument              | Description                                                    |
| --------------------- | -------------------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")                         |
| `label_entity_id`     | The entity label for the residue                               |
| `label_asym_id`       | The asymmetric ID for the residue                              |
| `auth_asym_id`        | The author asymmetric ID                                       |
| `label_comp_id`       | The label for the component                                    |
| `auth_comp_id`        | The author component ID                                        |
| `label_seq_id`        | The label sequence ID                                          |
| `auth_seq_id`         | The author sequence ID                                         |
| `pdbx_PDB_ins_code`   | The insertion code (optional)                                  |
| `label_atom_id`       | The label for the atom                                         |
| `auth_atom_id`        | The author atom ID                                             |
| `type_symbol`         | The chemical type symbol for the residue                       |
| `radius`              | The interaction radius for residue surroundings (default: 5.0) |
| `assembly_name`       | The assembly name (optional)                                   |
| `model_nums`          | The model numbers to fetch (optional)                          |
| `encoding`            | The encoding format for the response (`cif`, `bcif`)           |
| `copy_all_categories` | Whether to copy all categories (default: False)                |
| `data_source`         | Allows to control how the provided data source ID maps to input file (as specified by the server instance config)  (default: None)                     |
| `transform`           | Apply any transformations (optional)                           |
| `download`            | Whether to download the file (True/False)                      |
| `filename`            | The name of the file to save                                   |
| `file_directory`      | Directory to save the file                                     |
| `compress_gzip`       | Whether to compress the file (default: False)                  |


## Surrounding Ligands

Use the `.get_surrounding_ligands()` method to fetch data on ligands that are within a certain proximity of a residue in a structure. This method takes crystal symmetry into account (returned data includes `_molstar_atom_site_operator_mapping`).

```python
from rcsbapi.model import ModelQuery

# Fetch surrounding ligands for `ALA 284` in entry "1TQN"
query = ModelQuery()
result = query.get_surrounding_ligands(
    entry_id="1TQN",
    label_comp_id="ALA",
    label_seq_id=284,
    radius=5.0,
    download=True,
    file_directory="model-output"
)
print(result)
```

| Argument              | Description                                                                      |
| --------------------- | -------------------------------------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")                                           |
| `label_entity_id`     | The entity label for the ligand                                                  |
| `label_asym_id`       | The asymmetric ID for the ligand                                                 |
| `auth_asym_id`        | The author asymmetric ID                                                         |
| `label_comp_id`       | The label for the ligand component                                               |
| `auth_comp_id`        | The author component ID                                                          |
| `label_seq_id`        | The label sequence ID for the ligand                                             |
| `auth_seq_id`         | The author sequence ID for the ligand                                            |
| `pdbx_PDB_ins_code`   | The insertion code (optional)                                                    |
| `label_atom_id`       | The label for the ligand atom                                                    |
| `auth_atom_id`        | The author atom ID for the ligand                                                |
| `type_symbol`         | The chemical type symbol for the ligand                                          |
| `omit_water`          | Whether to exclude water molecules from the surrounding ligands (default: `False`). (*Note: this does not appear to be functional on the ModelServer API yet*) |
| `radius`              | The interaction radius for surrounding ligands (default: 5.0)                    |
| `assembly_name`       | The assembly name (optional)                                                     |
| `model_nums`          | The model numbers to fetch (optional)                                            |
| `encoding`            | The encoding format for the response (`cif`, `bcif`)                             |
| `copy_all_categories` | Whether to copy all categories (default: `False`)                                  |
| `data_source`         | Allows to control how the provided data source ID maps to input file (as specified by the server instance config)  (default: None)                     |
| `transform`           | Apply any transformations (optional)                                             |
| `download`            | Whether to download the file (True/False)                                        |
| `filename`            | The name of the file to save                                                     |
| `file_directory`      | Directory to save the file                                                       |
| `compress_gzip`       | Whether to compress the file (default: `False`)                                    |


## Assembly Data

Use the `.get_assembly()` method to extract a structural assembly (select group of instances or "chains") from an entry.

```python
from rcsbapi.model import ModelQuery

# Fetch assembly "3" for the entry "13PK"
query = ModelQuery()
result = query.get_assembly(entry_id="13PK", name="3", download=True, file_directory="model-output")
print(result)
```

| Argument              | Description                                          |
| --------------------- | ---------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")               |
| `name`                | The assembly id (default: "1")                       |
| `model_nums`          | The model numbers to fetch (optional)                |
| `encoding`            | The encoding format for the response (`cif`, `bcif`) |
| `copy_all_categories` | Whether to copy all categories (default: False)      |
| `data_source`         | Allows to control how the provided data source ID maps to input file (as specified by the server instance config)  (default: None)                     |
| `transform`           | Apply any transformations (optional)                 |
| `download`            | Whether to download the file (True/False)            |
| `filename`            | The name of the file to save                         |
| `file_directory`      | Directory to save the file                           |
| `compress_gzip`       | Whether to compress the file (default: False)        |


## Full Structure

Use the `.get_full_structure()` method to fetch complete structural data for a given entry.

```python
from rcsbapi.model import ModelQuery

# Fetch the full structure for the entry "2HHB" and store content in `result` variable
query = ModelQuery()
result = query.get_full_structure(entry_id="2HHB")
print(result[:500])

# Or, download the structure:
result = query.get_full_structure(
    entry_id="2HHB",
    encoding="cif",
    download=True,
    file_directory="model-output"
)
print(result)
```

| Argument              | Description                                                |
| --------------------- | ---------------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")                     |
| `model_nums`          | The model numbers to fetch (optional). If set, only include atoms with the corresponding `_atom_site.pdbx_PDB_model_num` field.                    |
| `encoding`            | The encoding format for the response (`cif` (default), `bcif`) |
| `copy_all_categories` | Whether to copy all categories (default: False)            |
| `transform`           | Apply any transformations (optional)                       |
| `download`            | Whether to download the file (True/False)                  |
| `filename`            | The name of the file to save                               |
| `file_directory`      | Directory to save the file                                 |
| `compress_gzip`       | Whether to compress the file (default: False)              |
| `data_source`         | Allows to control how the provided data source ID maps to input file (as specified by the server instance config)  (default: None)                     |


## Symmetry Mates

Use the `.get_symmetry_mates()` method to compute crystal symmetry mates within a specified radius.

```python
from rcsbapi.model import ModelQuery

# Generate the symmetry mates (unit cell replications) for the entry "1TQN"
query = ModelQuery()
result = query.get_symmetry_mates(entry_id="1TQN", download=True, file_directory="model-output")
print(result)
```

| Argument              | Description                                              |
| --------------------- | -------------------------------------------------------- |
| `entry_id`            | The ID of the structure (e.g., "2HHB")                   |
| `radius`              | The interaction radius for symmetry mates (default: 5.0) |
| `model_nums`          | The model numbers to fetch (optional)                    |
| `encoding`            | The encoding format for the response (`cif`, `bcif`)     |
| `copy_all_categories` | Whether to copy all categories (default: False)          |
| `data_source`         | Allows to control how the provided data source ID maps to input file (as specified by the server instance config)  (default: None)                     |
| `transform`           | Apply any transformations (optional)                     |
| `download`            | Whether to download the file (True/False)                |
| `filename`            | The name of the file to save                             |
| `file_directory`      | Directory to save the file                               |
| `compress_gzip`       | Whether to compress the file (default: False)            |


## Working with Multiple Structures

Let's say you want to download or fetch data for several structures at once. You can do so by providing a list to the `.get_multiple_structures()` method:

```python

# List of structure IDs to query
entry_ids = ["1CBS", "4HHB"]

# Fetch multiple structures (e.g., "full" type) and save the result
results = query.get_multiple_structures(
    entry_ids,
    query_type="full",
    encoding="cif",
    download=True,
    compress_gzip=True,
    file_directory="model-output"
)

print(results)
```

The `.get_multiple_structures()` method is ammenable to any of the available types of queries via the `query_type` argument:

| Query type method             | Corresponding `query_type` value     |
|-------------------------------|--------------------------------------|
| `.get_full_structure()`       | `full`                               |
| `.get_ligand()`               | `ligand`                             |
| `.get_atoms()`                | `atoms`                              |
| `.get_residue_interaction()`  | `residue_interaction`                |
| `.get_residue_surroundings()` | `residue_surroundings`               |
| `.get_surrounding_ligands()`  | `surrounding_ligands`                |
| `.get_symmetry_mates()`       | `symmetry_mates`                     |
| `.get_assembly()`             | `assembly`                           |


## ModelQuery Defaults 

The `ModelQuery` class supports defining **default values** for common parameters at instantiation. These include:

* `encoding`
* `file_directory`
* `download`
* `compress_gzip`

These default values will be automatically applied to all subsequent method calls (e.g., `.get_full_structure()`, `.get_ligand()`, etc.) unless you explicitly override them.

```python
from rcsbapi.model import ModelQuery

# Set defaults during instantiation
query = ModelQuery(
    encoding="cif",
    file_directory="model-output",
    download=True,
    compress_gzip=False
)

# Now run a query without repeating those arguments
result = query.get_full_structure(
    entry_id="2HHB",
    filename="2HHB_full_structure.cif"
)
print(result)
```