# from comex.codeviews.AST.AST_driver import ASTDriver
# from comex.codeviews.DFG.DFG_driver import DFGDriver
import pickle

from loguru import logger
from tqdm import tqdm

from antipatterns.cfg import Dataset
from comex.utils import src_parser

logger.remove()
logger.add(lambda msg: tqdm.write("\n" + msg, end="\n"), colorize=True)

ignore = {"cs": [9164, 1442, 3691, 4086, 5491, 10220, 11226, 7303,
                 7202  # wrong but unsure how to exclude
                 ], "java": []}

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
            java = Translation("./data/RANDOM/translation.java", ignore)
            jsum = java.summarize()
            print(jsum)
        if "cs" in checks:
            logger.info("Starting CS")
            cs = Translation("./data/RANDOM/translation.cs", ignore)
            csum = cs.summarize(concern="local_function_statement")
            print(csum)
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
