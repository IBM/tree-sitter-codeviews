import os
import json

from codeviews.AST.AST_driver import ASTDriver


def check_result(test_name:str,gold_path:str,saving_path:str) :
    gold_path = gold_path.replace(" ", "\ ")
    saving_path = saving_path.replace(" ", "\ ")
    stream = os.popen("jq --argfile a {} --argfile b {} -n 'def post_recurse(f): def r: (f | select(. != null) | r), .; r; def post_recurse: post_recurse(.[]?); ($a | (post_recurse | arrays) |= sort) as $a | ($b | (post_recurse | arrays) |= sort) as $b | $a == $b'".format(gold_path,saving_path))
    output = stream.read()
    output = output.strip()

    if not (output == "true") :
        print("{} : JSON Test Failed".format(test_name))
    else :
        print("{} : JSON Test Passed".format(test_name))


def save_result(answer,saving_path:str) :
    with open(saving_path,"w") as f :
        json.dump(answer,f,indent=4)

if __name__ == '__main__' :
    parent_dir = os.path.abspath(os.path.dirname(__file__))
    super_parent_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    immediate_parent = parent_dir.split(super_parent_dir)[1].replace("/","").replace("\\","")

    test_folder = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), immediate_parent)
    test_folder = os.path.join(test_folder,"test_cases")
    
    print("Test Folder : {}".format(test_folder))

    test_cases = os.listdir(test_folder)
    try :
        test_cases.remove(".DS_Store")
    except Exception as e :
        pass



    for test in test_cases :

        program_path = os.path.join(test_folder,test,test+".java")
        file_handle = open(program_path, 'r')
        src_code = file_handle.read()
        file_handle.close()
        saving_path = os.path.join(test_folder,test,test+"-answer.json")

        # Make sure to add the postprocess. write to json like inside ASTDriver for this to work
        ASTDriver(src_language = 'java', src_code = src_code,  output_file = saving_path, properties = {})
       
        gold_path = os.path.join(test_folder,test,test+"-gold.json")
        check_result(test,gold_path,saving_path)

