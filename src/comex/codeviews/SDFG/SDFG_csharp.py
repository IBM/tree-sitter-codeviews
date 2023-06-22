import os
import time
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
#         # GITHUB_ACTIONS
#         x in os.environ for x in ("PYCHARM_HOSTED",)
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
        class_node = return_first_parent_of_types(node, "class_declaration")
        if full_ref is None:
            full_ref = node
        self.parent_class = class_node
        self.unresolved_name = st(full_ref)
        if self.unresolved_name.startswith("this."):
            self.unresolved_name = st(full_ref)[5:]
        if class_node is not None:
            class_name = st(class_node.child_by_field_name("name"))
            self.parent_class = class_name
            if self.unresolved_name.startswith(class_name + "."):
                self.unresolved_name = self.unresolved_name[len(class_name) + 1:]
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
        if node.parent.type == "member_access_expression":
            og_node = node.parent
            node = recursively_get_children_of_types(og_node, ['identifier'], index=parser.index,
                                                                 check_list=parser.symbol_table["scope_map"])[0]
        variable_index = get_index(node, parser.index)
        self.variable_scope = parser.symbol_table["scope_map"][variable_index]
        if variable_index in parser.declaration_map:
            self.scope = parser.symbol_table["scope_map"][parser.declaration_map[variable_index]]
        else:
            # self.scope = variable_scope
            # Declaration does not exist hence it is given
            # the outermost scope
            self.scope = [0]
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
        return node.named_children[-1]
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
    mapped_node = None
    if core is None:
        current_node = used or defined
        if current_node.type == "member_access_expression":
            current_node = recursively_get_children_of_types(current_node, ['identifier'], index=parser.index,
                                                             check_list=parser.symbol_table["scope_map"])[-1]
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
                    if (used or defined).type == "identifier":
                        method_cs = (used or defined).parent.named_children[0]
                        # set_add(rda_table[statement_id]["def"],
                        #         Identifier(parser, (used or defined).parent.named_children[0], statement_id, full_ref=None,
                        #                    # declaration=True,
                        #                    method_call=True))
                    add_entry(parser, rda_table, statement_id, defined=used or defined, core=method_cs,
                              # declaration=True,
                              method_call=True)
                    add_entry(parser, rda_table, statement_id, used=used or defined, core=method_cs,
                              # declaration=True,
                              method_call=True)
                if mapped_node is not None:
                    set_add(rda_table[statement_id]["def"],
                            Identifier(parser, mapped_node, statement_id, full_ref=mapped_node, declaration=declaration,
                                       method_call=method_call))
                return
            if defined is not None:
                add_entry(parser, rda_table, statement_id, defined=defined, core=current_node, declaration=declaration,
                          method_call=method_call)
                if mapped_node is not None:
                    set_add(rda_table[statement_id]["def"],
                            Identifier(parser, mapped_node, statement_id, full_ref=mapped_node, declaration=declaration,
                                       method_call=method_call))
            else:
                add_entry(parser, rda_table, statement_id, used=used, core=current_node, declaration=declaration,
                          method_call=method_call)
            return
        elif current_node.next_sibling and current_node.next_sibling.type == "." and current_node.parent is not None and current_node.parent.type == "invocation_expression":
            if not st(current_node).startswith(system_type):
                if (used or defined).type == "identifier":
                    set_add(rda_table[statement_id]["def"],
                            Identifier(parser, used or defined, statement_id, full_ref=None,
                                       # declaration=True,
                                       method_call=True))
    if st(core).startswith(system_type):
        return
    if defined is not None:
        if get_index(defined, parser.index) not in parser.symbol_table["scope_map"]:
            return
        set_add(rda_table[statement_id]["def"],
                Identifier(parser, defined, statement_id, full_ref=core, declaration=declaration,
                           method_call=method_call))
        if mapped_node is not None:
            set_add(rda_table[statement_id]["def"],
                    Identifier(parser, mapped_node, statement_id, full_ref=mapped_node, declaration=declaration,
                               method_call=method_call))
    else:
        if get_index(used, parser.index) not in parser.symbol_table["scope_map"]:
            return
        if mapped_node is not None and method_call:
            set_add(rda_table[statement_id]["def"],
                    Identifier(parser, mapped_node, statement_id, full_ref=mapped_node, declaration=declaration,
                               method_call=method_call))
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
        additional_cs = []
        for n in result:
            if n.type == "parameter" and n == n.parent.named_children[0]:
                additional_cs.append(n)
        for n in additional_cs:
            result.remove(n)
    for child in node.named_children:
        if node.type == "parameter" and child == node.named_children[0]:
            continue
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
            table.append(str(read_index(index, key)[0][0] + 1) + "\n")
        except:
            table.append(str(key) + "\n")
        for key2 in new_result[key]:
            table.append(f"\t{key2}:")
            for entry in new_result[key][key2]:
                table.append(str(entry) + ",")
            table.append("\n")
    logger.debug("".join(table))


def start_rda(index, rda_table, graph, pre_solve=False):
    if debug and not pre_solve:
        print_table(index, rda_table)
    remove_set = []
    # "method_return", "class_return"
    if pre_solve:
        remove_set = ["method_call", "method_return", "class_return", "constructor_call"]
    graph = copy.deepcopy(graph)
    remove_edges = []
    if remove_set:
        for edge in graph.edges:
            if "label" in graph.edges[edge] and graph.edges[edge]["label"] in remove_set:
                remove_edges.append(edge)
        graph.remove_edges_from(remove_edges)

    cfg = graph
    nodes = graph.nodes
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
        iteration_returners = {}
        for node in nodes:
            connected_feeders = []
            returning_feeders = []
            for (s, t) in cfg.in_edges(node):
                if "label" in cfg.edges[s, t, 0] and cfg.edges[s, t, 0]["label"] in ["method_return", "class_return"]:
                    returning_feeders.append(s)
                else:
                    connected_feeders.append(s)
            feeder_union = set()
            returner_union = set()
            for feeder in connected_feeders:
                feeder_union = feeder_union.union(old_result[feeder]["OUT"])
            for returner in returning_feeders:
                returner_union = returner_union.union(old_result[returner]["OUT"])
            for (s, t) in cfg.out_edges(node):
                if s != t:
                    iteration_returners[t] = iteration_returners[t].union(
                        returner_union) if t in iteration_returners else returner_union
            new_result[node]["IN"] = feeder_union
            def_info = rda_table[node]["def"] if node in rda_table else set()
            names_defined = [defined.name for defined in def_info]
            # if defined.param_declaration is None
            selective_difference = set()
            for already_defined in feeder_union:
                # if already_defined.immutable_declaration:
                #     selective_difference.add(already_defined)
                if already_defined.name in names_defined:
                    continue
                else:
                    selective_difference.add(already_defined)
            new_result[node]["OUT"] = selective_difference.union(def_info)
        for node in iteration_returners:
            def_info = rda_table[node]["def"] if node in rda_table else set()
            names_defined = [defined.name for defined in def_info]
            selective_difference = set()
            for already_defined in iteration_returners[node]:
                # if already_defined.immutable_declaration:
                #     selective_difference.add(already_defined)
                if already_defined.name in names_defined:
                    continue
                else:
                    selective_difference.add(already_defined)
            new_result[node]["OUT"] = new_result[node]["OUT"].union(selective_difference)
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
            if debug and not pre_solve:
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


def get_required_edges_from_def_to_use(index, cfg, rda_solution, rda_table, graph_nodes, all_classes,
                                       additional_edges=None, processed_edges=None, pre_solve=False, properties=None):
    if additional_edges is None:
        additional_edges = []
    if processed_edges is None:
        processed_edges = []
    final_graph = copy.deepcopy(cfg)
    # twin_edges = [
    #     "constructor_call", "method_call"
    # ]
    # twins = []
    # retain_edges = [
    #     "constructor_call", "class_return", "method_call", "method_return"
    # ]
    # retains = []
    # additional_edges = []
    # for edge in list(final_graph.edges()):
    #     edge_data = final_graph.get_edge_data(*edge)[0]
    #     if edge_data["label"] in retain_edges:
    #         retains.append(edge)
    #     # if edge_data["label"] in twin_edges:
    #     #     twins.append(edge)
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
                    # if available_def not in rda_solution[node]["OUT"]:
                    #     for line_def in rda_table[node]["def"]:
                    #         if line_def.name == available_def.name:
                    #             if line_def.declaration:
                    #                 available_def = line_def
                    # if available_def in rda_table[available_def.line]["def"]:
                    if scope_check(available_def.scope, used.scope):
                        # if available_def.declaration:
                        # if available_def.immutable_declaration:
                        #     for other_def in rda_solution[node]["IN"]:
                        #         if other_def.name == available_def.name and other_def.param_declaration:
                        #             if not used.core.startswith("this"):
                        #                 available_def = other_def
                        #             break
                        add_edge(final_graph, available_def.line, node, {'used_def': f"'{used.name}'"}, pre_solve)
                        used.satisfied = True
                    # else:
                    #         add_edge(final_graph, available_def.line, node, {'used_def': used.name}, pre_solve)
                    #         used.satisfied = True
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
                        add_edge(final_graph, available_def.line or node, used.line or node, {'used_def': f"'{used.name}'"},
                                 pre_solve)
                        used.satisfied = True
            if not used.satisfied:
                if used.core in all_classes:
                    static_derive_class = all_classes[used.core]
                    fields = recursively_get_children_of_types(static_derive_class, "field_declaration")
                    for field in fields:
                        field_pieces = st(field).replace(";", "").split()
                        if "static" in field_pieces:
                            if used.name.replace(used.core + ".", "") in field_pieces:
                                processed_edges.append((get_index(field, index), node))
                else:
                    if not pre_solve and properties.get("last_use", False):
                        for i in rda_table:
                            for entry in rda_table[i]["use"]:
                                if entry.name == used.name and i != node:
                                    # TODO: THIS IS AN AP - Make sure edges added here are right
                                    if i in cfg and node in cfg:
                                        # TODO: check missing i and handle it
                                        if not nx.has_path(cfg, i, node):
                                            continue
                                        add_edge(final_graph, i, node, {'color': 'green'})
                                    # used.satisfied = True
                            #         break
                            # if used.satisfied:
                            #     break
        if properties.get("last_def", False):
            for available_def in rda_solution[node]["IN"] - rda_solution[node]["OUT"]:
                ignore_nodes = ['for_statement', 'while_statement', 'if_statement', 'switch_statement', "for_each_statement"]
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
    if not pre_solve:
        for edge in additional_edges:
            if debug:
                add_edge(final_graph, *edge, {'color': 'yellow'})
            else:
                add_edge(final_graph, *edge)
        for edge in processed_edges:
            add_edge(final_graph, *edge)
    # for edge in twins:
    #     continue
    #     add_edge(final_graph, edge[0], edge[1])
    #     add_edge(final_graph, edge[1], edge[0])
    return final_graph


def rda_cfg_map(rda_solution, CFG_results, remove_unused=True):
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
            if remove_unused:
                graph.remove_edge(*edge)
            # logger.warning("Unable to remap edge {}", edge)
        attrs[edge] = data
    nx.set_edge_attributes(graph, attrs)
    return graph


def call_variable(call_variable_map, node, edge_for, check_virtual=True):
    for virtual_var, actual_var in call_variable_map[node]:
        if check_virtual:
            if st(virtual_var) == edge_for:
                return actual_var
        else:
            if st(actual_var) == edge_for:
                return virtual_var
    return None


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

    method_declaration = ['method_declaration']
    handled_types = assignment + def_statement + increment_statement + method_calls + method_declaration + switch_type

    method_invocation = method_calls + ["object_creation_expression", "explicit_constructor_invocation"]

    call_variable_map = {}
    handled_cases = ["switch_section", "local_declaration_statement"] + ["class_declaration"]

    # if_statement = ["if_statement", "else"]
    # for_statement = ["for_statement"]
    # enhanced_for_statement = ["for_each_statement"]
    # while_statement = ["while_statement"]

    additional_edges = []
    processed_edges = []
    cfg_graph = copy.deepcopy(CFG_results.graph)

    node_list = CFG_results.node_list

    all_classes = {
        st(node_list[read_index(index, x)].child_by_field_name("name")): node_list[read_index(index, x)]
        for x, y in cfg_graph.nodes(data=True) if 'type_label' in y and y['type_label'] == "class_declaration"
    }
    uninitiated_classes = [x for x, y in cfg_graph.nodes(data=True) if 'type_label' in y and
                           y['type_label'] == "class_declaration" and cfg_graph.in_degree(x) == 0]

    start_rda_init_time = time.time()
    for edge in list(cfg_graph.edges()):
        edge_data = cfg_graph.get_edge_data(*edge)[0]
        # If there is object creation
        if edge_data["label"] == "class_return":
            # call_statement = node_list[read_index(index, edge[1])]
            # call_node = recursively_get_children_of_types(call_statement, method_invocation)[0]
            if read_index(index, edge[0]) not in node_list:
                continue
            last_statement = node_list[read_index(index, edge[0])]
            class_node = return_first_parent_of_types(last_statement, "class_declaration")
            class_name = st(class_node.child_by_field_name("name"))
            class_methods = recursively_get_children_of_types(class_node, method_declaration)
            class_id = get_index(class_node, index)
            # find all simple paths between class_id and edge[0]
            all_paths = nx.all_simple_paths(cfg_graph, source=class_id, target=edge[0])
            # only_path = nx.shortest_path(cfg_graph, source=class_id, target=edge[0])
            unique_constructor_children = set()
            for path in all_paths:
                for node in path:
                    unique_constructor_children.add(node)
            if len(unique_constructor_children) == 0:
                unique_constructor_children.add(edge[0])
            # unique_constructor_children = set(only_path)
            # for nkey, nvalue in node_list.items():
            #     if node_has_parent(nvalue, class_node):
            #         unique_constructor_children.add(index[nkey])
            for class_method in class_methods:
                class_method_name = st(class_method.child_by_field_name("name"))
                if class_method_name != class_name:
                    add_edge(cfg_graph, edge[0], get_index(class_method, index))

            for n_id in unique_constructor_children:
                additional_edges.append((n_id, edge[1]))
        # 702 -> 776 check C#
        # Handle method_call edges and all constructor calls if there are parameters
        elif edge_data["label"] in ["constructor_call", "method_call"]:

            # class_attributes = ["field_declaration", "static_initializer"]
            # Not included: ["record_declaration", "method_declaration","compact_constructor_declaration","class_declaration","interface_declaration","annotation_type_declaration","enum_declaration","block","static_initializer","constructor_declaration"]

            call_statement = node_list[read_index(index, edge[0])]
            if call_statement.type in method_invocation:
                call_node = call_statement
            else:
                marked_index = int(edge_data["controlflow_type"].rsplit("|", 1)[-1])
                call_nodes = recursively_get_children_of_types(call_statement, method_invocation)
                for call_node in call_nodes:
                    if marked_index == get_index(call_node, index):
                        break
            method = node_list[read_index(index, edge[1])]
            if method.type == "class_declaration":
                class_node = method
                constructors = recursively_get_children_of_types(class_node, "constructor_declaration")
                if constructors:
                    if "target_constructor" in edge_data:
                        target_constructor = edge_data["target_constructor"]
                        for constructor in constructors:
                            if get_index(constructor, index) == target_constructor:
                                method = constructor
                                break
                    else:
                        continue
                        # TODO if this else is hit its an AP
                        # method = constructors[0]
                else:
                    continue
            actual_variables = recursively_get_children_of_types(call_node.child_by_field_name("arguments"), variable_type, index=parser.index,
                                                                          stop_types=statement_types[
                                                                              "statement_holders"])
                # call_node.child_by_field_name("arguments")
            virtual_variables = []
            for node in method.named_children:
                if "parameter_list" in node.type:
                    virtual_variables = recursively_get_children_of_types(node, variable_type, index=parser.index,
                                                                          stop_types=statement_types[
                                                                              "statement_holders"])
            if actual_variables:
                # TODO: Handle var_args Type... IterableObject
                var_args = False
                if var_args or len(actual_variables) == len(virtual_variables):
                    for actual_var, virtual_var in zip(actual_variables, virtual_variables):
                        method_statement_id = edge[1]
                        if method_statement_id not in call_variable_map:
                            call_variable_map[method_statement_id] = []
                        call_variable_map[method_statement_id].append((virtual_var, actual_var))
                    processed_edges.append(edge)
                else:
                    # print(edge[0], edge[1])
                    logger.error("Number of actual and virtual variables do not match")
                    if not var_args:
                        pass
                        # assert len(actual_variables) == len(virtual_variables)
        elif edge_data["label"] == "method_return":
            return_statement = node_list[read_index(index, edge[0])]
            if return_statement.type == "return_statement" and return_statement.named_children:
                processed_edges.append(edge)
        elif edge_data["label"] == "lambda_invocation":
            processed_edges.append(edge)

    for class_id in uninitiated_classes:
        class_node = node_list[read_index(index, class_id)]
        class_name = st(class_node.child_by_field_name("name"))
        class_methods = recursively_get_children_of_types(class_node, method_declaration)

        descendants = [x for x in nx.descendants(cfg_graph, class_id) if
                       cfg_graph.out_degree(x) == 0 and cfg_graph.in_degree(x) == 1]

        for class_method in class_methods:
            class_method_name = st(class_method.child_by_field_name("name"))
            if class_method_name != class_name:
                for descendant in descendants:
                    add_edge(cfg_graph, descendant, get_index(class_method, index))

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
            if root_node.children[1].type == "invocation_expression":
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
            if parent_statement is None:
                continue
            if parent_statement.type in handled_cases:
                continue
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
    # rda_solution = start_rda(index, rda_table, CFG_results)
    # # pp.pprint(rda_solution)
    # final_graph = get_required_edges_from_def_to_use(CFG_results.parser.index, CFG_results.graph, rda_solution, rda_table,
    #                                                  CFG_results.graph.nodes, properties=properties)
    # debug_graph = rda_cfg_map(rda_solution, CFG_results)
    # return final_graph, debug_graph, rda_table, rda_solution

    end_rda_init_time = time.time()
    end_rda_presolve_time = 0
    start_rda_presolve_time = 0
    end_alias_analysis_time = 0
    start_alias_analysis_time = 0
    if properties.get("alex_algo", True):
        start_rda_presolve_time = time.time()
        rda_solution = start_rda(index, rda_table, cfg_graph, pre_solve=True)
        # pp.pprint(rda_solution)
        final_graph = get_required_edges_from_def_to_use(index, cfg_graph, rda_solution, rda_table,
                                                         cfg_graph.nodes, all_classes, additional_edges,
                                                         processed_edges,
                                                         pre_solve=True, properties=properties)
        used_classes_or_methods = set()
        for edge in cfg_graph.edges:
            if "label" in cfg_graph.edges[edge] and cfg_graph.edges[edge]["label"] in ["method_call",
                                                                                       "constructor_call"]:
                final_graph.nodes[edge[0]][cfg_graph.edges[edge]["label"]] = edge[1]
                used_classes_or_methods.add(edge[1])
        end_rda_presolve_time = time.time()
        start_alias_analysis_time = time.time()
        al_analysis = set()
        proc_analysis = set()

        for node in final_graph.nodes:
            if node not in used_classes_or_methods:
                continue
            if final_graph.nodes[node]["type_label"] == "method_declaration":
                if "main" in final_graph.nodes[node]["label"]:
                    continue
                handled_node_leaf_pair = set()
                for leaf in nx.algorithms.dag.descendants(final_graph, node):
                    if len([x for x in final_graph.edges(leaf) if x[0] != x[1]]) == 0:
                        # print("Leaf: ", leaf)
                        # final_graph.add_edge(leaf, "exit")
                        # used_names = [n.name for n in rda_table[leaf]['def']]
                        # if len(used_names) != 1:
                        #     logger.error("Multiple used names: %s", used_names)
                        # get shortest path from node to leaf
                        paths = nx.all_simple_paths(final_graph, node, leaf)
                        # print("All_Simple: ", node, leaf)
                        for path in paths:
                            # get first edge in path
                            first_edge = (path[0], path[1], 0)
                            # get last edge in path
                            last_edge = (path[-2], path[-1], 0)
                            # get data for edge
                            if "used_def" not in final_graph.edges[first_edge]:
                                continue
                            edge_for = final_graph.edges[first_edge]["used_def"][1:-1]
                            # get data for last edge
                            edge_for_last = final_graph.edges[last_edge]["used_def"][1:-1]
                            defined_cores = [d.name for d in rda_table[leaf]["def"]]
                            call_node = None
                            # print("cs:" + edge_for_last)
                            if edge_for_last not in defined_cores:
                                # "method_return", "class_return"
                                if any([x in final_graph.nodes[leaf] for x in ["method_call", "constructor_call"]]):
                                    if "method_call" in final_graph.nodes[leaf]:
                                        call_node = final_graph.nodes[leaf]["method_call"]
                                    elif "constructor_call" in final_graph.nodes[leaf]:
                                        call_node = final_graph.nodes[leaf]["constructor_call"]
                            node_leaf_key = str(leaf) + "_" + str(edge_for)
                            if node_leaf_key in handled_node_leaf_pair:
                                continue
                            handled_node_leaf_pair.add(node_leaf_key)
                            if node in call_variable_map:
                                if call_node:
                                    proc_analysis.add((node, leaf, edge_for, call_node))
                                # al_analysis.append((node, leaf, edge_for, call_node))
                                if edge_for_last not in defined_cores:
                                    n = -1
                                    while edge_for_last not in defined_cores:
                                        n = n - 1
                                        if abs(n - 1) > len(path):
                                            break
                                        last_edge = (path[n - 1], path[n], 0)
                                        if "used_def" not in final_graph.edges[last_edge]:
                                            continue
                                        edge_for_last = final_graph.edges[last_edge]["used_def"][1:-1]
                                        defined_cores = [d.name for d in rda_table[path[n]]["def"]]
                                        if edge_for_last in defined_cores:
                                            al_analysis.add((node, path[n], edge_for, None))
                                else:
                                    al_analysis.add((node, leaf, edge_for, call_node))

        while proc_analysis:
            temp_proc_analysis = set()
            for node, leaf, edge_for, call_node in proc_analysis:
                completed_analysis = set()
                for al_entry in al_analysis:
                    if al_entry[0] == call_node:
                        mapped_node = call_variable(call_variable_map, call_node, edge_for, check_virtual=False)
                        if al_entry[2] != st(mapped_node):
                            continue
                        leaf = al_entry[1]
                        completed_analysis.add((node, leaf, edge_for, al_entry[3]))
                        if al_entry[3] is not None:
                            temp_proc_analysis.add((node, leaf, edge_for, al_entry[3]))
                al_analysis.update(completed_analysis)
            proc_analysis = temp_proc_analysis

        for node, leaf, edge_for, call_node in al_analysis:
            mapped_node = call_variable(call_variable_map, node, edge_for)
            # print(st(mapped_node))
            if mapped_node:
                if mapped_node.type == "method_invocation":
                    # if a reference is passed back it is ignored in alias analysis
                    # to handle turn this into a while loop and trace the return chain
                    #     track_leaf = leaf
                    #     leaf_node = node_list[read_index(index, track_leaf)]
                    #     if leaf_node.type == "return_statement":
                    # print("skipped")
                    continue
                # [(st(a),st(b)) for a,b in call_variable_map[100]]
                # print(edge_for, final_graph.nodes[leaf]["label"])
                set_add(rda_table[leaf]["def"],
                        Identifier(parser, mapped_node, leaf, full_ref=mapped_node,
                                   declaration=True,
                                   method_call=True))
        end_alias_analysis_time = time.time()
    # print_table(index, rda_table)
    start_rda_time = time.time()
    rda_solution = start_rda(index, rda_table, cfg_graph)
    final_graph = get_required_edges_from_def_to_use(index, cfg_graph, rda_solution, rda_table,
                                                     cfg_graph.nodes, all_classes, additional_edges, processed_edges,
                                                     pre_solve=False, properties=properties)
    end_rda_time = time.time()
    if debug:
        logger.warning("RDA init, presolve, alias, rda: {}, {}, {}, {}", end_rda_init_time - start_rda_init_time,
                       end_rda_presolve_time - start_rda_presolve_time,
                       end_alias_analysis_time - start_alias_analysis_time,
                       end_rda_time - start_rda_time)
    debug_graph = rda_cfg_map(rda_solution, CFG_results, remove_unused=False)
    return final_graph, debug_graph, rda_table, rda_solution
