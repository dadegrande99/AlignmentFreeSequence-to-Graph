# Alignment-Free Sequence to Graph

This project, named "Alignment-Free Sequence to Graph", is a Python-based application that focuses on converting alignment-free sequences into a graph representation. The primary use case of this project is in the field of bioinformatics, where sequences of DNA, RNA, or proteins are often represented as graphs for further analysis.

The project utilizes the Neo4j graph database for storing and managing the graph data. Neo4j is a highly scalable, native graph database that excels at managing and querying highly connected data. It is a popular choice for projects that require efficient handling of complex relationships between data points.
This project is about creating an alignment-free

## Table of Contents

- [Alignment-Free Sequence to Graph](#alignment-free-sequence-to-graph)
  - [Table of Contents](#table-of-contents)
  - [Feature](#feature)
    - [Graph Database Manager](#graph-database-manager)
    - [Alignment-Free Sequence](#alignment-free-sequence)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Contributors](#contributors)
  - [License](#license)

## Feature

The project is structured around two main classes: `DBManager` and `AlignmentFreeGraph`.

### Graph Database Manager

The `DBManager` class is responsible for managing the connection and queries to the Neo4j database. It provides methods for connecting to the database, checking the connection, uploading data from a JSON file, executing queries, and more. This class is essential for the interaction between the Python application and the Neo4j database.

### Alignment-Free Sequence

The `AlignmentFreeGraph` class extends the `DBManager` class and implements the logic for converting an alignment-free sequence to a graph. It works with Direct Acyclic Graphs (DAGs) and uses a k-mer based approach, where k is a parameter that can be set by the user. This class is the core of the project, where the conversion of sequences to graph representations happens.

## Installation

To install the project, clone the repository and install the required Python packages.

```bash
git clone https://github.com/dadegrande99/alignment-free-sequence-to-graph.git
cd alignment-free-sequence-to-graph
pip install -r requirements.txt
```

## Usage

To use the project, you create an instance of the `DBManager` class with the necessary parameters for connecting to your Neo4j database.

```python
from dbmanager import DBManager

db_manager = DBManager(location='your_database_location', db_name='your_database_name', username='your_username', password='your_password')

# otherwise
db_manager = DBManager(configuration='your_secret_credentials.json')
```

or, you can utilize the functionalities of Alignment-Free Sequence to Graph with an instance of the `AlignmentFreeGraph` class in this way 

```python
from dbmanager import DBManager
from alignmentfreegraph import AlignmentFreeGraph

alignment_free_graph = AlignmentFreeGraph(location='your_database_location', db_name='your_database_name', username='your_username', password='your_password', k=3)

# otherwise
alignment_free_graph = AlignmentFreeGraph(configuration='your_secret_credentials.json', k=3)
```

## Contributors

- [Davide Grandesso](mailto:d.grandesso@campus.unimib.it)

## License

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.
