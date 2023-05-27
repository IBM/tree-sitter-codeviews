from collections import defaultdict
import copy

import pprint

import networkx as nx

from ...utils.src_parser import traverse_tree
from ...utils.cs_nodes import statement_types
from deepdiff import DeepDiff

from loguru import logger

pp = pprint.PrettyPrinter(indent=4)
system_type = ("Console", "System", "String")
debug = False
# if any(
#     # GITHUB_ACTIONS
#     x in os.environ for x in ("PYCHARM_HOSTED",)
# ):
#     debug = True

def scope_check(parent_scope, child_scope):
    for p in parent_scope:
        if p not in child_scope:
            return False
    return True


class Identifier:
    def __init__(self, parser, node, line=None, declaration=False, full_ref=None, method_call=False):
        self.core = st(node)
        if full_ref is None:
            full_ref = node
        self.unresolved_name = st(full_ref)
        self.line = line
        self.declaration = declaration
        self.method_call = method_call
        self.satisfied = method_call
        if self.method_call and self.declaration:
            method_resolution = self.unresolved_name.split(".")
            # br.attribute2.attr.method1
            # Option 1 - method call affects main object
            # resolved_name = br
            # resolved_name = method_resolution[0]
            # resolved_name = br.attribute2.attr
            # Option 2 - method call only affects subattribute
            resolved_name = ".".join(method_resolution[:-1])
            self.name = resolved_name
        else:
            self.name = self.unresolved_name
        if not self.name:
            self.name = self.unresolved_name
        self.scope = parser.symbol_table["scope_map"][get_index(node, parser.index)]
        if line is not None:
            self.real_line_no = read_index(parser.index, line)[0][0]

    def __eq__(self, other):
        # if not isinstance(other, Identifier):
        #     return NotImplemented
        # if self.name == other.name:
        #     if other.line is None and other.line is not None:
        #         other.line = self.line
        #     elif other.line is not None and self.line is None:
        #         self.line = other.line

        # if self.method_call and self.declaration:
        #     method_resolution = self.name.split(".")
        #     # Option 1 - method call affects main object
        #     # resolved_name = method_resolution[0]
        #     # Option 2 - method call only affects subattribute
        #     resolved_name = ".".join(method_resolution[:-1])
        #     return resolved_name == other.name and self.line == other.line and sorted(self.scope) == sorted(
        #         other.scope)
        # else:
        return self.name == other.name and self.line == other.line and sorted(self.scope) == sorted(
            other.scope) and self.method_call == other.method_call

    def __hash__(self):
        # if self.method_call and self.declaration:
        #     method_resolution = self.name.split(".")
        #     # Option 1 - method call affects main object
        #     resolved_name = method_resolution[0]
        #     # Option 2 - method call only affects subattribute
        #     # resolved_name = ".".join(method_resolution[:-1])
        #     return hash((resolved_name, self.line, str(self.scope), False))
        # else:
        return hash((self.name, self.line, str(self.scope), self.method_call))

    def __str__(self):
        result = [self.name]
        if self.line:
            result += [str(self.real_line_no)]
            result += ['|'.join(map(str, self.scope))]
        else:
            result += ["?"]
        if self.method_call:
            result += ["()"]
        return f"{{{','.join(result)}}}"


def st(child):
    if child is None:
        # logger.error
        return ""
    else:
        return child.text.decode()


def get_index(node, index):
    try:
        return index[(node.start_point, node.end_point, node.type)]
    except:
        return None


def read_index(index, idx):
    return list(index.keys())[list(index.values()).index(idx)]


def parent_remapping_callback(node):
    if node is None:
        return None
    elif node.type == "do_statement":
        return None
    elif node.type == "try_statement":
        return None
        # while_node = None
        # for child in node.children:
        #     if child.type == "while":
        #         while_node = child.next_named_sibling
        #         break
        # return while_node
    else:
        return node


def return_first_parent_of_types(node, parent_types, stop_types=None):
    if stop_types is None:
        stop_types = []
    if node.type in parent_types:
        return parent_remapping_callback(node)
    while node.parent is not None:
        if node.type in stop_types:
            return None
        if node.parent.type in parent_types:
            return parent_remapping_callback(node.parent)
        node = node.parent
    return None


#
# def set_add(lst, item):
#     for entry in lst:
#         if item == entry:
#             return
#     lst.append(item)
#
#
# def set_union(first_list, second_list):
#     resulting_list = list(first_list)
#     for x in second_list:
#         set_add(resulting_list, x)
#     return resulting_list
#
#
# def set_difference(first_list, second_list):
#     resulting_list = []
#     for item in first_list:
#         match_found = False
#         for item2 in second_list:
#             if item == item2:
#                 match_found = True
#                 break
#         if not match_found:
#             resulting_list.append(item)
#     return resulting_list
#
#
# def set_intersection(first_list, second_list):
#     resulting_list = []
#     for item in first_list:
#         match_found = False
#         for item2 in second_list:
#             if item == item2:
#                 match_found = True
#                 break
#         if match_found:
#             resulting_list.append(item)
#     return resulting_list


def set_add(lst, item):
    for entry in lst:
        if item == entry:
            return
    lst.append(item)


def set_union(first_list, second_list):
    resulting_list = list(first_list)
    resulting_list.extend(x for x in second_list if x not in resulting_list)
    return resulting_list


def set_difference(first_list, second_list):
    resulting_list = [item for item in first_list if item not in second_list]
    return resulting_list


def set_intersection(first_list, second_list):
    resulting_list = [item for item in first_list if item in second_list]
    return resulting_list


def add_entry(parser, rda_table, statement_id, used=None, defined=None, declaration=False, core=None,
              method_call=False):
    if statement_id not in rda_table:
        rda_table[statement_id] = defaultdict(list)
    if not used and not defined:
        return
    if core is None:
        current_node = used or defined
        if current_node.type == "member_access_expression":
            recurse_node = recursively_get_children_of_types(current_node, ['identifier'], index=parser.index,
                                                             check_list=parser.symbol_table["scope_map"])
            if recurse_node:
                current_node = recurse_node[-1]
            if defined is not None:
                defined = current_node
            else:
                used = current_node
        if (
                current_node.parent is not None
                and current_node.parent.type == "member_access_expression"
        ):
            # LOOK AT THE SYMBOL TABLE COMMENT AS WELL #? TODO
            # object_node = current_node.parent.child_by_field_name("name")
            # object_index = get_index(object_node, parser.index)
            # current_index = get_index(current_node, parser.index)
            # if object_index == current_index:
            #     all_calls.append(current_index)

            while (
                    current_node.parent is not None
                    and current_node.parent.type == "member_access_expression"
            ):
                current_node = current_node.parent

            if (
                    current_node.parent is not None
                    and current_node.parent.type == "invocation_expression"
            ):
                if not st(current_node).startswith(system_type):
                    add_entry(parser, rda_table, statement_id, defined=used or defined, core=current_node, declaration=True,
                              method_call=True)
                    add_entry(parser, rda_table, statement_id, used=used or defined, core=current_node, declaration=True,
                              method_call=True)
                return
            if defined is not None:
                add_entry(parser, rda_table, statement_id, defined=defined, core=current_node, declaration=declaration, method_call=method_call)
            else:
                add_entry(parser, rda_table, statement_id, used=used, core=current_node, declaration=declaration, method_call=method_call)
            return
    if defined is not None:
        if get_index(defined, parser.index) not in parser.symbol_table["scope_map"]:
            return
        set_add(rda_table[statement_id]["def"],
                Identifier(parser, defined, statement_id, full_ref=core, declaration=declaration, method_call=method_call))
    else:
        if get_index(used, parser.index) not in parser.symbol_table["scope_map"]:
            return
        set_add(rda_table[statement_id]["use"],
                Identifier(parser, used, full_ref=core, declaration=declaration, method_call=method_call))


def check_field_name(req_child):
    for i, child in enumerate(req_child.parent.children):
        if req_child == child:
            field_type = child.parent.field_name_for_child(i)
            if field_type is not None and field_type == "type":
                return False
    return True


def recursively_get_children_of_types(
        node, st_types, check_list=None, index=None, result=None, stop_types=None
):
    if stop_types is None:
        stop_types = []
    if result is None:
        result = []
    if node.type in stop_types:
        return result
    if check_list and index:
        result.extend(
            list(
                filter(
                    lambda child: child.type in st_types
                                  and get_index(child, index) in check_list
                                  and check_field_name(child),
                    # and child.parent.type in ['variable_declaration', 'object_creation_expression',
                    #                           'member_access_expression'],
                    node.children,
                )
            )
        )
    else:
        result.extend(list(filter(lambda child: child.type in st_types, node.children)))
    for child in node.named_children:
        if child in stop_types:
            continue
        if child.type not in st_types:
            result = recursively_get_children_of_types(
                child, st_types, result=result, stop_types=stop_types, index=index, check_list=check_list
            )
    return result


def compute_out(old_result, connected_derivers, def_set):
    result = []
    for node in connected_derivers:
        result = set_union(result, old_result[node]["IN"])
    # for node in result:
    #     if node in def_set:
    #         continue
    return result


def compute_in(use_set, out_set, def_set, all_defs):
    result = set_union(use_set, set_difference(out_set, def_set))
    # for node in result:
    #     if node in all_defs:
    #         continue
    return result


def print_table(index, new_result, iteration=0):
    table = [f"\nRDA: iteration {iteration}\n"]
    for key in new_result:
        try:
            table.append(str(read_index(index, key)[0][0]+1)+"\n")
        except:
            table.append(str(key)+"\n")
        for key2 in new_result[key]:
            table.append(f"\t{key2}:")
            for entry in new_result[key][key2]:
                table.append(str(entry)+",")
            table.append("\n")
    logger.debug("".join(table))


def start_rda(index, rda_table, CFG_results):
    if debug:
        print_table(index, rda_table)
    cfg = CFG_results.graph
    nodes = CFG_results.graph.nodes
    old_result = {}
    iteration = 0
    for node in nodes:
        old_result[node] = {
            "IN": set(),
            "OUT": set()
        }
    # for node in nodes:
    #     connected_derivers = [t for (s, t) in cfg.out_edges(node)]
    #     old_result[node]["OUT"] = compute_out(old_result, connected_derivers, rda_table[node]["def"] if node in rda_table else [])
    new_result = copy.deepcopy(old_result)
    while True:
        iteration = iteration + 1
        for node in nodes:
            connected_feeders = [s for (s, t) in cfg.in_edges(node)]
            feeder_union = set()
            for feeder in connected_feeders:
                feeder_union = feeder_union.union(old_result[feeder]["OUT"])
            new_result[node]["IN"] = feeder_union
            def_info = rda_table[node]["def"] if node in rda_table else set()
            names_defined = [defined.name for defined in def_info]
            selective_difference = set()
            for already_defined in feeder_union:
                if already_defined.name in names_defined:
                    continue
                else:
                    selective_difference.add(already_defined)
            new_result[node]["OUT"] = selective_difference.union(def_info)
        ddiff = DeepDiff(
            old_result,
            new_result,
            ignore_order=True,
        )
        if ddiff == {}:
            # for node in nodes:
            #     all_defs = []
            #     connected_feeders = [t for (s, t) in cfg.in_edges(node)]
            #     for feeder in connected_feeders:
            #         defs = rda_table[feeder]["def"] if feeder in rda_table else []
            #         all_defs += defs
            #     for outgoing in new_result[node]["IN"]:
            #         if outgoing in all_defs:
            #             continue
            #     connected_derivers = [t for (s, t) in cfg.out_edges(node)]
            #     for deriver in connected_derivers:
            #         for incoming in new_result[deriver]["IN"]:
            #             if incoming in rda_table[node]["def"]:
            #                 continue
            if debug:
                logger.info("RDA: Completed in iteration {}", iteration)
                print_table(index, new_result, iteration)
            break
        old_result = copy.deepcopy(new_result)
    return new_result


def add_edge(final_graph, a, b, attrib=None, pre_solve=False):
    if (pre_solve and attrib) or not final_graph.has_edge(a, b):
        final_graph.add_edge(a, b)
        if attrib is not None:
            nx.set_edge_attributes(final_graph, {(a, b, 0): attrib})


def get_required_edges_from_def_to_use(index, cfg, rda_solution, rda_table, graph_nodes, properties=None):
    final_graph = copy.deepcopy(cfg)
    final_graph.remove_edges_from(list(final_graph.edges()))
    for node in graph_nodes:
        rda_info = rda_table[node] if node in rda_table else None
        if rda_info is not None:
            use_info = rda_info["use"]
            # def_info = rda_info["def"]
        else:
            use_info = set()
            # def_info = set()
        # names_used = [used.name for used in use_info]
        for used in use_info:
            for available_def in rda_solution[node]["IN"]:
                if available_def.name == used.name:
                    # if available_def in rda_table[available_def.line]["def"]:
                    if available_def.declaration:
                        if scope_check(available_def.scope, used.scope):
                            add_edge(final_graph, available_def.line, node)
                            used.satisfied = True
                    else:
                        add_edge(final_graph, available_def.line, node)
                        used.satisfied = True
                elif "." in used.name or "." in available_def.name:
                    if len(used.name.split(".")) < len(available_def.name.split(".")):
                        smaller = used
                        bigger = available_def
                    else:
                        smaller = available_def
                        bigger = used
                    if bigger.name.strip().startswith(smaller.name.strip()):
                        if not bigger.name.strip().replace(smaller.name.strip(), "").strip().startswith("."):
                            continue

                        # add_edge(final_graph, bigger.line or node, smaller.line or node)
                        add_edge(final_graph, available_def.line or node, used.line or node)
                        used.satisfied = True
            if not used.satisfied:
                if properties.get("last_use", False):
                    for i in rda_table:
                        for entry in rda_table[i]["use"]:
                            if entry.name == used.name and i != node:
                                # TODO: THIS IS AN AP - Make sure edges added here are right
                                if not nx.has_path(cfg, i, node):
                                    continue
                                add_edge(final_graph, i, node, {'color': 'green'})
        if properties.get("last_def", False):
            for available_def in rda_solution[node]["IN"] - rda_solution[node]["OUT"]:
                ignore_nodes = ['for_statement', 'while_statement', 'if_statement', 'switch_statement']
                if read_index(index, node)[-1] in ignore_nodes or read_index(index, available_def.line)[
                    -1] in ignore_nodes:
                    continue
                add_edge(final_graph, available_def.line, node, {'color': 'orange'})
        # for definition in def_info:
        #     for available_def in rda_solution[node]["IN"]:
        #         if "." in definition.name or "." in available_def.name:
        #             if len(definition.name.split(".")) < len(available_def.name.split(".")):
        #                 smaller = definition
        #                 bigger = available_def
        #             else:
        #                 smaller = available_def
        #                 bigger = definition
        #             if bigger.name.strip().startswith(smaller.name.strip()):
        #                 if not bigger.name.strip().replace(smaller.name.strip(), "").strip().startswith("."):
        #                     continue
        #                 # add_edge(final_graph, bigger.line or node, smaller.line or node)
        #                 add_edge(final_graph, smaller.line or node, bigger.line or node)

    return final_graph


def rda_cfg_map(rda_solution, CFG_results):
    graph = CFG_results.graph
    attrs = {}
    for edge in list(graph.edges):
        out_set = rda_solution[edge[0]]["OUT"]
        in_set = rda_solution[edge[1]]["IN"]
        intersection = set_intersection(out_set, in_set)
        data = graph.get_edge_data(*edge)
        if intersection:
            data['label'] = ",".join([str(intr) for intr in intersection])
        else:
            graph.remove_edge(*edge)
            # logger.warning("Unable to remap edge {}", edge)
        attrs[edge] = data
    nx.set_edge_attributes(graph, attrs)
    return graph


def dfg_csharp(properties, CFG_results):
    properties = properties
    parser = CFG_results.parser
    index = parser.index
    tree = parser.tree
    assignment = ["assignment_expression"]
    def_statement = ["variable_declarator"]
    increment_statement = ["postfix_unary_expression", "prefix_unary_expression"]
    variable_type = ['identifier', 'this_expression']
    method_calls = ["invocation_expression"]

    switch_type = ['switch_expression', 'switch_statement']
    # switch_cases = ['switch_expression_arm', 'switch_section']
    handled_cases = ["switch_section", "local_declaration_statement"]

    method_declaration = ['method_declaration']
    handled_types = assignment + def_statement + increment_statement + method_calls + method_declaration + switch_type

    # if_statement = ["if_statement", "else"]
    # for_statement = ["for_statement"]
    # enhanced_for_statement = ["for_each_statement"]
    # while_statement = ["while_statement"]

    rda_table = {}
    for root_node in traverse_tree(tree, variable_type):
        if not root_node.is_named:
            if root_node.type == "while" and root_node.parent.type == "do_statement":
                root_node = root_node.next_named_sibling
                parent_id = get_index(root_node, index)
                identifiers_used = recursively_get_children_of_types(root_node, variable_type, index=parser.index,
                                                                     check_list=parser.symbol_table["scope_map"])
                for identifier in identifiers_used:
                    add_entry(parser, rda_table, parent_id, used=identifier)
            else:
                continue
        if root_node.type == "catch_clause":
            parent_id = get_index(root_node, index)
            if len(root_node.named_children) > 1:
                identifiers_used = recursively_get_children_of_types(root_node.named_children[-2], variable_type,
                                                                     index=parser.index,
                                                                     check_list=parser.symbol_table["scope_map"])
                if identifiers_used:
                    add_entry(parser, rda_table, parent_id, defined=identifiers_used[-1])
        if root_node.type == "return_statement":
            parent_id = get_index(root_node, index)
            if len(root_node.children) < 2:
                continue
            if root_node.children[1].type == "method_invocation":
                continue
            identifiers_used = recursively_get_children_of_types(root_node, variable_type, index=parser.index,
                                                                 check_list=parser.symbol_table["scope_map"])
            for identifier in identifiers_used:
                add_entry(parser, rda_table, parent_id, used=identifier)
        if root_node.type in def_statement:
            parent_statement = return_first_parent_of_types(root_node, statement_types["node_list_type"])
            parent_id = get_index(parent_statement, index)
            if parent_id not in CFG_results.graph.nodes:
                if parent_statement and parent_statement.type in handled_cases:
                    continue
                raise NotImplementedError
            # print(parent_id)
            # print(st(parent_statement))
            if len(root_node.children) == 2:
                name = root_node.children[0]
                value = root_node.children[1]
            else:
                name = root_node.children[0]
                value = None
            add_entry(parser, rda_table, parent_id, defined=name, declaration=True)
            if value is not None:
                identifiers_used = recursively_get_children_of_types(value, variable_type, index=parser.index,
                                                                     check_list=parser.symbol_table["scope_map"])
                for identifier in identifiers_used:
                    add_entry(parser, rda_table, parent_id, used=identifier)
        elif root_node.type in assignment:
            parent_statement = return_first_parent_of_types(root_node, statement_types["node_list_type"])
            parent_id = get_index(parent_statement, index)
            # print(parent_id)
            # print(st(parent_statement))
            left_nodes = root_node.child_by_field_name("left")
            right_node = root_node.child_by_field_name("right")
            operator_text = (
                root_node.text.split(left_nodes.text, 1)[-1]
                .rsplit(right_node.text, 1)[0]
                .strip()
                .decode()
            )
            right_nodes = [right_node]
            # JRef
            if parent_id not in CFG_results.graph.nodes:
                if parent_statement and parent_statement.type in handled_cases:
                    continue
                elif parent_statement.type == "expression_statement":
                    if recursively_get_children_of_types(parent_statement, ["switch_expression"]) is not None:
                        switch_expression = recursively_get_children_of_types(parent_statement, ["switch_expression"])
                        left_nodes = switch_expression[0].parent.children[0]
                        operator_text = switch_expression[0].parent.children[1].text
                        right_nodes = []
                else:
                    raise NotImplementedError
            # operator = root_node.child()
            # operator_text = operator.text.decode('utf-8')
            if operator_text != "=":
                right_nodes.append(left_nodes)
            # TODO triage
            add_entry(parser, rda_table, parent_id, defined=left_nodes)
            for node in right_nodes:
                if node.type in variable_type:
                    add_entry(parser, rda_table, parent_id, used=node)
                else:
                    identifiers_used = recursively_get_children_of_types(node, variable_type, index=parser.index,
                                                                         check_list=parser.symbol_table["scope_map"])
                    for identifier in identifiers_used:
                        add_entry(parser, rda_table, parent_id, used=identifier)
        elif root_node.type in increment_statement:
            parent_statement = return_first_parent_of_types(root_node, statement_types["node_list_type"])
            parent_id = get_index(parent_statement, index)
            if parent_id not in CFG_results.graph.nodes:
                if parent_statement and parent_statement.type in handled_cases:
                    continue
                raise NotImplementedError
            # print(parent_id)
            # print(st(parent_statement))
            if root_node.type in variable_type:
                add_entry(parser, rda_table, parent_id, used=root_node)
            else:
                identifiers_used = recursively_get_children_of_types(root_node, variable_type, index=parser.index,
                                                                     check_list=parser.symbol_table["scope_map"])
                for identifier in identifiers_used:
                    add_entry(parser, rda_table, parent_id, used=identifier)
                    add_entry(parser, rda_table, parent_id, defined=identifier)
        elif root_node.type in method_calls:
            parent_statement = return_first_parent_of_types(root_node, statement_types["node_list_type"])
            parent_id = get_index(parent_statement, index)
            if parent_id not in CFG_results.graph.nodes:
                if parent_statement and parent_statement.type in handled_cases:
                    continue
                raise NotImplementedError
            add_entry(parser, rda_table, parent_id, used=root_node.children[0], method_call=True)
            for node in root_node.children[1:]:
                if node.type in variable_type:
                    if return_first_parent_of_types(node, 'invocation_expression') is None:
                        add_entry(parser, rda_table, parent_id, used=node)
                else:
                    identifiers_used = recursively_get_children_of_types(node, variable_type, index=parser.index,
                                                                         check_list=parser.symbol_table["scope_map"])
                    for identifier in identifiers_used:
                        add_entry(parser, rda_table, parent_id, used=identifier)
        elif root_node.type in method_declaration:
            parent_id = get_index(root_node, index)
            for child in root_node.named_children:
                if child.type == "parameter_list":
                    for parameter in child.named_children:
                        if parameter.type == "parameter":
                            identifier = parameter.child_by_field_name("name")
                            if identifier.parent.type == "identifier" and not identifier.text:
                                identifier = identifier.parent
                            add_entry(parser, rda_table, parent_id, defined=identifier)
                    break
        elif root_node.type in switch_type:
            parent_statement = root_node
            parent_id = get_index(root_node, index)
            if parent_id not in CFG_results.graph.nodes:
                if parent_statement and parent_statement.type in handled_cases:
                    continue
                raise NotImplementedError
            if parent_statement.type == 'switch_expression':
                add_entry(parser, rda_table, parent_id, used=root_node.children[0])
            elif parent_statement.type == 'switch_statement':
                case_node = parent_statement.child_by_field_name("value")
                add_entry(parser, rda_table, parent_id, used=case_node)
        elif root_node.type == "for_each_statement":
            parent_statement = root_node
            parent_id = get_index(root_node, index)
            defined_node = parent_statement.child_by_field_name("left")
            used_node = parent_statement.child_by_field_name("right")
            add_entry(parser, rda_table, parent_id, defined=defined_node, declaration=True)
            add_entry(parser, rda_table, parent_id, used=used_node)
        else:
            # THIS ELSE IS VERY INEFFICIENT
            # Essentially considers all variable references as use
            # if return_first_parent_of_types(root_node, handled_types) is None:
            parent_statement = return_first_parent_of_types(
                root_node,
                # statement_types["node_list_type"],
                # [x for x in statement_types["node_list_type"] if x not in block_types],
                statement_types["non_control_statement"] + statement_types["control_statement"],
                stop_types=['block'] + handled_types
            )
            parent_id = get_index(parent_statement, index)
            if parent_id is None:
                continue
            if parent_id not in CFG_results.graph.nodes:
                if parent_statement and parent_statement.type in handled_cases:
                    continue
                raise NotImplementedError
            # print(root_node.type)
            # print(parent_statement.type)

            # print("...")

            # print(parent_id)
            # print(st(parent_statement))

            # if parent_statement and parent_statement.type in block_types:
            #     continue

            # if root_node.type in variable_type:
            #     add_entry(parser, rda_table, parent_id, used=root_node)
            # else:
            identifiers_used = recursively_get_children_of_types(root_node, variable_type, stop_types=handled_types,
                                                                 index=parser.index,
                                                                 check_list=parser.symbol_table["scope_map"])
            for identifier in identifiers_used:
                add_entry(parser, rda_table, parent_id, used=identifier)
    rda_solution = start_rda(index, rda_table, CFG_results)
    # pp.pprint(rda_solution)
    final_graph = get_required_edges_from_def_to_use(CFG_results.parser.index, CFG_results.graph, rda_solution, rda_table,
                                                     CFG_results.graph.nodes, properties=properties)
    debug_graph = rda_cfg_map(rda_solution, CFG_results)
    return final_graph, debug_graph, rda_table, rda_solution
