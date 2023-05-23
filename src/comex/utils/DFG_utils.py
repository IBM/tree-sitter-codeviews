# This code is from https://github.com/microsoft/CodeBERT/blob/master/GraphCodeBERT/clonedetection/parser/utils.py

def tree_to_token_index(root_node):
    """Returns all tokens in the tree rooted at the given root node using index values"""
    if (
        len(root_node.children) == 0 or root_node.type == "string"
    ) and root_node.type != "comment":
        return [(root_node.start_point, root_node.end_point, root_node.type)]
    else:
        code_tokens = []
        for child in root_node.children:
            code_tokens += tree_to_token_index(child)
        return code_tokens


def tree_to_variable_index(root_node, index_to_code):
    """Returns all tokens in the tree rooted at the given root node"""
    if (
        len(root_node.children) == 0 or root_node.type == "string"
    ) and root_node.type != "comment":
        index = (root_node.start_point, root_node.end_point, root_node.type)
        _, code = index_to_code[index]
        if root_node.type != code:
            return [(root_node.start_point, root_node.end_point, root_node.type)]
        else:
            return []
    else:
        code_tokens = []
        for child in root_node.children:
            code_tokens += tree_to_variable_index(child, index_to_code)
        return code_tokens


def index_to_code_token(index, code):
    """Returns code value given the indexes of a particular token"""
    start_point = index[0]
    end_point = index[1]
    if start_point[0] == end_point[0]:
        s = code[start_point[0]][start_point[1] : end_point[1]]
    else:
        s = ""
        s += code[start_point[0]][start_point[1] :]
        for i in range(start_point[0] + 1, end_point[0]):
            s += code[i]
        s += code[end_point[0]][: end_point[1]]
    return s
