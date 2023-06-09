import os.path
import time

import networkx as nx
from loguru import logger

from comex.codeviews.CFG.CFG_driver import CFGDriver
from comex.codeviews.SDFG.SDFG_csharp import dfg_csharp
from comex.codeviews.SDFG.SDFG_java import dfg_java
from comex.utils import postprocessor, DFG_utils

debug = False

# if any(
#         # GITHUB_ACTIONS
#         x in os.environ for x in ("PYCHARM_HOSTED",)
# ):
#     debug = True


class DfgRda:
    def __init__(
            self,
            src_language="java",
            src_code="",
            output_file=None,
            graph_format="dot",
            properties=None,
    ):
        if not properties:
            properties = {
                "CFG": {},
                "DFG": {
                    "last_use": True,
                    "last_def": True,
                    "alex_algo": True,
                },
            }
        self.src_language = src_language
        self.src_code = src_code
        self.properties = properties
        self.graph = nx.MultiDiGraph()
        # time to create the CFG
        start = time.time()
        self.CFG_Results = CFGDriver(
            self.src_language, self.src_code, "", self.properties["CFG"]
        )
        end = time.time()
        self.CFG = self.CFG_Results.graph
        self.rda_table = None
        self.rda_result = None
        # time to create the DFG
        start_dfg = time.time()
        self.graph, self.debug_graph, self.rda_table, self.rda_result = self.rda(
            self.properties["DFG"]
        )
        end_dfg = time.time()
        if debug:
            logger.warning("CFG time: " + str(end - start) + " DFG time: " + str(end_dfg - start_dfg))
        if output_file:
            if graph_format == "all" or graph_format == "json":
                self.json = postprocessor.write_networkx_to_json(
                    self.graph, output_file
                )
            if graph_format == "all" or graph_format == "dot":
                postprocessor.write_to_dot(
                    self.graph, output_file.rsplit(".", 1)[0] + ".dot", output_png=True
                )
            if graph_format == "all" or graph_format == "dot":
                postprocessor.write_to_dot(
                    self.debug_graph, output_file.rsplit(".", 1)[0] + "_debug.dot", output_png=True
                )
            self.json = postprocessor.write_networkx_to_json(self.graph, output_file)

    def get_graph(self):
        return self.graph

    def index_to_code(self):
        tokens_index = DFG_utils.tree_to_token_index(self.CFG_Results.root_node)
        code = self.src_code.split("\n")
        # code_tokens is a list of all tokens in code - all leaves of the CST
        code_tokens = [DFG_utils.index_to_code_token(x, code) for x in tokens_index]
        index_to_code = {}

        for (ind, code) in zip(tokens_index, code_tokens):
            if ind in self.CFG_Results.parser.index:
                idx = self.CFG_Results.parser.index[ind]
            else:
                idx = -1
            index_to_code[ind] = (idx, code)

        return index_to_code

    def rda(self, properties):
        lang_map = {
            "java": dfg_java,
            "cs": dfg_csharp,
        }
        driver = lang_map[self.src_language]
        return driver(properties, self.CFG_Results)


if __name__ == '__main__':
    # file = "tests/data/RANDOM/translation.cs"
    # # sample_id = random.randint(0, 11800 - 1)
    # sample_id = 11132
    # with open(file, "r") as f:
    #     lines = f.read().splitlines()
    # sample_file = lines[sample_id]

    # "cs",
    for extension in ("java", "cs"):
        file = f"data/test_manual.{extension}"
        if not os.path.isfile(file):
            continue
        with open(file, "r") as f:
            sample_file = f.read()

        output_file = f"data/{extension}_test.json"
        # src_code = src_parser.pre_process_src(extension, sample_file, wrap_class=False)
        src_code = sample_file
        # with open("data/test." + extension, "w") as f:
        #     f.write(src_code)
        result = DfgRda(
            src_language=extension,
            src_code=src_code,
            output_file=None,
        )
        graph = result.graph
        postprocessor.write_to_dot(
            graph,
            output_file.rsplit(".", 1)[0] + ".dot",
            output_png=True,
        )
        debug_graph = result.debug_graph
        postprocessor.write_to_dot(
            debug_graph,
            output_file.rsplit(".", 1)[0] + "_debug.dot",
            output_png=True,
        )
