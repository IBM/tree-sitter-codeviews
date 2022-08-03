from codeviews.DFG.DFG import DFGGraph
from utils import DFG_utils
from utils import java_nodes

class DFGGraph_java(DFGGraph):
    def __init__(self, src_language, src_code, properties, root_node, parser):
        super().__init__(src_language, src_code, properties, root_node, parser)

        self.statement_types =  {
            'node_list_type':['declaration', 'expression_statement', 'labeled_statement', 'if_statement', 'while_statement', 'for_statement', 'enhanced_for_statement', 'assert_statement', 'do_statement', 'break_statement', 'continue_statement', 'return_statement', 'yield_statement', 'switch_expression', 'synchronized_statement', 'local_variable_declaration', 'throw_statement', 'try_statement', 'try_with_resources_statement', 'method_declaration','constructor_declaration', 'switch_block_statement_group', 'switch_rule', 'throw_statement', 'explicit_constructor_invocation'],
            'non_control_statement' : ['declaration', 'expression_statement', 'local_variable_declaration'],
            'control_statement' : ['if_statement', 'while_statement', 'for_statement', 'enhanced_for_statement', 'do_statement', 'break_statement', 'continue_statement', 'return_statement', 'yield_statement', 'switch_expression', 'synchronized_statement',  'try_statement', 'try_with_resources_statement', 'yield_statement'],
            'loop_control_statement' : ['while_statement', 'for_statement', 'enhanced_for_statement'],
            'not_implemented' : ['try_with_resources_statement'],
            'inner_node_type': ['declaration', 'expression_statement', 'local_variable_declaration'],
            'outer_node_type' : ['for_statement']           
        }
        self.records = {
            'basic_blocks': {},
            'method_list': {},
            'function_calls': {},
            'switch_child_map': {},
            'label_statement_map': {}
        }

        _,self.node_list,self.graph_node_list,_ = java_nodes.get_nodes(root_node = self.root_node, node_list = {}, graph_node_list = [], index = self.index, records = self.records, statement_types = self.statement_types)
        DFG,_= self.DFG_java(root_node,self.index_to_code,{}) 
        self.graph = self.to_networkx(DFG, self.graph_node_list)

    def DFG_java(self,root_node,index_to_code,states):
        assignment=['assignment_expression']
        def_statement=['variable_declarator']
        increment_statement=['update_expression']
        if_statement=['if_statement','else']
        for_statement=['for_statement']
        enhanced_for_statement=['enhanced_for_statement']
        while_statement=['while_statement']
        do_first_statement=[]    
        states=states.copy()
        if (len(root_node.children)==0 or root_node.type=='string') and root_node.type!='comment' and root_node.is_named:
            idx,code=index_to_code[(root_node.start_point,root_node.end_point, root_node.type)]
            if root_node.type==code: # Its a keyword leaf node
                return [],states
            elif code in states: # its an identifier that has occured before 
                return [(code,idx,'comesFrom',[code],states[code].copy())],states
            else:
                if root_node.type=='identifier': # identifier occurs for first time so we add it to the states we are keeping track of 
                    states[code]=[idx]
                return [(code,idx,'comesFrom',[],[])],states
        elif root_node.type in def_statement:
            name=root_node.child_by_field_name('name')
            value=root_node.child_by_field_name('value')
            DFG=[]
            if value is None:
                indexs=DFG_utils.tree_to_variable_index(name,index_to_code)
                for index in indexs:
                    idx,code=index_to_code[index]
                    DFG.append((code,idx,'comesFrom',[],[]))
                    states[code]=[idx]
                return sorted(DFG,key=lambda x:x[1]),states
            else:
                name_indexs=DFG_utils.tree_to_variable_index(name,index_to_code)
                value_indexs=DFG_utils.tree_to_variable_index(value,index_to_code)
                temp,states=self.DFG_java(value,index_to_code,states)
                DFG+=temp            
                for index1 in name_indexs:
                    idx1,code1=index_to_code[index1]
                    for index2 in value_indexs:
                        idx2,code2=index_to_code[index2]
                        DFG.append((code1,idx1,'comesFrom',[code2],[idx2]))
                    states[code1]=[idx1]   
                return sorted(DFG,key=lambda x:x[1]),states
        elif root_node.type in assignment:
            left_nodes=root_node.child_by_field_name('left')
            right_nodes=root_node.child_by_field_name('right')
            DFG=[]
            temp,states=self.DFG_java(right_nodes,index_to_code,states)
            DFG+=temp            
            name_indexs=DFG_utils.tree_to_variable_index(left_nodes,index_to_code)
            value_indexs=DFG_utils.tree_to_variable_index(right_nodes,index_to_code)        
            for index1 in name_indexs:
                idx1,code1=index_to_code[index1]
                for index2 in value_indexs:
                    idx2,code2=index_to_code[index2]
                    DFG.append((code1,idx1,'computedFrom',[code2],[idx2]))
                states[code1]=[idx1]   
            return sorted(DFG,key=lambda x:x[1]),states
        elif root_node.type in increment_statement:
            DFG=[]
            indexs=DFG_utils.tree_to_variable_index(root_node,index_to_code)
            for index1 in indexs:
                idx1,code1=index_to_code[index1]
                for index2 in indexs:
                    idx2,code2=index_to_code[index2]
                    DFG.append((code1,idx1,'computedFrom',[code2],[idx2]))
                states[code1]=[idx1]
            return sorted(DFG,key=lambda x:x[1]),states   
        elif root_node.type in if_statement:
            DFG=[]
            current_states=states.copy()
            others_states=[]
            flag=False
            tag=False
            if 'else' in root_node.type:
                tag=True
            for child in root_node.children:
                if 'else' in child.type:
                    tag=True
                if child.type not in if_statement and flag is False:
                    temp,current_states=self.DFG_java(child,index_to_code,current_states)
                    DFG+=temp
                else:
                    flag=True
                    temp,new_states=self.DFG_java(child,index_to_code,states)
                    DFG+=temp
                    others_states.append(new_states)
            others_states.append(current_states)
            if tag is False:
                others_states.append(states)
            new_states={}
            for dic in others_states:
                for key in dic:
                    if key not in new_states:
                        new_states[key]=dic[key].copy()
                    else:
                        new_states[key]+=dic[key]
            for key in new_states:
                new_states[key]=sorted(list(set(new_states[key])))
            return sorted(DFG,key=lambda x:x[1]),new_states
        elif root_node.type in for_statement:
            DFG=[]
            for child in root_node.children:
                temp,states=self.DFG_java(child,index_to_code,states)
                DFG+=temp
            flag=False
            for child in root_node.children:
                if flag:
                    temp,states=self.DFG_java(child,index_to_code,states)
                    DFG+=temp                
                elif child.type=="local_variable_declaration":
                    flag=True
            dic={}
            for x in DFG:
                if (x[0],x[1],x[2]) not in dic:
                    dic[(x[0],x[1],x[2])]=[x[3],x[4]]
                else:
                    dic[(x[0],x[1],x[2])][0]=list(set(dic[(x[0],x[1],x[2])][0]+x[3]))
                    dic[(x[0],x[1],x[2])][1]=sorted(list(set(dic[(x[0],x[1],x[2])][1]+x[4])))
            DFG=[(x[0],x[1],x[2],y[0],y[1]) for x,y in sorted(dic.items(),key=lambda t:t[0][1])]
            return sorted(DFG,key=lambda x:x[1]),states
        elif root_node.type in enhanced_for_statement:
            name=root_node.child_by_field_name('name')
            value=root_node.child_by_field_name('value')
            body=root_node.child_by_field_name('body')
            DFG=[]
            for i in range(2):
                temp,states=self.DFG_java(value,index_to_code,states)
                DFG+=temp       
                name_indexs=DFG_utils.tree_to_variable_index(name,index_to_code)
                value_indexs=DFG_utils.tree_to_variable_index(value,index_to_code)        
                for index1 in name_indexs:
                    idx1,code1=index_to_code[index1]
                    for index2 in value_indexs:
                        idx2,code2=index_to_code[index2]
                        DFG.append((code1,idx1,'computedFrom',[code2],[idx2]))
                    states[code1]=[idx1]   
                temp,states=self.DFG_java(body,index_to_code,states)
                DFG+=temp                       
            dic={}
            for x in DFG:
                if (x[0],x[1],x[2]) not in dic:
                    dic[(x[0],x[1],x[2])]=[x[3],x[4]]
                else:
                    dic[(x[0],x[1],x[2])][0]=list(set(dic[(x[0],x[1],x[2])][0]+x[3]))
                    dic[(x[0],x[1],x[2])][1]=sorted(list(set(dic[(x[0],x[1],x[2])][1]+x[4])))
            DFG=[(x[0],x[1],x[2],y[0],y[1]) for x,y in sorted(dic.items(),key=lambda t:t[0][1])]
            return sorted(DFG,key=lambda x:x[1]),states
        elif root_node.type in while_statement:  
            DFG=[]
            for i in range(2):
                for child in root_node.children:
                    temp,states=self.DFG_java(child,index_to_code,states)
                    DFG+=temp    
            dic={}
            for x in DFG:
                if (x[0],x[1],x[2]) not in dic:
                    dic[(x[0],x[1],x[2])]=[x[3],x[4]]
                else:
                    dic[(x[0],x[1],x[2])][0]=list(set(dic[(x[0],x[1],x[2])][0]+x[3]))
                    dic[(x[0],x[1],x[2])][1]=sorted(list(set(dic[(x[0],x[1],x[2])][1]+x[4])))
            DFG=[(x[0],x[1],x[2],y[0],y[1]) for x,y in sorted(dic.items(),key=lambda t:t[0][1])]
            return sorted(DFG,key=lambda x:x[1]),states        
        else:
            DFG=[]
            for child in root_node.children:
                if child.type in do_first_statement:
                    temp,states=self.DFG_java(child,index_to_code,states)
                    DFG+=temp
            for child in root_node.children:
                if child.type not in do_first_statement:
                    temp,states=self.DFG_java(child,index_to_code,states)
                    DFG+=temp
            
            return sorted(DFG,key=lambda x:x[1]),states