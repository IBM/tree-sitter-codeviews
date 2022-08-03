import networkx as nx
from utils import java_nodes
from codeviews.CFG.CFG import CFGGraph

class CFGGraph_java(CFGGraph):
    def __init__(self, src_language, src_code, properties, root_node, parser):
        super().__init__(src_language, src_code, properties, root_node, parser)

        self.statement_types =  {
            'node_list_type':['declaration', 'expression_statement', 'labeled_statement', 'if_statement', 'while_statement', 'for_statement', 'enhanced_for_statement', 'assert_statement', 'do_statement', 'break_statement', 'continue_statement', 'return_statement', 'yield_statement', 'switch_expression', 'synchronized_statement', 'local_variable_declaration', 'throw_statement', 'try_statement', 'try_with_resources_statement', 'method_declaration','constructor_declaration', 'switch_block_statement_group', 'switch_rule', 'throw_statement', 'explicit_constructor_invocation'],
            'non_control_statement' : ['declaration', 'expression_statement', 'local_variable_declaration'],
            'control_statement' : ['if_statement', 'while_statement', 'for_statement', 'enhanced_for_statement', 'do_statement', 'break_statement', 'continue_statement', 'return_statement', 'yield_statement', 'switch_expression', 'synchronized_statement',  'try_statement', 'try_with_resources_statement', 'yield_statement'],
            'loop_control_statement' : ['while_statement', 'for_statement', 'enhanced_for_statement'],
            'not_implemented' : ['try_with_resources_statement'],
            'inner_node_type': ['declaration', 'expression_statement', 'local_variable_declaration'],
            'outer_node_type' : ['for_statement']           
        }

        self.CFG_node_list = []
        self.CFG_edge_list = []
        self.records = {
            'basic_blocks': {},
            'method_list': {},
            'function_calls': {},
            'switch_child_map': {},
            'label_statement_map': {}
        }
        
        self.index_counter = max(self.index.values())
        self.CFG_node_list, self.CFG_edge_list = self.CFG_java() 
        self.graph = self.to_networkx(self.CFG_node_list, self.CFG_edge_list)


    def get_basic_blocks(self, CFG_node_list, CFG_edge_list):
        G = self.to_networkx(CFG_node_list, CFG_edge_list)
        components = nx.weakly_connected_components(G)
        # NOTE: May need to sort these components according to line number (this one is more foolproof but harder to implement) or the first element in the set (less foolproof, but I think it can be proved, easier to implement). 
        # As of now coincidentally the AST node numbering and the list of nodes in networkx are according ot the line numbers
        block_index = 1
        for block in components:
            block_list = sorted(list(block))
            self.records['basic_blocks'][block_index] = block_list
            block_index += 1


    def get_key(self, val, dictionary):
        for key, value in dictionary.items():
            if val in value:
                return key

    def append_block_index(self, CFG_node_list):
        new_list = []
        for node in CFG_node_list:
            block_index = self.get_key(node[0], self.records['basic_blocks'])
            new_list.append((node[0], node[1], node[2], node[3], block_index))     
        return new_list

    def add_edge(self, src_node, dest_node, edge_type):
        if src_node == None or dest_node == None:
            print("Node where adding edge is attempted is none")
        else:
            self.CFG_edge_list.append((src_node, dest_node, edge_type))

    def get_next_index(self, node_key, node_value):

        next_node = node_value.next_named_sibling
        if next_node == None:
            # Sibling not found

            current_node = node_value
            while current_node.parent is not None:
                if current_node.parent.type in self.statement_types['loop_control_statement']:
                    next_node = current_node.parent
                    break
                next_node = current_node.next_named_sibling
                if next_node is not None:
                    break
                current_node = current_node.parent

        if next_node == None:
            return 2
        if next_node.type == 'block':
            for child in next_node.children:
                if child.is_named:
                    next_node = child
                    break

        return self.index[(next_node.start_point, next_node.end_point, next_node.type)]

    def edge_first_line(self, current_node_key, current_node_value):
        # We need to add an edge to the first statement in the next basic block
        node_index = self.index[current_node_key]
        try:
            current_block_index = self.get_key(node_index, self.records['basic_blocks'])
            next_block_index = current_block_index + 1
            first_line_index = self.records['basic_blocks'][next_block_index][0]
            src_node = node_index
            dest_node = first_line_index
            self.add_edge(src_node, dest_node, 'first_next_line') # We could maybe differentiate this
        except:
            # Most probably the block is empty
            # add a direct edge to the next statement
            # print("HIT AN EMPTY BLOCK")
            next_index = self.get_next_index(current_node_key, current_node_value)
            self.add_edge(node_index, next_index, 'next_line')


    def edge_to_body(self, current_node_key, current_node_value, body_type, edge_type):
        # We need to add an edge to the first statement in the body block
        src_node = self.index[current_node_key]
        body_node = current_node_value.child_by_field_name(body_type)

        if body_node.type == 'block':
            for child in body_node.children:
                if child.is_named:
                    body_node = child
                    break
        if body_node.is_named and body_node.type in self.statement_types['node_list_type']:          
            dest_node = self.index[(body_node.start_point, body_node.end_point, body_node.type)]
            self.add_edge(src_node, dest_node, edge_type)

    def get_block_last_line(self, current_node_value, block_type):
        # Find the last line in the body block 
        block_node = current_node_value.child_by_field_name(block_type)
        if block_node is None:
            for child in reversed(current_node_value.children):
                if child.is_named:
                    block_node = child
                    break

        if block_node.is_named is False:
            return self.index[(current_node_value.start_point, current_node_value.end_point, current_node_value.type)], current_node_value.type
       
        while block_node.type == 'block':
            named_children = list(filter(lambda child : child.is_named == True, reversed(block_node.children)))
            if len(named_children) == 0:
                # It means there is an empty block - thats why no named nodes inside
                return self.index[(current_node_value.start_point, current_node_value.end_point, current_node_value.type)], current_node_value.type
            block_node = named_children[0]
            if block_node.type in self.statement_types['node_list_type']:
                return self.index[(block_node.start_point, block_node.end_point, block_node.type)], block_node.type
        return self.index[(block_node.start_point, block_node.end_point, block_node.type)], block_node.type

    def function_list(self, current_node):
        if current_node.type == 'method_invocation':
        # maintain a list of all method invocations
            method_name = current_node.child_by_field_name('name').text.decode('UTF-8')
            
            parent_node = None
            pointer_node = current_node
            while pointer_node is not None:
                if pointer_node.parent is not None and pointer_node.parent.type in self.statement_types['node_list_type']:
                    parent_node = pointer_node.parent
                    break
                pointer_node = pointer_node.parent

            # Removing this if condition will treat all print sttements as function calls as well
            if method_name != 'println' and method_name != 'print':
                # index : (AST_id, method_name) (AST_id is of the parent node)
                if method_name in self.records['function_calls'].keys():
                    self.records['function_calls'][method_name].append((self.index_counter, self.index[(parent_node.start_point,parent_node.end_point,parent_node.type)]))
                else:
                    self.index_counter += 1
                    self.records['function_calls'][method_name] = [(self.index_counter, self.index[(parent_node.start_point,parent_node.end_point,parent_node.type)])]
                    # Patent node of function call AST id maps to AST id or index of dummy external funciton call node
                    # self.records['function_calls'][index] = (self.index_counter, method_name)
                    if method_name not in self.records['method_list'].keys():
                        self.CFG_node_list.append((self.index_counter, 0, 'function_call: '+method_name, 'external_function'))

        for child in current_node.children:
            if child.is_named:
                self.function_list(child)

    def add_dummy_nodes(self):
        self.CFG_node_list.append((1, 0, 'start_node', 'start'))
        self.CFG_node_list.append((2, 0, 'exit_node', 'exit'))

    def add_dummy_edges(self):
        for node_name, node_index in self.records['function_calls'].items():
            for node in node_index:
                if node_name not in self.records['method_list'].keys():
                    self.add_edge(node[1], node[0], 'function_call')
                    self.add_edge(node[0],node[1], 'function_return')
                else:
                    self.add_edge(node[1], self.records['method_list'][node_name], 'recursive_method_call')

    def CFG_java(self):
        warning_counter = 0
        node_list = {}
        # node_list is a dictionary that maps from (node.start_point, node.end_point, node.type) to the node object of tree-sitter
        _,node_list, self.CFG_node_list, self.records = java_nodes.get_nodes(root_node = self.root_node, node_list = node_list, graph_node_list = self.CFG_node_list, index = self.index, records = self.records, statement_types = self.statement_types)
        # Initial for loop required for basic block creation and simple control flow within a block ----------------------------
        for node_key, node_value in node_list.items():
            current_node_type = node_key[2]
            if current_node_type in self.statement_types['non_control_statement']:
                if java_nodes.return_switch_child(node_value) is None:
                    try: 
                        next_node = node_value.next_named_sibling
                        src_node = self.index[node_key]
                        dest_node = self.index[(next_node.start_point, next_node.end_point, next_node.type)]
                        if dest_node in self.records['switch_child_map'].keys():
                            dest_node = self.records['switch_child_map'][dest_node]
                        self.add_edge(src_node, dest_node, 'next_line')
                    except: 
                        pass

            elif current_node_type in self.statement_types['not_implemented']:
                print("WARNING: Not implemented ", current_node_type)
                warning_counter += 1

        self.get_basic_blocks(self.CFG_node_list, self.CFG_edge_list)
        self.CFG_node_list = self.append_block_index(self.CFG_node_list)

        self.function_list(self.root_node)

        self.add_dummy_nodes()
        self.add_dummy_edges()
        #------------------------------------------------------------------------------
        # At this point, the self.CFG_node_list has basic block index appended to it
        #------------------------------------------------------------------------------
        for node_key, node_value in node_list.items():
            current_node_type = node_key[2]
            current_index = self.index[node_key]
            if current_node_type == 'method_declaration' or current_node_type == 'constructor_declaration':
                # We need to add an edge to the first statement in the next basic block
                self.add_edge(1, current_index, 'next')
                self.edge_first_line(node_key, node_value)
                last_line_index, line_type = self.get_block_last_line(node_value, 'body')
                if line_type in self.statement_types['non_control_statement']:
                    if last_line_index in self.records['switch_child_map'].keys():
                        last_line_index = self.records['switch_child_map'][last_line_index]
                    self.add_edge(last_line_index, 2, 'exit_next')

            # ------------------------------------------------------------------------------------------------
            elif current_node_type == 'synchronized_statement':
                self.edge_first_line(node_key, node_value)
                last_line_index, line_type = self.get_block_last_line(node_value, 'body')
                if line_type in self.statement_types['non_control_statement']:
                    self.add_edge(last_line_index, 2, 'exit_next')

            # ------------------------------------------------------------------------------------------------
            elif current_node_type == 'labeled_statement':
                self.edge_first_line(node_key, node_value)

            # ------------------------------------------------------------------------------------------------
            elif current_node_type == 'if_statement':
                # Find the if block body and the else block body if exists (first statement inside them, add an edge)
                # Find the line just after the entire if_statement
                next_dest_index = self.get_next_index(node_key, node_value)
                # consequence
                self.edge_to_body(node_key, node_value, 'consequence', 'pos_next')
                # Find the last line in the consequence block and add an edge to the next statement
                last_line_index, line_type = self.get_block_last_line(node_value, 'consequence')
                # Also add an edge from the last guy to the next statement after the if
                # print(last_line_index, line_type)
                if line_type in self.statement_types['non_control_statement']:
                    self.add_edge(last_line_index, next_dest_index, 'next_line')

                #alternative = node_value.child_by_field_name('alternative')
                #print("alternative", alternative)
                if node_value.child_by_field_name('alternative') is not None:

                    # alternative
                    self.edge_to_body(node_key, node_value, 'alternative', 'neg_next')
                    # Find the last line in the alternative block 
                    last_line_index, line_type = self.get_block_last_line(node_value, 'alternative')
                    # print(last_line_index, line_type)
                    if line_type in self.statement_types['non_control_statement']:
                        self.add_edge(last_line_index, next_dest_index, 'next_line')
                else:
                    # When else is not there add a direct edge from if node to the next statement
                    self.add_edge(current_index, next_dest_index, 'next_line')
                    
            # ------------------------------------------------------------------------------------------------
            elif current_node_type in self.statement_types['loop_control_statement']:
                # Get the node immediately after the while statement
                next_dest_index = self.get_next_index(node_key, node_value)

                # Add an edge from this node to the first line in the body
                self.edge_to_body(node_key, node_value, 'body', 'pos_next')

                # Find the last line in the body block 
                last_line_index, line_type = self.get_block_last_line(node_value, 'body')

                # Add an edge from this node to the next line after the loop statement
                self.add_edge(current_index, next_dest_index, 'neg_next')
                # Add an edge from the last statement in the body to this node
                if line_type in self.statement_types['non_control_statement']:
                    self.add_edge(last_line_index, current_index, 'loop_control')

                #Add a self loop in case of for loops
                if current_node_type != 'while_statement':
                    self.add_edge(current_index, current_index, 'loop_update')

            # ------------------------------------------------------------------------------------------------
            elif current_node_type == 'do_statement':
                # Find the corresponding while statement
                # Add an edge from this node to the first line in the body
                # Find the last statement in the body and an edge frpom last line to the while node
                # Add an edge from the while node to the first line in the block or to the current do node
                # Add an edge from the while node to the next statement after the do_statement

                # Get the node immediately after the while statement
                next_dest_index = self.get_next_index(node_key, node_value)

                # Add an edge from this node to the first line in the body
                self.edge_to_body(node_key, node_value, 'body', 'pos_next')

                # Find the last line in the body block 
                last_line_index, line_type = self.get_block_last_line(node_value, 'body')

                # Search the CFG_node_list for parameterized_expression with parent do_statement with AST_id = src_node
                while_index = 0
                for k,v in node_list.items():
                    # print(k,v)
                    if k[2] == 'parenthesized_expression' and self.index[(v.parent.start_point, v.parent.end_point, v.parent.type)] == current_index:
                        while_index = self.index[k]
                        # print(while_index)
                        break

                # Find the last statement in the body and an edge frpom last line to the while node
                self.add_edge(last_line_index, while_index, 'next')

                # Add an edge from the while node to the first line in the block or to the current do node
                # self.CFG_edge_list.append((while_node, dest_node, 'loop_control')) # First node of block
                self.add_edge(while_index, current_index, 'loop_control') # do node

                # Add an edge from the while node to the next statement after the do_statement
                self.add_edge(while_index, next_dest_index, 'neg_next')

            # ------------------------------------------------------------------------------------------------
            elif current_node_type == 'continue_statement':
                # Go up the parent chain until we reach a loop_control statement or do statement
                # add edge from this node to the loop_control statement or do statement


                parent_node = node_value.parent
                loop_node = None
                while(parent_node is not None):
                    if parent_node.type in self.statement_types['loop_control_statement'] or parent_node.type == 'do_statement':
                        loop_node = parent_node
                        break
                    parent_node = parent_node.parent

                # add edge from this node to the loop_control statement or do statement

                src_node = self.index[node_key]
                dest_node = self.index[(loop_node.start_point, loop_node.end_point, loop_node.type)]
                label_name = list(filter(lambda child : child.type == 'identifier', node_value.children))
                if len(label_name)>0:
                    target_name = label_name[0].text.decode('UTF-8')+":"
                    dest_node = self.records['label_statement_map'][target_name]
                self.CFG_edge_list.append((src_node, dest_node, 'jump_next'))

            # ------------------------------------------------------------------------------------------------
            elif current_node_type == 'break_statement':
                # if it is inside a switch, it is handled here and also refer to switch_expression,
                # if it is inside a loop, handle it here
                parent_node = node_value.parent
                loop_node = None
                while(parent_node is not None):
                    if parent_node.type in self.statement_types['loop_control_statement'] or parent_node.type == 'do_statement' or parent_node.type == 'switch_expression':
                        loop_node = parent_node
                        break
                    parent_node = parent_node.parent

                next_dest_index = self.get_next_index((loop_node.start_point, loop_node.end_point, loop_node.type), loop_node)
                label_name = list(filter(lambda child : child.type == 'identifier', node_value.children))
                if len(label_name)>0:
                    target_name = label_name[0].text.decode('UTF-8')+":"
                    next_dest_index = self.records['label_statement_map'][target_name]
                self.add_edge(current_index, next_dest_index, 'jump_next')
            # ------------------------------------------------------------------------------------------------
            elif current_node_type == 'yield_statement':
                # if it is inside a switch, it is handled here and also refer to switch_expression,
                parent_node = node_value.parent
                loop_node = None
                while(parent_node is not None):
                    if parent_node.type in self.statement_types['loop_control_statement'] or parent_node.type == 'do_statement' or parent_node.type == 'switch_expression':
                        loop_node = parent_node
                        break
                    parent_node = parent_node.parent
                
                    
                try:    
                    next_dest_index = self.index[(loop_node.start_point, loop_node.end_point, loop_node.type)]
                except:
                    # Handle yield when no loop parent or switch parent
                    next_dest_index = self.get_next_index((node_value.start_point, node_value.end_point, node_value.type), node_value)
                    

                self.add_edge(current_index, next_dest_index, 'yield_exit')
            # ------------------------------------------------------------------------------------------------
            elif current_node_type == 'switch_expression':
                # First check if the switch expression_statement is part of a non-control statement, and add an edge to the next line
                switch_parent = java_nodes.return_switch_parent(node_value, self.statement_types['non_control_statement'])
                if switch_parent is not None:

                    try: 
                        next_node = switch_parent.next_named_sibling
                        src_node = self.index[node_key]
                        dest_node = self.index[(next_node.start_point, next_node.end_point, next_node.type)]
                        if dest_node in self.records['switch_child_map'].keys():
                            dest_node = self.records['switch_child_map'][dest_node]
                        self.add_edge(src_node, dest_node, 'next_line')

                    except Exception as e: 
                        print(e)
                        pass


                # Find all the case blocks associated with this switch node and add an edge to each of them
                # Find the last line in each case block and add an edge to the next case block unless it is a break statement
                # BUt if the block is empty, add an edge to the next case label
                # in case of a break statement, add an edge to the next statement outside the switch
                # in case of default, add an edge to the next statement outside the switch
                # in case of no default, add an edge from last block to the next statement outside the switch
                case_node_list = {}
                #default_exists = False

                # Find the next statement outside the switch
                next_dest_index = self.get_next_index(node_key, node_value)

                # For each case label block, find the first statement in the block and add an edge to it
                for k,v in node_list.items():
                    # print(k,v)
                    if (k[2] == 'switch_block_statement_group' or k[2] == 'switch_rule') and self.index[(v.parent.parent.start_point, v.parent.parent.end_point, v.parent.parent.type)] == current_index:
                        case_node_list[k]=v
                        case_node_index = self.index[k]
                        self.add_edge(current_index, case_node_index, 'switch_case')
                        # case_label = list(filter(lambda child : child.type == 'switch_label', v.children))
                        # if case_label == 'default':
                        #     default_exists = True
                        
                for k,v in case_node_list.items():
                    current_case_index = self.index[k]
                    case_statements = list(filter(lambda child : (child.is_named and child.type != 'switch_label'), v.children))
                    next_case_node = v.next_named_sibling
                    try:
                        next_case_node_index = self.index[(next_case_node.start_point, next_case_node.end_point, next_case_node.type)]
                    except:
                        next_case_node_index = None

                    if len(case_statements) == 0:
                        # There is no case body, so add an edge from this case to the next case label, if exists
                        self.add_edge(current_case_index, next_case_node_index, 'fall through')


                    else:
                        # The case body exists
                        # Find the first line in each case block and add an edge from case label to it
                        block_node = None
                        for child in v.children:
                            # Need to write a loop for unlimited layers of nesting
                            if child.is_named and child.type != 'switch_label':
                                if child.type == 'block':
                                    for child in child.children:
                                        if child.is_named and child.type != 'switch_label':
                                            block_node = child
                                            break
                                else:
                                    block_node = child
                                break

                        first_line_index = self.index[(block_node.start_point, block_node.end_point, block_node.type)]
                        self.add_edge(current_case_index, first_line_index, 'case_next')

                        # Find the last line in each case block and add an edge to the next case block unless it is a break statement
                        block_node = None
                        for child in reversed(v.children):
                            # Need to write a loop for unlimited layers of nesting
                            if child.is_named:
                                if child.type == 'block':
                                    for child in reversed(child.children):
                                        if child.is_named:
                                            block_node = child
                                            break
                                else:
                                    block_node = child
                                break

                        last_line_index = self.index[(block_node.start_point, block_node.end_point, block_node.type)]
                        if block_node.type in self.statement_types['non_control_statement']:
                            # print(block_node.text.decode('UTF-8'))
                            self.add_edge(last_line_index, next_case_node_index, 'fall through')

                        # in case of default, add an edge to the next statement outside the switch
                        # in case of no default, add an edge from last block to the next statement outside the switch
                        if next_case_node_index is None:
                            # This is the last block
                            if block_node.type in self.statement_types['non_control_statement']:
                                self.add_edge(last_line_index, next_dest_index, 'switch_out')

                # in case of a break statement, add an edge to the next statement outside the switch
                # -> Handled in break statement

            # ------------------------------------------------------------------------------------------------
            elif current_node_type == 'return_statement':
                self.add_edge(current_index, 2, 'return_exit')

            # ------------------------------------------------------------------------------------------------
            elif current_node_type == 'try_statement' or current_node_type == 'try_with_resources_statement':
                # Add edge from try block to first statement inside the block
                self.edge_to_body(node_key, node_value, 'body', 'next')
                catch_node_list = {}
                finally_node = None
                # Identify all catch blocks - add an edge from catch node to first line inside block
                for k,v in node_list.items():

                    
                    if k[2] == 'catch_clause' and self.index[(v.parent.start_point, v.parent.end_point, v.parent.type)] == current_index:
                        catch_node_list[k]=v
                        self.edge_to_body(k, v, 'body', 'next')
                        # catch_node_index = self.index[k]
                        # self.add_edge(current_index, catch_node_index, 'catch_next')

                    elif k[2] == 'finally_clause' and self.index[(v.parent.start_point, v.parent.end_point, v.parent.type)] == current_index:
                        finally_node = v
                        self.edge_first_line(k,v) # Not sure if this works


                # From each line inside the try block, an edge going to each catch block
                try_body = node_value.child_by_field_name('body')
                statements = list(filter(lambda child : child.type in self.statement_types['node_list_type'], try_body.children))

                if len(statements) > 0:
                    for statement in statements:
                        statement_index = self.index[(statement.start_point, statement.end_point, statement.type)]
                        for catch_node in catch_node_list.keys():
                            catch_index = self.index[catch_node]
                            # if statement.type != 'return_statement': The Exception can occur on the RHS so the catch_exception edge should be there
                            self.add_edge(statement_index, catch_index, 'catch_exception')
                
                # Find the next statement outside the try block
                next_dest_index = self.get_next_index(node_key, node_value)
                exit_next = None

                # finally block is optional
                if finally_node is not None:
                    # From last line of finally to next statement outside the try block
                    last_line_index, line_type = self.get_block_last_line(finally_node, 'body')
                    if line_type in self.statement_types['non_control_statement']:
                        self.add_edge(last_line_index, next_dest_index, 'finally_exit')
                    # For the remaining portion, set finally block as next node if exists
                    exit_next = self.index[(finally_node.start_point, finally_node.end_point, finally_node.type)]
                else:
                    exit_next = next_dest_index
                
                # From last line of try block to finally or to next statement outside the try block
                last_line_index, line_type = self.get_block_last_line(node_value, 'body')
                if line_type in self.statement_types['non_control_statement']:
                    self.add_edge(last_line_index, exit_next, 'try_exit')
                # From last line of every catch block to finally or to next statement outside the try block
                for catch_node, catch_value in catch_node_list.items():
                    last_line_index, line_type = self.get_block_last_line(catch_value, 'body')
                    if line_type in self.statement_types['non_control_statement']:
                        self.add_edge(last_line_index, exit_next, 'catch_exit')  
                    # Case of empty catch block
                    elif last_line_index == self.index[catch_node]:
                        self.add_edge(last_line_index, exit_next, 'catch_exit')   
            # ------------------------------------------------------------------------------------------------
            elif current_node_type == 'throw_statement':
                # Control goes to the first catch in the call stack (dynamic call stack) Nothing to do statically
                # Essentially exits the function
                
                parent = node_value.parent
                try_flag = False
                while parent is not None:
                    if parent.type == 'catch_clause' or parent.type == 'finally_clause':
                        break
                    if parent.type == 'try_statement' or parent.type == 'try_with_resources_statement':
                        try_flag = True
                        break
                    parent = parent.parent
                if try_flag is False:
                    self.add_edge(current_index, 2, 'throw_exit')


        if warning_counter > 0:
            print("Total number of warnings from unimplemented statement types: ", warning_counter)
        return self.CFG_node_list, self.CFG_edge_list
       

    
   