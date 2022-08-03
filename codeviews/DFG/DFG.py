from utils import DFG_utils
import networkx as nx

class DFGGraph:
    def __init__(self, src_language, src_code, properties, root_node, parser):
        self.src_language = src_language
        self.src_code = src_code
        self.properties = properties
        self.root_node = root_node
        self.parser = parser
        self.index = self.parser.index
        self.all_tokens = self.parser.all_tokens
        self.label = self.parser.label
        self.method_map = self.parser.method_map
        self.start_line = self.parser.start_line
        self.start_line[-1] = 0
        self.index_to_code = self.tokenize()    
    
    def tokenize(self):
        tokens_index=DFG_utils.tree_to_token_index(self.root_node)     
        code=self.src_code.split('\n')
        # code_tokens is a list of all tokens in code - all leaves of the CST
        code_tokens=[DFG_utils.index_to_code_token(x,code) for x in tokens_index]  
        index_to_code={}

        for (index,code) in zip(tokens_index,code_tokens):
            if index in self.index:
                idx = self.index[index]
            else:
                idx = -1
            index_to_code[index]=(idx,code) 

        return index_to_code

    def to_statement_level_DFG(self, DFG_edgelist, graph_node_list):
        # print("Printing DFG edgelist")
        # print(*DFG_edgelist, sep = '\n')
        # print("Printing inside DFG")
        # print(*graph_node_list, sep = '\n')
        # for edge in DFG_edgelist:
        #     print(edge[0], edge[1], self.start_line[edge[1]])
        G=nx.MultiDiGraph()
        for node in graph_node_list:
            G.add_node(node[0], line_number = node[1], node_type = node[3], label = node[2])

        for edge in DFG_edgelist:
            for idx in (edge[4]):
                # print(edge)
                
                # print(edge[3], src_line, edge[0], dest_line)
                try:
                    src_line = self.start_line[idx]
                    dest_line = self.start_line[edge[1]]
                    nodes = [x for x,y in G.nodes(data=True) if y['line_number']==src_line]
                    src = nodes[0]
                    nodes = [x for x,y in G.nodes(data=True) if y['line_number']==dest_line]
                    dest = nodes[0]

                    if src in G.nodes and dest in G.nodes and (src,dest) not in G.edges():
                        if self.properties.get("minimized",False) is True and edge[2]=='comesFrom':
                            pass
                        else:
                            
                            G.add_edge(src, dest, dataflow_type = edge[2], edge_type = edge[2])
                except Exception as e:
                    print(e)

        return G

    def to_networkx_simple(self, DFG_edgelist):
        G=nx.MultiDiGraph()
        # We first add all the nodes in the graph
        for edge in DFG_edgelist:
            if edge[1] in self.index.values() and edge[1] not in self.method_map and edge[1] in self.label.keys():
                line_number = self.start_line[edge[1]]
                node_type = [index for index,value in self.index.items() if value == edge[1]][0][2]
                G.add_node(edge[1], line_number = line_number, node_name = edge[0], node_type = node_type, label = self.label[edge[1]])
        for edge in DFG_edgelist:
            for idx in (edge[4]):
                if idx in G.nodes and edge[1] in G.nodes:
                    if self.properties.get("minimized",False) is True and edge[2]=='comesFrom':
                        pass
                    else:
                        G.add_edge(idx, edge[1], dataflow_type = edge[2], edge_type = edge[2])
        try:
            G.remove_node(-1)
        except:
            pass
        nx.set_edge_attributes(G, 'DFG_edge', 'edge_type')
        nx.set_edge_attributes(G, '#00A3FF', 'color')
        return G
    

    def to_networkx_collapsed(self, DFG_edgelist):
        G=nx.MultiDiGraph()
        name_to_index_map = {}
        for token in self.all_tokens:
            if token not in self.method_map:
                name_to_index_map[self.label[token]] = set()
        for edge in DFG_edgelist:
            if edge[1] in self.all_tokens and edge[1] not in self.method_map:
                name_to_index_map[self.label[edge[1]]].add(edge[1])
        # At this point the dictionary is completely populated

        for name, indexes in name_to_index_map.items():
            the_chosen_index = min(indexes)
            node_type = [index for index,value in self.index.items() if value == edge[1]][0][2]
            line_number = self.start_line[the_chosen_index]
            G.add_node(the_chosen_index, line_number = line_number, node_composition = str(indexes), node_name = name, node_type = node_type, label = name)

        for edge in DFG_edgelist:
            edge_name = self.label[edge[1]]
            if edge_name in name_to_index_map.keys():
                the_chosen_index = min(name_to_index_map[edge_name])
                for i in (edge[4]):
                    idx_name = self.label[i]
                    if idx_name in name_to_index_map.keys():
                        idx = min(name_to_index_map[idx_name])
                        if idx in G.nodes and edge[1] in G.nodes:
                            if self.properties["minimized"] is True and edge[2]=='comesFrom':
                                pass
                            else:
                                G.add_edge(idx, the_chosen_index, dataflow_type = edge[2], edge_type = edge[2])
            nx.set_edge_attributes(G, 'DFG_edge', 'edge_type')
            nx.set_edge_attributes(G, '#00A3FF', 'color')
        return G


    def to_networkx(self, DFG_edgelist, graph_node_list):
        if self.properties.get("statements", False):
            return self.to_statement_level_DFG(DFG_edgelist,graph_node_list)
        if self.properties.get("collapsed", False)==True:
            return self.to_networkx_collapsed(DFG_edgelist)
        return self.to_networkx_simple(DFG_edgelist)
        

    


