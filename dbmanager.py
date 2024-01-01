import json
import os
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
                self.location = data["uri"]
                self.db_name = data["db_name"]
                self.username = data["user"]
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

    def relation_upload(self, from_label: str, from_prop: dict, to_label: str, to_prop: dict, label: str = None):
        if label is None:
            label = "RELATION"

        query = "MATCH (a:" + from_label + "), (b:" + to_label + ") WHERE "
        for key, value in from_prop.items():
            query += "a." + str(key) + " = '" + str(value) + "' AND "
        for key, value in to_prop.items():
            query += "b." + str(key) + " = '" + str(value) + "' AND "
        query = query[:-5] + " CREATE (a)-[:" + label + "]->(b)"

        self.graph.run(query)

    def relation_dict_upload(self, relation: dict, label: str = None):
        if relation is None:
            raise ValueError("Relation not specified")

        if label is None:
            if "label" in relation:
                label = relation["label"]
                del relation["label"]
            else:
                label = "RELATION"

        self.relation_upload(relation["from"]["label"], relation["from"]["properties"],
                             relation["to"]["label"], relation["to"]["properties"], label)

    def relations_upload(self, relations: list, label: str = None):
        for relation in relations:
            self.relation_dict_upload(relation, label)

    def query(self, query: str):
        return self.graph.run(query).data()

    def delete_all(self):
        self.graph.delete_all()
