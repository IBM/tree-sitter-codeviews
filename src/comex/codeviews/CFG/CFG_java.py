import traceback
import networkx as nx
from .CFG import CFGGraph
from ...utils import java_nodes
from loguru import logger

class CFGGraph_java(CFGGraph):
    def __init__(self, src_language, src_code, properties, root_node, parser):
        super().__init__(src_language, src_code, properties, root_node, parser)

        self.node_list = None
        self.statement_types = java_nodes.statement_types
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
            "switch_child_map": {},
            "label_statement_map": {},
            "return_statement_map": {},
            "lambda_map": {},
        }
        self.types = ["scoped_type_identifier", "type_identifier", "generic_type"]
        self.index_counter = max(self.index.values())
        self.CFG_node_indices = []
        self.symbol_table = self.parser.symbol_table
        self.declaration = self.parser.declaration
        self.declaration_map = self.parser.declaration_map
        self.CFG_node_list, self.CFG_edge_list = self.CFG_java()
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
    def get_containing_method(self, node):
        while node is not None:
            if node.type == 'lambda_expression':
                return node
            if node.type == "method_declaration" or node.type == "constructor_declaration":
                return node
            if node.type == "static_initializer":
                return node
            node = node.parent
        while node is not None:
            if node.type in self.statement_types["node_list_type"]:
                return node
            node = node.parent

    def get_lambda_body(self, node):
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
    
    def get_all_lambda_body(self, node):
        """Returns the body of a lambda expression, breadthfirst"""
        bfs_queue = []
        output = []
        bfs_queue.append(node)
        while bfs_queue != []:
            top = bfs_queue.pop(0)
            if top.type == "lambda_expression":
                output.append(top)
                # return [top]
            for child in top.children:
                if child.type == "lambda_expression" or child.type not in self.statement_types["node_list_type"]:
                    bfs_queue.append(child)

        return output

    def append_block_index(self, CFG_node_list):
        new_list = []
        for node in CFG_node_list:
            block_index = self.get_key(node[0], self.records["basic_blocks"])
            new_list.append((node[0], node[1], node[2], node[3], block_index))
        return new_list

    def add_edge(self, src_node, dest_node, edge_type, additional_data=None):
        # current_node_list = list(map(lambda x: x[0], self.CFG_node_list))
        if src_node == None or dest_node == None:
            logger.error(
                "Node where adding edge is attempted is none {}->{}",
                src_node,
                dest_node,
            )
            logger.warning(traceback.format_stack()[-2])
            # print(src_node, dest_node, edge_type)
            raise NotImplementedError
        else:
            for src, dest, ty, *_ in self.CFG_edge_list:
                if src == src_node and dest == dest_node:
                    return
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

    def get_next_index(self, node_value):
        # If exiting a method, don't return
        next_node = node_value.next_named_sibling
        while next_node is not None and next_node.type == "block" and len(list(filter(lambda child : child.is_named, next_node.children))) == 0:
            next_node = next_node.next_named_sibling
        if next_node is not None and next_node.type == "class_declaration":
            # Check if its a local class
            if self.check_inner_class(node_value):
                next_node = next_node.next_named_sibling
        next_node_index = -1  # Just using a dummy initial value
        if next_node == None:
            current_node = node_value
            while current_node.parent is not None:
                if (current_node.parent.type in self.statement_types["loop_control_statement"]):
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
                    break
                current_node = current_node.parent

        if next_node == None:
            return 2, None
        if next_node.type in self.statement_types["definition_types"]:
            return 2, None
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
            self.add_edge(src_node, dest_node, "first_next_line")  # We could maybe differentiate this
        except:
            # Most probably the block is empty
            # add a direct edge to the next statement
            if current_node_value.type == "method_declaration":
                return
            next_index, next_node = self.get_next_index(current_node_value)
            self.handle_next(current_node_value, next_node, "next_line 9")

    def edge_to_body(self, current_node_key, current_node_value, body_type, edge_type):
        # We need to add an edge to the first statement in the body block
        src_node = self.index[current_node_key]
        body_node = current_node_value.child_by_field_name(body_type)
        flag = False
        while body_node.type == "block":
            for child in body_node.children:
                if child.is_named:
                    flag = True
                    body_node = child
                    break
            if flag == False:
                return
        if (body_node.is_named and body_node.type in self.statement_types["node_list_type"]):
            dest_node = self.get_index(body_node)
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
            return (current_node_value, current_node_value.type)

        while block_node.type in self.statement_types["statement_holders"]:
            named_children = list(filter(lambda child: child.is_named == True, reversed(block_node.children)))
            if len(named_children) == 0:
                # It means there is an empty block - thats why no named nodes inside
                return (current_node_value, current_node_value.type)
                    
            block_node = named_children[0]
            if block_node.type in self.statement_types["node_list_type"]:
                return (block_node, block_node.type)
        return (block_node, block_node.type)
    
    def get_class_name(self,node):
        reference_node = node.child_by_field_name("object")
        types = ["scoped_type_identifier", "type_identifier", "generic_type"]

        if reference_node is None or reference_node.type == "this":
            while node is not None:
                if node.type == "class_declaration":
                    # class_index = self.get_index(node)
                    class_name = list(filter(lambda child: child.type == "identifier", node.children))[0]
                    class_name = [class_name.text.decode("UTF-8")]
                    break
                node = node.parent
            try:
                class_name += self.records['extends'][class_name[0]]
            except:
                pass
            return class_name
        try:
            reference_index = self.get_index(reference_node)
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
    def get_return_type(self,current_node):
        method_name = current_node.child_by_field_name("name").text.decode("UTF-8")
        class_name = self.get_class_name(current_node)
        if class_name is not None:
            class_name = class_name[0]
            method_name = (class_name, method_name)
        else:
            method_name = (None, method_name)
        signature = ()
        argument_list = current_node.child_by_field_name("arguments")
        argument_list = list(filter(lambda child : child.is_named, argument_list.children))
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
            "boolean": "boolean",
            "decimal_floating_point_literal": "double", # If float, won't work
        }
        signature = []
        for argument in argument_list:
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
    
    def function_list(self, current_node, node_list):
        current_index = self.get_index(current_node)
        if current_node.type == "method_invocation":
            parent_node = None
            pointer_node = current_node
            while pointer_node is not None:
                if (pointer_node.parent is not None and pointer_node.parent.type in self.statement_types["node_list_type"]):
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
            base_method_name = current_node.child_by_field_name("name").text.decode("UTF-8")
            signature = ()
            argument_list = current_node.child_by_field_name("arguments")
            argument_list = list(filter(lambda child : child.is_named, argument_list.children))
            signature = self.get_signature(argument_list)

            class_name_list = self.get_class_name(current_node)
            if class_name_list is None:
                method_name = (None, base_method_name)
                function_key = (method_name, signature)
                if method_name[1] != "println" and method_name[1] != "print":
                    if function_key in self.records["function_calls"].keys():
                        self.records["function_calls"][function_key].append((current_index, parent_index))
                    else:
                        self.records["function_calls"][function_key] = [(current_index,parent_index)]
            else:
                for class_name in class_name_list:
                    method_name = (class_name, base_method_name)
                    function_key = (method_name, signature)
                    if method_name[1] != "println" and method_name[1] != "print":
                        if function_key in self.records["function_calls"].keys():
                            self.records["function_calls"][function_key].append((current_index, parent_index))
                        else:
                            self.records["function_calls"][function_key] = [(current_index,parent_index)]
        elif current_node.type == "object_creation_expression":
            parent_node = None
            pointer_node = current_node
            while pointer_node is not None:
                if (pointer_node.parent is not None and pointer_node.parent.type in self.statement_types["node_list_type"]):
                    try:
                        p = pointer_node.parent
                        parent_node = node_list[(p.start_point, p.end_point, p.type)]
                        # parent_node = pointer_node.parent
                        break
                    except Exception as e:
                        pass
                pointer_node = pointer_node.parent
            parent_index = self.get_index(parent_node)
            type_name = list(filter(lambda child : child.type in self.types, current_node.children))
            type_name = type_name[0].text.decode("utf-8")
            try:
                self.records["object_instantiate"][type_name].append((current_index,parent_index))
            except:
                self.records["object_instantiate"][type_name] = [(current_index,parent_index)]
                    # break
            signature = ()
            argument_list = current_node.child_by_field_name("arguments")
            argument_list = list(filter(lambda child : child.is_named, argument_list.children))
            signature = self.get_signature(argument_list)
            method_name = (type_name, type_name)
            function_key = (method_name, signature)
            if function_key in self.records["constructor_calls"].keys():
                self.records["constructor_calls"][function_key].append((current_index, parent_index))
            else:
                self.records["constructor_calls"][function_key] = [(current_index,parent_index)]

        elif  current_node.type == "explicit_constructor_invocation":
            parent_node = current_node
            parent_index = self.get_index(parent_node)
            type_name = current_node.child_by_field_name("constructor").text.decode("utf-8")
            if type_name == 'this': # TODO: Add super also here for now
                type_name_list = self.get_class_name(current_node)
                for type_name in type_name_list:
                    # TODO: Replace this condition with a method level check flag
                    if type_name != "test":
                        try:
                            self.records["object_instantiate"][type_name].append((current_index,current_index))
                        except:
                            self.records["object_instantiate"][type_name] = [(current_index,current_index)]

                        signature = ()
                        argument_list = current_node.child_by_field_name("arguments")
                        argument_list = list(filter(lambda child : child.is_named, argument_list.children))
                        signature = self.get_signature(argument_list)
                        method_name = (type_name, type_name)
                        function_key = (method_name, signature)
                        if function_key in self.records["constructor_calls"].keys():
                            self.records["constructor_calls"][function_key].append((current_index, parent_index))
                        else:
                            self.records["constructor_calls"][function_key] = [(current_index,parent_index)]
            
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
            class_children = list(filter(lambda child: child.is_named and child.type != "method_declaration" and child.type != "class_declaration", class_node.children))
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
    
    def inner_function(self,current_node):
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
                inner_node.append(self.records["method_list"][((class_name,method_name), signature)])
                return
            else:
                self.returns_inner_definition(c, inner_node)
        return

    # def add_dummy_edges(self):
    #     for node_name, node_index in self.records["function_calls"].items():
    #         # node_index[0] is suppposed to be the statement node number of the function call
    #         # node_index[1] is the dummy index value assigned to the dummy node created for the external function call
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
                                if list_signature_list[i] != "Unknown" and node_signature_list[i] != "Unknown" and list_signature_list[i] != node_signature_list[i]:
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
                    edge_type = "method_call|"+str(node[0])
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
                    edge_type = "constructor_call|"+str(node[0])
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
            #TODO: maintain a return map for all points of return
            try:
                for return_node in self.records["return_statement_map"][lambda_index]:
                    self.add_edge(return_node, self.get_index(statement_node), "lambda_return 1")
            except:
                pass
                for lambda_expression in self.get_all_lambda_body(statement_node):
                # Note: Might need to move this to before the try
                    last_line, line_type = self.get_block_last_line(lambda_expression, "body")
                    if line_type not in self.statement_types['node_list_type']:
                        self.add_edge(self.get_index(lambda_expression), self.get_index(statement_node), "lambda_return 2")
                    else:
                        last_line_index = self.get_index(last_line)
                        self.add_edge(last_line_index, self.get_index(statement_node), "lambda_return 3")
            

                

    def return_next_node(self,node_value):
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
        class_attributes = ["field_declaration", "static_initializer"]
        # Not included: ["record_declaration", "method_declaration","compact_constructor_declaration","class_declaration","interface_declaration","annotation_type_declaration","enum_declaration","block","static_initializer","constructor_declaration"]
        current_index = self.get_index(node_value)
        current_node = node_value.child_by_field_name("body")
        flag = False
        # Chain all class level attributes together and append to class declaration.
        current_fields = list(filter(lambda x: x.type in class_attributes, current_node.children))
        for field in current_fields:
            if field.type == "static_initializer":
                # Find the first line insdie the block
                block = list(filter(lambda x : x.type == "block", field.children))[0]
                try:
                    field = list(filter(lambda x : x.is_named, block.children))[-1]
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

    def CFG_java(self):
        warning_counter = 0
        node_list = {}
        # node_list is a dictionary that maps from (node.start_point, node.end_point, node.type) to the node object of tree-sitter
        _, self.node_list, self.CFG_node_list, self.records = java_nodes.get_nodes(
            root_node=self.root_node,
            node_list=node_list,
            graph_node_list=self.CFG_node_list,
            index=self.index,
            records=self.records,
        )
        # self.CFG_node_indices = list(map(lambda x: self.index[x], node_list.keys()))
        # Initial for loop required for basic block creation and simple control flow within a block ----------------------------
        for node_key, node_value in node_list.items():
            current_node_type = node_key[2]
            if current_node_type in self.statement_types["non_control_statement"]:
                src_node = self.index[node_key]
                # if node_value.next_named_sibling is not None and node_value.next_named_sibling.type == "static_initializer":
                # if current_node_type == "field_declaration" and node_value.next_named_sibling is not None and node_value.next_named_sibling.type == "constructor_declaration":
                #     self.add_edge(src_node, self.get_index(node_value.next_named_sibling), "constructor_next 2")
                if (
                    java_nodes.return_switch_child(node_value) is None
                    and node_value.parent is not None
                    and node_value.parent.type
                    in self.statement_types["statement_holders"]
                ):
                    # There is no switch expression in the subtree starting at this statement node
                    try: 
                        check = False
                        next_node = node_value.next_named_sibling
                        if next_node is not None and next_node.type == "static_initializer":
                            try:
                                child = list(filter(lambda x : x.type == "block", next_node.children))[0]
                                next_node = child
                            except:
                                pass
                        while next_node is not None and next_node.type == "block" and len(list(filter(lambda child : child.is_named, next_node.children))) == 0:
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
                            dest_node = self.get_index(next_node)
                            check = True
                            if next_node.type in self.statement_types["node_list_type"] and next_node.type not in self.statement_types["definition_types"]:
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
                        if check is False and next_node.type in self.statement_types['node_list_type'] and next_node.type not in self.statement_types["definition_types"]:
                            self.add_edge(src_node, dest_node, "next_line 1")

                        
                    except:
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
        for node_key, node_value in node_list.items():
            current_node_type = node_key[2]
            current_index = self.index[node_key]
            if (current_node_type == "method_declaration" or current_node_type == "constructor_declaration"):
                try:
                    # If main method exists, this will work
                    if current_index == self.records["main_method"]:
                        self.add_edge(1, self.records["main_class"], "next")
                        # self.add_edge(self.records["main_class"], current_index, "next")
                except:
                    if node_value.parent.parent.type == "class_declaration":
                        # We need to add an edge to the first statement in the next basic block
                        self.add_edge(1, current_index, "next")

                self.edge_first_line(node_key, node_value)
                last_line, line_type = self.get_block_last_line(node_value, "body")
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
            #------------------------------------------------------------------------------
            elif current_node_type == "interface_declaration":
                self.edge_first_line(node_key, node_value)
            #------------------------------------------------------------------------------
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
            elif current_node_type == "synchronized_statement":
                self.edge_first_line(node_key, node_value)
                next_dest_index, next_node = self.get_next_index(node_value)
                last_line, line_type = self.get_block_last_line(node_value, "body")
                last_line_index = self.get_index(last_line)
                # if line_type in self.statement_types["non_control_statement"]:
                #     self.add_edge(last_line_index, 2, "exit_next")
                # Add an edge from start of synchronized to the line after it to signify async execution
                self.handle_next(node_value, next_node, "sync_next")
            # ------------------------------------------------------------------------------------------------
            elif current_node_type == "labeled_statement":
                self.edge_first_line(node_key, node_value)
            # ------------------------------------------------------------------------------------------------
            elif current_node_type == "if_statement":
                # Find the if block body and the else block body if exists (first statement inside them, add an edge)
                # Find the line just after the entire if_statement
                next_dest_index, next_node = self.get_next_index(node_value)
                # consequence
                self.edge_to_body(node_key, node_value, "consequence", "pos_next")
                # Find the last line in the consequence block and add an edge to the next statement
                last_line, line_type = self.get_block_last_line(node_value, "consequence")
                last_line_index = self.get_index(last_line)
                # Also add an edge from the last guy to the next statement after the if
                if line_type in self.statement_types["non_control_statement"]:
                    self.handle_next(last_line, next_node, "next_line 2")
                
                empty_if = False
                if last_line_index == current_index:
                    empty_if = True
                    self.handle_next(node_value, next_node, "next_line 3")
                if node_value.child_by_field_name("alternative") is not None:
                    # alternative
                    self.edge_to_body(node_key, node_value, "alternative", "neg_next")
                    # Find the last line in the alternative block
                    last_line, line_type = self.get_block_last_line(node_value, "alternative")
                    if line_type in self.statement_types["non_control_statement"]:
                        self.handle_next(last_line, next_node, "next_line 4")

                    if empty_if and last_line_index == current_index:
                        self.handle_next(node_value, next_node, "next_line 5")
                else:
                    # When else is not there add a direct edge from if node to the next statement
                    # if next_node is not None:
                    self.handle_next(node_value, next_node, "next_line 6")

            # ------------------------------------------------------------------------------------------------
            elif current_node_type in self.statement_types["loop_control_statement"]:
                # Get the node immediately after the while statement
                next_dest_index, next_node = self.get_next_index(node_value)

                # Add an edge from this node to the first line in the body
                self.edge_to_body(node_key, node_value, "body", "pos_next")

                # Find the last line in the body block
                last_line, line_type = self.get_block_last_line(node_value, "body")
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
                # if next_node is not None:
                self.edge_to_body(node_key, node_value, "body", "pos_next")

                # Find the last line in the body block
                last_line, line_type = self.get_block_last_line(node_value, "body")
                last_line_index = self.get_index(last_line)
                # Search the CFG_node_list for parameterized_expression with parent do_statement with AST_id = src_node
                while_index = 0
                while_node = None
                
                for k, v in node_list.items():
                    if (k[2] == "parenthesized_expression" and self.get_index(v.parent) == current_index):
                        while_index = self.index[k]
                        while_node = v
                        # break
                # Find the last statement in the body and an edge from last line to the while node
                self.add_edge(last_line_index, while_index, "next")

                # Add an edge from the while node to the first line in the block or to the current do node
                # self.CFG_edge_list.append((while_node, dest_node, 'loop_control')) # First node of block
                self.add_edge(while_index, current_index, "loop_control")  # do node

                # Add an edge from the while node to the next statement after the do_statement
                self.handle_next(while_node, next_node, "neg_next")

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
                dest_node = self.get_index(loop_node)
                label_name = list(filter(lambda child: child.type == "identifier", node_value.children))
                if len(label_name) > 0:
                    target_name = label_name[0].text.decode("UTF-8") + ":"
                    dest_node = self.index[self.records["label_statement_map"][target_name]]  # Check on this later
                self.CFG_edge_list.append((src_node, dest_node, "jump_next"))

            # ------------------------------------------------------------------------------------------------
            elif current_node_type == "break_statement":
                # break with a label
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
                    # if it is inside a switch, it is handled here and also refer to switch_expression,
                    # if it is inside a loop, handle it here
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

                    next_dest_index, next_node = self.get_next_index(loop_node)
                    self.handle_next(node_value, next_node, "jump_next")
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
                    next_node = loop_node
                    next_dest_index = self.get_index(loop_node)
                except:
                    # Handle yield when no loop parent or switch parent
                    next_dest_index, next_node = self.get_next_index(node_value)
                self.handle_next(node_value, next_node, "yield_exit")
            # ------------------------------------------------------------------------------------------------
            elif current_node_type == "lambda_expression":
                self.edge_to_body(node_key, node_value, "body", "lambda_next")

            elif current_node_type == "switch_expression":
                # First check if the switch expression_statement is part of a non-control statement, and add an edge to the next line
                switch_parent = java_nodes.return_switch_parent_statement(node_value, self.statement_types["non_control_statement"])
                if switch_parent is not None:
                    try:
                        next_node = switch_parent.next_named_sibling
                        src_node = self.index[node_key]
                        dest_node = self.get_index(next_node)
                        if dest_node in self.records["switch_child_map"].keys():
                            dest_node = self.records["switch_child_map"][dest_node]
                        self.add_edge(src_node, dest_node, "next_line 7")

                    except Exception as e:
                        pass

                # Find all the case blocks associated with this switch node and add an edge to each of them
                # Find the last line in each case block and add an edge to the next case block unless it is a break statement
                # BUt if the block is empty, add an edge to the next case label
                # in case of a break statement, add an edge to the next statement outside the switch
                # in case of default, add an edge to the next statement outside the switch
                # in case of no default, add an edge from last block to the next statement outside the switch
                case_node_list = {}
                default_exists = False
                # default_list = []

                # Find the next statement outside the switch
                next_dest_index, next_node = self.get_next_index(node_value)

                # For each case label block, find the first statement in the block and add an edge to it
                for k, v in node_list.items():
                    if (k[2] == "switch_block_statement_group" or k[2] == "switch_rule") and self.get_index(v.parent.parent) == current_index:
                        case_node_list[k] = v
                        case_node_index = self.index[k]
                        self.add_edge(current_index, case_node_index, "switch_case")
                        case_label = list(filter(lambda child: child.type == "switch_label", v.children))
                        for case in case_label:
                            default_case = list(filter(lambda child: child.type == "default", case.children))
                            if len(default_case) > 0:
                                default_exists = True
                # If no default exists, add an edge from switch node to the next line after it
                if not default_exists:
                    self.handle_next(node_value, next_node, "switch_exit")

                for k, v in case_node_list.items():
                    current_case_index = self.index[k]
                    current_case = v
                    case_statements = list(filter(lambda child: (child.is_named and child.type != "switch_label"),v.children))
                    case_labels = list(filter(lambda child: (child.is_named and child.type == "switch_label"),v.children))
                    next_case_node = v.next_named_sibling
                    try:
                        next_case_node_index = self.get_index(next_case_node)
                    except:
                        next_case_node_index = None

                    block_node = None
                    if len(case_statements) == 0:
                        default_flag = False
                        # Check if its a default statement, then add an edge to the next statement outside the switch
                        for case_label in case_labels:
                            default_case = list(
                                filter(
                                    lambda child: child.type == "default",
                                    case_label.children,
                                )
                            )
                            if len(default_case) > 0:
                                self.handle_next(current_case, next_node, "default_exit")
                                default_flag = True
                                break
                        # There is no case body, so add an edge from this case to the next case label, if exists
                        if not default_flag and next_case_node_index is not None:
                            self.add_edge(current_case_index, next_case_node_index, "fall through")

                    else:
                        # The case body exists
                        empty_block = False
                        if (
                            len(case_statements) > 1
                            and case_statements[0].type == "block"
                            and len(list(filter(lambda child: child.is_named, case_statements[0].children))) == 0
                        ):
                            empty_block = True
                            # Empty block followed by other statement in the same case
                            next_line = case_statements[1]
                            next_line_index = self.get_index(next_line)
                            self.add_edge(current_case_index, next_line_index, "next_line 8")

                        # Find the first line in each case block and add an edge from case label to itandl empty case block
                        
                        explicit_block = None
                        for child in v.children:
                            # Need to write a loop for unlimited layers of nesting
                            if child.is_named and child.type != "switch_label":
                                if child.type == "block":
                                    explicit_block = child
                                    for child in child.children:
                                        if (
                                            child.is_named
                                            and child.type != "switch_label"
                                        ):
                                            block_node = child
                                            break
                                else:
                                    block_node = child
                                break
                        if block_node is None:
                            # Add fall through edge to next case label
                            if empty_block == False and next_case_node_index is not None:
                                self.add_edge(current_case_index, next_case_node_index, "fall through")
                        else:
                            first_line_index = self.get_index(block_node)
                            self.add_edge(current_case_index, first_line_index, "case_next")

                        # if the case contains a set of braces and the break outside it,
                        # then add an edge from the last line inside the block to the first line outside it
                        if explicit_block is not None:
                            next_line = explicit_block.next_named_sibling
                            if next_line is not None:
                                next_line_index = self.get_index(next_line)
                                block_node = None
                                for child in reversed(explicit_block.children):
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
                                if block_node is not None:
                                    last_line_index = self.get_index(block_node)
                                    if (block_node.type in self.statement_types["non_control_statement"]):
                                        self.add_edge(last_line_index, next_line_index, "fall through")

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
                        if block_node is not None:
                            last_line_index = self.get_index(block_node)
                            if block_node.type in self.statement_types["non_control_statement"] and next_case_node_index is not None:
                                self.add_edge(
                                    last_line_index,
                                    next_case_node_index,
                                    "fall through",
                                )

                        # in case of default, add an edge to the next statement outside the switch
                        # in case of no default, add an edge from last block to the next statement outside the switch
                    if next_case_node_index is None:
                        # This is the last block
                        if block_node is not None:
                            if (block_node.type in self.statement_types["non_control_statement"]):
                                self.handle_next(block_node, next_node, "switch_out")
                        else:
                            self.handle_next(v, next_node, "switch_out")

                # in case of a break statement, add an edge to the next statement outside the switch
                # -> Handled in break statement
            # ------------------------------------------------------------------------------------------------
            elif current_node_type == "return_statement":
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
            # elif current_node_type == "assert_statement":
            #     self.add_edge(current_index, 2, "assert_false")
            # ------------------------------------------------------------------------------------------------
            elif (
                current_node_type == "try_statement"
                or current_node_type == "try_with_resources_statement"
            ):
                # Add edge from try block to first statement inside the block
                self.edge_to_body(node_key, node_value, "body", "next")
                catch_node_list = {}
                finally_node = None
                # Identify all catch blocks - add an edge from catch node to first line inside block
                for k, v in node_list.items():

                    if (k[2] == "catch_clause" and self.get_index(v.parent) == current_index):
                        catch_node_list[k] = v
                        self.edge_to_body(k, v, "body", "next")
                    elif (k[2] == "finally_clause" and self.get_index(v.parent) == current_index):
                        finally_node = v
                        self.edge_first_line(k, v)  # Not sure if this works

                # From each line inside the try block, an edge going to each catch block
                try_body = node_value.child_by_field_name("body")
                statements = []
                statements = self.get_all_statements(try_body, node_list, statements)
                if len(statements) > 0:
                    for statement in statements:
                        statement_index = self.get_index(statement)
                        for catch_node in catch_node_list.keys():
                            catch_index = self.index[catch_node]
                            # if statement.type != 'return_statement': The Exception can occur on the RHS so the catch_exception edge should be there
                            self.add_edge(statement_index, catch_index, "catch_exception")

                # Find the next statement outside the try block
                next_dest_index, next_node = self.get_next_index(node_value)
                exit_next = None

                # finally block is optional
                if finally_node is not None:
                    # From last line of finally to next statement outside the try block
                    last_line, line_type = self.get_block_last_line(finally_node, "body")
                    if line_type in self.statement_types["non_control_statement"]:
                        self.handle_next(last_line, next_node, "finally_exit")
                    # For the remaining portion, set finally block as next node if exists
                    exit_next = finally_node
                else:
                    exit_next = next_node

                # From last line of try block to finally or to next statement outside the try block
                last_line, line_type = self.get_block_last_line(node_value, "body")
                # if line_type in self.statement_types['non_control_statement']: # Inside try, edges to finally should be irrespective of control or non control statements
                if line_type in self.statement_types["node_list_type"]:
                    self.handle_next(last_line, exit_next, "try_exit")
                # From last line of every catch block to finally or to next statement outside the try block
                for catch_node, catch_value in catch_node_list.items():
                    last_line, line_type = self.get_block_last_line(catch_value, "body")
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
                # try_flag = False
                try_node = None
                while parent is not None:
                    if parent.type == "catch_clause" or parent.type == "finally_clause":
                        break
                    if (
                        parent.type == "try_statement"
                        or parent.type == "try_with_resources_statement"
                    ):
                        try_flag = True
                        try_node = parent
                        break
                    parent = parent.parent
                if try_node is None:
                    # self.add_edge(current_index, 2, "throw_exit")
                    pass
                else:
                    # try_node is like the current_node, helps us find the corresponding catch clauses

                    # Add edge from try block to first statement inside the block
                    # self.edge_to_body(node_key, node_value, 'body', 'next')
                    catch_node_list = {}
                    # finally_node = None
                    # Identify all catch blocks
                    for k, v in node_list.items():
                        if ( k[2] == "catch_clause" and self.get_index(v.parent) == current_index):
                            catch_node_list[k] = v
                    # if len(catch_node_list) == 0:
                    #     self.add_edge(current_index, 2, "throw_exit")
        
        self.add_method_call_edges()
        if warning_counter > 0:
            logger.warning("Total number of warnings from unimplemented statement types: ", warning_counter)
        return self.CFG_node_list, self.CFG_edge_list
