rcsb-api - Query RCSB PDB data from Python
===============================================

The ``rcsb-api`` package provides a Python interface to 
`RCSB PDB API services <https://www.rcsb.org/docs/programmatic-access/web-services-overview>`_. 
Use it to search and fetch macromolecular structure data from RCSB PDB (at RCSB.org).

Availability
------------

Get it from PyPI:

.. code-block:: bash

   pip install rcsb-api

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
   data_api/additional_examples.md
   data_api/api.rst


License
-------

Code is licensed under the MIT license. See the 
`LICENSE <https://github.com/rcsb/py-rcsb-api/blob/master/LICENSE>`_ for details.


Citing
------

Please cite the ``rcsb-api`` package by URL:

  https://rcsbapi.readthedocs.io

You should also cite the RCSB.org API services this package utilizes:

  Yana Rose, Jose M. Duarte, Robert Lowe, Joan Segura, Chunxiao Bi, Charmi Bhikadiya, Li Chen, Alexander S. Rose, Sebastian Bittrich, Stephen K. Burley, John D. Westbrook. RCSB Protein Data Bank: Architectural Advances Towards Integrated Searching and Efficient Access to Macromolecular Structure Data from the PDB Archive, Journal of Molecular Biology, 2020. DOI: 10.1016/j.jmb.2020.11.003
