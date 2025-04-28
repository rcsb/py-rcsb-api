#  File Download Module

This module facilitates downloads from [files.wwpdb.org](https://files.wwpdb.org/).

Currently supports these file types:
- mmCIF
- bCIF (binary CIF)
- PDB
- PDBML (XML)
- FASTA

But many more file types are available. Available types from files.wwpdb.org summarized here: [File Download Services page](https://www.rcsb.org/docs/programmatic-access/file-download-services#pdb-entry-files).
More configured files are available through the [ModelServer API](https://models.rcsb.org/#/General/ligand-post).

## Quickstart
To import this sub-package:
```python
from rcsbapi.files import download
```

Then, you can specify IDs and which file formats to download for each ID.
```python
from rcsbapi.files import download

download(
    # You can specify multiple IDs
    pdb_ids=["4HHB"],
    # Valid strings are "mmCIF", "bCIF", "PDB", "PDBML", "FASTA"
    file_type_list=["mmCIF"],
    # Specify where to download the file using `download_dir`
    download_dir=".",
)
```
