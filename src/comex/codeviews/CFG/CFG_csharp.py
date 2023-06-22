import traceback

import networkx as nx
from loguru import logger

from .CFG import CFGGraph
from ...utils import cs_nodes


def get_index(node, index):
    return index[(node.start_point, node.end_point, node.type)]


def recursively_get_children_of_types(
        node, st_types, check_list=None, index=None, result=None
):
    if result is None:
        result = []
    if check_list and index:
        result.extend(
            list(
                filter(
                    lambda child: child.type in st_types
                                  and get_index(child, index) in check_list,
                    node.children,
                )
            )
        )
    else:
        result.extend(list(filter(lambda child: child.type in st_types, node.children)))
    for child in node.children:
        result = recursively_get_children_of_types(
            child, st_types, check_list, index, result=result
        )
    return result


class CFGGraph_csharp(CFGGraph):
    def __init__(self, src_language, src_code, properties, root_node, parser):
        super().__init__(src_language, src_code, properties, root_node, parser)

        self.node_list = None
        self.statement_types = cs_nodes.statement_types

        self.CFG_node_list = []
        self.CFG_edge_list = []
        self.records = {
            "basic_blocks": {},
            "method_list": {},
            "constructor_list": {},
            "return_type": {},
            "class_list": {},
            "extends": {},
            "function_calls": {},
            "constructor_calls": {},
            "object_instantiate": {},
            "label_statement_map": {},
            "return_statement_map": {},
            "label_switch_map": {},
            "switch_child_map": {},
            "switch_equivalent_map": {},
            "lambda_map": {},
        }
        # TODO: Check this against C# grammar.json
        self.types = ["scoped_type_identifier", "type_identifier", "generic_type"]

        self.index_counter = max(self.index.values())
        self.CFG_node_indices = []
        self.symbol_table = self.parser.symbol_table
        self.declaration = self.parser.declaration
        self.declaration_map = self.parser.declaration_map
        self.CFG_node_list, self.CFG_edge_list = self.CFG_cs()
        self.graph = self.to_networkx(self.CFG_node_list, self.CFG_edge_list)

    def get_index(self, node):
        return self.index[(node.start_point, node.end_point, node.type)]

    def check_inner_class(self, node):
        while node.parent is not None:
            if node.parent.type == "class_declaration":
                return True
            node = node.parent
        return False

    def get_basic_blocks(self, CFG_node_list, CFG_edge_list):
        G = self.to_networkx(CFG_node_list, CFG_edge_list)
        components = nx.weakly_connected_components(G)
        # NOTE: May need to sort these components according to line number (this one is more foolproof but harder to implement) or the first element in the set (less foolproof, but I think it can be proved, easier to implement).
        # As of now coincidentally the AST node numbering and the list of nodes in networkx are according ot the line numbers
        block_index = 1
        for block in components:
            block_list = sorted(list(block))
            self.records["basic_blocks"][block_index] = block_list
            block_index += 1

    def get_key(self, val, dictionary):
        for key, value in dictionary.items():
            if val in value:
                return key

    # TODO: Check the correctness of this function
    def get_containing_method(self, node):
        operator_declaration = ["operator_declaration", "conversion_operator_declaration"]
        method_declaration = ["method_declaration", "constructor_declaration", "local_function_statement"]
        while node is not None:
            if node.type == 'lambda_expression':
                return node
            if node.type in method_declaration:
                return node
            if node.type == "accessor_list" or node.type in operator_declaration:
                return node
            node = node.parent
        while node is not None:
            if node.type in self.statement_types["node_list_type"]:
                return node
            node = node.parent

    def append_block_index(self, CFG_node_list):
        new_list = []
        for node in CFG_node_list:
            block_index = self.get_key(node[0], self.records["basic_blocks"])
            new_list.append((node[0], node[1], node[2], node[3], block_index))
        return new_list

    def add_edge(self, src_node, dest_node, edge_type, additional_data=None):
        if src_node == None or dest_node == None:
            logger.error(
                "Node where adding edge is attempted is none {}->{}",
                src_node,
                dest_node,
            )
            logger.warning(traceback.format_stack()[-2])
            # print(src_node, dest_node, edge_type)
            raise NotImplementedError
        elif dest_node == 2:
            # print("Attempt to add exit node")
            return
        else:
            for src, dest, ty, *_ in self.CFG_edge_list:
                if src == src_node and dest == dest_node and "method_call" not in edge_type:
                    return
            # print(src_node, dest_node, edge_type)
            self.CFG_edge_list.append((src_node, dest_node, edge_type, additional_data))

    def handle_next(self, src_node, dest_node, edge_type):
        if dest_node == None:
            try:
                current_containing_method = self.get_index(self.get_containing_method(src_node))
            except:
                return
            try:
                self.records["return_statement_map"][current_containing_method].append(self.get_index(src_node))
            except:
                self.records["return_statement_map"][current_containing_method] = [self.get_index(src_node)]

        else:
            self.add_edge(self.get_index(src_node), self.get_index(dest_node), edge_type)

    # TODO: Change all calls of get_next_index to match
    def get_next_index(self, node_value):
        # If exiting a method, don't return
        next_node = node_value.next_named_sibling
        # TODO: Check if "block" works or not
        while next_node is not None and next_node.type == "block" and len(
                list(filter(lambda child: child.is_named, next_node.children))) == 0:
            next_node = next_node.next_named_sibling
        # TODO: Check if check_inner_class works properly or not)
        if next_node is not None and next_node.type == "class_declaration":
            # Check if its a local class
            if self.check_inner_class(node_value):
                next_node = next_node.next_named_sibling
        next_node_index = -1  # Just using a dummy initial value
        if next_node == None:
            # Sibling not found
            current_node = node_value
            while current_node.parent is not None:
                if (
                        current_node.parent.type
                        in self.statement_types["loop_control_statement"]
                ):
                    next_node = current_node.parent
                    break
                if current_node.parent.type == "if_statement":
                    next_node_index, next_node = self.get_next_index(current_node.parent)
                    break
                next_node = current_node.next_named_sibling
                if current_node.type in self.statement_types["definition_types"]:
                    next_node = None
                    break
                if next_node is not None:
                    for i, child in enumerate(next_node.parent.children):
                        # if child.type == "while" and child.parent.type == "do_statement":
                        #     return None
                        if (
                                child.type == "while"
                                and child.parent.type == "do_statement"
                        ):
                            while_node = child.next_named_sibling
                            next_node = while_node
                            break
                        if (
                                child.type in ["catch_clause", "finally_clause"]
                                and child.parent.type == "try_statement"
                        ):
                            next_node = None
                            break
                        if child == next_node:
                            field_name = next_node.parent.field_name_for_child(i)
                            if field_name is None:
                                break
                            else:
                                next_node = None
                                break
                if next_node is not None:
                    break
                current_node = current_node.parent

        if next_node == None:
            return 2, None
        if next_node.type in self.statement_types["definition_types"]:
            return 2, None

        # if next_node.type == "block":
        #     for child in next_node.children:
        #         if child.is_named:
        #             next_node = child
        #             break

        # return self.index[(next_node.start_point, next_node.end_point, next_node.type)]
        try:
            # WARNING: Might need to replace if with while
            if next_node.type == "block":
                for child in next_node.children:
                    if child.is_named:
                        next_node = child
                        break
            # Returns the index of the next node and the node object of the next node
            try:
                current_containing_method = self.get_index(self.get_containing_method(node_value))
                next_containing_method = self.get_index(self.get_containing_method(next_node))
            except:
                return 2, None
            if current_containing_method != next_containing_method:
                return 2, None
            else:
                return (self.get_index(next_node), next_node)

        except Exception as e:
            # return 2, None
            # print("DO NOT IGNORE", e)
            logger.warning(traceback.format_stack()[-2])
            raise NotImplementedError
            return next_node_index, next_node

    def edge_first_line(self, current_node_key, current_node_value):
        # We need to add an edge to the first statement in the next basic block
        node_index = self.index[current_node_key]
        try:
            current_block_index = self.get_key(node_index, self.records["basic_blocks"])
            next_block_index = current_block_index + 1
            first_line_index = self.records["basic_blocks"][next_block_index][0]
            src_node = node_index
            dest_node = first_line_index
            self.add_edge(
                src_node, dest_node, "first_next_line"
            )  # We could maybe differentiate this
        except:
            # Most probably the block is empty
            # add a direct edge to the next statement
            if current_node_value.type == "method_declaration":
                return
            next_index, next_node = self.get_next_index(current_node_value)
            self.handle_next(current_node_value, next_node, "next_line")

    def edge_to_body(self, current_node_key, current_node_value, body_type, edge_type):
        # We need to add an edge to the first statement in the body block
        src_node = self.index[current_node_key]
        # [current_node_value.field_name_for_child(i) for i,child in enumerate(current_node_value.children)]
        body_node = current_node_value.child_by_field_name(body_type)
        if body_node is None:
            body_nodes = [
                child for child in current_node_value.children if child.type == "block"
            ]
            if body_nodes:
                body_node = body_nodes[0]
            elif current_node_value.type == "while_statement":
                body_node = current_node_value.named_children[-1]
            else:
                try:
                    body_node = current_node_value.named_children[0]
                except:
                    body_node = current_node_value.named_children[-1]
        flag = False
        while body_node.type == "block":
            for child in body_node.children:
                if child.is_named:
                    flag = True
                    body_node = child
                    break
            if flag is False:
                return
        if (
                body_node.is_named
                and body_node.type in self.statement_types["node_list_type"]
        ):
            dest_node = self.index[
                (body_node.start_point, body_node.end_point, body_node.type)
            ]
            self.add_edge(src_node, dest_node, edge_type)

    def get_block_last_line(self, current_node_value, block_type):
        # Find the last line in the body block
        block_node = current_node_value.child_by_field_name(block_type)
        if block_node is None:
            block_node = [
                node
                for node in current_node_value.named_children
                if node.type == block_type
            ]
            if len(block_node) == 0:
                for child in reversed(current_node_value.children):
                    if child.is_named:
                        block_node = child
                        break
            else:
                block_node = block_node[0]

        if block_node.is_named is False:
            return (current_node_value, current_node_value.type)
        # if block_node.is_named is False:
        #     return (
        #         self.index[
        #             (
        #                 current_node_value.start_point,
        #                 current_node_value.end_point,
        #                 current_node_value.type,
        #             )
        #         ],
        #         current_node_value.type,
        #     )

        while block_node.type == "block":
            named_children = list(
                filter(
                    lambda child: child.is_named == True, reversed(block_node.children)
                )
            )
            if len(named_children) == 0:
                # It means there is an empty block - thats why no named nodes inside
                return (current_node_value, current_node_value.type)
                # return (
                #     self.index[
                #         (
                #             current_node_value.start_point,
                #             current_node_value.end_point,
                #             current_node_value.type,
                #         )
                #     ],
                #     current_node_value.type,
                # )
            block_node = named_children[0]
            if block_node.type in self.statement_types["node_list_type"]:
                return (block_node, block_node.type)
                # return (
                #     self.index[
                #         (block_node.start_point, block_node.end_point, block_node.type)
                #     ],
                #     block_node.type,
                # )
        return (block_node, block_node.type)
        # return (
        #     self.index[(block_node.start_point, block_node.end_point, block_node.type)],
        #     block_node.type,
        # )

    # TODO: Check correctness of the next 3 functions
    def get_class_name(self, node):
        reference_node = node.child_by_field_name("function")
        if reference_node is not None:
            try:
                reference_node = list(filter(lambda child: child.type == "member_access_expression", reference_node.children))[0]
        #     # reference_node = list(filter(lambda child: child.type == "member_access_expression", node.children))[0]
        #     reference_node = list(filter(lambda child: child.type == "member_access_expression", reference_node.children))[0]
            except:
                try:
                    reference_node = list(filter(lambda child: child.type == "identifier", reference_node.children))[0]
                except:
                    reference_node = None
            #     print(reference_node)
            #     pass
                
        types = ["scoped_type_identifier", "type_identifier", "generic_type"]
        if reference_node is None or reference_node.type == "this":
            while node is not None:
                if node.type == "class_declaration":
                    # class_index = self.get_index(node)
                    class_name = list(filter(lambda child: child.type == "identifier", node.children))[0]
                    class_name = [class_name.text.decode("UTF-8")]
                    break
                if node.type == "struct_declaration":
                    class_name = list(filter(lambda child: child.type == "identifier", node.children))[0]
                    class_name = [class_name.text.decode("UTF-8")]
                if node.type == "local_function_statement":
                    class_name = list(filter(lambda child: child.type == "identifier", node.children))[0]
                    class_name = [class_name.text.decode("UTF-8")]
                node = node.parent

            if class_name is None:
                class_name = ["Unknown"]
            # try:
            #     class_name += self.records['extends'][class_name[0]]
            # except:
            #     class_name = ["Unknown"]
            #     pass
            return class_name
        try:
            reference_index = self.get_index(reference_node)
            # reference_node = reference_node.text.decode("UTF-8").split(".")[0:-1]
            declaration_index = self.declaration_map[reference_index]
            class_name = [self.symbol_table["data_type"][declaration_index]]
            try:
                class_name += self.records['extends'][class_name[0]]

            except:
                pass
            return class_name

        except:
            # If a static method has been explicitly called on a class name
            if reference_node is not None:
                if reference_node.type == "object_creation_expression":
                    class_name = list(filter(lambda child: child.type in types, reference_node.children))[0]
                    class_name = [class_name.text.decode("UTF-8")]
                else:
                    class_name = [reference_node.text.decode("UTF-8")]
                try:
                    class_name += self.records['extends'][class_name[0]]
                except:
                    pass
                return class_name

            return None

    def get_return_type(self, current_node):
        method_name = current_node.child_by_field_name("name").text.decode("UTF-8")
        class_name = self.get_class_name(current_node)
        if class_name is not None:
            class_name = class_name[0]
            method_name = (class_name, method_name)
        else:
            method_name = (None, method_name)
        signature = ()
        argument_list = current_node.child_by_field_name("arguments")
        argument_list = list(filter(lambda child: child.is_named, argument_list.children))
        signature = self.get_signature(argument_list)
        function_key = (method_name, signature)
        try:
            data_type = self.records["return_type"][function_key]
        except:
            data_type = "void"
        # records["return_type"][((class_name,method_name), signature)] = return_type
        return data_type

    def get_signature(self, argument_list):
        literal_type_map = {
            "character_literal": "char",
            "string_literal": "String",
            "decimal_integer_literal": "int",
            "integer_literal": "int",
            "boolean": "boolean",
            "decimal_floating_point_literal": "double",  # If float, won't work
        }
        signature = []
        for argument in argument_list:
            argument = argument.named_children[-1]
            if argument.type == "identifier":
                identifier_index = self.get_index(argument)
                try:
                    declaration_index = self.declaration_map[identifier_index]
                    data_type = self.symbol_table["data_type"][declaration_index]
                except Exception as e:
                    data_type = "Unknown"
                signature.append(data_type)
            elif argument.type == "method_invocation":
                try:
                    data_type = self.get_return_type(argument)
                except:
                    data_type = "Unknown"
                signature.append(data_type)
            elif argument.type == "field_access":
                field_variable = argument.children[-1]
                identifier_index = self.get_index(field_variable)
                try:
                    declaration_index = self.declaration_map[identifier_index]
                    data_type = self.symbol_table["data_type"][declaration_index]
                except Exception as e:
                    data_type = "Unknown"
                signature.append(data_type)
            elif argument.type == "this":
                signature.append(self.get_class_name(argument)[0])
            else:
                try:
                    signature.append(literal_type_map[argument.type])
                except:
                    signature.append("Unknown")
        return tuple(signature)

    # def function_list(self, current_node):
    #     if current_node.type == "method_invocation":
    #         # maintain a list of all method invocations
    #         method_name = current_node.child_by_field_name("name").text.decode("UTF-8")

    #         parent_node = None
    #         pointer_node = current_node
    #         while pointer_node is not None:
    #             if (
    #                     pointer_node.parent is not None
    #                     and pointer_node.parent.type
    #                     in self.statement_types["node_list_type"]
    #             ):
    #                 parent_node = pointer_node.parent
    #                 break
    #             pointer_node = pointer_node.parent

    #         # Removing this if condition will treat all print sttements as function calls as well
    #         if method_name != "println" and method_name != "print":
    #             # index : (AST_id, method_name) (AST_id is of the parent node)
    #             if method_name in self.records["function_calls"].keys():
    #                 self.records["function_calls"][method_name].append(
    #                     (
    #                         self.index_counter,
    #                         self.index[
    #                             (
    #                                 parent_node.start_point,
    #                                 parent_node.end_point,
    #                                 parent_node.type,
    #                             )
    #                         ],
    #                     )
    #                 )
    #             else:
    #                 self.index_counter += 1
    #                 self.records["function_calls"][method_name] = [
    #                     (
    #                         self.index_counter,
    #                         self.index[
    #                             (
    #                                 parent_node.start_point,
    #                                 parent_node.end_point,
    #                                 parent_node.type,
    #                             )
    #                         ],
    #                     )
    #                 ]
    #                 # Patent node of function call AST id maps to AST id or index of dummy external funciton call node
    #                 # self.records['function_calls'][index] = (self.index_counter, method_name)
    #                 if method_name not in self.records["method_list"].keys():
    #                     self.CFG_node_list.append(
    #                         (
    #                             self.index_counter,
    #                             0,
    #                             "function_call: " + method_name,
    #                             "external_function",
    #                         )
    #                     )

    #     for child in current_node.children:
    #         if child.is_named:
    #             self.function_list(child)
    # TODO: Check correctness nd function calls to this
    def function_list(self, current_node, node_list):
        current_index = self.get_index(current_node)
        if current_node.type == "method_invocation" or current_node.type == "invocation_expression" :
            parent_node = None
            pointer_node = current_node
            while pointer_node is not None:
                if (pointer_node.parent is not None and pointer_node.parent.type in self.statement_types[
                    "node_list_type"]):
                    try:
                        p = pointer_node.parent
                        parent_node = node_list[(p.start_point, p.end_point, p.type)]
                        break
                    except Exception as e:
                        pass
                pointer_node = pointer_node.parent
            parent_index = self.get_index(parent_node)
            # maintain a list of all method invocations
            # IDENTIFY THE CLASS THAT THE ALIAS BELONGS TO AND USE THAT IN THE MAP MAYBE? 
            base_method_name = current_node.child_by_field_name("function").text.decode("UTF-8")
            base_method_name = base_method_name.split(".")[-1]
            # print(base_method_name)
            signature = ()
            argument_list = current_node.child_by_field_name("arguments")
            argument_list = list(filter(lambda child: child.is_named, argument_list.children))
            # print(argument_list)
            signature = self.get_signature(argument_list)
            class_name_list = self.get_class_name(current_node)
            # print(class_name_list)
            if class_name_list is None:
                method_name = (None, base_method_name)
                function_key = (method_name, signature)
                if method_name[1] != "println" and method_name[1] != "print":
                    if function_key in self.records["function_calls"].keys():
                        self.records["function_calls"][function_key].append((current_index, parent_index))
                    else:
                        self.records["function_calls"][function_key] = [(current_index, parent_index)]
            else:
                for class_name in class_name_list:
                    method_name = (class_name, base_method_name)
                    function_key = (method_name, signature)
                    if method_name[1] != "println" and method_name[1] != "print":
                        if function_key in self.records["function_calls"].keys():
                            self.records["function_calls"][function_key].append((current_index, parent_index))
                        else:
                            self.records["function_calls"][function_key] = [(current_index, parent_index)]
        elif current_node.type == "object_creation_expression":
            parent_node = None
            pointer_node = current_node
            while pointer_node is not None:
                if (pointer_node.parent is not None and pointer_node.parent.type in self.statement_types[
                    "node_list_type"]):
                    try:
                        p = pointer_node.parent
                        parent_node = node_list[(p.start_point, p.end_point, p.type)]
                        # parent_node = pointer_node.parent
                        break
                    except Exception as e:
                        pass
                pointer_node = pointer_node.parent
            parent_index = self.get_index(parent_node)
            # type_name = list(filter(lambda child : child.type in self.types, current_node.children))
            # type_name = type_name[0].text.decode("utf-8")
            type_name = current_node.child_by_field_name("type").text.decode("utf-8")
            try:
                self.records["object_instantiate"][type_name].append((current_index, parent_index))
            except:
                self.records["object_instantiate"][type_name] = [(current_index, parent_index)]
                # break
            signature = ()
            argument_list = current_node.child_by_field_name("arguments")
            try:
                argument_list = list(filter(lambda child: child.is_named, argument_list.children))
            except:
                argument_list = []
            signature = self.get_signature(argument_list)
            method_name = (type_name, type_name)
            function_key = (method_name, signature)
            if function_key in self.records["constructor_calls"].keys():
                self.records["constructor_calls"][function_key].append((current_index, parent_index))
            else:
                self.records["constructor_calls"][function_key] = [(current_index, parent_index)]

        elif current_node.type == "explicit_constructor_invocation":
            parent_node = current_node
            parent_index = self.get_index(parent_node)
            type_name = current_node.child_by_field_name("constructor").text.decode("utf-8")
            if type_name == 'this':  # TODO: Add super also here for now
                type_name_list = self.get_class_name(current_node)
                for type_name in type_name_list:
                    # TODO: Replace this condition with a method level check flag
                    if type_name != "test":
                        try:
                            self.records["object_instantiate"][type_name].append((current_index, current_index))
                        except:
                            self.records["object_instantiate"][type_name] = [(current_index, current_index)]

                        signature = ()
                        argument_list = current_node.child_by_field_name("arguments")
                        argument_list = list(filter(lambda child: child.is_named, argument_list.children))
                        signature = self.get_signature(argument_list)
                        method_name = (type_name, type_name)
                        function_key = (method_name, signature)
                        if function_key in self.records["constructor_calls"].keys():
                            self.records["constructor_calls"][function_key].append((current_index, parent_index))
                        else:
                            self.records["constructor_calls"][function_key] = [(current_index, parent_index)]

            elif type_name == 'super':
                pass
            else:
                raise Exception("Explicit constructor invocation not handled")

        elif current_node.type == "method_declaration" or current_node.type == "constructor_declaration":
            last_line, _ = self.get_block_last_line(current_node, "body")
            try:
                self.records["return_statement_map"][current_index].append(self.get_index(last_line))
            except:
                self.records["return_statement_map"][current_index] = [self.get_index(last_line)]

        elif current_node.type == "class_declaration":
            # If constructor exits, find the last line of the constructor
            # If no constructor, find the last line before a method starts
            # If empty of if only methods, then just return from the class
            constructor_node = None
            constructor_count = 0
            empty_flag = True
            last_statement = None
            class_node = current_node.child_by_field_name("body")
            class_children = list(filter(lambda
                                             child: child.is_named and child.type != "method_declaration" and child.type != "class_declaration",
                                         class_node.children))
            for child in reversed(class_children):
                if child.type in self.statement_types["node_list_type"]:
                    empty_flag = False
                    if last_statement is None and child.type != "constructor_declaration":
                        last_statement = child
                if child.type == "constructor_declaration":
                    constructor_node = child
                    constructor_count += 1
                    break
            if empty_flag == True:
                try:
                    self.records["return_statement_map"][current_index].append(current_index)
                except:
                    self.records["return_statement_map"][current_index] = [current_index]
            elif constructor_count == 1:
                last_line, _ = self.get_block_last_line(constructor_node, "body")
                try:
                    self.records["return_statement_map"][current_index].append(self.get_index(last_line))
                except:
                    self.records["return_statement_map"][current_index] = [self.get_index(last_line)]
            elif last_statement is not None:
                last_index = self.get_index(last_statement)
                try:
                    self.records["return_statement_map"][current_index].append(last_index)
                except:
                    self.records["return_statement_map"][current_index] = [last_index]
            elif constructor_node is not None:
                last_line, _ = self.get_block_last_line(constructor_node, "body")
                try:
                    self.records["return_statement_map"][current_index].append(self.get_index(last_line))
                except:
                    self.records["return_statement_map"][current_index] = [self.get_index(last_line)]

        for child in current_node.children:
            if child.is_named:
                self.function_list(child, node_list)

    # TODO: Check correctness
    def get_all_statements(self, current_node, node_list, statements):
        for child in current_node.children:
            if child.is_named and child.type in self.statement_types["node_list_type"]:
                child_key = (child.start_point, child.end_point, child.type)
                if child_key in node_list.keys():
                    statements.append(child)
            self.get_all_statements(child, node_list, statements)
        return statements

    def add_dummy_nodes(self):
        self.CFG_node_list.append((1, 0, "start_node", "start"))
        # self.CFG_node_list.append((2, 0, "exit_node", "exit"))

    # def add_dummy_edges(self):
    #     for node_name, node_index in self.records["function_calls"].items():
    #         for node in node_index:
    #             if node_name not in self.records["method_list"].keys():
    #                 self.add_edge(node[1], node[0], "function_call")
    #                 self.add_edge(node[0], node[1], "function_return")
    #             else:
    #                 self.add_edge(
    #                     node[1],
    #                     self.records["method_list"][node_name],
    #                     "recursive_method_call",
    #                 )

    def get_signature_nodes(self, node):
        signature = []
        formal_parameters = node.child_by_field_name('parameters')
        formal_parameters = list(filter(lambda x: x.type == 'formal_parameter', formal_parameters.children))

        for formal_parameter in formal_parameters:
            for child in formal_parameter.children:
                if child.type != "identifier":
                    signature.append(child.text.decode('utf-8'))
        return tuple(signature)

    def get_class_name_nodes(self, node):
        type_identifiers = ["type_identifier", "generic_type", "scoped_type_identifier"]
        "Returns the class name when a method declaration or constructor declaration is passed to it"

        while node is not None:
            if node.type == "class_body" and node.parent.type == "class_declaration":
                node = node.parent
                class_index = self.index[(node.start_point, node.end_point, node.type)]
                class_name = list(filter(lambda child: child.type == "identifier", node.children))[0]
                return class_index, class_name.text.decode("UTF-8")
            elif node.type == "class_body" and node.parent.type == "object_creation_expression":
                node = node.parent
                class_index = self.index[(node.start_point, node.end_point, node.type)]
                class_name = list(filter(lambda child: child.type in type_identifiers, node.children))[0]
                return class_index, class_name.text.decode("UTF-8")
            node = node.parent

    def inner_function(self, current_node):
        """Returns true if the current node is inside an inner function"""
        method_counter = 0
        while current_node is not None:
            if current_node.type == "method_declaration":
                method_counter += 1
            current_node = current_node.parent
        if method_counter > 1:
            return True
        else:
            return False

    def returns_inner_definition(self, node, inner_node):

        """Returns the inner definition index if exists"""
        for c in node.children:
            if c.is_named and c.type == "method_declaration":
                method_name = list(filter(lambda child: child.type == "identifier", c.children))[0].text.decode("utf-8")
                _, class_name = self.get_class_name_nodes(c)
                signature = self.get_signature_nodes(c)
                # TODO: Take out the common unitility functions like get class name and signture
                inner_node.append(self.records["method_list"][((class_name, method_name), signature)])
                return
            else:
                self.returns_inner_definition(c, inner_node)
        return

    def get_matched_constructor(self, node):
        for node_signature, node_ind in self.records["constructor_calls"].items():
            for node_search in node_ind:
                if node == node_search:
                    if node_signature in self.records["constructor_list"].keys():
                        method_index = self.records["constructor_list"][node_signature]
                        return method_index

        for node_signature, node_ind in self.records["constructor_calls"].items():
            for node_search in node_ind:
                flag = False
                if node == node_search:
                    for list_signature, list_index in self.records["constructor_list"].items():
                        flag = True
                        list_signature_list = list(list_signature[1])
                        node_signature_list = list(node_signature[1])
                        if len(list_signature_list) != len(node_signature_list):
                            flag = False
                        else:
                            for i in range(len(list_signature_list)):
                                if list_signature_list[i] != "Unknown" and node_signature_list[i] != "Unknown" and \
                                        list_signature_list[i] != node_signature_list[i]:
                                    flag = False
                                    break
                        if flag == True:
                            return list_index

    def add_method_call_edges(self):
        # print("Method List")
        # print(*self.records["method_list"].items(), sep="\n")
        # print("Constructor List")
        # print(*self.records["constructor_list"].items(), sep="\n")
        # print("Function Calls")
        # print(*self.records["function_calls"].items(), sep="\n")
        # print("Object instantiations")
        # print(*self.records["object_instantiate"].items(), sep="\n")
        # print("Constuctor Calls")
        # print(*self.records["constructor_calls"].items(), sep="\n")
        # print("extends")
        # print(self.records["extends"])
        # print("Declaration Map")
        # print(self.declaration_map)
        # print("SymboL_TABLE.DATATYPES")
        # print(self.symbol_table["data_type"])
        # print("declaration")
        # print(self.declaration)
        # print("____________________________________________________________________________")
        # print("return_statement_map")
        # print(self.records["return_statement_map"])

        for node_signature, node_index in self.records["function_calls"].items():
            # node_index[1] is suppposed to be the statement node number of the function call
            # node_index[0] is the dummy index value assigned to the dummy node created for the external function call
            # Update: node_index[0] is no longer dummy index but the ast id of the function invocation node
            for node in node_index:
                if node_signature in self.records["method_list"].keys():
                    method_index = self.records["method_list"][node_signature]
                    # Find the class name before indexing records["method_list"]
                    edge_type = "method_call|" + str(node[0])
                    self.add_edge(node[1], self.records["method_list"][node_signature], edge_type)
                    # Add the returning edge
                    # Use the return statement index available in records. And add an edge from all the return statements to the calling line here
                    try:
                        for return_node in self.records["return_statement_map"][method_index]:
                            self.add_edge(return_node, node[1], "method_return")
                    except:
                        # If you can't find return statements, then add an edge from the last line 
                        # Handled by adding the last line to the return statement map in self.function_calls
                        pass
        for node_name, node_index in self.records["object_instantiate"].items():
            for node in node_index:
                if node_name in self.records["class_list"].keys():
                    class_index = self.records["class_list"][node_name]
                    edge_type = "constructor_call|" + str(node[0])
                    additional_data_index = self.get_matched_constructor(node)
                    additional_data = {}
                    if additional_data_index is not None:
                        additional_data = {"target_constructor": additional_data_index}
                    # for node_signature, node_ind in self.records["constructor_calls"].items():
                    #     for node_search in node_ind:
                    #         if node == node_search:
                    #             if node_signature in self.records["constructor_list"].keys():
                    #                 method_index = self.records["constructor_list"][node_signature]
                    #                 additional_data = {"target_constructor": method_index}
                    #                 print(node_signature, method_index)
                    #                 break
                    #     if additional_data:
                    #         break
                    # assert additional_data
                    # print("ADDING EDGE", node[1], class_index, edge_type, additional_data)
                    self.add_edge(node[1], class_index, edge_type, additional_data=additional_data)
                    try:
                        for return_node in self.records["return_statement_map"][class_index]:
                            self.add_edge(return_node, node[1], "class_return")
                    except Exception as e:
                        # If you can't find return statements, then add an edge from the last line 
                        # Handled by adding the last line to the return statement map in self.function_calls
                        pass

        for node_signature, node_index in self.records["constructor_calls"].items():
            for node in node_index:
                if node_signature in self.records["constructor_list"].keys():
                    method_index = self.records["constructor_list"][node_signature]
                    try:
                        for return_node in self.records["return_statement_map"][method_index]:
                            self.add_edge(return_node, node[1], "class_return")
                    except:
                        # If you can't find return statements, then add an edge from the last line 
                        # Handled by adding the last line to the return statement map in self.function_calls
                        pass

        # for lambda expressions
        # for node_key, lambda_expression in self.records["lambda_map"].items():
        for lambda_key, statement_node in self.records["lambda_map"].items():
            # lambda_index = self.index[node_key]
            lambda_index = self.index[lambda_key]
            # self.edge_to_body(node_key, lambda_expression, "body", "lambda_invocation")
            self.add_edge(self.get_index(statement_node), lambda_index, "lambda_invocation")
            # TODO: maintain a return map for all points of return
            try:
                for return_node in self.records["return_statement_map"][lambda_index]:
                    self.add_edge(return_node, self.get_index(statement_node), "lambda_return 1")
            except:
                pass
                for lambda_expression in self.get_all_lambda_body(statement_node):
                    # Note: Might need to move this to before the try
                    last_line, line_type = self.get_block_last_line(lambda_expression, "body")
                    if line_type not in self.statement_types['node_list_type']:
                        self.add_edge(self.get_index(lambda_expression), self.get_index(statement_node),
                                      "lambda_return 2")
                    else:
                        last_line_index = self.get_index(last_line)
                        self.add_edge(last_line_index, self.get_index(statement_node), "lambda_return 3")

    def return_next_node(self, node_value):
        # node_value = node_value.parent  
        next_node = node_value.next_named_sibling
        while next_node is None and node_value.parent.type in self.statement_types['statement_holders']:
            if node_value.parent.parent.type == 'method_declaration':
                next_node = node_value.parent.next_named_sibling
                return next_node
            else:
                node_value = node_value.parent
                next_node = node_value.next_named_sibling
        if node_value.parent.type in self.statement_types['statement_holders']:
            return next_node
        return None

    def add_class_edge(self, node_value):
        class_attributes = ["field_declaration", "accessor_list"]
        # Not included: ["record_declaration", "method_declaration","compact_constructor_declaration","class_declaration","interface_declaration","annotation_type_declaration","enum_declaration","block","static_initializer","constructor_declaration"]
        current_index = self.get_index(node_value)
        current_node = node_value.child_by_field_name("body")
        flag = False
        # Chain all class level attributes together and append to class declaration.
        current_fields = list(filter(lambda x: x.type in class_attributes, current_node.children))
        for field in current_fields:
            if field.type == "accessor_list":
                # Find the first line insdie the block
                block = list(filter(lambda x: x.type == "block", field.children))[0]
                try:
                    field = list(filter(lambda x: x.is_named, block.children))[-1]
                except:
                    continue
                field_index = self.get_index(field)
            else:
                field_index = self.get_index(field)
                self.add_edge(current_index, field_index, "class_next")
            current_index = field_index

        # If constructor exists, chain it to the last field
        constructors = list(filter(lambda x: x.type == "constructor_declaration", current_node.children))
        for constructor in constructors:
            constructor_index = self.get_index(constructor)
            self.add_edge(current_index, constructor_index, "constructor_next")

        # In case main method exists, chain main method at the end
        try:
            methods = list(filter(lambda x: x.type == "method_declaration", current_node.children))
            for method in methods:
                if self.records["main_method"] == self.get_index(method):
                    self.add_edge(current_index, self.records["main_method"], "main_method_next")
        except:
            pass

    def read_index(self, index):
        return list(self.index.keys())[list(self.index.values()).index(index)]

    def CFG_cs(self):
        warning_counter = 0
        node_list = {}
        # node_list is a dictionary that maps from (node.start_point, node.end_point, node.type) to the node object
        # of tree-sitter
        _, self.node_list, self.CFG_node_list, self.records = cs_nodes.get_nodes(
            root_node=self.root_node,
            node_list=node_list,
            graph_node_list=self.CFG_node_list,
            index=self.index,
            records=self.records,
        )
        # for eq_case, cases in self.records["switch_equivalent_map"].items():
        #     equivalent = [eq_case] + cases
        #     for k,v in self.records["label_statement_map"].items():
        #         if v in equivalent:
        #             for case in equivalent:
        #                 if case not in self.records["label_statement_map"]:
        #                     self.records["label_statement_map"]

        # Initial for loop required for basic block creation and simple control flow within a block ----------------------------
        for node_key, node_value in node_list.items():
            current_node_type = node_key[2]
            if current_node_type in self.statement_types["non_control_statement"] and current_node_type not in \
                    self.statement_types["scope_only_blocks"]:
                # if current_node_type not in self.statement_types['terminal_inner']:
                if (
                        cs_nodes.return_switch_child(node_value) is None
                        and node_value.parent is not None
                        and node_value.parent.type
                        in self.statement_types["statement_holders"]
                ):
                    # if cs_nodes.return_switch_child(node_value) is None:
                    try:
                        # print("_________________-")
                        # print(node_value.text.decode("utf-8"), node_value.type)
                        check = False
                        src_node = self.index[node_key]
                        if node_value.type == "labeled_statement":
                            if "statement" in node_value.named_children[-1].type:
                                src_node = get_index(
                                    node_value.named_children[-1], self.index
                                )
                        next_node = node_value.next_named_sibling
                        if next_node is not None and next_node.type == "accessor_list":
                            try:
                                child = list(filter(lambda x: x.type == "block", next_node.children))[0]
                                next_node = child
                            except:
                                pass
                        while next_node is not None and next_node.type == "block" and len(
                                list(filter(lambda child: child.is_named, next_node.children))) == 0:
                            next_node = next_node.next_named_sibling
                        # If it is a local class, skip it and go for the next node
                        if next_node is not None and next_node.type == "class_declaration":
                            # Check if its a local class
                            if self.check_inner_class(node_value):
                                next_node = next_node.next_named_sibling
                        # TODO: This might break next line, check all test cases
                        # if next_node is None and self.get_containing_method(node_value).type == "constructor_declaration": 
                        #     self.handle_next(node_value, None, "constructor_return")
                        if next_node is None and node_value.parent.type == 'block':
                            next_node = self.return_next_node(node_value)
                            if next_node is None:
                                continue
                            dest_node = self.get_index(next_node)
                            check = True
                            if next_node.type in self.statement_types["node_list_type"] and next_node.type not in \
                                    self.statement_types["definition_types"]:
                                self.add_edge(src_node, dest_node, "next_line $")

                        flag = False
                        while next_node.type == "block" and len(next_node.named_children):
                            for child in next_node.children:
                                if child.is_named:
                                    if child.type in self.statement_types["node_list_type"]:
                                        flag = True
                                        next_node = child
                                        break
                                    else:
                                        next_node = child
                                        break

                            if flag == True:
                                break

                        dest_node = self.get_index(next_node)
                        if dest_node in self.records["switch_child_map"].keys():
                            dest_node = self.records["switch_child_map"][dest_node]
                        if check is False and next_node.type in self.statement_types[
                            'node_list_type'] and next_node.type not in self.statement_types["definition_types"]:
                            self.add_edge(src_node, dest_node, "next_line 1")
                        # if next_node and next_node.type == "block":
                        #     for child in next_node.children:
                        #         if child.type in self.statement_types["node_list_type"]:
                        #             self.add_edge(
                        #                 src_node,
                        #                 self.index[
                        #                     (
                        #                         child.start_point,
                        #                         child.end_point,
                        #                         child.type,
                        #                     )
                        #                 ],
                        #                 "into_block",
                        #             )
                        #             break
                        # else:
                        #     dest_node = self.index[
                        #         (
                        #             next_node.start_point,
                        #             next_node.end_point,
                        #             next_node.type,
                        #         )
                        #     ]
                        #     if dest_node in self.records["switch_child_map"].keys():
                        #         dest_node = self.records["switch_child_map"][dest_node]
                        #     for i, child in enumerate(next_node.parent.children):
                        #         if child == next_node:
                        #             field_name = next_node.parent.field_name_for_child(
                        #                 i
                        #             )
                        #             if field_name is None:
                        #                 self.add_edge(src_node, dest_node, "next_line")
                        #             else:
                        #                 # TODO Triage
                        #                 next_node = None
                    except Exception as e:
                        # print("EXCEPTION: ", e)
                        # print(traceback.format_exc())
                        pass

            elif current_node_type in self.statement_types["not_implemented"]:
                logger.warning("WARNING: Not implemented ", current_node_type)
                warning_counter += 1

        self.get_basic_blocks(self.CFG_node_list, self.CFG_edge_list)
        self.CFG_node_list = self.append_block_index(self.CFG_node_list)
        self.CFG_node_indices = list(map(lambda x: x[0], self.CFG_node_list))
        self.function_list(self.root_node, node_list)
        self.add_dummy_nodes()
        # self.add_dummy_edges()
        # ------------------------------------------------------------------------------
        # At this point, the self.CFG_node_list has basic block index appended to it
        # ------------------------------------------------------------------------------
        first_guy_hit = False
        for node_key, node_value in node_list.items():
            current_node_type = node_key[2]
            current_index = self.index[node_key]
            if current_node_type in [
                "method_declaration",
                "interface_declaration",
                "constructor_declaration",
                "property_declaration",
            ]:
                # We need to add an edge to the first statement in the next basic block
                # if not first_guy_hit:
                #     first_guy_hit = True
                #     self.add_edge(1, current_index, "next")
                try:
                    # If main method exists, this will work
                    # print(self.records["main_method"], "main method", self.records["main_class"], "main class")

                    if current_index == self.records["main_method"]:
                        self.add_edge(1, self.records["main_class"], "next")
                        # self.add_edge(self.records["main_class"], current_index, "next")
                except Exception as e:
                    # print("Exxxxxxx", e)
                    declarations = ["class_declaration", "interface_declaration"]
                    if node_value.type != "interface_declaration" and node_value.parent.parent.type in declarations:
                        # We need to add an edge to the first statement in the next basic block
                        self.add_edge(1, current_index, "next")

                self.edge_first_line(node_key, node_value)
                # TODO: Change all occurences of get_block_last_line
                last_line, line_type = self.get_block_last_line(
                    node_value, "body"
                )
                last_line_index = self.get_index(last_line)
                try:
                    if current_case_index == self.records["main_method"]:
                        if line_type in self.statement_types["non_control_statement"]:
                            if last_line_index in self.records["switch_child_map"].keys():
                                last_line_index = self.records["switch_child_map"][last_line_index]
                            # self.add_edge(last_line_index, 2, "exit_next")
                except:
                    # No main method in this snippet
                    pass
                # TODO: Not sure if this part makes sense
                if line_type in self.statement_types["non_control_statement"]:
                    if last_line_index in self.records["switch_child_map"].keys():
                        last_line_index = self.records["switch_child_map"][
                            last_line_index
                        ]
                    if line_type == "labeled_statement":
                        statement_node = node_list[self.read_index(last_line_index)]
                        if "statement" in statement_node.named_children[-1].type:
                            last_line_index = get_index(
                                statement_node.named_children[-1], self.index
                            )
                    # self.add_edge(last_line_index, 2, "exit_next")

            # ------------------------------------------------------------------------------------------------
            elif current_node_type == "interface_declaration":
                self.edge_first_line(node_key, node_value)
            # ------------------------------------------------------------------------------
            if current_node_type == "class_declaration":
                self.add_class_edge(node_value)
            elif current_node_type == "import_declaration":
                next_node = node_value.next_named_sibling
                if next_node is not None and next_node.type != "import_declaration":
                    try:
                        self.add_edge(current_index, self.records["main_class"], "next")
                    except:
                        pass
            # ------------------------------------------------------------------------------------------------
            elif current_node_type == "lock_statement":
                self.edge_first_line(node_key, node_value)
                last_line, line_type = self.get_block_last_line(
                    node_value, "body"
                )
                last_line_index = self.get_index(last_line)
                next_dest_index, next_node = self.get_next_index(node_value)
                if line_type in self.statement_types["non_control_statement"]:
                    self.add_edge(last_line_index, next_dest_index, "lock_released")
                #     self.add_edge(last_line_index, 2, 'exit_next')

            # ------------------------------------------------------------------------------------------------
            elif current_node_type == "labeled_statement":
                self.edge_first_line(node_key, node_value)
            # ------------------------------------------------------------------------------------------------
            elif current_node_type in [
                "checked_statement",
                "fixed_statement",
                "unsafe_statement",
                "using_statement",
                "local_function_statement",
            ]:
                self.edge_first_line(node_key, node_value)
                last_line, line_type = self.get_block_last_line(
                    node_value, "body"
                )
                last_line_index = self.get_index(last_line)
                next_dest_index, next_node = self.get_next_index(node_value)
                if line_type in self.statement_types["non_control_statement"] and line_type not in self.statement_types[
                    "scope_only_blocks"]:
                    self.handle_next(last_line, next_node, "next_line *")
                    # self.add_edge(
                    #     last_line_index,
                    #     self.index[
                    #         (
                    #             node_value.start_point,
                    #             node_value.end_point,
                    #             node_value.type,
                    #         )
                    #     ],
                    #     "return_control",
                    # )
                # next_dest_index, next_node = self.get_next_index(node_value)
                # self.add_edge(self.index[node_key], next_dest_index, 'next_line')

            # ------------------------------------------------------------------------------------------------
            elif current_node_type == "if_statement":
                # Find the if block body and the else block body if exists (first statement inside them, add an edge)
                # Find the line just after the entire if_statement
                next_dest_index, next_node = self.get_next_index(node_value)
                # consequence
                self.edge_to_body(node_key, node_value, "consequence", "pos_next")
                # Find the last line in the consequence block and add an edge to the next statement
                last_line, line_type = self.get_block_last_line(
                    node_value, "consequence"
                )
                last_line_index = self.get_index(last_line)
                # Also add an edge from the last guy to the next statement after the if
                # print(last_line_index, line_type)
                if line_type in self.statement_types["non_control_statement"]:
                    self.handle_next(last_line, next_node, "next_line")

                # alternative = node_value.child_by_field_name('alternative')
                # print("alternative", alternative)
                empty_if = False
                if last_line_index == current_index:
                    empty_if = True
                    self.handle_next(node_value, next_node, "next_line")
                if node_value.child_by_field_name("alternative") is not None:

                    # alternative
                    self.edge_to_body(node_key, node_value, "alternative", "neg_next")
                    # Find the last line in the alternative block
                    last_line, line_type = self.get_block_last_line(
                        node_value, "alternative"
                    )
                    # print(last_line_index, line_type)
                    if line_type in self.statement_types["non_control_statement"]:
                        self.handle_next(last_line, next_node, "next_line")
                    if empty_if and last_line_index == current_index:
                        self.handle_next(node_value, next_node, "next_line")
                else:
                    # When else is not there add a direct edge from if node to the next statement
                    # if node_value.parent.type == "block" and node_value.parent.parent.type == "do_statement":
                    #     pass
                    # TODO FIX LOGIC IMP
                    # elif cs_nodes.return_index_of_first_parent_of_type(node_value, 'switch_section') is not None:
                    #     pass
                    # else:
                    self.handle_next(node_value, next_node, "next_line")
                    # self.add_edge(current_index, next_dest_index, "next_line")

            # ------------------------------------------------------------------------------------------------
            elif current_node_type in self.statement_types["loop_control_statement"]:
                # Get the node immediately after the while statement
                next_dest_index, next_node = self.get_next_index(node_value)

                # Add an edge from this node to the first line in the body
                self.edge_to_body(node_key, node_value, "body", "pos_next")

                # Find the last line in the body block
                last_line, line_type = self.get_block_last_line(
                    node_value, "body"
                )
                last_line_index = self.get_index(last_line)
                # Add an edge from this node to the next line after the loop statement
                self.handle_next(node_value, next_node, "neg_next")
                # Add an edge from the last statement in the body to this node
                if line_type in self.statement_types["non_control_statement"]:
                    self.add_edge(last_line_index, current_index, "loop_control")

                # Add a self loop in case of for loops
                if current_node_type != "while_statement":
                    self.add_edge(current_index, current_index, "loop_update")

            # ------------------------------------------------------------------------------------------------
            elif current_node_type == "do_statement":
                # Find the corresponding while statement
                # Add an edge from this node to the first line in the body
                # Find the last statement in the body and an edge frpom last line to the while node
                # Add an edge from the while node to the first line in the block or to the current do node
                # Add an edge from the while node to the next statement after the do_statement

                # Get the node immediately after the while statement
                next_dest_index, next_node = self.get_next_index(node_value)

                # Add an edge from this node to the first line in the body
                self.edge_to_body(node_key, node_value, "body", "pos_next")

                # Find the last line in the body block
                last_line, line_type = self.get_block_last_line(
                    node_value, "block"
                )
                last_line_index = self.get_index(last_line)
                # Search the CFG_node_list for parameterized_expression with parent do_statement with AST_id = src_node
                # for k, v in node_list.items():
                #     # print(k,v)
                #     if self.index[
                #         (v.parent.start_point, v.parent.end_point, v.parent.type)] == current_index:
                #         if 'expression' in k[2]:
                #             while_index = self.index[k]
                #             break
                while_index = None
                for child in node_value.children:
                    if child.type == "while":
                        while_node = child.next_named_sibling
                        while_index = self.index[
                            (
                                while_node.start_point,
                                while_node.end_point,
                                while_node.type,
                            )
                        ]
                        break

                # Find the last statement in the body and an edge frpom last line to the while node
                if line_type not in self.statement_types["control_statement"]:
                    self.add_edge(last_line_index, while_index, "next")

                # Add an edge from the while node to the first line in the block or to the current do node
                # self.CFG_edge_list.append((while_node, dest_node, 'loop_control')) # First node of block
                self.add_edge(while_index, current_index, "loop_control")  # do node

                # Add an edge from the while node to the next statement after the do_statement
                self.add_edge(while_index, next_dest_index, "neg_next")

            # ------------------------------------------------------------------------------------------------
            elif current_node_type == "continue_statement":
                # Go up the parent chain until we reach a loop_control statement or do statement
                # add edge from this node to the loop_control statement or do statement

                parent_node = node_value.parent
                loop_node = None
                while parent_node is not None:
                    if (
                            parent_node.type
                            in self.statement_types["loop_control_statement"]
                            or parent_node.type == "do_statement"
                    ):
                        loop_node = parent_node
                        break
                    parent_node = parent_node.parent

                # add edge from this node to the loop_control statement or do statement

                src_node = self.index[node_key]
                dest_node = self.index[
                    (loop_node.start_point, loop_node.end_point, loop_node.type)
                ]
                label_name = list(filter(lambda child: child.type == "identifier", node_value.children))
                # label_name = list(filter(lambda child: child.type == 'identifier', node_value.children))
                # if len(label_name) > 0:
                #     target_name = label_name[0].text.decode('UTF-8').strip()
                #     dest_node = self.records['label_statement_map'][target_name]
                if len(label_name) > 0:
                    target_name = label_name[0].text.decode("UTF-8") + ":"
                    dest_node = self.index[self.records["label_statement_map"][target_name]]  # Check on this later
                self.CFG_edge_list.append((src_node, dest_node, "jump_next"))

            # ------------------------------------------------------------------------------------------------
            elif current_node_type == "break_statement":
                # if it is inside a switch, it is handled here and also refer to switch_expression,
                # if it is inside a loop, handle it here
                label_name = list(filter(lambda child: child.type == "identifier", node_value.children))
                if len(label_name) > 0:
                    target_name = label_name[0].text.decode("UTF-8") + ":"
                    # next_dest_index = self.records['label_statement_map'][target_name]
                    label_key = self.records["label_statement_map"][target_name]
                    label_node = node_list[label_key]
                    next_dest_index, next_node = self.get_next_index(label_node)
                    # need to get the node corresponding to this index, and then get the next node
                    self.handle_next(node_value, next_node, "jump_next")
                else:
                    parent_node = node_value.parent
                    loop_node = None
                    while parent_node is not None:
                        if (
                                parent_node.type
                                in self.statement_types["loop_control_statement"]
                                + ["do_statement"]
                                or parent_node.type == "switch_expression"
                                or parent_node.type == "switch_statement"
                        ):
                            loop_node = parent_node
                            break
                        parent_node = parent_node.parent

                    # if loop_node is not None:
                    #     next_dest_index, next_node = self.get_next_index(
                    #         (loop_node.start_point, loop_node.end_point, loop_node.type),
                    #         loop_node,
                    #     )
                    #     # label_name = list(filter(lambda child: child.type == 'identifier', node_value.children))
                    #     # if len(label_name) > 0:
                    #     #     target_name = label_name[0].text.decode('UTF-8') + ":"
                    #     #     next_dest_index = self.records['label_statement_map'][target_name]
                    #     self.add_edge(current_index, next_dest_index, "jump_next")
                    next_dest_index, next_node = self.get_next_index(loop_node)
                    self.handle_next(node_value, next_node, "jump_next")
            # ------------------------------------------------------------------------------------------------
            elif current_node_type == "goto_statement":
                target_name = node_value.text.decode("UTF-8").replace(";", "").replace("goto", "").strip()
                if target_name in self.records["label_statement_map"]:
                    next_dest_index = self.records["label_statement_map"][target_name]
                else:
                    switch_node = cs_nodes.return_index_of_first_parent_of_type(
                        node_value, "switch_statement"
                    )
                    switch_id = self.index[
                        (
                            switch_node.start_point,
                            switch_node.end_point,
                            switch_node.type,
                        )
                    ]
                    next_dest_index = self.records["label_switch_map"][switch_id][
                        target_name
                    ]
                self.add_edge(current_index, next_dest_index, "jump_next")
            # ------------------------------------------------------------------------------------------------
            elif current_node_type == "yield_statement":
                # if it is inside a switch, it is handled here and also refer to switch_expression,
                parent_node = node_value.parent
                loop_node = None
                while parent_node is not None:
                    if (
                            parent_node.type
                            in self.statement_types["loop_control_statement"]
                            or parent_node.type == "do_statement"
                            or parent_node.type == "switch_expression"
                    ):
                        loop_node = parent_node
                        break
                    parent_node = parent_node.parent

                try:
                    next_dest_index = self.index[
                        (loop_node.start_point, loop_node.end_point, loop_node.type)
                    ]
                except:
                    # Handle yield when no loop parent or switch parent
                    next_dest_index, next_node = self.get_next_index(node_value)

                self.add_edge(current_index, next_dest_index, "yield_exit")
            # ------------------------------------------------------------------------------------------------
            elif (
                    current_node_type == "switch_expression"
                    or current_node_type == "switch_statement"
            ):
                # First check if the switch expression_statement is part of a non-control statement, and add an edge to the next line
                # if current_node_type == 'switch_expression':
                #     switch_parent = cs_nodes.return_switch_parent(node_value,
                #                                                   self.statement_types['non_control_statement'])
                #     self.add_edge(self.index[(switch_parent.start_point, switch_parent.end_point, switch_parent.type)], current_index, 'next_line')

                # try:
                #     next_node = switch_parent.next_named_sibling
                #     src_node = self.index[node_key]
                #     dest_node = self.index[(next_node.start_point, next_node.end_point, next_node.type)]
                #     if dest_node in self.records['switch_child_map'].keys():
                #         dest_node = self.records['switch_child_map'][dest_node]
                #     self.add_edge(src_node, dest_node, 'next_line')
                #
                # except Exception as e:
                #     print(e)
                #     pass

                # Find all the case blocks associated with this switch node and add an edge to each of them
                # Find the last line in each case block and add an edge to the next case block unless it is a break statement
                # BUt if the block is empty, add an edge to the next case label
                # in case of a break statement, add an edge to the next statement outside the switch
                # in case of default, add an edge to the next statement outside the switch
                # in case of no default, add an edge from last block to the next statement outside the switch
                case_node_list = {}
                # default_exists = False

                # Find the next statement outside the switch
                next_dest_index, next_node = self.get_next_index(node_value)

                if current_index in self.records["label_switch_map"]:
                    if "default" not in self.records["label_switch_map"][current_index]:
                        self.add_edge(
                            current_index, next_dest_index, "switch_no_default"
                        )

                # For each case label block, find the first statement in the block and add an edge to it
                for k, v in node_list.items():
                    # print(k,v)
                    source_index = None
                    if k[2] == "switch_expression_arm" or k[2] == "switch_section":
                        if k[2] == "switch_expression_arm":
                            targ = v.parent
                            if (
                                    self.index[
                                        (targ.start_point, targ.end_point, targ.type)
                                    ]
                                    == current_index
                            ):
                                case_node_index = self.index[k]
                                self.add_edge(
                                    current_index, case_node_index, "switch_case"
                                )
                                case_node_list[k] = v
                        else:
                            targ = v.parent.parent
                            if (
                                    self.index[
                                        (targ.start_point, targ.end_point, targ.type)
                                    ]
                                    == current_index
                            ):
                                source_index = current_index
                                type_edge = "switch_case"
                                sink_index = None
                                for eq_case in self.records["switch_equivalent_map"][
                                    self.index[k]
                                ]:
                                    sink_index = eq_case
                                    self.add_edge(source_index, sink_index, type_edge)
                                    type_edge = "fall through"
                                    source_index = sink_index
                            current_case_index = self.index[k]
                            # case_statements = list(
                            #     filter(lambda child: (child.is_named and child.type != 'case_switch_label'), v.children))
                            # case_statements = v.named_children
                            next_case_node = v.next_named_sibling
                            try:
                                next_case_node_index = self.index[
                                    (
                                        next_case_node.start_point,
                                        next_case_node.end_point,
                                        next_case_node.type,
                                    )
                                ]
                            except:
                                next_case_node_index = None

                            # INVALID IN THE CASE OF C#
                            # if not len(case_statements) > 1:
                            #     # There is no case body, so add an edge from this case to the next case label, if exists
                            #     self.add_edge(current_case_index, next_case_node_index, 'fall through')

                            # else:
                            # The case body exists
                            # Find the first line in each case block and add an edge from case label to it
                            block_node = None
                            for child_node in v.named_children[1:]:
                                # Need to write a loop for unlimited layers of nesting
                                if "block" in child_node.type:
                                    block_node = child_node.named_children[0]
                                    break
                                else:
                                    if "label" not in child_node.type:
                                        block_node = child_node
                                        break
                            first_line_index = self.index[
                                (
                                    block_node.start_point,
                                    block_node.end_point,
                                    block_node.type,
                                )
                            ]
                            if first_line_index in self.records["switch_child_map"]:
                                first_line_index = self.records["switch_child_map"][
                                    first_line_index
                                ]
                            if source_index is not None:
                                self.add_edge(
                                    source_index, first_line_index, "case_next"
                                )

                            # Find the last line in each case block and add an edge to the next case block unless it is a break statement
                            block_node = None
                            for child in reversed(v.children):
                                # Need to write a loop for unlimited layers of nesting
                                if child.is_named:
                                    if child.type == "block":
                                        for child in reversed(child.children):
                                            if child.is_named:
                                                block_node = child
                                                break
                                    else:
                                        block_node = child
                                    break

                            # last_line_index = self.index[
                            #     (block_node.start_point, block_node.end_point, block_node.type)]
                            # if block_node.type in self.statement_types['non_control_statement']:
                            #     # print(block_node.text.decode('UTF-8'))
                            #     self.add_edge(last_line_index, next_case_node_index, 'fall through')

                            # in case of default, add an edge to the next statement outside the switch
                            # in case of no default, add an edge from last block to the next statement outside the switch
                            if next_case_node_index is None:
                                # This is the last block
                                if (
                                        block_node.type
                                        in self.statement_types["non_control_statement"]
                                ):
                                    self.add_edge(
                                        last_line_index, next_dest_index, "switch_out"
                                    )
                            # case_label = list(filter(lambda child : child.type == 'switch_label', v.children))
                            # if case_label == 'default':
                            #     default_exists = True

                for k, v in case_node_list.items():
                    current_case_index = self.index[k]
                    parent = v.parent
                    while parent.parent is not None:
                        parent = parent.parent
                        if parent.type == "local_declaration_statement":
                            break
                    next_dest_index, next_node = self.get_next_index(parent)
                    self.add_edge(current_case_index, next_dest_index, "switch_out")

                # in case of a break statement, add an edge to the next statement outside the switch
                # -> Handled in break statement

            # ------------------------------------------------------------------------------------------------
            elif current_node_type == "return_statement":
                # self.add_edge(current_index, 2, "return_exit")
                # Check if it returns a function with an inner definition
                # method_list will give us the index of the inner function
                inner_definition = []
                self.returns_inner_definition(node_value, inner_definition)

                if len(inner_definition) > 0:
                    inner_definition = inner_definition[0]
                    # inner_index = self.index[(inner_definition.start_point, inner_definition.end_point, inner_definition.type)]
                    # TODOD: Perhaps remove this because inconsistent wih newly decided logic
                    self.add_edge(current_index, inner_definition, "return_next")

                if not self.inner_function(node_value):
                    # pass
                    # Instead of an edge to exit node, we update the return map
                    # self.add_edge(current_index, 2, "return_exit")
                    containing_method = self.get_index(self.get_containing_method(node_value))

                    try:
                        self.records["return_statement_map"][containing_method].append(current_index)
                    except:
                        self.records["return_statement_map"][containing_method] = [current_index]
                # else: TODO: When inner functions are properly implemented
                #       save it in the return map?
                #     next_dest_index, next_node = self.get_next_index(node_value)
                #     self.add_edge(current_index, next_dest_index, "return_exit")

            # ------------------------------------------------------------------------------------------------
            elif current_node_type == "try_statement":
                # Add edge from try block to first statement inside the block
                self.edge_to_body(node_key, node_value, "body", "next")
                catch_node_list = {}
                finally_node = None
                # Identify all catch blocks - add an edge from catch node to first line inside block
                for k, v in node_list.items():

                    if (
                            k[2] == "catch_clause"
                            and self.index[
                        (v.parent.start_point, v.parent.end_point, v.parent.type)
                    ]
                            == current_index
                    ):
                        catch_node_list[k] = v
                        self.edge_to_body(k, v, "body", "next")
                        # catch_node_index = self.index[k]
                        # self.add_edge(current_index, catch_node_index, 'catch_next')

                    elif (
                            k[2] == "finally_clause"
                            and self.index[
                                (v.parent.start_point, v.parent.end_point, v.parent.type)
                            ]
                            == current_index
                    ):
                        finally_node = v
                        # ? TODO Triage
                        # self.add_edge(current_index, get_index(v, self.index), "always_finally")
                        self.edge_first_line(k, v)  # Not sure if this works

                # From each line inside the try block, an edge going to each catch block
                try_body = node_value.child_by_field_name("body")
                check_list = [node[0] for node in self.CFG_node_list]
                statements = recursively_get_children_of_types(
                    try_body,
                    self.statement_types["node_list_type"],
                    check_list,
                    self.index,
                )

                if len(statements) > 0:
                    for statement in statements:
                        statement_index = self.index[
                            (statement.start_point, statement.end_point, statement.type)
                        ]
                        for catch_node in catch_node_list.keys():
                            if statement.type != "throw_statement":
                                catch_index = self.index[catch_node]
                                # if statement.type != 'return_statement': The Exception can occur on the RHS so the catch_exception edge should be there
                                self.add_edge(
                                    statement_index, catch_index, "catch_exception"
                                )

                # Find the next statement outside the try block
                next_dest_index, next_node = self.get_next_index(node_value)
                exit_next = None

                # finally block is optional
                if finally_node is not None:
                    # From last line of finally to next statement outside the try block
                    last_line, line_type = self.get_block_last_line(
                        finally_node, "body"
                    )
                    if line_type in self.statement_types["non_control_statement"]:
                        self.handle_next(last_line, next_node, "finally_exit")
                    # For the remaining portion, set finally block as next node if exists
                    # exit_next = self.index[
                    #     (
                    #         finally_node.start_point,
                    #         finally_node.end_point,
                    #         finally_node.type,
                    #     )
                    # ]
                    exit_next = finally_node
                else:
                    exit_next = next_node

                # From last line of try block to finally or to next statement outside the try block
                last_line, line_type = self.get_block_last_line(
                    node_value, "body"
                )
                if (
                        line_type in self.statement_types["non_control_statement"]
                        or finally_node is not None
                ):
                    self.handle_next(last_line, exit_next, "try_exit")
                # From last line of every catch block to finally or to next statement outside the try block
                for catch_node, catch_value in catch_node_list.items():
                    last_line, line_type = self.get_block_last_line(
                        catch_value, "body"
                    )
                    last_line_index = self.get_index(last_line)
                    if line_type in self.statement_types["non_control_statement"]:
                        self.handle_next(last_line, exit_next, "catch_exit")
                        # Case of empty catch block
                    elif last_line_index == self.index[catch_node]:
                        self.handle_next(last_line, exit_next, "catch_exit")
                        # ------------------------------------------------------------------------------------------------
            elif current_node_type == "throw_statement":
                # Control goes to the first catch in the call stack (dynamic call stack) Nothing to do statically
                # Essentially exits the function

                parent = node_value.parent
                try_flag = False
                while parent is not None:
                    if parent.type == "catch_clause" or parent.type == "finally_clause":
                        break
                    if parent.type == "try_statement":
                        if any(
                                [c.type == "catch_clause" for c in parent.named_children]
                        ):
                            try_flag = True
                        break
                    parent = parent.parent
                if try_flag is False:
                    self.add_edge(current_index, 2, "throw_exit")
                else:
                    for child in parent.named_children:
                        if child.type == "catch_clause":
                            self.add_edge(
                                current_index,
                                get_index(child, self.index),
                                "throw_catch",
                            )
            else:
                pass
        self.add_method_call_edges()
        if warning_counter > 0:
            logger.warning(
                "Total number of warnings from unimplemented statement types: ",
                warning_counter,
            )
        return self.CFG_node_list, self.CFG_edge_list
