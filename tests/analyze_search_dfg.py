# from comex.codeviews.AST.AST_driver import ASTDriver
# from comex.codeviews.DFG.DFG_driver import DFGDriver

from loguru import logger
from tqdm import tqdm

from antipatterns.dfg import Dataset

logger.remove()
logger.add(lambda msg: tqdm.write("\n" + msg, end="\n"), colorize=True)

ignore = {"java": []}
checks = [
    "java"
]

combined_config = {
    "AST": {
        "exists": False,
        "collapsed": False,
        "minimized": False,
        "blacklisted": ["expression_statement", "method_invocation", "class_body", "class_declaration", "modifiers"]

    },
    "DFG": {
        "exists": True,
        "collapsed": False,
        "minimized": False,
        "statements": True
    },
    "CFG": {
        "exists": True

    }
}

random_sample = 0
fixed_run = None
min_set = False
# fixed_run = 15

if __name__ == "__main__":
    pickler = "./data/RANDOM/dfg_search.pkl"
    # os.path.exists(pickler)
    if False:
        with open(pickler, "rb") as pickle_f:
            java = pickle.load(pickle_f)
    else:
        java = {}
        cs = {}
        result = []
        if "java" in checks:
            logger.info("Starting Java")
            java = Dataset("./data/RANDOM/search.java", combined_config, random_sample, ignore, kind="search", fixed_run=fixed_run, min_set=min_set)
            # jsum = java.summarize()
            # print(jsum)
        result.append(java)
        # with open(pickler, "wb") as pickle_f:
        #     pickle.dump(result, pickle_f)

    # cs.analyze(CFGDriver)

    # line ="public virtual int Stem(char[] s, int len){for (int i = 0; i < len; i++){switch (s[i]){case 'ä':case 'à':case 'á':case 'â':s[i] = 'a';break;case 'ö':case 'ò':case 'ó':case 'ô':s[i] = 'o';break;case 'ï':case 'ì':case 'í':case 'î':s[i] = 'i';break;case 'ü':case 'ù':case 'ú':case 'û':s[i] = 'u';break;}}len = Step1(s, len);return Step2(s, len);}"
    # cs.pre_process_src("public class test {" + line + "}")

    # result = cs.run(CFGDriver, 1058)
    # postprocessor.write_to_dot(
    #     result.graph, "analyze_dataset_sample.dot", output_png=True
    # )
