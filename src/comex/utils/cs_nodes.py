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
# based on handling simmilarity
statement_types = {
    "node_list_type": non_control_statements
    + control_statements
    + ["method_declaration"],
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
}
# TODO: add method_return_types

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
            if root_node.type in [
                "method_declaration",
                "interface_declaration",
                "constructor_declaration",
                "property_declaration",
            ]:
                method_name = list(
                    filter(lambda child: child.type == "identifier", root_node.children)
                )
                parameter_list = list(
                    filter(
                        lambda child: child.type == "parameter_list", root_node.children
                    )
                )
                label = method_name[-1].text.decode("UTF-8")
                if parameter_list:
                    label = label + parameter_list[0].text.decode("UTF-8")
                type_label = root_node.type
                # ? make sure records is being updated for the newer updates if required
                records["method_list"][method_name[-1].text.decode("UTF-8")] = index[
                    root_node.start_point, root_node.end_point, root_node.type
                ]
                graph_node_list.append(
                    (
                        index[
                            (root_node.start_point, root_node.end_point, root_node.type)
                        ],
                        method_name[-1].start_point[0],
                        label,
                        type_label,
                    )
                )
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
