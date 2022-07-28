import json
import time
from codeviews.AST.AST_driver import ASTDriver
from codeviews.CFG.CFG_driver import CFGDriver
from codeviews.CST.CST_driver import CSTDriver
from codeviews.DFG.DFG_driver import DFGDriver
from codeviews.combined_graph.combined_driver import CombinedDriver

start_time = time.time()
# ----------------------------------------------------------------
input_file = open('config.json', 'r')
config = json.load(input_file)

# Set the Language you want to test here
src_language = config['src_language']
# Set the test file path here
file_name = config['file_name']
file_path = './code_test_files/' + src_language+'/'+file_name
file_handle = open(file_path, 'r')
src_code = file_handle.read()

code_view = config['code_view']
graph_format = config['graph_format']
output_file = "./output_json/DFG_output.json"

# ----------------------------------------------------------------
if config['combined'] == True:
    codeviews = config['combined_views']
    print("Combined view")
    output_file = "./output_graphs/combined_output"
    CombinedDriver(src_language = src_language, src_code = src_code, output_file = output_file, graph_format = graph_format, codeviews = codeviews)

# Use the following cases if you want to generate simple AST, CST, CFG or DFG without using the combined driver
else:

    if code_view == 'DFG':
        DFGDriver(src_language, src_code, output_file)
    
    elif code_view == 'CFG':
        CFGDriver(src_language, src_code, output_file)
        
    elif code_view == 'AST':
        ASTDriver(src_language, src_code, output_file)
    
    elif code_view == 'CST':
        CSTDriver(src_language, src_code)
    
    elif code_view == 'combined_graph':
        pass

    else:
        print("code_view is not supported")

    
print("\n--- Time taken: %s seconds ---\n" % (time.time() - start_time))