from dbmanager import DBManager


class AlignmenmtFreeGraph(DBManager):
    def __init__(self, location: str = None, db_name: str = None, username: str = None,
                 password: str = None, configuration: [dict, str] = None, k: int = 3):
        super().__init__(location, db_name, username, password, configuration)
        if k < 1:
            raise ValueError("k must be greater than 1")
        self.k = k
        self.compute_hashtable()

    def connect(self, location: str = None, db_name: str = None, username: str = None, password: str = None, configuration: [dict, str] = None):
        if super().connect(location, db_name, username, password, configuration):
            if self.is_acyclic():
                return True
            else:
                raise ValueError("Graph must be acyclic")

    def initialize_hashtable(self):
        res = self.get_all_nodes()
        ids = []
        for r in res:
            ids.append(int(r["n"].get("id")))
        ids.sort()
        self.hashtable = {ids[i]: {} for i in range(len(ids))}

    def compute_hashtable(self, k: int = None):
        self.initialize_hashtable()

        if k is not None:
            if k < 1:
                raise ValueError("k must be greater than 1")
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
        if self.k > 2:
            query += ", type(r1) as Color"
        else:
            query += ", \"\" as Color"

        res = self.graph.run(query)

        for r in res:
            if r["KMers"] not in self.hashtable[r["ID"]]:
                self.hashtable[r["ID"]][r["KMers"]] = []
            self.hashtable[r["ID"]][r["KMers"]].append(r["Color"])

        return self.hashtable

    def sequence_from_hash(self, sequence: str = None, k: int = None):
        if sequence is None:
            raise ValueError("sequence must be not None")
        if k is not None and k != self.k:
            self.compute_hashtable(k)
        if len(sequence) < self.k:
            return None

        chunks = [sequence[i:i+self.k]
                  for i in range(0, len(sequence), self.k) if len(sequence[i:i+self.k]) == self.k]
        save = {}
        for i, chuck in enumerate(chunks):
            for el in self.hashtable:
                for triple in self.hashtable[el]:
                    if chuck == triple:
                        if (i*self.k+(int(i == 0))) not in save:
                            save[i*self.k+(int(i == 0))] = el
        return tuple(save.values())
