# from comex.codeviews.AST.AST_driver import ASTDriver
# from comex.codeviews.DFG.DFG_driver import DFGDriver
import pickle

from loguru import logger
from tqdm import tqdm

from antipatterns.dfg import Dataset
from comex.utils import src_parser

logger.remove()
logger.add(lambda msg: tqdm.write("\n" + msg, end="\n"), colorize=True)

ignore = {"cs": [], "java": []}
random_sample = 0
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
        "statements": True,
        "last_use": True,
        "last_def": True,
    },
    "CFG": {
        "exists": True

    }
}
checks = [
    "cs",
    "java"
]


class Translation(Dataset):
    def read_src(self, line, ind, kind=""):
        src = src_parser.pre_process_src(self.extension, line, wrap_class=True)
        self.src[ind] = src
        return src


if __name__ == "__main__":
    pickler = "./data/RANDOM/translation.pkl"
    if False:
        with open(pickler, "rb") as pickle_f:
            java, cs = pickle.load(pickle_f)
    else:
        java = {}
        cs = {}
        result = []
        if "java" in checks:
            logger.info("Starting Java")
            java = Translation("./data/RANDOM/translation.java", combined_config, random_sample, ignore, kind="translation")
            # jsum = java.summarize()
            # print(jsum)
        if "cs" in checks:
            logger.info("Starting CS")
            cs = Translation("./data/RANDOM/translation.cs", combined_config, random_sample, ignore, kind="translation")
            # csum = cs.summarize(concern="local_function_statement")
            # print(csum)
        result.append(java)
        result.append(cs)
        with open(pickler, "wb") as pickle_f:
            pickle.dump(result, pickle_f)

    # cs.analyze(CFGDriver)

    # line ="public virtual int Stem(char[] s, int len){for (int i = 0; i < len; i++){switch (s[i]){case 'ä':case 'à':case 'á':case 'â':s[i] = 'a';break;case 'ö':case 'ò':case 'ó':case 'ô':s[i] = 'o';break;case 'ï':case 'ì':case 'í':case 'î':s[i] = 'i';break;case 'ü':case 'ù':case 'ú':case 'û':s[i] = 'u';break;}}len = Step1(s, len);return Step2(s, len);}"
    # cs.pre_process_src("public class test {" + line + "}")

    # ind = 7030
    # result = cs.run(CFGDriver, ind)
    # with open("analyze_dataset_sample.cs", "w") as f:
    #     f.write(cs.src[ind])
    # postprocessor.write_to_dot(
    #     result.graph, "analyze_dataset_sample.dot", output_png=True
    # )
