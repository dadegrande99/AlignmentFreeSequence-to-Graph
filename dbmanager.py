import json
import networkx as nx
import matplotlib.pyplot as plt
from py2neo import Graph


class DBManager:

    def __init__(self, location: str = None, db_name: str = None, username: str = None, password: str = None, configuration: [dict, str] = None):
        self.set_values(location, db_name, username, password, configuration)

        if self.location is None:
            raise ValueError("Location not specified")
        if self.username is None:
            raise ValueError("Username not specified")
        if self.password is None:
            raise ValueError("Password not specified")

        self.graph = None
        self.connect()

    def set_values(self, location: str = None, db_name: str = None, username: str = None, password: str = None, configuration: [dict, str] = None):
        if configuration is not None:
            if isinstance(configuration, dict):
                self.location = configuration["uri"]
                self.db_name = configuration["db_name"]
                self.username = configuration["user"]
                self.password = configuration["password"]
            elif isinstance(configuration, str):
                with open(configuration) as f:
                    data = json.load(f)
                if "neo4j" in data:
                    data = data["neo4j"]
                if "uri" in data:
                    self.location = data["uri"]
                if "db_name" in data:
                    self.db_name = data["db_name"]
                if "user" in data:
                    self.username = data["user"]
                if "password" in data:
                    self.password = data["password"]

        if location is not None:
            self.location = location
        if db_name is not None:
            self.db_name = db_name
        else:
            self.db_name = ""
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password

    def connect(self, location: str = None, db_name: str = None, username: str = None, password: str = None, configuration: [dict, str] = None):
        self.set_values(location, db_name, username, password, configuration)

        self.graph = Graph(self.location + "/" + self.db_name,
                           auth=(self.username, self.password))

        conn = self.check_connection()
        if not conn:
            raise ConnectionError("Connection failed")
        return True

    def is_acyclic(self):
        query = """
        OPTIONAL MATCH path = (startNode)-[*]->(startNode)
        WITH COLLECT(path) AS paths
        RETURN REDUCE(acc = false, p IN paths | acc OR length(p) > 1) AS isCyclic
        """
        result = self.query(query)

        return not result[0]["isCyclic"]

    def check_connection(self):
        try:
            self.graph.run("RETURN 1")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def upload_from_json(self, file_path: str, direction: int = 1):
        with open(file_path) as f:
            data = json.load(f)

        if "nodes" in data:
            for node in data["nodes"]:
                self.node_upload(node)
            del data["nodes"]

        if "relations" in data:
            for relation in data["relations"]:
                self.relation_dict_upload(relation, direction=direction)
            del data["relations"]

        for node in data:
            self.node_upload(node)

    def node_upload(self, node: dict, label: str = None):
        if label is None:
            if "label" in node:
                label = node["label"]
                del node["label"]
            else:
                raise ValueError("Label not specified")

        query = "CREATE (:" + label + " {"
        for key, value in node.items():
            if key != "label":
                query += str(key) + ": '" + str(value) + "', "
        query = query[:-2] + "})"

        self.graph.run(query)

    def nodes_upload(self, nodes: list, label: str = None):
        for node in nodes:
            self.node_upload(node, label)

    def relation_upload(self, from_label: str, from_prop: dict, to_label: str, to_prop: dict, label: str = None, direction: int = 1):
        if label is None:
            label = "RELATION"

        if direction == 1:
            direction = ("-", "->")
        elif direction == -1:
            direction = ("<-", "-")
        else:
            raise ValueError("Direction incorrect")

        query = "MATCH (a:" + from_label + "), (b:" + to_label + ") WHERE "
        for key, value in from_prop.items():
            query += "a." + str(key) + " = '" + str(value) + "' AND "
        for key, value in to_prop.items():
            query += "b." + str(key) + " = '" + str(value) + "' AND "
        query = query[:-5] + " CREATE (a)" + direction[0] + \
            "[:" + label + "]" + direction[1] + "(b)"

        self.graph.run(query)

    def relation_dict_upload(self, relation: dict, label: str = None, direction: int = 1):
        if relation is None:
            raise ValueError("Relation not specified")

        if label is None:
            if "label" in relation:
                label = relation["label"]
                del relation["label"]
            else:
                label = "RELATION"

        self.relation_upload(relation["from"]["label"], relation["from"]["properties"],
                             relation["to"]["label"], relation["to"]["properties"], label, direction)

    def relations_upload(self, relations: list, label: str = None, direction: int = 1):
        for relation in relations:
            self.relation_dict_upload(relation, label, direction)

    def query(self, query: str):
        return self.graph.run(query).data()

    def delete_all(self):
        self.graph.delete_all()

    def get_all_nodes(self, label: str = None, limit: int = None, order: bool = None):
        query = "MATCH (n"
        if label is not None:
            query += ":" + label
        query += ")\nRETURN n"
        if order is not None:
            query += "\nORDER BY ID(n)"
            if not order:
                query += " DESC"
        if limit is not None:
            query += "\n LIMIT " + str(limit)
        return self.query(query)

    def get_all_relationships(self, label: str = None, limit: int = None):
        query = "MATCH (n)-[r]"
        if label is not None:
            query += ":" + label
        query += "]-(m) RETURN r"
        if limit is not None:
            query += " LIMIT " + str(limit)
        return self.query(query)

    def get_networkx_di_graph(self):
        query = """
        MATCH (n)-[r]->(m)
        RETURN n, r, m
        """
        result = self.query(query)

        graph_nx = nx.DiGraph()

        for record in result:
            node1 = record["n"]
            node2 = record["m"]
            relationship = record["r"]

            graph_nx.add_node(node1["id"], name=node1["name"])
            graph_nx.add_node(node2["id"], name=node2["name"])

            if graph_nx.has_edge(node1["id"], node2["id"]):
                graph_nx[node1["id"]][node2["id"]]["label"] += "+" + \
                    (type(relationship).__name__)
            else:
                graph_nx.add_edge(node1["id"], node2["id"],
                                  label=type(relationship).__name__)

        return graph_nx
