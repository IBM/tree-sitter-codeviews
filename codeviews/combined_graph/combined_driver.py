import networkx as nx
from codeviews.AST.AST_driver import ASTDriver
from codeviews.CFG.CFG_driver import CFGDriver

from codeviews.DFG.DFG_driver import DFGDriver
from utils import postprocessor

class CombinedDriver():
    def __init__(self,src_language = "", src_code = "", output_file = "./output_graphs/combined_output", graph_format = "dot", codeviews = {}):
        self.src_language = src_language
        self.src_code = src_code
        self.codeviews = codeviews

        self.graph = nx.MultiDiGraph()

        if self.codeviews["DFG"]["exists"] == True:
            self.DFG = DFGDriver(self.src_language, self.src_code, "", self.codeviews["DFG"]).graph

        if self.codeviews["AST"]["exists"] == True:
            self.AST = ASTDriver(self.src_language, self.src_code, "", self.codeviews["AST"]).graph

        if self.codeviews["CFG"]["exists"] == True:
            self.CFG = CFGDriver(self.src_language, self.src_code, "", self.codeviews["CFG"]).graph

        self.combine()
        if graph_format == "json":
            postprocessor.write_networkx_to_json(self.graph, output_file+".json")
        else:
            postprocessor.write_to_dot(self.graph, output_file+".dot")
        

    def check_validity(self):
        """Write logic for valid combinations here"""
        return True

    def AST_simple(self):
        self.graph = self.AST
        postprocessor.write_to_dot(self.graph, "./output_graphs/AST_output.dot")
        postprocessor.write_networkx_to_json(self.graph, "./output_json/AST_output.json")
    
    def DFG_simple(self):
        self.graph = self.DFG
        postprocessor.write_to_dot(self.graph, "./output_graphs/DFG_output.dot")
        postprocessor.write_networkx_to_json(self.graph, "./output_json/DFG_output.json")
    
    def CFG_simple(self):
        self.graph = self.CFG
        postprocessor.write_to_dot(self.graph, "./output_graphs/CFG_output.dot")
        postprocessor.write_networkx_to_json(self.graph, "./output_json/CFG_output.json")

    def DFG_collapsed(self):
        self.graph = self.DFG
        postprocessor.write_to_dot(self.graph, "./output_graphs/DFG_collapsed_output.dot")
        postprocessor.write_networkx_to_json(self.graph, "./output_json/DFG__collapsed_output.json")
    
    def AST_collapsed(self):
        self.graph = self.AST
        postprocessor.write_to_dot(self.graph, "./output_graphs/AST_collapsed_output.dot")
        postprocessor.write_networkx_to_json(self.graph, "./output_json/AST_collapsed_output.json")

    def combine_AST_DFG_simple(self):
        self.graph.add_nodes_from(self.AST.nodes(data=True))
        self.graph.add_nodes_from(self.DFG.nodes(data=True))
        self.graph.add_edges_from(self.AST.edges(data=True))
        self.graph.add_edges_from(self.DFG.edges(data=True))
        

        postprocessor.write_to_dot(self.graph, "./output_graphs/AST_DFG_simple_output.dot")
        postprocessor.write_networkx_to_json(self.graph, "./output_json/AST_DFG_simple_output.json")

    def combine_CFG_DFG_simple(self):
        self.graph.add_nodes_from(self.CFG.nodes(data=True))
        self.graph.add_nodes_from(self.DFG.nodes(data=True))
        self.graph.add_edges_from(self.CFG.edges(data=True))
        self.graph.add_edges_from(self.DFG.edges(data=True))
        

        postprocessor.write_to_dot(self.graph, "./output_graphs/CFG_DFG_simple_output.dot")
        postprocessor.write_networkx_to_json(self.graph, "./output_json/CFG_DFG_simple_output.json")


    def combine_AST_CFG_simple(self):
        self.graph.add_nodes_from(self.AST.nodes(data=True))
        self.graph.add_nodes_from(self.CFG.nodes(data=True))
        self.graph.add_edges_from(self.AST.edges(data=True))
        self.graph.add_edges_from(self.CFG.edges(data=True))
        

        postprocessor.write_to_dot(self.graph, "./output_graphs/AST_CFG_simple_output.dot")
        postprocessor.write_networkx_to_json(self.graph, "./output_json/AST_CFG_simple_output.json")

    def combine_AST_CFG_DFG_simple(self):
        self.graph.add_nodes_from(self.AST.nodes(data=True))
        self.graph.add_nodes_from(self.CFG.nodes(data=True))
        self.graph.add_nodes_from(self.DFG.nodes(data=True))
        self.graph.add_edges_from(self.AST.edges(data=True))
        self.graph.add_edges_from(self.CFG.edges(data=True))
        self.graph.add_edges_from(self.DFG.edges(data=True))
        postprocessor.write_to_dot(self.graph, "./output_graphs/AST_CFG_DFG_simple_output.dot")
        postprocessor.write_networkx_to_json(self.graph, "./output_json/AST_CFG_DFG_simple_output.json")

    def combine_AST_DFG_collapsed(self):
        self.graph.add_nodes_from(self.AST.nodes(data=True))
        self.graph.add_nodes_from(self.DFG.nodes(data=True))
        self.graph.add_edges_from(self.AST.edges(data=True))
        self.graph.add_edges_from(self.DFG.edges(data=True))
        postprocessor.write_to_dot(self.graph, "./output_graphs/AST_DFG_collapsed_output.dot")
        postprocessor.write_networkx_to_json(self.graph, "./output_json/AST_DFG_collapsed_output.json")


    def combine(self):
        """Combine all combinations into a single graph"""
    
        if self.codeviews["AST"]["exists"] == True and self.codeviews["CFG"]["exists"] == True and self.codeviews["DFG"]["exists"] == True:
            # if self.codeviews["DFG"]["collapsed"] == False and self.codeviews["AST"]["collapsed"] == False:
            self.combine_AST_CFG_DFG_simple()

        elif self.codeviews["AST"]["exists"] == True and self.codeviews["DFG"]["exists"] == True:
            if self.codeviews["DFG"]["collapsed"] == False and self.codeviews["AST"]["collapsed"] == False:
                self.combine_AST_DFG_simple()

        
            elif self.codeviews["DFG"]["collapsed"] == True and self.codeviews["AST"]["collapsed"] == True:
                self.combine_AST_DFG_collapsed()

        elif self.codeviews["AST"]["exists"] == True and self.codeviews["CFG"]["exists"] == True:
            # if self.codeviews["DFG"]["collapsed"] == False and self.codeviews["AST"]["collapsed"] == False:
            self.combine_AST_CFG_simple()

        elif self.codeviews["CFG"]["exists"] == True and self.codeviews["DFG"]["exists"] == True:
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
