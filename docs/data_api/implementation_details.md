# Implementation Details
### Parsing Schema
Upon initialization of the package, the GraphQL schema is fetched from the GraphQL Data API endpoint. After fetching the schema, the Python package parses the schema and creates a graph object to represent it within the package. This graph representation of how fields and types connect is key to how queries are automatically constructed using a path finding algorithm. The graph is constructed as a directed graph in [rustworkx](https://www.rustworkx.org/), so `rustworkx` must be able to be installed on your machine to use this. If you experience installation or usage issues, please create an issue on [GitHub](https://github.com/rcsb/py-rcsb-api/issues) and we will consider implementing alternative support.

### Constructing queries
Queries are constructed by finding every [simple path](https://en.wikipedia.org/wiki/Simple_path#:~:text=Simple%20path%20(graph%20theory)%2C,does%20not%20have%20repeating%20vertices) from the `input_type` to each final requested field in `return_data_list`. The simple paths are searched for path(s) matching the given path in `return_data_list`. The given path must be sufficiently specific to allow for only one possible path. If there are multiple possible paths, a [ValueError](query_construction.md#valueerror-not-a-unique-field) is raised.

### Error Handling
In GraphQL, all requests return HTTP status code 200 and instead, errors appear in the returned JSON. The package will parse these errors, throwing a `ValueError` and displaying the corresponding error message or messages. To access the full query and return JSON in an interactive editor, you can use the `get_editor_link()` method on the DataQuery object. (see [Helpful Methods](query_construction.md#get_editor_link))
