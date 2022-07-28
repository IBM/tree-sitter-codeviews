from tree_parser.custom_parser import CustomParser

class JavaParser(CustomParser):
    def __init__(self, src_language, src_code):
        super().__init__(src_language, src_code)

    def create_all_tokens(self, src_code, root_node, all_tokens, label, method_map, start_line):
        # Needs to be modifed for every language

        remove_list = ['class_declaration','method_declaration', 'method_invocation']

        # For reach identifier, if the parent is field_access -> keep going up till you reach the highest parent
        # else map to self
        # check if parent of highest mapped identifier is method invocation, then add it to the list
        # This logic helps create more meaningful tokens when it comes to variable names of object oriented languages like Java

        if root_node.is_named and (len(root_node.children)==0 or root_node.type=='string') and root_node.type!='comment' :
            index = self.index[(root_node.start_point,root_node.end_point,root_node.type)]
            label[index] = root_node.text.decode('UTF-8')
            start_line[index] = root_node.start_point[0]
            all_tokens.append(index)
            
            current_node = root_node

            if current_node.parent is not None and current_node.parent.type in remove_list:
                method_map.append(index)

            if current_node.parent is not None and current_node.parent.type == 'field_access':
                object_node = current_node.parent.child_by_field_name('field')
                object_index = self.index[(object_node.start_point,object_node.end_point,object_node.type)]
                current_index = self.index[(current_node.start_point,current_node.end_point,current_node.type)]
                if object_index ==  current_index:
                    method_map.append(current_index)   

                while current_node.parent is not None and current_node.parent.type == 'field_access':
                    current_node = current_node.parent

                if current_node.parent is not None and current_node.parent.type == 'method_invocation':
                        method_map.append(index)
                label[index] = current_node.text.decode('UTF-8')

        else:      
            for child in root_node.children:
                self.create_all_tokens(src_code, child, all_tokens, label, method_map, start_line)
            
        return all_tokens, label, method_map, start_line
