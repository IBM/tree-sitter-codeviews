import os

import networkx as nx
from ...tree_parser.parser_driver import ParserDriver


class CSTGraph:
    def __init__(self, src_language, src_code, root_node):
        self.src_language = src_language
        self.src_code = src_code
        self.root_node = root_node
        self.index = {}
        self.create_CST_id(self.root_node, self.index, [0])
        self.graph = self.to_networkx()
        grandparent_folder = os.path.abspath(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        # postprocessor.write_to_dot(self.graph, os.path.join(grandparent_folder,"output_graphs/CST_output.dot"))

    def postorder_traversal(self, node):
        if node.children:
            for child in node.children:
                self.postorder_traversal(child)
        # print(node.type)

    def create_CST_id(self, root_node, CST_index, CST_id):
        current_node_id = CST_id[0]
        CST_id[0] += 1
        CST_index[
            (root_node.start_point, root_node.end_point, root_node.type)
        ] = current_node_id
        for child in root_node.children:

            child_id = self.create_CST_id(child, CST_index, CST_id)
        return current_node_id  # redundant

    def get_CST_nodes(self, root_node, CST, CST_index):
        current_node_id = CST_index[
            (root_node.start_point, root_node.end_point, root_node.type)
        ]
        label = str(root_node.start_point[0]) + "_" + root_node.type
        CST.add_node(
            current_node_id,
            label=label,
            shape="box",
            style="rounded, filled",
            fillcolor="#BFE6D3",
            color="white",
        )
        for child in root_node.children:

            child_id = self.get_CST_nodes(child, CST, CST_index)
            if child_id != None:
                CST.add_edge(current_node_id, child_id)
        return current_node_id

    def to_networkx(self):
        G = nx.MultiDiGraph()
        self.get_CST_nodes(self.root_node, G, self.index)
        nx.set_edge_attributes(G, "CST_edge", "edge_type")
        nx.set_edge_attributes(G, "blue", "color")
        nx.set_edge_attributes(G, "vee", "shape")
        return G


class CSTDriver:
    def __init__(self, src_language="java", src_code=""):
        self.src_language = src_language
        self.src_code = src_code
        self.parser = ParserDriver(src_language, src_code).parser
        self.root_node, self.tree = self.parser.parse()
        self.graph = CSTGraph(self.src_language, self.src_code, self.root_node)
