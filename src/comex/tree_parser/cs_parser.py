from ..tree_parser.custom_parser import CustomParser
from loguru import logger

class CSParser(CustomParser):
    def __init__(self, src_language, src_code):
        super().__init__(src_language, src_code)

    def check_declaration(self, current_node):
        parent_types = ["variable_declarator", "catch_declaration", "parameter"]
        current_types = ["identifier"]
        if (
                current_node.parent is not None
                and current_node.parent.type in parent_types
                and current_node.type in current_types
        ):
            return True
        return False

    def get_type(self, node):
        """ Given a variable declarator node, return the variable type of the identifier"""
        datatypes = ["alias_qualified_name", "array_type", "function_pointer_type",
                     "generic_name", "global", "identifier", "implicit_type", "nullable_type",
                     "pointer_type", "predefined_type", "qualified_name", "ref_type", "scoped_type",
                     "tuple_type"]
        # TODO: Triage this
        # print(node.type, node.text.decode('utf-8'))
        if node.type == "parameter":
            return node.children[0].text.decode('utf-8')

        for child in node.parent.children:
            # print(child.type, child.text.decode('utf-8'))
            if child.type in datatypes:
                if child.type == "implicit_type":
                    # print("___________")
                    try:
                        object_type = node.named_children[-1].named_children[-1].named_children[0]
                        return object_type.text.decode('utf-8')
                    except:
                        logger.warning("ERROR")
                
                # print(child.type, child.text.decode('utf-8'))
                return child.text.decode('utf-8')
        return None

    def scope_check(self, parent_scope, child_scope):
        for p in parent_scope:
            if p not in child_scope:
                # print("parent", parent_scope, "child", child_scope)
                return False
        return True
    
    # TODO: Check correctness
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

        remove_list = [
            "class_declaration",
            "method_declaration",
            "invocation_expression",
            # ? Not sure if these should go in this logic
            # 'constructor_initializer', 'implicit_object_creation_expression', 'object_creation_expression', 'primary_constructor_base_type'
        ]
        block_types = [
            "block",
            "checked_statement",
            "fixed_statement",
            "unsafe_statement",
            "using_statement",
            "if_statement",
            "while_statement",
            "for_statement",
            "for_each_statement",
            "do_statement",
            "switch_expression",
            "switch_expression_arm",
            "switch_section",
            "switch_statement",
            "try_statement",
            "method_declaration",
            "constructor_declaration",
            "property_declaration",
            "interface_declaration",
            "throw_statement",
        ]
        # For reach identifier, if the parent is field_access -> keep going up till you reach the highest parent
        # else map to self
        # check if parent of highest mapped identifier is method invocation, then add it to the list
        # This logic helps create more meaningful tokens when it comes to variable names of object oriented languages like Java

        # if root_node.is_named and root_node.type

        # if root_node.type == '{':
        #     print(root_node.type)
        #     # current_scope = symbol_table['scope_stack'][-1]
        #     symbol_table['scope_id'] = symbol_table['scope_id'] + 1
        #     symbol_table['scope_stack'].append(symbol_table['scope_id'])

        # elif root_node.type == '}':
        #     print(root_node.type)
        #     symbol_table['scope_stack'].pop(-1)

        if root_node.is_named and root_node.type in block_types:
            # print(root_node.type)
            # current_scope = symbol_table['scope_stack'][-1]
            symbol_table["scope_id"] = symbol_table["scope_id"] + 1
            symbol_table["scope_stack"].append(symbol_table["scope_id"])

        if (
                root_node.is_named
                and (len(root_node.children) == 0 or root_node.type == "string")
                and root_node.type != "comment"
        ):
            index = self.index[
                (root_node.start_point, root_node.end_point, root_node.type)
            ]
            label[index] = root_node.text.decode("UTF-8")
            # if label[index] == 'true':
            #     print("FOUND TRUEE")
            start_line[index] = root_node.start_point[0]
            all_tokens.append(index)
            symbol_table["scope_map"][index] = symbol_table["scope_stack"].copy()
            # print("Adding to scope map", index, symbol_table['scope_map'][index])

            current_node = root_node

            if (
                    current_node.parent is not None
                    and current_node.parent.type in remove_list
            ):
                method_map.append(index)
                # print(current_node.text.decode('utf-8'), current_node.next_named_sibling)
                if current_node.next_named_sibling.type == "argument_list":
                    # print("ADDING METHOD", current_node.type, current_node.text.decode('utf-8'))
                    method_calls.append(index)

            if (
                    current_node.parent is not None
                    and current_node.parent.type == "member_access_expression"
            ):
                object_node = current_node.parent.child_by_field_name("name")
                object_index = self.index[
                    (object_node.start_point, object_node.end_point, object_node.type)
                ]
                current_index = self.index[
                    (
                        current_node.start_point,
                        current_node.end_point,
                        current_node.type,
                    )
                ]
                if object_index == current_index:
                    # ? not sure about this yet Console.writeline - if i say expression it will pick console if i say name it will pick the object but java side it picks the parent?
                    method_map.append(current_index)

                while (
                        current_node.parent is not None
                        and current_node.parent.type == "member_access_expression"
                ):
                    if current_node.parent.next_named_sibling is not None and current_node.parent.next_named_sibling.type == "argument_list":
                        break
                    else:
                        current_node = current_node.parent

                if (
                        current_node.parent is not None
                        and current_node.parent.type == "invocation_expression"
                ):
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
                if current_node.type == "member_access_expression":
                    field_variable = current_node.children[-1]
                    # entire_variable_name = current_node.text.decode('utf-8')
                    field_variable_name = field_variable.text.decode('utf-8')
                    
                    for (ind,var) in declaration.items():
                        if var == field_variable_name:
                            parent_scope = symbol_table['scope_map'][ind]
                            if self.scope_check(parent_scope, current_scope):
                                declaration_map[index] = ind
                                break
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
                    # for (ind, var) in declaration.items():
                    #     if var == label[index]:
                    #         parent_scope = symbol_table['scope_map'][ind]
                    #         # print(ind,var)
                    #         if self.scope_check(parent_scope, current_scope):
                    #             # print(ind, var)
                    #             # print("^^", current_node.parent.type, index, var, "Current:", current_scope, "Parent:", parent_scope)
                    #             declaration_map[index] = ind
                    #             break

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
