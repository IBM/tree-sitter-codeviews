from ..tree_parser.custom_parser import CustomParser

class JavaParser(CustomParser):
    def __init__(self, src_language, src_code):
        super().__init__(src_language, src_code)

    def check_declaration(self, current_node):

        # node_list_type = ['local_variable_declaration','declaration', 'expression_statement', 'labeled_statement', 'if_statement', 'while_statement', 'for_statement', 'enhanced_for_statement', 'assert_statement', 'do_statement', 'break_statement', 'continue_statement', 'return_statement', 'yield_statement', 'switch_expression', 'synchronized_statement', 'local_variable_declaration', 'throw_statement', 'try_statement', 'try_with_resources_statement', 'method_declaration','constructor_declaration', 'switch_block_statement_group', 'switch_rule', 'throw_statement', 'explicit_constructor_invocation']
        parent_types = ["variable_declarator", "catch_formal_parameter", "formal_parameter"]
        current_types = ["identifier"]
        if (
            current_node.parent is not None
            and current_node.parent.type in parent_types
            and current_node.type in current_types
        ):
            if current_node.parent.type == "variable_declarator":
                # TODO: If it is a class attribute need to maintain class_name.class_variable so that the correct datatype can be mapped
                if len(list(filter(lambda x: x.type == "=", current_node.parent.children)))> 0:
                    if current_node.next_sibling is not None and current_node.next_sibling.type == "=":
                        return True
                    else:
                        return False
                else:
                    return True
            return True
        return False
    
    def get_type(self, node):
        """ Given a variable declarator node, return the variable type of the identifier"""
        datatypes = ['type_identifier', 'integral_type', 'floating_point_type', 'void_type', 'boolean_type', 'scoped_type_identifier', 'generic_type']
        if node.type == "formal_parameter":
            return node.children[0].text.decode('utf-8')
        
        for child in node.parent.children:
            if child.type in datatypes:
                return child.text.decode('utf-8')
        return None
    
    def scope_check(self, parent_scope, child_scope):
        for p in parent_scope:
            if p not in child_scope:
                return False
        return True
    def longest_scope_match(self, name_matches, symbol_table):
        """Given a list of name matches, return the longest scope match"""
        # [(ind, var), (ind,var)]
        scope_array = list(map(lambda x: symbol_table['scope_map'][x[0]], name_matches))
        # scope_array.sort(key=lambda x: len(x), reverse=True)
        # index = max(range(len(scope_array)), key=lambda x: len(x))
        max_val = max(scope_array, key=lambda x: len(x))
        for i in range(len(scope_array)):
            if scope_array[i] == max_val:
                return name_matches[i][0]
        


    def create_all_tokens(
        self,
        src_code,
        root_node,
        all_tokens,
        label,
        method_map,
        method_calls,
        start_line,
        declaration,
        declaration_map,
        symbol_table,
    ):
        # Needs to be modifed for every language
        remove_list = ["class_declaration", "method_declaration", "method_invocation"]
        # node_list_type = ['local_variable_declaration', 'declaration', 'expression_statement', 'labeled_statement',
        #                   'if_statement', 'while_statement', 'for_statement', 'enhanced_for_statement',
        #                   'assert_statement', 'do_statement', 'break_statement', 'continue_statement',
        #                   'return_statement', 'yield_statement', 'synchronized_statement',
        #                   'local_variable_declaration', 'throw_statement', 'try_statement',
        #                   'try_with_resources_statement', 'method_declaration', 'constructor_declaration',
        #                   'switch_expression', 'switch_block_statement_group', 'switch_rule', 'throw_statement',
        #                   'explicit_constructor_invocation']
        block_types = [
            "block",
            "if_statement",
            "while_statement",
            "for_statement",
            "enhanced_for_statement",
            "do_statement",
            "switch_expression",
            "switch_block_statement_group",
            "switch_rule",
            "throw_statement",
            "synchronized_statement",
            "try_statement",
            "try_with_resources_statement",
            "method_declaration",
            "constructor_declaration",
            "explicit_constructor_invocation",
        ]

        if root_node.is_named and root_node.type in block_types:
            """On entering a new block, increment the scope id and push it to the scope_stack"""
            # current_scope = symbol_table['scope_stack'][-1]
            symbol_table["scope_id"] = symbol_table["scope_id"] + 1
            symbol_table["scope_stack"].append(symbol_table["scope_id"])

        if (
            root_node.is_named
            and (len(root_node.children) == 0 or root_node.type == "string")
            and root_node.type != "comment"
        ): # All identifiers
            index = self.index[(root_node.start_point, root_node.end_point, root_node.type)]
            label[index] = root_node.text.decode("UTF-8")
            start_line[index] = root_node.start_point[0]
            all_tokens.append(index)
            """Store a copy of the current scope stack in the scope map for each token. This token belongs to all the scopes in the current scope stack."""
            
            symbol_table["scope_map"][index] = symbol_table["scope_stack"].copy()

            
            current_node = root_node
            if (current_node.parent is not None and current_node.parent.type in remove_list):
                method_map.append(index)
                if current_node.next_named_sibling.type == "argument_list":
                    method_calls.append(index)

            if (current_node.parent is not None and current_node.parent.type == "field_access"):
                object_node = current_node.parent.child_by_field_name("field")
                object_index = self.index[(object_node.start_point, object_node.end_point, object_node.type)]
                current_index = self.index[(current_node.start_point,current_node.end_point,current_node.type)]
                if object_index == current_index:
                    method_map.append(current_index)

                while (current_node.parent is not None and current_node.parent.type == "field_access"):
                    current_node = current_node.parent

                if (current_node.parent is not None and current_node.parent.type == "method_invocation"):
                    method_map.append(index)
                label[index] = current_node.text.decode("UTF-8")
                
            if self.check_declaration(current_node):
                variable_name = label[index]
                declaration[index] = variable_name

                variable_type = self.get_type(current_node.parent)
                if variable_type is not None:
                    symbol_table["data_type"][index] = variable_type
            else:
                current_scope = symbol_table['scope_map'][index]

                if current_node.type == "field_access":   
                    field_variable = current_node.children[-1]
                    # entire_variable_name = current_node.text.decode('utf-8')
                    field_variable_name = field_variable.text.decode('utf-8')

                    for (ind,var) in declaration.items():
                        if var == field_variable_name:
                            parent_scope = symbol_table['scope_map'][ind]
                            if self.scope_check(parent_scope, current_scope):
                                declaration_map[index] = ind
                                break

                    
                        # Identify the leftmost - that is the reference - identify its class
                # TODO: Handle field accesses
                # If we can add the coorect declaration_map entry, we should be done.
                # For this we need to identify the class to which it belongs, and the corresponding field variable
                else:
                    name_matches = []
                    for (ind, var) in declaration.items():
                        if var == label[index]:
                            parent_scope = symbol_table['scope_map'][ind]
                            if self.scope_check(parent_scope, current_scope):
                                name_matches.append((ind,var))
                    for (ind, var) in name_matches:
                        parent_scope = symbol_table['scope_map'][ind]
                        closest_index = self.longest_scope_match(name_matches, symbol_table)
                        declaration_map[index] = closest_index
                        break

        else:
            for child in root_node.children:
                self.create_all_tokens(
                    src_code,
                    child,
                    all_tokens,
                    label,
                    method_map,
                    method_calls,
                    start_line,
                    declaration,
                    declaration_map,
                    symbol_table,
                )

        if root_node.is_named and root_node.type in block_types:
            """On exiting a block, pop the scope id from the scope_stack"""
            symbol_table["scope_stack"].pop(-1)

        return (
            all_tokens,
            label,
            method_map,
            method_calls,
            start_line,
            declaration,
            declaration_map,
            symbol_table,
        )
