import json
import os
import random
import time
import traceback
from pathlib import Path

import pandas as pd
from loguru import logger
from pqdm.threads import pqdm
from collections import Counter

from comex.codeviews.combined_graph.combined_driver import CombinedDriver
from comex.utils import postprocessor

hard_timeout = 0


class Dataset:
    def __init__(self, file, combined_config, random_sample, ignore, fixed_run=None, kind="", min_set=False):
        self.rda_table = {}
        self.lines = []
        self.combined_config = combined_config
        self.random_sample = random_sample
        self.ignore = ignore
        self.fixed_run = fixed_run
        self.selected = []
        _, extension = file.rsplit(".", 1)
        self.extension = extension
        if os.path.isdir(file):
            for path in Path(file).rglob(f'*.{self.extension}'):
                self.lines.append(path.read_text())
        else:
            if self.extension == "json":
                self.extension = kind
                df = pd.read_json(file)
                df = self.df_filter(df)
                self.lines = df["flines"].tolist()
            elif kind == "search":
                include_path = file.rsplit(".", 1)[0] + ".txt"
                include_list = []
                if os.path.exists(include_path) and min_set:
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

        self.save_successful_runs = False

        self.kind = kind
        self.driver = None
        self.graph = {}
        self.ignore = ignore
        self.src = {}
        self.index = {}
        self.analyze(CombinedDriver, kind=kind)
        self.result = None

    def df_filter(self, df):
        return df

    def run(self, driver, ind, languages=None):
        # record start time
        start_time = time.time()
        results = {}
        if languages is None:
            languages = [self.extension]
        for language in languages:
            results[language] = driver(
                src_language=language,
                src_code=self.src[ind],
                output_file=None,
                codeviews=self.combined_config,
            )
        # record end time
        end_time = time.time()
        # record time taken
        time_taken = end_time - start_time
        # If time taken is greater than hard timeout, then skip
        if hard_timeout and time_taken > hard_timeout:
            logger.error(f"TimeoutError: {ind} {time_taken}")
            raise TimeoutError
        return results

    @staticmethod
    def have_bidirectional_relationship(G, node1, node2):
        return G.has_edge(node1, node2) and G.has_edge(node2, node1)

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
        if self.random_sample and ind not in self.selected:
            return "skipped"
        if self.fixed_run and isinstance(self.fixed_run, list):
            if ind not in self.fixed_run:
                return "skipped"
        elif self.fixed_run and ind != self.fixed_run:
            return "skipped"
        if ind in self.ignore[self.extension]:
            return "skipped"
        # logger.info(ind)
        actual_src = self.read_src(line, ind, kind=self.kind)
        if actual_src is None:
            return "skipped"
        # FAILURE
        try:
            result = self.run(self.driver, ind)
            # self.result = result[self.extension].results["DFG"]
            # self.rda_table = self.result.rda_table
            self.graph[ind] = result[self.extension].graph

            # check if graph has no edges
            # if not self.graph[ind].edges():
            #     raise Exception("No edges in graph")

            # self.index[ind] = result.parser.index

            # if self.random_sample:
            #     self.manual_check(ind, prefix=self.extension + "-manual")

            # # AP1: - No incoming edges for node with use ignoring method calls
            # # - FP for same line declarations fixed
            # # - FP undirected no path - TODO
            # # Highlights definition propagation issues
            # names_defined = set()
            # unsatisfied_names = set()
            # if self.graph[ind].out_degree(1) > 1:
            #     return "skipped"
            # if not self.result.graph.edges():
            #     self.manual_check(ind, prefix=self.extension + "-none")
            #     return "no_dfg"
            # for node in self.rda_table:
            #     rda_entry = self.rda_table[node]
            #     unsat_in_node = set()
            #     for identifier in rda_entry["use"]:
            #         if not identifier.satisfied:
            #             unsat_in_node.add(identifier.name)
            #     for identifier in rda_entry["def"]:
            #         names_defined.add(identifier.name)
            #         unsat_in_node.discard(identifier.name)
            #     unsatisfied_names = unsatisfied_names.union(unsat_in_node)
            # if names_defined.intersection(unsatisfied_names):
            #     self.manual_check(ind, prefix=self.extension + "-AP1")
            #     logger.error("AP1: No definition used {}: {}", ind, names_defined.intersection(unsatisfied_names))
            #     return "AP1"
            # # AP2: bidirectional edges detected
            # # - FP in case of loops bypassed by ignoring all cases with loops :/
            # if not any(word in line for word in ['while', 'for']):
            #     no_error = True
            #     for u, v in self.result.graph.edges():
            #         if u == v:
            #             continue
            #         if u > v:  # Avoid duplicates, such as (1, 2) and (2, 1)
            #             v, u = u, v
            #         if self.have_bidirectional_relationship(self.result.graph, u, v):
            #             self.manual_check(ind, prefix=self.extension + "-AP2")
            #             no_error = False
            #             logger.error("AP2: dual edge: {}", ind)
            #             break
            #     if not no_error:
            #         return "AP2"
            # # AP3: difference in CS and Java RDA table - difficult due to error node - not worth in codesearch
            # # # AP4: - Valid identifiers missing in RDA table
            # # # global variables hit as FP's
            # # edges = [tup[:-1] for tup in self.graph[ind].edges]
            # # if len(edges) != len(set(edges)):
            # #     self.manual_check(ind, prefix=self.extension + "-AP1")
            # #     logger.error("AP1: Missing edge: {}", ind)
            # #     AP1 = AP1 + 1
            # #     continue
            if self.save_successful_runs:
                self.manual_check(ind, prefix=self.extension + "-SUCCESS", formats="dot", actual_src=actual_src, type=self.kind)
                return "success"
            return "skipped"
        except Exception as e:
            logger.error("FAIL: ID: {} | Error: {}", ind, e)
            error = traceback.format_exc()
            self.manual_check(ind, prefix=self.extension + "-FAIL", formats=error, actual_src=actual_src, type=self.kind)
            logger.warning(error)
            return "failing"

    def analyze(self, driver, kind=""):
        self.selected = random.sample(range(len(self.lines)), self.random_sample)
        self.driver = driver
        self.kind = kind
        if self.fixed_run is None or isinstance(self.fixed_run, list):
            runners = os.cpu_count()
        else:
            runners = 1
        tested = pqdm(enumerate(self.lines), self.run_singleton, n_jobs=runners, argument_type='args')
        logger.success("Completed DFG analysis of {} files", len(self.lines))
        for value, count in Counter(tested).most_common():
            print(value, count)

    def manual_check(self, index, prefix, formats="dot", actual_src=None, type=""):
        os.makedirs(f"./data/RANDOM/dfg_{type}/{prefix}", exist_ok=True)
        output_file = f"./data/RANDOM/dfg_{type}/{prefix}/{index}.json"
        with open(f"./data/RANDOM/dfg_{type}/{prefix}/{index}.{self.extension}", "w") as f:
            if actual_src is not None:
                f.write(actual_src)
            else:
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
            with open(f"./data/RANDOM/dfg_{type}/{prefix}/{index}.log", "w") as f:
                f.write(formats)

    def summarize(self, concern=""):
        all_tags = []
        for ind in self.index:
            for tag in self.index[ind]:
                if tag[2] == concern:
                    self.manual_check(ind, prefix=self.extension + "-concern", type=self.kind)
                all_tags.append(tag[2])
        data = pd.Series(all_tags)
        return data.value_counts()
