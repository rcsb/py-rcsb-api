# Implementation Details
### Parsing Schema
Upon initialization of the package, the GraphQL schema is fetched from the RCSB PDB website. After fetching the file, the Python package parses the schema and creates a graph object to represent it within the package. This graph representation of how fields and types connect is key to how queries are automatically constructed using a shortest path algoritm. By default the graph is constructed as a directed graph in [rustworkx](https://www.rustworkx.org/), but if an `ImportError` is encountered, a [NetworkX](https://networkx.org/) directed graph is created instead.

### Constructing queries
Queries are constructed by finding the shortest path from an `input_type` to each item in the `return_data_list`. The name of each field in the path is found and used to construct a GraphQL query. Currently, constructing queries is not implemented using Networkx and only rustworkx is supported.

### Error Handling
In GraphQL, all requests return HTTP status code 200 and instead errors appear in the JSON that is returned. The package will parse these errors, throwing a ValueError and displaying the corresponding error message or messages. To access the full query and return JSON in an interactive editor, you can use the `get_editor_link()` method on the Query object. (see [Helpful Methods](query_construction.html#get-editor-link()))