from comex.tree_parser.parser_driver import ParserDriver
from comex.utils.cs_nodes import statement_types as cs_statement_types
from comex.utils.java_nodes import statement_types as java_statement_types


def traverse_tree(tree, finest_granularity=None):
    if finest_granularity is None:
        finest_granularity = []
    cursor = tree.walk()

    reached_root = False
    while not reached_root:
        yield cursor.node

        if cursor.goto_first_child() and cursor.node.type not in finest_granularity:
            continue

        if cursor.goto_next_sibling():
            continue

        retracing = True
        while retracing:
            if not cursor.goto_parent():
                retracing = False
                reached_root = True

            if cursor.goto_next_sibling():
                retracing = False


def pre_process_src(extension, line, wrap_class=False, ignore_error=False):
    if wrap_class:
        line = "public class test {" + line + "}"
    parsed = ParserDriver(extension, line)
    # new_line_pos = set()
    fixed = ""
    if extension == "java":
        statement_types = java_statement_types
    else:
        statement_types = cs_statement_types
    if not ignore_error:
        if parsed.parser.root_node.has_error:
            return None
        # for tag in parsed.parser.index:
        #     if tag[2] == "ERROR":
        #         return None
        # if tag[2] in statement_types["node_list_type"]:
        #     new_line_pos.add(tag[0][-1]-1)
    # for pos, char in enumerate(line):
    #     fixed = fixed + char
    #     if pos in new_line_pos:
    #         fixed = fixed + "\n"
    for node in traverse_tree(parsed.tree):
        # ? keeping on node.children check causes literals to be dropped case 7129
        if node.type in statement_types["node_list_type"]:
            fixed = fixed + "\n"
        if (
                not node.children and "literal" not in node.parent.type
        ) or "literal" in node.type:
            fixed = fixed + node.text.decode() + " "

    return fixed
