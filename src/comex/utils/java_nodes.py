statement_types = {
    "node_list_type": [
        "declaration",
        "expression_statement",
        "labeled_statement",
        "if_statement",
        "while_statement",
        "for_statement",
        "enhanced_for_statement",
        "assert_statement",
        "do_statement",
        "break_statement",
        "continue_statement",
        "return_statement",
        "yield_statement",
        "switch_expression",
        "synchronized_statement",
        "local_variable_declaration",
        "throw_statement",
        "try_statement",
        "try_with_resources_statement",
        "method_declaration",
        "constructor_declaration",
        "switch_block_statement_group",
        "switch_rule",
        "throw_statement",
        "explicit_constructor_invocation",
        "class_declaration",
        "field_declaration",
        "import_declaration",
        "lambda_expression",
        "interface_declaration"
    ],
    "non_control_statement": [
        "declaration",
        "expression_statement",
        "local_variable_declaration",
        "explicit_constructor_invocation",
        "assert_statement",
        "field_declaration",
        "import_declaration"
    ],  # ON extending support fo files, explicit constructor invocation needs to be handled
    "control_statement": [
        "if_statement",
        "while_statement",
        "for_statement",
        "enhanced_for_statement",
        "do_statement",
        "break_statement",
        "continue_statement",
        "return_statement",
        "yield_statement",
        "switch_expression",
        "synchronized_statement",
        "try_statement",
        "try_with_resources_statement",
        "yield_statement",
    ],
    "loop_control_statement": [
        "while_statement",
        "for_statement",
        "enhanced_for_statement",
    ],
    "not_implemented": [],
    "inner_node_type": [
        "declaration",
        "expression_statement",
        "local_variable_declaration",
    ],
    "outer_node_type": ["for_statement"],
    "statement_holders": [
        "block",
        "switch_block_statement_group",
        "switch_block",
        "constructor_body",
        "class_body",
        "module_body",
        "program"
    ],
    "definition_types": ["method_declaration", "constructor_declaration", "class_declaration", "field_declaration", "interface_declaration"]
}

method_return_types = ['integral_type', 'void_type', 'type_identifier', 'generic_type', 'scoped_type_identifier', 'floating_point_type', 'boolean_type', 'array_type']

def get_child_of_type(node, type_list):
    out = list(filter(lambda x : x.type in type_list, node.children))
    if len(out) > 0:
        return out[0]
    else: 
        return None
    
def return_switch_child(node):
    # Make it breadthfirst search, and return if you hit a node_list_type
    bfs_queue = []
    for child in node.children:
        bfs_queue.append(child)
    while bfs_queue != []:
        top = bfs_queue.pop(0)
        if top.type == "switch_expression":
            return top
        if top.type in statement_types["node_list_type"]:
            return None
        for child in top.children:
            bfs_queue.append(child)
    return None

def return_switch_parent(node, non_control_statement):
    """Searches for a switch expression while going up the tree and returns it"""
    
    while node.parent is not None and (node.parent.type != "class_body" and node.parent.type != "method_body"):
        if node.parent.type == "block" and node.type == "switch_expression":
            return node
        if node.parent.type in non_control_statement:
            return node.parent
        node = node.parent
    return None

def return_switch_parent_statement(node, non_control_statement):
    """Searches for a switch expression while going up the tree and returns it"""
    
    while node.parent is not None and (node.parent.type != "class_body" and node.parent.type != "method_body"):
        if node.parent.type in non_control_statement:
            return node.parent
        node = node.parent
    return None

def has_inner_definition(node):
    """Checks if a node has a definition inside it"""
    if node.type in statement_types["definition_types"]:
        return True
    for child in node.children:
        if has_inner_definition(child):
            return True
    return False
def find_method_declaration(node):
    """Searches for a method declaration while going up the tree and returns it"""
    while node.parent is not None:
        if node.parent.type == "method_declaration":
            return node.parent
        node = node.parent
    return None
# def get_last_node(node):
#     """Returns the last statement in the method block"""

def get_signature(node):
    signature = []
    formal_parameters = node.child_by_field_name('parameters')
    formal_parameters = list(filter(lambda x: x.type == 'formal_parameter', formal_parameters.children))
    for formal_parameter in formal_parameters:
        for child in formal_parameter.children:
            if child.type != "identifier":
                signature.append(child.text.decode('utf-8'))
    return tuple(signature)

def get_anonymous_class(node):
    """Checks if a node contains an anonymous class and returns it breadthfirst"""
    bfs_queue = []
    bfs_queue.append(node)
    while bfs_queue != []:
        top = bfs_queue.pop(0)
        if top.type == "class_body" and top.parent.type == "object_creation_expression":
            return top
        for child in top.children:
            bfs_queue.append(child)
    return None

def check_anonymous_class(node):
    """Checks if a node contains a lambda expression"""
    if get_anonymous_class(node) is None:
        return False
    else:
        initial_node = node
        class_node = get_anonymous_class(node)
        parent_node = class_node.parent
        while parent_node is not None:
            if parent_node.type in statement_types["node_list_type"]:            
                if parent_node == initial_node:
                    return True
                else:
                    return False
            parent_node = parent_node.parent

def get_lambda_body_depth(node):
    """Returns the body of a lambda expression"""
    for child in node.children:
        if get_lambda_body(child) is not None:
            return get_lambda_body(child)
        elif child.type == "lambda_expression":
            return child
    return None

def get_lambda_body(node):
    """Returns the body of a lambda expression, breadthfirst"""
    bfs_queue = []

    bfs_queue.append(node)
    while bfs_queue != []:
        top = bfs_queue.pop(0)
        if top.type == "lambda_expression":
            return top
        for child in top.children:
            bfs_queue.append(child)
    return None

def get_all_lambda_body(node):
    """Returns the body of a lambda expression, breadthfirst"""
    bfs_queue = []
    output = []
    bfs_queue.append(node)
    while bfs_queue != []:
        top = bfs_queue.pop(0)
        if top.type == "lambda_expression":
            output.append(top)
        for child in top.children:
            if child.type == "lambda_expression" or child.type not in statement_types["node_list_type"]:
                bfs_queue.append(child)

    return output

def check_lambda(node):
    """Checks if a node contains a lambda expression"""
    if get_lambda_body(node) is None:
        return False
    else:
        initial_node = node
        lambda_node = get_lambda_body(node)
        parent_node = lambda_node.parent
        while parent_node is not None:
            if parent_node.type in statement_types["node_list_type"]:
                
                if parent_node == initial_node:
                    return True
                else:
                    return False
            parent_node = parent_node.parent

def abstract_method(node):
    method_body = get_child_of_type(node, ["block"])
    while node is not None:
        if node.type == "class_body" and node.parent.type == "class_declaration":
            node = node.parent

            modifiers = get_child_of_type(node, ["modifiers"])
            if modifiers is not None and "abstract" in modifiers.text.decode("utf-8") and method_body is None:
                return True
        node = node.parent
    return False

def get_class_name(node, index):
    "Returns the class name when a method declaration or constructor declaration is passed to it"
    type_identifiers = ["type_identifier", "generic_type", "scoped_type_identifier"]
    while node is not None:
        if node.type == "class_body" and node.parent.type == "class_declaration":
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
        
        elif node.type == "class_body" and node.parent.type == "object_creation_expression":
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

    if (
        root_node.type == "parenthesized_expression"
        and root_node.parent is not None
        and root_node.parent.type == "do_statement"
    ):
        label = "while" + root_node.text.decode("UTF-8")
        type_label = "while"
        node_list[(root_node.start_point, root_node.end_point, root_node.type)] = root_node
        graph_node_list.append((index[(root_node.start_point, root_node.end_point, root_node.type)],root_node.start_point[0],label,type_label))

    elif root_node.type == "catch_clause":
        node_list[(root_node.start_point, root_node.end_point, root_node.type)] = root_node
        catch_parameter = list(filter(lambda child: child.type == "catch_formal_parameter", root_node.children))
        label = "catch (" + catch_parameter[0].text.decode("UTF-8") + ")"
        type_label = "catch"
        graph_node_list.append((index[(root_node.start_point, root_node.end_point, root_node.type)],root_node.start_point[0],label,type_label))

    elif root_node.type == "finally_clause":
        node_list[(root_node.start_point, root_node.end_point, root_node.type)] = root_node
        label = "finally"
        type_label = "finally"
        graph_node_list.append((index[(root_node.start_point, root_node.end_point, root_node.type)],root_node.start_point[0],label,type_label))

    elif root_node.type in statement_types["node_list_type"]:
        if (
            root_node.type in statement_types["inner_node_type"]
            and root_node.parent is not None
            and root_node.parent.type in statement_types["outer_node_type"]
            and root_node.parent.child_by_field_name("body") != root_node
        ):
            pass
            # If it has a parent and the parent is a for loop type and it is an initialization or update statement, omit it
        elif (
            root_node.type in statement_types["inner_node_type"]
            and return_switch_child(root_node) is not None
        ):
            # There is a switch expression in the subtree starting from this statement_node
            switch_child = return_switch_child(root_node)
            child_index = index[(switch_child.start_point, switch_child.end_point, switch_child.type)]
            current_index = index[(root_node.start_point, root_node.end_point, root_node.type)]
            records["switch_child_map"][current_index] = child_index
        else:
            node_list[(root_node.start_point, root_node.end_point, root_node.type)] = root_node
            # Set default label values for the node and then modify based on node type if required in the following if-else ladder
            label = root_node.text.decode("UTF-8")
            type_label = "expression_statement"
            if check_anonymous_class(root_node) and root_node.type not in statement_types["definition_types"]:
                try:
                    label = label.split("{")[0] + label.split("}")[-1]
                except:
                    # print("INCORRECT anonymous class label", label)
                    pass
            # elif check_lambda(root_node) and root_node.type not in statement_types["definition_types"]:
            elif check_lambda(root_node) and root_node.type not in statement_types["definition_types"]:
                raw_label = root_node.text.decode("utf-8")

                label = ""
                for lambda_expression in get_all_lambda_body(root_node):
                    split_label = raw_label.split(lambda_expression.text.decode("utf-8"),2)
                    raw_label = split_label[0]
                    if len(split_label) >1:
                        label = split_label[1] + label
                    lambda_node = (lambda_expression.start_point, lambda_expression.end_point, lambda_expression.type)
                    records["lambda_map"][lambda_node] = root_node
                label = raw_label + label

            elif root_node.type == "lambda_expression":
                try:
                    if "{" in label:
                        label = label.split("{")[0] + label.split("}")[-1]
                    else:
                        label = root_node.text.decode('utf-8')
                except:
                    raise Exception("INCORRECT lambda expression label", label)
                    # print("INCORRECT lambda expression label", label)

            elif (root_node.type == "method_declaration" or root_node.type == "constructor_declaration"):
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
                    if method_name == "main":
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

                except:
                    pass
                graph_node_list.append((method_index, root_node.start_point[0],label,type_label))
            elif (
                root_node.type == "class_declaration"
                # or root_node.type == "constructor_declaration"
            ):
                modifiers = list(filter(lambda child: child.type != "class_body", root_node.children))
                class_name = list(filter(lambda child: child.type == "identifier", root_node.children))[0].text.decode("UTF-8")
                label = ""
                for modifier in modifiers:
                    label = label + modifier.text.decode("UTF-8") + " "
                type_label = root_node.type
                class_index = index[(root_node.start_point, root_node.end_point, root_node.type)]
                records["class_list"][class_name] = class_index

                superclass_node = get_child_of_type(root_node, ["superclass"])
                if superclass_node is not None:
                    parent_name = get_child_of_type(superclass_node, ["type_identifier", "generic_type", "scoped_type_identifier"]).text.decode("UTF-8")
                    try:
                        records['extends'][class_name].append(parent_name)
                    except:
                        records['extends'][class_name] = [parent_name]

            
            elif root_node.type == "interface_declaration":
                definition = list(
                    filter(
                        lambda child: child.type != "interface_body",
                        root_node.children,
                    )
                )
                label = ""
                for x in definition:
                    label = label + x.text.decode("UTF-8") + " "
                
                type_label = "interface_declaration"

            elif root_node.type == "if_statement":
                condition = list(
                    filter(
                        lambda child: child.type == "parenthesized_expression",
                        root_node.children,
                    )
                )
                label = "if" + condition[0].text.decode("UTF-8")
                type_label = "if"

            elif root_node.type == "for_statement":
                try:
                    init = root_node.child_by_field_name("init").text.decode("UTF-8")
                    if init[-1] != ";":
                        init = init + ";"
                except:
                    init = ""
                try:
                    condition = root_node.child_by_field_name("condition").text.decode(
                        "UTF-8"
                    )
                except:
                    condition = ""
                try:
                    update = root_node.child_by_field_name("update").text.decode(
                        "UTF-8"
                    )
                except:
                    update = ""
                label = "for(" + init + condition + ";" + update + ")"
                type_label = "for"

            elif root_node.type == "enhanced_for_statement":
                try:
                    modifiers = str(
                        list(
                            filter(
                                lambda child: child.type == "modifiers",
                                root_node.children,
                            )
                        )
                    )
                    modifier = modifiers[0].text.decode("UTF-8")
                except:
                    modifier = ""
                try:
                    types = root_node.child_by_field_name("type").text.decode("UTF-8")
                except:
                    types = ""

                try:
                    variables = list(
                        filter(
                            lambda child: child.type == "identifier", root_node.children
                        )
                    )
                    variable = variables[0].text.decode("UTF-8")
                except:
                    variable = ""
                try:
                    value = root_node.child_by_field_name("value").text.decode("UTF-8")
                except:
                    value = ""
                label = (
                    "for(" + modifier + " " + types + " " + variable + ":" + value + ")"
                )
                type_label = "for"

            elif root_node.type == "while_statement":
                condition = list(
                    filter(
                        lambda child: child.type == "parenthesized_expression",
                        root_node.children,
                    )
                )
                label = "while" + condition[0].text.decode("UTF-8")
                type_label = "while"

            elif root_node.type == "do_statement":
                label = "do"
                type_label = "do"

            elif root_node.type == "switch_expression":
                parent_statement = return_switch_parent(root_node, statement_types["non_control_statement"])
                if parent_statement is not None:
                    label = parent_statement.text.decode("UTF-8").split("{")[0]
                else:
                    condition = list(filter(lambda child: child.type == "parenthesized_expression",root_node.children))
                    label = "switch" + condition[0].text.decode("UTF-8")
                type_label = "switch"

            elif (
                root_node.type == "switch_block_statement_group"
                or root_node.type == "switch_rule"
            ):
                case_label = list(
                    filter(
                        lambda child: child.type == "switch_label", root_node.children
                    )
                )
                label = case_label[0].text.decode("UTF-8") + ":"
                type_label = "case"

            elif (
                root_node.type == "try_statement"
                or root_node.type == "try_with_resources_statement"
            ):
                label = "try"
                type_label = "try"

            elif root_node.type == "synchronized_statement":
                condition = list(
                    filter(
                        lambda child: child.type == "parenthesized_expression",
                        root_node.children,
                    )
                )
                label = "synchronized " + condition[0].text.decode("UTF-8")
                type_label = "synchronized"
            elif root_node.type == "labeled_statement":
                name = list(
                    filter(lambda child: child.type == "identifier", root_node.children)
                )
                label = name[0].text.decode("UTF-8") + ":"
                records["label_statement_map"][label] = (
                    root_node.start_point,
                    root_node.end_point,
                    root_node.type,
                )
                type_label = "label"
            elif root_node.type == "return_statement":
                if has_inner_definition(root_node):
                    label = "return"
                else:
                    label = root_node.text.decode("UTF-8")
                type_label = "return"
            
            if (
                root_node.type != "method_declaration"
                and root_node.type != "constructor_declaration"
            ):
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
        root_node, node_list, graph_node_list, records = get_nodes(
            root_node=child,
            node_list=node_list,
            graph_node_list=graph_node_list,
            index=index,
            records=records,
        )

    return root_node, node_list, graph_node_list, records
