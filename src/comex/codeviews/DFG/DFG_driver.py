from ...tree_parser.parser_driver import ParserDriver
from ...utils import postprocessor
from ..SDFG.SDFG import DfgRda


class DFGDriver:
    def __init__(
        self,
        src_language="java",
        src_code="",
        output_file="DFG_output.json",
        properties={},
    ):
        self.src_language = src_language

        self.parser = ParserDriver(src_language, src_code).parser
        self.root_node = self.parser.root_node
        self.src_code = self.parser.src_code
        self.properties = properties.get("DFG", {})
        if self.properties.get("statements", False):
            result = DfgRda(
                src_language=src_language,
                src_code=src_code,
                properties=properties,
            )
            self.rda_table = result.rda_table
            self.rda_result = result.rda_result
            self.graph = result.graph
        if output_file:
            self.json = postprocessor.write_networkx_to_json(self.graph, output_file)
            postprocessor.write_to_dot(
                self.graph,
                # os.path.join(grandparent_folder,"output_graphs/AST_output.dot"),
                output_file.split(".")[0] + ".dot",
                output_png=True,
            )