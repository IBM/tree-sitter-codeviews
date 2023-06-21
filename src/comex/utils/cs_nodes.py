scope_only_blocks = [
    "checked_statement",
    "fixed_statement",
    "unsafe_statement",
    "using_statement",
    "local_function_statement",
]
class_declaration_statements = [
    "constructor_declaration",
    "interface_declaration",
    "property_declaration",
    "class_declaration",
    "field_declaration",
    "struct_declaration",
    "local_function_statement",
    
]

inner_node_type = [
    "empty_statement",
    "local_declaration_statement",
    # 'local_variable_declaration'
    # ! used in DFG graphcodebert - Swapped with local_declaration_statement
    # '_declaration',
    "labeled_statement",
    "expression_statement",
    
] + scope_only_blocks
non_control_statements = inner_node_type + class_declaration_statements
loop_control_statements = ["for_each_statement", "while_statement", "for_statement"]
control_statements = loop_control_statements + [
    "do_statement",
    "goto_statement",
    "throw_statement",
    "if_statement",
    "break_statement",
    "continue_statement",
    "return_statement",
    "yield_statement",
    "switch_expression",
    "switch_statement",
    "switch_expression_arm",
    "switch_section",
    "lock_statement",  # 'synchronized_statement',
    "try_statement",
    # 'try_with_resources_statement'
]
statement_holders = [
        "block",
        # "switch_block_statement_group",
        "switch_body",
        "switch_section",
        "declaration_list"
        # "constructor_body",
        # "declaration_list",
        # "module_body",
        # "program"
    ]
# based on handling simmilarity
statement_types = {
    "node_list_type": non_control_statements
    + control_statements
    + ["method_declaration", "local_function_statement"],
    "scope_only_blocks": scope_only_blocks,
    "outer_node_type": ["for_statement"],
    "inner_node_type": inner_node_type,
    "non_control_statement": non_control_statements,
    "control_statement": control_statements,
    "loop_control_statement": loop_control_statements,
    # 'terminal_inner': ['switch_expression_arm', 'switch_section'],
    "not_implemented": [
        # 'try_with_resources_statement'
    ],
    "statement_holders": statement_holders,
    "definition_types": ["method_declaration", "constructor_declaration", "class_declaration", "field_declaration", "interface_declaration", "operator_declaration", "conversion_operator_declaration"]
}
# TODO: add method_return_types
method_return_types = ['integral_type', 'void_type', 'type_identifier', 'generic_type', 'scoped_type_identifier', 'floating_point_type', 'boolean_type', 'array_type']


def cl(child):
    if child is None:
        # logger.error
        return ""
    else:
        return child.text.decode()


def return_switch_child(node):
    """Searches for a switch descendent in the tree and returns it"""
    if node.type in ["switch_expression", "switch_statement"]:
        return node

    for child in node.children:
        t = return_switch_child(child)
        if t is not None:
            return t

    return None


def return_switch_parent(node, non_control_statement):
    """Searches for a switch expression while going up the tree and returns it"""
    while node.parent is not None:
        if node.parent.type in non_control_statement:
            return node.parent
        node = node.parent

    return None


def return_index_of_first_parent_of_type(node, parent_type):
    while node.parent is not None:
        if node.parent.type == parent_type:
            return node.parent
        node = node.parent
    return None
def get_signature(node):
    signature = []
    formal_parameters = node.child_by_field_name('parameters')
    formal_parameters = list(filter(lambda x: x.type == 'parameter', formal_parameters.named_children))
    # for formal_parameter in formal_parameters:
    #     for child in formal_parameter.children:
    #         if child.type != "identifier":
    #             signature.append(child.text.decode('utf-8'))\
    for formal_parameter in formal_parameters:
        param_type = formal_parameter.child_by_field_name('type')
        if param_type is None:
            try:
                param_type = list(filter(lambda x: x.type == 'identifier', formal_parameter.named_children))[0]
                param_text = param_type.text.decode('utf-8')
                if '[]' in param_text:
                    param_text = param_text.split('[',1)
                    param_text = " [".join(param_text)
                signature.append(param_text)
            except:
                pass
        else:
            param_text = param_type.text.decode('utf-8')
            if '[]' in param_text:
                param_text = param_text.split('[',1)
                # print(param_text)
                param_text = " [".join(param_text)
                # print(param_text)
            signature.append(param_text)

    return tuple(signature)

def abstract_method(node):
    method_body = get_child_of_type(node, ["block"])
    while node is not None:
        if node.type == "declaration_list" and node.parent.type == "class_declaration":
            node = node.parent

            modifiers = get_child_of_type(node, ["modifiers"])
            if modifiers is not None and "abstract" in modifiers.text.decode("utf-8") and method_body is None:
                return True
        node = node.parent
    return False
def get_child_of_type(node, type_list):
    out = list(filter(lambda x : x.type in type_list, node.children))
    if len(out) > 0:
        return out[0]
    else: 
        return None
def get_class_name(node, index):
    "Returns the class name when a method declaration or constructor declaration is passed to it"
    type_identifiers = ["type_identifier", "generic_type", "scoped_type_identifier"]
    while node is not None:
        if node.type == "declaration_list" and node.parent.type == "class_declaration":
            node = node.parent
        
            class_index = index[(node.start_point, node.end_point, node.type)]
            class_name = [(list(filter(lambda child: child.type == "identifier", node.children))[0]).text.decode("UTF-8")]
            
            interface_node = get_child_of_type(node, ["super_interfaces"])
            if interface_node is not None:
                class_name.append(get_child_of_type(interface_node, ["type_list"]).text.decode("UTF-8"))

            superclass_node = get_child_of_type(node, ["superclass"])
            if superclass_node is not None:
                class_name.append(get_child_of_type(superclass_node, ["type_identifier"]).text.decode("UTF-8"))

            return class_index, class_name
        
        elif node.type == "declaration_list" and node.parent.type == "object_creation_expression":
            node = node.parent
            class_index = index[(node.start_point, node.end_point, node.type)]
            class_name = [list(filter(lambda child: child.type in type_identifiers, node.children))[0].text.decode("UTF-8")]
            return class_index, class_name
        elif node.type == "interface_body" and node.parent.type == "interface_declaration":
            return None
            node = node.parent
            class_index = index[(node.start_point, node.end_point, node.type)]
            class_name = list(filter(lambda child: child.type == "identifier", node.children))[0]
            return class_index, class_name.text.decode("UTF-8")
        node = node.parent

def get_nodes(root_node=None, node_list={}, graph_node_list=[], index={}, records={}):
    """
    Returns statement level nodes recursively from the concrete syntax tree passed to it. Uses records to maintain required supplementary information.
    noe_list maintains an intermediate representation and graph_node_list returns the final list.
    """
    #  These are within statements so handled separately - logic after assumed statements to be finest granularity
    if (
        "while" in root_node.type
        and root_node.parent is not None
        and root_node.parent.type == "do_statement"
    ):
        while_node = root_node.next_named_sibling
        label = "while(" + while_node.text.decode("UTF-8") + ")"
        type_label = "while"
        node_list[
            (while_node.start_point, while_node.end_point, while_node.type)
        ] = while_node
        graph_node_list.append(
            (
                index[(while_node.start_point, while_node.end_point, while_node.type)],
                while_node.start_point[0],
                label,
                type_label,
            )
        )
    elif root_node.type == "catch_clause":
        node_list[
            (root_node.start_point, root_node.end_point, root_node.type)
        ] = root_node
        catch_parameter = list(
            filter(lambda child: child.type == "catch_declaration", root_node.children)
        )
        label = "catch " + catch_parameter[0].text.decode("UTF-8")
        type_label = "catch"
        graph_node_list.append(
            (
                index[(root_node.start_point, root_node.end_point, root_node.type)],
                root_node.start_point[0],
                label,
                type_label,
            )
        )

    elif root_node.type == "finally_clause":
        node_list[
            (root_node.start_point, root_node.end_point, root_node.type)
        ] = root_node
        label = "finally"
        type_label = "finally"
        graph_node_list.append(
            (
                index[(root_node.start_point, root_node.end_point, root_node.type)],
                root_node.start_point[0],
                label,
                type_label,
            )
        )


    elif root_node.type in statement_types["node_list_type"]:

        if (
            root_node.type in statement_types["inner_node_type"]
            and root_node.parent is not None
            and root_node.parent.type in statement_types["outer_node_type"]
            and root_node.parent.child_by_field_name("body") != root_node
        ):
            pass
            # If it has a parent and the parent is a for loop type and it is an initialization or update statement,
            # omit it
        elif (
            root_node.type in statement_types["inner_node_type"]
            and return_switch_child(root_node) is not None
        ):
            # ? How does this logic work when there are more than 1 switch as a child
            switch_child = return_switch_child(root_node)
            child_index = index[
                (switch_child.start_point, switch_child.end_point, switch_child.type)
            ]
            current_index = index[
                (root_node.start_point, root_node.end_point, root_node.type)
            ]
            records["switch_child_map"][current_index] = child_index

        else:

            node_list[
                (root_node.start_point, root_node.end_point, root_node.type)
            ] = root_node
            # Set default label values for the node and then modify based on node type if required in the following
            # if-else ladder
            label = root_node.text.decode("UTF-8")
            type_label = "expression_statement"
            # print(label, root_node.type)
            if root_node.type in [
                "method_declaration",
                "interface_declaration",
                "constructor_declaration",
                "property_declaration",
            ]:
                # method_name = list(
                #     filter(lambda child: child.type == "identifier", root_node.children)
                # )
                # parameter_list = list(
                #     filter(
                #         lambda child: child.type == "parameter_list", root_node.children
                #     )
                # )
                # label = method_name[-1].text.decode("UTF-8")
                # if parameter_list:
                #     label = label + parameter_list[0].text.decode("UTF-8")
                # type_label = root_node.type
                # # ? make sure records is being updated for the newer updates if required
                # records["method_list"][method_name[-1].text.decode("UTF-8")] = index[
                #     root_node.start_point, root_node.end_point, root_node.type
                # ]
                # graph_node_list.append(
                #     (
                #         index[
                #             (root_node.start_point, root_node.end_point, root_node.type)
                #         ],
                #         method_name[-1].start_point[0],
                #         label,
                #         type_label,
                #     )
                # )
                label = ""
                for child in root_node.children:
                    if child.type != "block" and child.type != "constructor_body":
                        label = label + " " + child.text.decode('utf-8')
                method_name = list(
                    filter(lambda child: child.type == "identifier", root_node.children)
                )
                method_name = method_name[0].text.decode("UTF-8")
                method_index = index[(root_node.start_point, root_node.end_point, root_node.type)]
                type_label = root_node.type
                try:
                    signature = get_signature(root_node)
                    class_index, class_name_list = get_class_name(root_node, index)
                    if method_name == "Main":
                        # print("Main method found")
                        records["main_method"] = method_index
                        records["main_class"] = class_index
                    if abstract_method(root_node) == False:
                        for class_name in class_name_list:
                            if root_node.type == "constructor_declaration":
                                if class_name == method_name:
                                    records["constructor_list"][((class_name,method_name), signature)] = method_index
                                return_type = None
                            else:
                                records["method_list"][((class_name,method_name), signature)] = method_index
                                try:
                                    return_type = list(filter(lambda child: child.type in method_return_types, root_node.children))
                                    return_type = return_type[0].text.decode("UTF-8")
                                except:
                                    raise Exception("No return type found for method, update method_return_types", method_name)
                            
                            records["return_type"][((class_name,method_name), signature)] = return_type

                except Exception as e:
                    # print("*******", e)
                    pass
                graph_node_list.append((method_index, root_node.start_point[0],label,type_label))
            elif (
                root_node.type == "class_declaration"
                # or root_node.type == "constructor_declaration"
            ):
                modifiers = list(filter(lambda child: child.type != "declaration_list", root_node.children))
                class_name = list(filter(lambda child: child.type == "identifier", root_node.children))[0].text.decode("UTF-8")
                label = ""
                for modifier in modifiers:
                    label = label + modifier.text.decode("UTF-8") + " "
                type_label = root_node.type
                class_index = index[(root_node.start_point, root_node.end_point, root_node.type)]
                records["class_list"][class_name] = class_index

            elif root_node.type == "if_statement":
                condition = root_node.child_by_field_name("condition")
                label = f"if ( {cl(condition)} )"
                type_label = "if"
            elif root_node.type == "unsafe_statement":
                label = ""
                for child in root_node.children:
                    if not any(typ in child.type for typ in ["body", "block"]):
                        if label:
                            label = label + " "
                        label = label + child.text.decode().strip()
                type_label = "unsafe"
            elif root_node.type == "fixed_statement":
                label = ""
                for child in root_node.children:
                    if not any(typ in child.type for typ in ["body", "block"]):
                        if label:
                            label = label + " "
                        label = label + child.text.decode().strip()
                type_label = "fixed"
            elif root_node.type == "checked_statement":
                label = ""
                for child in root_node.children:
                    if not any(typ in child.type for typ in ["body", "block"]):
                        if label:
                            label = label + " "
                        label = label + child.text.decode().strip()
                type_label = "checked"
            elif root_node.type == "empty_statement":
                label = "empty"
                type_label = "empty"
            elif root_node.type == "using_statement":
                # "statement" in root_node.type and root_node.parent.type
                # ? how to handle such nodes?
                #     pass
                node_list[
                    (root_node.start_point, root_node.end_point, root_node.type)
                ] = root_node
                label = ""
                for child in root_node.children:
                    if not any(typ in child.type for typ in ["body", "block"]):
                        if label:
                            label = label + " "
                        label = label + child.text.decode().strip()
                type_label = "using"
                graph_node_list.append(
                    (
                        index[
                            (root_node.start_point, root_node.end_point, root_node.type)
                        ],
                        root_node.start_point[0],
                        label,
                        type_label,
                    )
                )

            elif root_node.type == "for_statement":
                init = root_node.child_by_field_name("initializer")
                condition = root_node.child_by_field_name("condition")
                update = root_node.child_by_field_name("update")
                label = f"for ( {cl(init)} ; {cl(condition)} ; {cl(update)} )"
                type_label = "for"

            elif root_node.type == "for_each_statement":
                l_type = root_node.child_by_field_name("type")
                l_left = root_node.child_by_field_name("left")
                l_right = root_node.child_by_field_name("right")
                label = f"foreach ( {cl(l_type)} {cl(l_left)} in {cl(l_right)} )"
                type_label = "foreach"

            elif root_node.type == "while_statement":
                label = ""
                block_hit = False
                for i, child in enumerate(root_node.children):
                    if not any(typ in child.type for typ in ["body", "block"]):
                        if not block_hit and len(root_node.children) - 1 == i:
                            continue
                        if label:
                            label = label + " "
                        label = label + child.text.decode().strip()
                type_label = "while"

            elif root_node.type == "do_statement":
                label = "do"
                type_label = "do"

            elif root_node.type == "switch_expression":
                parent_statement = return_switch_parent(
                    root_node, statement_types["non_control_statement"]
                )
                if parent_statement is not None:
                    label = parent_statement.text.decode("UTF-8").split("{")[0]
                # else:
                #     condition = list(filter(lambda child: child.type == 'parenthesized_expression', root_node.children))
                #     label = 'switch' + condition[0].text.decode('UTF-8')
                type_label = "switch_expression"

            elif root_node.type == "switch_statement":
                # parent_statement = return_switch_parent(root_node, statement_types['non_control_statement'])
                # if parent_statement is not None:
                #     label = parent_statement.text.decode('UTF-8').split('{')[0]
                # else:
                lvalue = root_node.child_by_field_name("value")
                label = f"switch ( {cl(lvalue)} )"
                type_label = "switch_statement"

            elif root_node.type == "switch_expression_arm":
                label = root_node.text.decode("UTF-8")
                type_label = "case_expression"
            elif root_node.type == "switch_section":
                type_label = "case"
                current_case_index = index[
                    (root_node.start_point, root_node.end_point, root_node.type)
                ]
                records["switch_equivalent_map"][current_case_index] = []
                parent_switch = return_index_of_first_parent_of_type(
                    root_node, "switch_statement"
                )
                parent_switch_index = index[
                    (
                        parent_switch.start_point,
                        parent_switch.end_point,
                        parent_switch.type,
                    )
                ]
                for equivalent_label in root_node.named_children:
                    if "label" in equivalent_label.type:
                        label = equivalent_label.text.decode("UTF-8").rsplit(":", 1)[0].strip()
                        label_index = index[
                            (
                                equivalent_label.start_point,
                                equivalent_label.end_point,
                                equivalent_label.type,
                            )
                        ]
                        if parent_switch_index not in records["label_switch_map"]:
                            records["label_switch_map"][parent_switch_index] = {}
                        records["label_switch_map"][parent_switch_index][
                            label
                        ] = label_index
                        records["switch_equivalent_map"][current_case_index].append(
                            label_index
                        )
                        graph_node_list.append(
                            (
                                label_index,
                                equivalent_label.start_point[0],
                                label,
                                type_label,
                            )
                        )

            elif root_node.type == "try_statement":
                # or root_node.type == 'try_with_resources_statement':
                label = "try"
                type_label = "try"

            # elif root_node.type == 'synchronized_statement':
            #     condition = list(filter(lambda child: child.type == 'parenthesized_expression', root_node.children))
            #     label = 'synchronized ' + condition[0].text.decode('UTF-8')
            #     type_label = 'synchronized'
            elif root_node.type == "labeled_statement":
                name = list(
                    filter(lambda child: child.type == "identifier", root_node.children)
                )
                label = name[0].text.decode("UTF-8").strip()
                records["label_statement_map"][label] = index[
                    (root_node.start_point, root_node.end_point, root_node.type)
                ]
                type_label = "label"

            elif root_node.type == "local_function_statement":
                label = ""
                for child in root_node.children:
                    if not any(typ in child.type for typ in ["body", "block"]):
                        if label:
                            label = label + " "
                        label = label + child.text.decode().strip()
                type_label = "local_function"
            elif root_node.type == "local_declaration_statement":
                label = ""
                for child in root_node.children:
                    if not any(typ in child.type for typ in ["body", "block"]):
                        if label:
                            label = label + " "
                        label = label + child.text.decode().strip()
                type_label = "local_declaration"
            elif root_node.type == "lock_statement":
                label = ""
                for child in root_node.children:
                    if not any(typ in child.type for typ in ["body", "block"]):
                        if label:
                            label = label + " "
                        label = label + child.text.decode().strip()
                type_label = "lock"
            # else:
            #     # TODO integrate logger.error
            #     label = ''
            #     for child in root_node.children:
            #         if not any(typ in child.type for typ in ["body", "block"]):
            #             label = label + child.text.decode().strip()
            #     type_label = root_node.type
            if root_node.type not in [
                "method_declaration",
                "constructor_declaration",
                "property_declaration",
                "switch_section",
            ]:
                graph_node_list.append(
                    (
                        index[
                            (root_node.start_point, root_node.end_point, root_node.type)
                        ],
                        root_node.start_point[0],
                        label,
                        type_label,
                    )
                )

    for child in root_node.children:
        # if child.parent.type == "local_declaration_statement":
        #     continue
        root_node, node_list, graph_node_list, records = get_nodes(
            root_node=child,
            node_list=node_list,
            graph_node_list=graph_node_list,
            index=index,
            records=records,
        )

    return root_node, node_list, graph_node_list, records
