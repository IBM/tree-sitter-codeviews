import json
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import git
# "nested_do_while_java", CFG wrong
files = ["nested_adjacent_for_loops_java", "nested_ifs_java", "obj_d2_java", "objc_d3_java", "obj_d1_java", "obja_d4_java", "test5_java", "test11"]
for file in files:
    json_file_path = f'tests/data/SDFG/{file}/{file}-gold.json'
    commit_hash = 'f385b64e'
    trim_label = False

    repo = git.Repo(".")
    previous_json_file = repo.git.show('{}:{}'.format(commit_hash, json_file_path), quiet=True)
    # , k=1000, seed=42, pos={node: [node, node] for node in G}
    current_data = json.load(open(json_file_path))
    previous_data = json.loads(previous_json_file)
    current_graph = json_graph.node_link_graph(current_data)
    previous_graph = json_graph.node_link_graph(previous_data)

    removed_edges = list(set(previous_graph.edges) - set(current_graph.edges))
    added_edges = list(set(current_graph.edges) - set(previous_graph.edges))
    common_edges = list(set(current_graph.edges) & set(previous_graph.edges))

    removed_nodes = list(set(previous_graph.nodes) - set(current_graph.nodes))
    added_nodes = list(set(current_graph.nodes) - set(previous_graph.nodes))
    common_nodes = list(set(current_graph.nodes) & set(previous_graph.nodes))

    interested_nodes = []
    for edge in removed_edges+added_edges:
        interested_nodes.append(edge[0])
        interested_nodes.append(edge[1])


    union_nodes = set(interested_nodes + removed_nodes + added_nodes)
    pos = nx.kamada_kawai_layout(union_nodes)
    nx.draw_networkx_edges(previous_graph, pos, edgelist=removed_edges, edge_color='r')
    nx.draw_networkx_edges(current_graph, pos, edgelist=added_edges, edge_color='b')
    nx.draw_networkx_nodes(previous_graph, pos, nodelist=removed_nodes, node_color='r')
    nx.draw_networkx_nodes(current_graph, pos, nodelist=added_nodes, node_color='b')

    node_labels = {}
    for node in union_nodes:
        if node in current_graph.nodes and node in previous_graph.nodes:
            node_labels[node] = current_graph.nodes[node].get('label', '')
            if trim_label:
                node_labels[node] = node_labels[node].split("_")[0]+"_common"
        elif node in current_graph.nodes:
            node_labels[node] = current_graph.nodes[node].get('label', '')
            if trim_label:
                node_labels[node] = node_labels[node].split("_")[0]+"_new"
        else:
            node_labels[node] = previous_graph.nodes[node].get('label', '')
            if trim_label:
                node_labels[node] = node_labels[node].split("_")[0]+"_old"
    nx.draw_networkx_labels(current_graph, pos, labels=node_labels, bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='gray', lw=1, alpha=0.8))

    plt.axis('off')

    # common_edges = [(u, v) for (u, v, i) in common_edges if u not in common_nodes and v not in common_nodes]
    # nx.draw_networkx_edges(current_graph, pos, edgelist=common_edges, edge_color='k')
    # nx.draw_networkx_nodes(current_graph, pos, nodelist=common_nodes, node_color='none', edgecolors='k')
    if union_nodes:
        x_values, y_values = zip(*pos.values())
        x_max = max(x_values)
        x_min = min(x_values)
        x_margin = (x_max - x_min) * 2
        plt.xlim(x_min - x_margin, x_max + x_margin)
        plt.show()

    # import json
    # import networkx as nx
    # from networkx.readwrite import json_graph
    # import matplotlib.pyplot as plt
    # import git
    #
    # json_file_path = 'tests/data/SDFG/nested_adjacent_for_loops_java/nested_adjacent_for_loops_java-gold.json'
    #
    # commit_hash = 'f385b64e'
    #
    # repo = git.Repo(".")
    #
    # previous_json_file = repo.git.show('{}:{}'.format(commit_hash, json_file_path), quiet=True)
    #
    # with open(json_file_path) as f:
    #     data = json.load(f)
    #     G = json_graph.node_link_graph(data, directed=True)
    #
    # # , k=1000, seed=42, pos={node: [node, node] for node in G}
    # # nx.draw_networkx_nodes(G, pos, nodelist=G.nodes(), node_color='r')
    # # nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color='r')
    # # nx.draw_networkx_labels(G, pos, labels={node: node for node in G.nodes()}, font_size=10, font_color='k')
    # # plt.title('Current version')
    # # plt.show()
    #
    # if previous_json_file != json.dumps(data, sort_keys=True):
    #     G_previous = json_graph.node_link_graph(json.loads(previous_json_file), directed=True)
    #
    #     pos_previous = nx.spring_layout(G_previous)
    #
    #     nodes_only_in_current = set(G.nodes()) - set(G_previous.nodes())
    #     nodes_only_in_previous = set(G_previous.nodes()) - set(G.nodes())
    #     common_nodes = set(G.nodes()) & set(G_previous.nodes())
    #     edges_only_in_current = set(G.edges()) - set(G_previous.edges())
    #     edges_only_in_previous = set(G_previous.edges()) - set(G.edges())
    #     common_edges = set(G.edges()) & set(G_previous.edges())
    #
    #     pos = nx.spring_layout(G)
    #     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    #     ax1.set_title('Current version')
    #     nx.draw_networkx_nodes(G, pos, nodelist=nodes_only_in_current, node_color='r', ax=ax1)
    #     nx.draw_networkx_nodes(G, pos, nodelist=common_nodes, node_color='g', ax=ax1)
    #     nx.draw_networkx_edges(G, pos, edgelist=edges_only_in_current, edge_color='r', ax=ax1)
    #     nx.draw_networkx_edges(G, pos, edgelist=common_edges, edge_color='g', ax=ax1)
    #     nx.draw_networkx_labels(G, pos, labels={node[0]: node[1]["label"] for node in G.nodes(data=True)}, font_size=10, font_color='k', ax=ax1)
    #     ax2.set_title('Previous version')
    #
    #     nx.draw_networkx_nodes(G_previous, pos_previous, nodelist=nodes_only_in_previous, node_color='b', ax=ax2)
    #     nx.draw_networkx_nodes(G_previous, pos_previous, nodelist=common_nodes, node_color='g', ax=ax2)
    #     nx.draw_networkx_edges(G_previous, pos_previous, edgelist=edges_only_in_previous, edge_color='b', ax=ax2)
    #     nx.draw_networkx_edges(G_previous, pos_previous, edgelist=common_edges, edge_color='g', ax=ax2)
    #     nx.draw_networkx_labels(G_previous, pos_previous, labels={node[0]: node[1]["label"] for node in G_previous.nodes(data=True)}, font_size=10, font_color='k', ax=ax2)
    #     plt.show()