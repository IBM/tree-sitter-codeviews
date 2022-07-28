import networkx as nx
import json
from networkx.readwrite import json_graph

def networkx_to_json(graph):
    """Convert a networkx graph to a json object"""
    graph_json = json_graph.node_link_data(graph)
    return graph_json

def write_networkx_to_json(graph, filename):
    """Convert a networkx graph to a json object"""
    graph_json = json_graph.node_link_data(graph)
    with open(filename, 'w') as f:
        json.dump(graph_json, f)
    return graph_json

def to_dot(graph):
        return nx.nx_pydot.to_pydot(graph)

def write_to_dot(graph, filename):
    nx.nx_pydot.to_pydot(graph)
    nx.nx_pydot.write_dot(graph, filename)