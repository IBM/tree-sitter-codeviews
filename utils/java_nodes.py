
def return_switch_child(node):
    """ Searches for a switch descendent in the tree and returns it"""
    if node.type == 'switch_expression':
        return node

    for child in node.children:
        t = return_switch_child(child)
        if t is not None: return t

    return None

def return_switch_parent(node, non_control_statement):
    """ Searches for a switch expression while going up the tree and returns it"""
    while node.parent is not None:
        if node.parent.type in non_control_statement:
            return node.parent
        node = node.parent

    return None

def get_nodes(root_node=None, node_list={}, graph_node_list=[], index={}, records = {}, statement_types = {}):
    """
    Returns statement level nodes recursively from the concrete syntax tree passed to it. Uses records to maintain required supplementary information. 
    noe_list maintains an intermediate representation and graph_node_list returns the final list. 
    """

    if root_node.type == 'parenthesized_expression' and root_node.parent is not None and root_node.parent.type == 'do_statement':
        label = 'while' + root_node.text.decode('UTF-8')
        type_label = 'while'
        node_list[(root_node.start_point,root_node.end_point, root_node.type)] = root_node
        # print(root_node.start_point, root_node.start_point[0], label)
        graph_node_list.append((index[(root_node.start_point,root_node.end_point,root_node.type)], root_node.start_point[0], label, type_label))

    elif root_node.type == 'catch_clause':
        node_list[(root_node.start_point,root_node.end_point, root_node.type)] = root_node
        catch_parameter = list(filter(lambda child : child.type == 'catch_formal_parameter', root_node.children))
        label = 'catch ('+catch_parameter[0].text.decode('UTF-8')+')'
        type_label = 'catch'
        # print(root_node.start_point, root_node.start_point[0], label)
        graph_node_list.append((index[(root_node.start_point,root_node.end_point,root_node.type)], root_node.start_point[0], label, type_label))

    elif root_node.type == 'finally_clause':
        node_list[(root_node.start_point,root_node.end_point, root_node.type)] = root_node
        label = 'finally'
        type_label = 'finally'
        # print(root_node.start_point, root_node.start_point[0], label)
        graph_node_list.append((index[(root_node.start_point,root_node.end_point,root_node.type)], root_node.start_point[0], label, type_label))

    # elif root_node.type == 'marker_annotation':
    #             print("MARKER", root_node.start_point)


    elif root_node.type in statement_types['node_list_type']:

        if root_node.type in statement_types['inner_node_type'] and root_node.parent is not None and root_node.parent.type in statement_types['outer_node_type'] and root_node.parent.child_by_field_name('body') != root_node:
            pass
            # If it has a parent and the parent is a for loop type and it is an initialization or update statement, omit it
        elif root_node.type in statement_types['inner_node_type'] and return_switch_child(root_node) is not None:
            switch_child = return_switch_child(root_node)
            child_index = index[(switch_child.start_point,switch_child.end_point,switch_child.type)]
            current_index = index[(root_node.start_point,root_node.end_point, root_node.type)]
            records['switch_child_map'][current_index] = child_index
            
        else: 
        
            node_list[(root_node.start_point,root_node.end_point, root_node.type)] = root_node
            # Set default label values for the node and then modify based on node type if required in the following if-else ladder
            label = root_node.text.decode('UTF-8')
            type_label = 'expression_statement'
            

            if root_node.type == 'method_declaration' or root_node.type == 'constructor_declaration':
                # print("INSIDE METHOD DECLARATION")
                method_name = list(filter(lambda child : child.type == 'identifier', root_node.children))
                parameter_list = list(filter(lambda child : child.type == 'formal_parameters' or child.type == 'formal_parameter', root_node.children))
                label = method_name[0].text.decode('UTF-8') +parameter_list[0].text.decode('UTF-8')
                type_label = root_node.type
                # print(label, root_node.start_point)
                records['method_list'][method_name[0].text.decode('UTF-8')] = index[root_node.start_point,root_node.end_point,root_node.type]
                graph_node_list.append((index[(root_node.start_point,root_node.end_point,root_node.type)], method_name[0].start_point[0], label, type_label))
            
            elif root_node.type == 'if_statement':
                condition = list(filter(lambda child : child.type == 'parenthesized_expression', root_node.children))
                label = 'if' + condition[0].text.decode('UTF-8')
                type_label = 'if'


            elif root_node.type == 'for_statement':
                try: 
                    init = root_node.child_by_field_name('init').text.decode('UTF-8')
                except:
                    init = ""
                try:
                    condition = root_node.child_by_field_name('condition').text.decode('UTF-8')
                except:
                    condition = ""
                try:
                    update = root_node.child_by_field_name('update').text.decode('UTF-8')
                except:
                    update = ""
                label = 'for(' + init + condition + ';' + update + ')'
                type_label = 'for'

            
            elif root_node.type == 'enhanced_for_statement':
                try:
                    modifiers = str(list(filter(lambda child : child.type == 'modifiers', root_node.children)))
                    modifier = modifiers[0].text.decode('UTF-8')
                except: 
                    modifier = ""
                try: 
                    types = root_node.child_by_field_name('type').text.decode('UTF-8')
                except:
                    types = ""
                
                try:
                    variables = list(filter(lambda child : child.type == 'identifier', root_node.children))
                    variable = variables[0].text.decode('UTF-8')
                except: 
                    variable = ""
                try:
                    value = root_node.child_by_field_name('value').text.decode('UTF-8')
                except:
                    value = ""
                label = 'for(' + modifier + " "+ types + " "+ variable+ ':' + value + ')'
                type_label = 'for'

            elif root_node.type == 'while_statement':
                condition = list(filter(lambda child : child.type == 'parenthesized_expression', root_node.children))
                label = 'while' + condition[0].text.decode('UTF-8')
                type_label = 'while'

            elif root_node.type == 'do_statement':
                label = 'do'
                type_label = 'do'

            elif root_node.type == 'switch_expression':
                parent_statement  = return_switch_parent(root_node, statement_types['non_control_statement'])
                if parent_statement is not None:
                    label = parent_statement.text.decode('UTF-8').split('{')[0]
                else:
                    condition = list(filter(lambda child : child.type == 'parenthesized_expression', root_node.children))
                    label = 'switch' + condition[0].text.decode('UTF-8')
                type_label = 'switch'

            elif root_node.type == 'switch_block_statement_group' or root_node.type == 'switch_rule':
                case_label = list(filter(lambda child : child.type == 'switch_label', root_node.children))
                label = case_label[0].text.decode('UTF-8') + ':'
                type_label = 'case'

            elif root_node.type == 'try_statement' or root_node.type == 'try_with_resources_statement':
                label = 'try'
                type_label = 'try'

            elif root_node.type == 'synchronized_statement':
                condition = list(filter(lambda child : child.type == 'parenthesized_expression', root_node.children))
                label = 'synchronized ' + condition[0].text.decode('UTF-8')
                type_label = 'synchronized'
            elif root_node.type == 'labeled_statement':
                name = list(filter(lambda child : child.type == 'identifier', root_node.children))
                label = name[0].text.decode('UTF-8') + ":"
                records['label_statement_map'][label] = index[(root_node.start_point,root_node.end_point,root_node.type)]
                type_label = 'label'
            # print(root_node.start_point, root_node.start_point[0], label)
            if root_node.type != 'method_declaration' and root_node.type != 'constructor_declaration':
                graph_node_list.append((index[(root_node.start_point,root_node.end_point,root_node.type)], root_node.start_point[0], label, type_label))

    for child in root_node.children:
        root_node, node_list, graph_node_list, records = get_nodes(root_node = child, node_list = node_list, graph_node_list = graph_node_list, index = index, records = records, statement_types = statement_types)

    return root_node, node_list, graph_node_list, records