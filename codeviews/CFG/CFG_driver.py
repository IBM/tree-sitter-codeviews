from codeviews.CFG.CFG_java import CFGGraph_java
# from codeviews.CFG.CFG_python import CFGGraph_python
from tree_parser.parser_driver import ParserDriver
from utils import postprocessor


class CFGDriver:
    def __init__(
        self,
        src_language="java",
        src_code="",
        output_file="./output_json/CFG_output.json",
        properties={},
    ):
        self.src_language = src_language

        self.parser = ParserDriver(src_language, src_code).parser
        self.root_node = self.parser.root_node
        self.src_code = self.parser.src_code
        self.properties = properties

        self.CFG_map = {
                        "java": CFGGraph_java, 
                        # "python": CFGGraph_python
                        }

        self.CFG = self.CFG_map[self.src_language](
            self.src_language,
            self.src_code,
            self.properties,
            self.root_node,
            self.parser,
        )
        self.graph = self.CFG.graph

        postprocessor.write_to_dot(self.graph, "./output_graphs/CFG_output.dot")
        # postprocessor.write_networkx_to_json(self.graph, "./output_json/CFG_output.json")
