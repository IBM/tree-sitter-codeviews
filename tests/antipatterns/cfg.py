import json
import os
import traceback
from collections import Counter
from pathlib import Path

import pandas as pd
from loguru import logger
from pqdm.threads import pqdm

from comex.codeviews.CFG.CFG_driver import CFGDriver
from comex.utils import postprocessor


class Dataset:
    def __init__(self, file, ignore, kind=""):
        _, extension = file.rsplit(".", 1)
        self.lines = []
        self.extension = extension
        if os.path.isdir(file):
            for path in Path(file).rglob(f'*.{self.extension}'):
                self.lines.append(path.read_text())
        else:
            if kind == "search":
                include_path = file.rsplit(".", 1)[0]+".txt"
                include_list = []
                if os.path.exists(include_path):
                    include_list = pd.read_csv(include_path, header=None)[0].tolist()
                df = pd.read_json(path_or_buf=file, lines=True)
                df.replace("", float("NaN"), inplace=True)
                df = df.dropna(subset='original_string')
                df = df.drop_duplicates(subset='url', keep="last")
                if include_list:
                    df = df[df['url'].isin(include_list)]
                self.lines = df['original_string'].tolist()
            else:
                with open(file, "r") as f:
                    self.lines = f.read().splitlines()
        self.kind = ""
        self.driver = None
        self.graph = {}
        self.ignore = ignore
        self.src = {}
        self.index = {}
        self.analyze(CFGDriver, kind=kind)

    def run(self, driver, ind):
        return driver(
            src_language=self.extension,
            src_code=self.src[ind],
            output_file=None,
            properties={},
        )

    def read_src(self, line, ind, kind=""):
        if kind == "search":
            src = "public class test {\n" + line + "\n}"
        else:
            json_snippet = json.loads(line)['original_string']
            # src = src_parser.pre_process_src(self.extension, line, wrap_class=True)
            src = "public class test {\n" + json_snippet + "\n}"
        self.src[ind] = src
        return src

    def run_singleton(self, ind, line):
        if ind in self.ignore[self.extension]:
            return "skipped"
        src = self.read_src(line, ind, self.kind)
        if src is None:
            logger.error("PARSE: Error in Parsing: {}", ind)
            return "skipped"
        # FAILURE
        try:
            result = self.run(self.driver, ind)
            self.graph[ind] = result.graph
            self.index[ind] = result.parser.index
            # UG = self.graph[ind].to_undirected()
            # # ANTIPATTERN - Entry node should have one exit in function level dataset
            # if self.graph[ind].out_degree(1) > 1:
            #     self.manual_check(ind, prefix=self.extension + "-AP1")
            #     logger.error("AP1: Entry has multiple outs: {}", ind)
            #     return "AP1"
            # # ANTIPATTERN - No entry or exit
            # if self.graph[ind].out_degree(1) == 0 or self.graph[ind].in_degree(2) == 0:
            #     self.manual_check(ind, prefix=self.extension + "-AP2")
            #     logger.error("AP2: No entry or exit: {}", ind)
            #     return "AP2"
            # # ANTIPATTERN - No path from 1 -> 2 for function level dataset
            # try:
            #     nx.shortest_path(UG, source=1, target=2)
            # except nx.NetworkXNoPath:
            #     self.manual_check(ind, prefix=self.extension + "-AP3")
            #     logger.error("AP3: Failed to resolve IN->OUT flow ID: {}", ind)
            #     return "AP3"
            # # ANTIPATTERN - Disconnected graphs in main graph
            # sub_graphs = [UG.subgraph(c) for c in nx.connected_components(UG)]
            # if len(sub_graphs) > 1:
            #     self.manual_check(ind, prefix=self.extension + "-AP4")
            #     logger.error(
            #         "AP4: Multiple Disconnected Graphs Detected ID: {}", ind
            #     )
            #     return "AP4"
            # # ANTIPATTERN - Nodes without attributes we defined
            # if any([not bool(data) for node, data in list(UG.nodes(data=True))]):
            #     self.manual_check(ind, prefix=self.extension + "-AP5")
            #     logger.error("AP5: Node without data ID: {}", ind)
            #     return "AP5"
            # # ANTIPATTERN - Nodes except entry node should have in-degree > 0
            # if any([v == 0 and n != 1 for n, v in self.graph[ind].in_degree]):
            #     self.manual_check(ind, prefix=self.extension + "-AP6")
            #     logger.error("AP6: Node without indegree ID: {}", ind)
            #     return "AP6"
            # # ANTIPATTERN - Nodes except exit node should have out-degree > 0
            # if any([v == 0 and n != 2 for n, v in self.graph[ind].out_degree]):
            #     self.manual_check(ind, prefix=self.extension + "-AP7")
            #     logger.error("AP7: Node without outdegree ID: {}", ind)
            #     return "AP7"
            # # ANTIPATTERN - 2 nodes connected by more than one edge in same dir - redundant cases not handled
            # edges = [tup[:-1] for tup in self.graph[ind].edges]
            # if len(edges) != len(set(edges)):
            #     self.manual_check(ind, prefix=self.extension + "-AP8")
            #     logger.error("AP8: Duplicated Edges: {}", ind)
            #     return "AP8"
            return "success"
            # Other Possible
            # These are rough but can be implemented once guaranteed checks all pass
            # ANTIPATTERN - Rough Check ... Node Label Length ... Checks for count of ; 2 in for-loop
        except Exception as e:
            logger.error("FAIL: ID: {} | Error: {}", ind, e)
            error = traceback.format_exc()
            self.manual_check(ind, prefix=self.extension + "-FAIL", formats=error)
            logger.warning(error)
            return "failing"

    def analyze(self, driver, kind=""):
        self.driver = driver
        self.kind = kind
        # ind = list(range(len(self.lines)))
        # tested = []
        # for ind, line in enumerate(tqdm(self.lines, position=0, leave=True)):
        #     tested.append(self.run_singleton(ind,line))
        tested = pqdm(enumerate(self.lines), self.run_singleton, n_jobs=os.cpu_count(), argument_type='args')
        logger.success("Completed CFG analysis of {} files", len(self.lines))
        for value, count in Counter(tested).most_common():
            print(value, count)

    def manual_check(self, index, prefix, formats="dot"):
        os.makedirs(f"./data/RANDOM/cfg/{prefix}", exist_ok=True)
        output_file = f"./data/RANDOM/cfg/{prefix}/{index}.json"
        with open(f"./data/RANDOM/cfg/{prefix}/{index}.{self.extension}", "w") as f:
            f.write(self.src[index])
        if formats == "json":
            postprocessor.write_networkx_to_json(self.graph[index], output_file)
        elif formats == "dot":
            postprocessor.write_to_dot(
                self.graph[index],
                output_file.rsplit(".", 1)[0] + ".dot",
                output_png=True,
            )
        else:
            with open(f"./data/RANDOM/cfg/{prefix}/{index}.log", "w") as f:
                f.write(formats)

    def summarize(self, concern=""):
        all_tags = []
        for ind in self.index:
            for tag in self.index[ind]:
                if tag[2] == concern:
                    self.manual_check(ind, prefix=self.extension + "-concern")
                all_tags.append(tag[2])
        data = pd.Series(all_tags)
        return data.value_counts()
