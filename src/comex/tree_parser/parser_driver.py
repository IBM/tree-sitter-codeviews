from ..tree_parser.java_parser import JavaParser
from ..tree_parser.cs_parser import CSParser
from ..utils import preprocessor

class ParserDriver:
    """Driver class for the parser"""

    def __init__(self, src_language, src_code):
        """Initialize the driver. Preprocess the code before parsing"""
        self.src_language = src_language
        self.src_code = self.pre_process_src_code(src_language, src_code)

        self.parser_map = {
            "java": JavaParser,
            "cs": CSParser,
            # 'python': PythonParser
            # Add more languages here
        }
        self.parser = self.parser_map[self.src_language](self.src_language, self.src_code)
        self.root_node, self.tree = self.parser.parse()
        (
            self.all_tokens,
            self.label,
            self.method_map,
            self.method_calls,
            self.start_line,
            self.declaration,
            self.declaration_map,
            self.symbol_table,
        ) = self.create_all_tokens()


    def pre_process_src_code(self, src_language, src_code):
        """Pre-process the source code"""
        src_code = preprocessor.remove_empty_lines(src_code)
        src_code = preprocessor.remove_comments(src_language, src_code)
        return src_code

    # Needs to be modified for every language
    def create_all_tokens(self):
        """Return the variable list"""
        return self.parser.create_all_tokens(
            self.src_code,
            self.parser.root_node,
            self.parser.all_tokens,
            self.parser.label,
            self.parser.method_map,
            self.parser.method_calls,
            self.parser.start_line,
            self.parser.declaration,
            self.parser.declaration_map,
            self.parser.symbol_table,
        )
