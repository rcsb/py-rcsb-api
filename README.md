[![PyPi Release](https://img.shields.io/pypi/v/rcsb-api.svg)](https://pypi.org/project/rcsb-api/)
[![Build Status](https://dev.azure.com/rcsb/RCSB%20PDB%20Python%20Projects/_apis/build/status/rcsb.py-rcsb-api?branchName=master)](https://dev.azure.com/rcsb/RCSB%20PDB%20Python%20Projects/_build/latest?definitionId=40&branchName=master)
[![Documentation Status](https://readthedocs.org/projects/rcsbapi/badge/?version=latest)](https://rcsbapi.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14052470.svg)](https://doi.org/10.5281/zenodo.14052470)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/10424/badge)](https://www.bestpractices.dev/projects/10424)
[![FAIR checklist badge](https://fairsoftwarechecklist.net/badge.svg)](https://fairsoftwarechecklist.net/v0.2?f=31&a=30112&i=32111&r=133)
[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F-green)](https://fair-software.eu)


# <img src="https://github.com/user-attachments/assets/248d3e32-7644-46b2-bf18-b5248c9e6305" height="160"/><br>*rcsb-api*: Python Toolkit for Accessing RCSB.org APIs
Python interface for RCSB Protein Data Bank API services at [RCSB.org](https://www.rcsb.org/).

## Installation
This package requires Python 3.9 or later.

Install it from PyPI via `pip` or `uv`:

    pip install rcsb-api
    
    # or, if using uv:
    uv pip install rcsb-api

Or, download from [GitHub](https://github.com/rcsb/py-rcsb-api/) and install locally:

    git clone https://github.com/rcsb/py-rcsb-api.git
    cd py-rcsb-api
    pip install .

## Overview
The [_rcsb-api_](https://rcsbapi.readthedocs.io/en/latest/index.html) package provides a simple Pythonic interface to the suite of [RCSB PDB APIs](https://www.rcsb.org/docs/programmatic-access/web-apis-overview) for querying and fetching data in the PDB. Specifically, each API service is provided as a separate "module" (or sub-package) within the Python client, and offers the following set of key functionalities:

- [Search API module](https://rcsbapi.readthedocs.io/en/latest/search_api/quickstart.html) (`rcsbapi.search`):
  - Perform all search types available through the RCSB.org Advanced Search builder (e.g., full-text, attribute-based, sequence and structure similarity, sequence and structure motif)
  - Use simple Boolean logic to intuitively construct complex or nested queries
  - Upload custom structure files for structure similarity searches
  - Include computed structure models (CSMs) in search results

- [Data API module](https://rcsbapi.readthedocs.io/en/latest/data_api/quickstart.html) (`rcsbapi.data`):
  - Retrieve any subset of metadata, features, and/or annotations for a given list of PDB IDs (e.g., experimental method details, structural annotations, binding sites, etc.)
  - Easily fetch data for all structures across the archive
  - Simplified GraphQL query construction using a Python syntax

- [Sequence Coordinate API module](https://rcsbapi.readthedocs.io/en/latest/seq_api/quickstart.html) (`rcsbapi.sequence`):
  - Query alignments between structural and sequence databases as well as protein positional annotations/features integrated from multiple resources
  - Alignment data is available for NCBI RefSeq (including protein and genomic sequences), UniProt and PDB sequences
  - Protein positional features are integrated from UniProt, CATH, SCOPe and RCSB PDB and collected from the RCSB PDB Data Warehouse

- [Model API module](https://rcsbapi.readthedocs.io/en/latest/model_api/quickstart.html) (`rcsbapi.model`):
  - Provides access to molecular structure data (e.g., atomic coordinates) and related information (in mmCIF or BCIF formats)
  - Query for various structural data types, such as full structure, ligands, atoms, residue interactions, and more
  - Valuable for extracting out specific slices of a structure data file (not for bulk downloads, in which case see our [download services](https://www.rcsb.org/docs/programmatic-access/file-download-services))

Full package documentation is available at [readthedocs](https://rcsbapi.readthedocs.io/en/latest/).

### Training Materials

- Example usage for each module is available at [readthedocs](https://rcsbapi.readthedocs.io/en/latest/).
- Several Jupyter notebooks with example use cases and workflows for all supported API services are provided under [notebooks](notebooks/), which can be opened in Google Colab via the "Open in Colab" badge at the top of each notebook.
- Watch our webinar, [Streamlining Access to RCSB PDB APIs with Python](https://pdb101.rcsb.org/train/training-events/apis-python), which provides an introduction to our Search and Data APIs along with hands-on tutorials.

## Citing
Please cite the ``rcsb-api`` package with the following reference:

> Dennis W. Piehl, Brinda Vallat, Ivana Truong, Habiba Morsy, Rusham Bhatt, 
> Santiago Blaumann, Pratyoy Biswas, Yana Rose, Sebastian Bittrich, Jose M. Duarte,
> Joan Segura, Chunxiao Bi, Douglas Myers-Turnbull, Brian P. Hudson, Christine Zardecki,
> Stephen K. Burley. rcsb-api: Python Toolkit for Streamlining Access to RCSB Protein 
> Data Bank APIs, Journal of Molecular Biology, 2025.
> DOI: [10.1016/j.jmb.2025.168970](https://doi.org/10.1016/j.jmb.2025.168970)

You should also cite the RCSB.org API services this package utilizes:

> Yana Rose, Jose M. Duarte, Robert Lowe, Joan Segura, Chunxiao Bi, Charmi
> Bhikadiya, Li Chen, Alexander S. Rose, Sebastian Bittrich, Stephen K. Burley,
> John D. Westbrook. RCSB Protein Data Bank: Architectural Advances Towards
> Integrated Searching and Efficient Access to Macromolecular Structure Data
> from the PDB Archive, Journal of Molecular Biology, 2020.
> DOI: [10.1016/j.jmb.2020.11.003](https://doi.org/10.1016/j.jmb.2020.11.003)


## Documentation and Support
Please refer to the [readthedocs page](https://rcsbapi.readthedocs.io/en/latest/index.html) to learn more about package usage and other available features as well as to see more examples.

If you experience any issues installing or using the package, please submit an issue on [GitHub](https://github.com/rcsb/py-rcsb-api/issues) and we will try to respond in a timely manner.
