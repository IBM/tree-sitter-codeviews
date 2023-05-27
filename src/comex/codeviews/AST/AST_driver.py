from .AST import ASTGraph
from ...tree_parser.parser_driver import ParserDriver
from ...utils import postprocessor


class ASTDriver:
    def __init__(
        self,
        src_language="java",
        src_code="",
        output_file="AST_output.json",
        properties={},
    ):
        self.src_language = src_language
        self.src_code = src_code
        self.properties = properties
        self.parser = ParserDriver(src_language, src_code).parser
        self.root_node = self.parser.root_node
        self.AST = ASTGraph(
            self.src_language,
            self.src_code,
            self.properties,
            self.root_node,
            self.parser,
        )
        self.graph = self.AST.graph
        if output_file:
            self.json = postprocessor.write_networkx_to_json(self.graph, output_file)
            postprocessor.write_to_dot(
                self.graph, output_file.split(".")[0] + ".dot", output_png=True
            )
