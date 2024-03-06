from dbmanager import DBManager


class AlignmentFreeGraph(DBManager):

    """
    Alignment-Free Sequence to Graph class

    This class extends the DBManager class with the aim implements the Alignment-Free Sequence to Graph logic.
    To do this, it work only with Direct Acyclic Graph (DAG) and it uses a k-mer based approach, where k is a parameter that can be set by the user.
    """

    def __init__(self, location: str = None, db_name: str = None, username: str = None,
                 password: str = None, configuration: [dict, str] = None, k: int = 3):  # type: ignore
        """
        Alignment-Free Sequence to Graph constructor

        This constructor initialize the Alignment-Free Sequence to Graph class with the given parameters.
        It also initialize the hashtable attribute, that is a dictionary that contains the k-mers of the graph.
        The keys of the dictionary are the nodes of the graph, while the values are the k-mers of the graph.
        The k-mers are represented as a dictionary, where the keys are the k-mers and the values are the colors of the k-mers.
        The colors of the k-mers are represented as a list of strings, where each string is the type of the edge that connect the k-mer to the next k-mer.

        :param location: The location of the database, default is None (trype: str)
        :param db_name: The name of the database, default is None (type: str)
        :param username: The username of the database, default is None (type: str)
        :param password: The password of the database, default is None (type: str)
        :param configuration: The configuration of the database, default is None (type: dict or str)
        :param k: The k parameter, default is 3 (type: int)

        :raises ValueError: If k is less than 1
        """

        super().__init__(location, db_name, username, password, configuration)
        if k < 1:
            raise ValueError("k must be greater than 1")
        self.k = k
        self.compute_hashtable()

    def connect(self, location: str = None, db_name: str = None,
                username: str = None, password: str = None, configuration: [dict, str] = None):  # type: ignore
        """
        Connect to the database

        This method connect to the database with the given parameters.
        It also check if the graph is acyclic, if it is not, it raise a ValueError.

        :return: True if the connection is successful
        """

        if super().connect(location, db_name, username, password, configuration):
            if self.is_acyclic():
                return True
            else:
                raise ValueError("Graph must be acyclic")

    def initialize_hashtable(self):
        """
        Initialize of the hash-table
        """

        res = self.get_all_nodes()
        ids = []
        for r in res:
            ids.append(int(r["n"].get("id")))
        ids.sort()
        self.hashtable = {ids[i]: {} for i in range(len(ids))}

    def compute_hashtable(self, k: int = None):
        """
        This method compute the hash-table of the graph.

        Every time that this method is called, the hash-table is re-initialize and re-computed.
        If the K parameter is valid and it is different from the current K parameter, the K attribute is update and the hash-table is re-computed with the new K parameter.

        :param k: The k parameter, default is None (type: int)

        :raises ValueError: If k is less than 1

        :return: The hash-table of the graph
        """

        self.initialize_hashtable()

        if k is not None:
            if k < 1:
                raise ValueError("k must be greater than 0")
            self.k = k

        query = "MATCH (a0)"

        for i in range(1, self.k):
            query += f"-[r{i}]->(a{i})"

        if self.k > 2:
            query += f"\nWHERE"
            for i in range(1, self.k-1):
                query += f" type(r{i})=type(r{i+1}) AND "
            query = query[:-5]

        query += f"\nRETURN toInteger(a0.id) as ID, "

        for i in range(self.k):
            query += f"a{i}.name + "
        query = query[:-3]

        query += " as KMers"

        if self.k > 1:
            query += ", type(r1) as Color"
            res = self.graph.run(query)
            for r in res:
                if r["KMers"] not in self.hashtable[r["ID"]]:
                    self.hashtable[r["ID"]][r["KMers"]] = []
                self.hashtable[r["ID"]][r["KMers"]].append(r["Color"])
        else:
            res = self.graph.run(query)
            for r in res:
                if r["KMers"] not in self.hashtable[r["ID"]]:
                    self.hashtable[r["ID"]][r["KMers"]] = []

        self.remove_duplicates()

        return self.hashtable

    def get_k(self):
        return self.k

    def get_hashtable(self):
        return self.hashtable

    def set_k(self, k: int):
        """
        This method set the K parameter of the graph.
        When the K parameter is set, the hash-table is re-computed.

        :param k: The k parameter (type: int)

        :raises ValueError: If k is None or if k is less than 1
        """
        if k is None:
            raise ValueError("k must be not None")
        if k < 1:
            raise ValueError("k must be greater than 1")
        self.k = k
        self.compute_hashtable()

    def sequence_from_hash(self, sequence: str = None, k: int = None):
        """
        This method compute the sequence from the hash-table of the graph.

        This function divide the sequence in k-mers and then it search the k-mers in the hash-table.

        :param sequence: The sequence to compute, default is None (type: str)
        :param k: The k parameter, default is None (type: int)

        :raises ValueError: If sequence is None

        :return: The vertex in the graph that represent the sequence if the sequence is in the graph (type: tuple)
        """

        if sequence is None:
            raise ValueError("sequence must be not None")
        if k is not None and k != self.k:
            self.compute_hashtable(k)

        sequence = sequence.upper()
        sequence = sequence.replace(" ", "")
        if len(sequence) < self.k:
            return ()

        chunks = [sequence[i:i+self.k]
                  for i in range(0, len(sequence), self.k) if len(sequence[i:i+self.k]) == self.k]
        save = {}

        for i, chuck in enumerate(chunks):
            for el in self.hashtable:
                for triple in self.hashtable[el]:
                    if chuck == triple:
                        if (i*self.k+(int(i == 0))) not in save:
                            save[i*self.k+(int(i == 0))] = el

        if len(save) < len(chunks):
            return ()

        res = set(self.hashtable[save[1]][chunks[0]])
        for i in range(1, len(chunks)):
            res = res.intersection(
                set(self.hashtable[save[i*self.k+(int(i == 0))]][chunks[i]]))

        if len(res) == 0:
            return tuple(save.values())
        else:
            return ()

    def sequence_from_graph(self, sequence: str = None, k: int = None):
        """
        This method compute the sequence from the graph.

        This function divide the sequence in k-mers and then it search the k-mers in the graph.

        :param sequence: The sequence to compute, default is None (type: str)
        :param k: The k parameter, default is None (type: int)

        :raises ValueError: If sequence is None

        :return: The vertex in the graph that represent the sequence if the sequence is in the graph (type: tuple)
        """

        if sequence is None:
            raise ValueError("sequence must be not None")
        if k is not None and k != self.k:
            self.compute_hashtable(k)

        sequence = sequence.upper()
        sequence = sequence.replace(" ", "")
        if len(sequence) < self.k:
            return ()

        chunks = [sequence[i:i+self.k]
                  for i in range(0, len(sequence), self.k) if len(sequence[i:i+self.k]) == self.k]
        save = {}

        for i, chuck in enumerate(chunks):
            query = f"MATCH (a0:base {{ name:\"{chuck[0]}\"}})"
            for j in range(1, self.k):
                query += f"-[r{j}]->(a{j}:base {{ name:\"{chuck[j]}\"}})"
            query += f"\nWHERE "
            for j in range(1, self.k-1):
                query += f"type(r{j})=type(r{j+1}) AND "
            query = query[:-5]
            query += f"\nRETURN toInteger(a0.id) as ID"

            res = self.graph.run(query)
            for r in res:
                if (i*self.k+(int(i == 0))) not in save:
                    save[i*self.k+(int(i == 0))] = r["ID"]

        return tuple(save.values())

    def upload_from_json(self, file_path: str, direction: int = 1):
        super().upload_from_json(file_path, direction)
        self.compute_hashtable()

    def upload_from_gfa(self, file_path: str):
        """
        This method uploads a graph from a GFA file.

        :param file_path: Path of the file

        :raises ValueError: If the file is not in the correct format
        """

        with open(file_path, 'r') as f:
            lines = f.readlines()

        for line in lines:
            parts = line.strip().split()

            if parts[0] == 'S':
                node = {
                    'id': parts[1],
                    'name': parts[2],
                    'label': 'base'
                }
                self.node_upload(node)

            elif parts[0] == 'L':
                relation = {
                    'from': {
                        'label': 'base',
                        'properties': {
                            'id': parts[1]
                        }
                    },
                    'to': {
                        'label': 'base',
                        'properties': {
                            'id': parts[3]
                        }
                    },
                    'label': parts[5].split(':')[2] if len(parts) > 5 else '',
                    'direction': 1 if parts[2] == '+' else -1
                }
                self.relation_dict_upload(relation)
        self.compute_hashtable()

    def delete_all(self):
        super().delete_all()
        self.compute_hashtable()

    def relation_upload(self, from_label: str, from_prop: dict, to_label: str, to_prop: dict, label: str = None, direction: int = 1):
        super().relation_upload(from_label, from_prop, to_label, to_prop, label, direction)
        if self.is_acyclic():
            self.compute_hashtable()
        else:
            super().reletion_remove(from_label, from_prop, to_label, to_prop, label, direction)

    def max_id(self):
        """
        This method return the maximum id of the graph

        :return: The maximum id of the graph (type: int)
        """
        query = "MATCH (n) RETURN max(toInteger(n.id)) as max"
        res = self.graph.run(query)
        for r in res:
            return r["max"]

    def remove_duplicates(self):
        """
        This method remove the duplicates k-mers from the hash-table
        """

        kmer_counts = {}
        # Count each k-mer
        for node in self.hashtable:
            for kmer in self.hashtable[node]:
                if kmer not in kmer_counts:
                    kmer_counts[kmer] = 1
                else:
                    kmer_counts[kmer] += 1

        remove_kmers = []
        # Find colors to remove
        for node in self.hashtable:
            for kmer in self.hashtable[node]:
                if kmer_counts[kmer] > 1:
                    remove_kmers.append((node, kmer))

        # Remove colors
        for el in remove_kmers:
            self.hashtable[el[0]].pop(el[1])
