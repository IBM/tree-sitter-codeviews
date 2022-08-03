from codeviews.DFG.DFG_java import DFGGraph_java
# from codeviews.DFG.DFG_python import DFGGraph_python
from tree_parser.parser_driver import ParserDriver
from utils import postprocessor


class DFGDriver:
    def __init__(self, src_language = 'java', src_code = '', output_file = "./output_json/DFG_output.json", properties = {}):
        self.src_language = src_language
       
        self.parser = ParserDriver(src_language, src_code).parser
        self.root_node = self.parser.root_node
        self.src_code = self.parser.src_code
        self.properties = properties
        self.DFG_map = {
            'java':DFGGraph_java,
            # 'python':DFGGraph_python
        }
        self.DFG = self.DFG_map[self.src_language](self.src_language, self.src_code, self.properties, self.root_node, self.parser)
        self.graph = self.DFG.graph

        postprocessor.write_to_dot(self.graph, "./output_graphs/DFG_output.dot")
        # postprocessor.write_networkx_to_json(self.graph, output_file)