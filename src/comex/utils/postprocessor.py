import copy
import json
import os
import re
from subprocess import check_call

import networkx as nx
from networkx.readwrite import json_graph


def networkx_to_json(graph):
    """Convert a networkx graph to a json object"""
    graph_json = json_graph.node_link_data(graph)
    return graph_json


def write_networkx_to_json(graph, filename):
    """Convert a networkx graph to a json object"""
    graph_json = json_graph.node_link_data(graph)
    if not os.getenv("GITHUB_ACTIONS"):
        with open(filename, "w") as f:
            json.dump(graph_json, f)
    return graph_json


def to_dot(graph):
    return nx.nx_pydot.to_pydot(graph)


def write_to_dot(og_graph, filename, output_png=False):
    graph = copy.deepcopy(og_graph)
    if not os.getenv("GITHUB_ACTIONS"):
        for node in graph.nodes:
            if 'label' in graph.nodes[node]:
                graph.nodes[node]['label'] = re.escape(graph.nodes[node]['label'])
        nx.nx_pydot.write_dot(graph, filename)
        if output_png:
            check_call(
                ["dot", "-Tpng", filename, "-o", filename.rsplit(".", 1)[0] + ".png"]
            )
