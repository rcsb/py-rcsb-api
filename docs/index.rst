rcsb-api - Query RCSB PDB data from Python
===============================================

The ``rcsb-api`` package provides a Python interface to 
`RCSB PDB API services <https://www.rcsb.org/docs/programmatic-access/web-apis-overview>`_. 
Use it to search and fetch macromolecular structure data from RCSB PDB `at RCSB.org <https://www.rcsb.org/>`_.

Availability
------------

Install it from PyPI via ``pip`` or ``uv``:

.. code-block:: bash

   pip install rcsb-api

   # or, if using uv:
   uv pip install rcsb-api

Or, download from `GitHub <https://github.com/rcsb/py-rcsb-api>`_


Contents
--------

.. toctree::
   :caption: Search API
   :maxdepth: 2

   search_api/quickstart.md
   search_api/query_construction.md
   search_api/attributes.md
   search_api/additional_examples.md
   search_api/api.rst

.. toctree::
   :caption: Data API
   :maxdepth: 2

   data_api/quickstart.md
   data_api/query_construction.md
   data_api/implementation_details.md
   data_api/custom_configuration.md
   data_api/additional_examples.md
   data_api/api.rst

.. toctree::
   :caption: Sequence Coordinates API
   :maxdepth: 2

   seq_api/quickstart.md
   seq_api/additional_examples.md
   seq_api/api.rst

.. toctree::
   :caption: Model Server API
   :maxdepth: 2

   model_api/quickstart.md
   model_api/api.rst

License
-------

Code is licensed under the MIT license. See the 
`LICENSE <https://github.com/rcsb/py-rcsb-api/blob/master/LICENSE>`_ for details.


Citing
------

Please cite the ``rcsb-api`` package with the following reference:

  Dennis W. Piehl, Brinda Vallat, Ivana Truong, Habiba Morsy, Rusham Bhatt, Santiago Blaumann, Pratyoy Biswas, Yana Rose, Sebastian Bittrich, Jose M. Duarte, Joan Segura, Chunxiao Bi, Douglas Myers-Turnbull, Brian P. Hudson, Christine Zardecki, Stephen K. Burley. rcsb-api: Python Toolkit for Streamlining Access to RCSB Protein Data Bank APIs, Journal of Molecular Biology, 2025. DOI: https://doi.org/10.1016/j.jmb.2025.168970

You should also cite the RCSB.org API services this package utilizes:

  Yana Rose, Jose M. Duarte, Robert Lowe, Joan Segura, Chunxiao Bi, Charmi Bhikadiya, Li Chen, Alexander S. Rose, Sebastian Bittrich, Stephen K. Burley, John D. Westbrook. RCSB Protein Data Bank: Architectural Advances Towards Integrated Searching and Efficient Access to Macromolecular Structure Data from the PDB Archive, Journal of Molecular Biology, 2020. DOI: https://doi.org/10.1016/j.jmb.2020.11.003


Support
------

If you experience any issues installing or using the package, please submit an issue on 
`GitHub <https://github.com/rcsb/py-rcsb-api/issues>`_ and we will try to respond in a timely manner.
