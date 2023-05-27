import os

import networkx as nx

from ..AST.AST_driver import ASTDriver
from ..CFG.CFG_driver import CFGDriver
from ..DFG.DFG_driver import DFGDriver
from ...utils import postprocessor


class CombinedDriver:
    def __init__(
        self,
        src_language="java",
        src_code="",
        output_file=None,
        graph_format="dot",
        codeviews={},
    ):
        self.src_language = src_language
        self.src_code = src_code
        self.codeviews = codeviews
        self.graph = nx.MultiDiGraph()
        self.results = {}

        if self.codeviews["DFG"]["exists"] == True:
            self.results["DFG"] = DFGDriver(
                self.src_language, self.src_code, "", self.codeviews
            )
            self.DFG = self.results["DFG"].graph

        if self.codeviews["AST"]["exists"] == True:
            self.results["AST"] = ASTDriver(
                self.src_language, self.src_code, "", self.codeviews["AST"]
            )
            self.AST = self.results["AST"].graph

        if self.codeviews["CFG"]["exists"] == True:
            self.results["CFG"] = CFGDriver(
                self.src_language, self.src_code, "", self.codeviews["CFG"]
            )
            self.CFG = self.results["CFG"].graph

        self.combine()
        if output_file:
            if graph_format == "all" or graph_format == "json":
                self.json = postprocessor.write_networkx_to_json(
                    self.graph, output_file
                )
            if graph_format == "all" or graph_format == "dot":
                postprocessor.write_to_dot(
                    self.graph, output_file.split(".")[0] + ".dot", output_png=True
                )

    def get_graph(self):
        return self.graph

    def check_validity(self):
        """Write logic for valid combinations here"""
        return True

    def AST_simple(self):
        self.graph = self.AST
        grandparent_folder = os.path.abspath(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        # postprocessor.write_to_dot(self.graph, os.path.join(grandparent_folder,"output_graphs/AST_output.dot"))
        # postprocessor.write_networkx_to_json(self.graph, os.path.join(grandparent_folder,"./output_json/AST_output.json"))

    def DFG_simple(self):
        self.graph = self.DFG
        grandparent_folder = os.path.abspath(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        # postprocessor.write_to_dot(self.graph, os.path.join(grandparent_folder,"output_graphs/DFG_output.dot"))
        # postprocessor.write_networkx_to_json(self.graph, os.path.join(grandparent_folder,"./output_json/DFG_output.json"))

    def CFG_simple(self):
        self.graph = self.CFG
        grandparent_folder = os.path.abspath(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        # postprocessor.write_to_dot(self.graph, os.path.join(grandparent_folder,"output_graphs/CFG_output.dot"))
        # postprocessor.write_networkx_to_json(self.graph, os.path.join(grandparent_folder,"output_json/CFG_output.json"))

    def DFG_collapsed(self):
        self.graph = self.DFG
        grandparent_folder = os.path.abspath(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        # postprocessor.write_to_dot(self.graph, os.path.join(grandparent_folder,"output_graphs/DFG_collapsed_output.dot"))
        # postprocessor.write_networkx_to_json(self.graph, os.path.join(grandparent_folder,"output_json/DFG__collapsed_output.json"))

    def AST_collapsed(self):
        self.graph = self.AST
        grandparent_folder = os.path.abspath(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        # postprocessor.write_to_dot(self.graph, os.path.join(grandparent_folder,"output_graphs/AST_collapsed_output.dot"))
        # postprocessor.write_networkx_to_json(self.graph, os.path.join(grandparent_folder,"output_json/AST_collapsed_output.json"))

    def combine_AST_DFG_simple(self):
        self.graph.add_nodes_from(self.AST.nodes(data=True))
        self.graph.add_nodes_from(self.DFG.nodes(data=True))
        self.graph.add_edges_from(self.AST.edges(data=True))
        self.graph.add_edges_from(self.DFG.edges(data=True))

        grandparent_folder = os.path.abspath(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        # postprocessor.write_to_dot(self.graph, os.path.join(grandparent_folder,"output_graphs/AST_DFG_simple_output.dot"))
        # postprocessor.write_networkx_to_json(self.graph, os.path.join(grandparent_folder,"output_json/AST_DFG_simple_output.json"))

    def combine_CFG_DFG_simple(self):
        self.graph.add_nodes_from(self.CFG.nodes(data=True))
        self.graph.add_nodes_from(self.DFG.nodes(data=True))
        self.graph.add_edges_from(self.CFG.edges(data=True))
        self.graph.add_edges_from(self.DFG.edges(data=True))

        grandparent_folder = os.path.abspath(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        # postprocessor.write_to_dot(self.graph, os.path.join(grandparent_folder,"output_graphs/CFG_DFG_simple_output.dot"))
        # postprocessor.write_networkx_to_json(self.graph, os.path.join(grandparent_folder,"output_json/CFG_DFG_simple_output.json"))

    def combine_AST_CFG_simple(self):
        self.graph.add_nodes_from(self.AST.nodes(data=True))
        self.graph.add_nodes_from(self.CFG.nodes(data=True))
        self.graph.add_edges_from(self.AST.edges(data=True))
        self.graph.add_edges_from(self.CFG.edges(data=True))
        grandparent_folder = os.path.abspath(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        # postprocessor.write_to_dot(self.graph, os.path.join(grandparent_folder,"output_graphs/AST_CFG_simple_output.dot"))
        # postprocessor.write_networkx_to_json(self.graph, os.path.join(grandparent_folder,"output_json/AST_CFG_simple_output.json"))

    def combine_AST_CFG_DFG_simple(self):
        self.graph.add_nodes_from(self.AST.nodes(data=True))
        self.graph.add_nodes_from(self.CFG.nodes(data=True))
        self.graph.add_nodes_from(self.DFG.nodes(data=True))
        self.graph.add_edges_from(self.AST.edges(data=True))
        self.graph.add_edges_from(self.CFG.edges(data=True))
        self.graph.add_edges_from(self.DFG.edges(data=True))
        grandparent_folder = os.path.abspath(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        # postprocessor.write_to_dot(self.graph, os.path.join(grandparent_folder,"output_graphs/AST_CFG_DFG_simple_output.dot"))
        # postprocessor.write_networkx_to_json(self.graph, os.path.join(grandparent_folder,"output_json/AST_CFG_DFG_simple_output.json"))

    def combine_AST_DFG_collapsed(self):
        self.graph.add_nodes_from(self.AST.nodes(data=True))
        self.graph.add_nodes_from(self.DFG.nodes(data=True))
        self.graph.add_edges_from(self.AST.edges(data=True))
        self.graph.add_edges_from(self.DFG.edges(data=True))
        grandparent_folder = os.path.abspath(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        )
        # postprocessor.write_to_dot(self.graph, os.path.join(grandparent_folder,"output_graphs/AST_DFG_collapsed_output.dot"))
        # postprocessor.write_networkx_to_json(self.graph, os.path.join(grandparent_folder,"output_json/AST_DFG_collapsed_output.json"))

    def combine(self):
        """Combine all combinations into a single graph"""

        if (
            self.codeviews["AST"]["exists"] == True
            and self.codeviews["CFG"]["exists"] == True
            and self.codeviews["DFG"]["exists"] == True
        ):
            # if self.codeviews["DFG"]["collapsed"] == False and self.codeviews["AST"]["collapsed"] == False:
            self.combine_AST_CFG_DFG_simple()

        elif (
            self.codeviews["AST"]["exists"] == True
            and self.codeviews["DFG"]["exists"] == True
        ):
            if (
                self.codeviews["DFG"]["collapsed"] == False
                and self.codeviews["AST"]["collapsed"] == False
            ):
                self.combine_AST_DFG_simple()

            elif (
                self.codeviews["DFG"]["collapsed"] == True
                and self.codeviews["AST"]["collapsed"] == True
            ):
                self.combine_AST_DFG_collapsed()

        elif (
            self.codeviews["AST"]["exists"] == True
            and self.codeviews["CFG"]["exists"] == True
        ):
            # if self.codeviews["DFG"]["collapsed"] == False and self.codeviews["AST"]["collapsed"] == False:
            self.combine_AST_CFG_simple()

        elif (
            self.codeviews["CFG"]["exists"] == True
            and self.codeviews["DFG"]["exists"] == True
        ):
            # if self.codeviews["DFG"]["collapsed"] == False and self.codeviews["AST"]["collapsed"] == False:
            self.combine_CFG_DFG_simple()

        elif self.codeviews["AST"]["exists"] == True:
            if self.codeviews["AST"]["collapsed"] == True:
                self.AST_collapsed()
            else:
                self.AST_simple()

        elif self.codeviews["DFG"]["exists"] == True:
            if self.codeviews["DFG"]["collapsed"] == True:
                self.DFG_collapsed()
            else:
                self.DFG_simple()
        elif self.codeviews["CFG"]["exists"] == True:

            self.CFG_simple()
