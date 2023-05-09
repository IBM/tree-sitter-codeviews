# from comex.codeviews.AST.AST_driver import ASTDriver
# from comex.codeviews.DFG.DFG_driver import DFGDriver
import pickle

from loguru import logger
from tqdm import tqdm

from antipatterns.cfg import Dataset

logger.remove()
logger.add(lambda msg: tqdm.write("\n" + msg, end="\n"), colorize=True)

ignore = {"java": [
    # 85, 413, 1250, 1520,  # lambda expression not supported
                   ]}

checks = [
    "java"
]

if __name__ == "__main__":
    pickler = "./data/RANDOM/search.pkl"
    if False:
        with open(pickler, "rb") as pickle_f:
            java = pickle.load(pickle_f)
    else:
        java = {}
        cs = {}
        result = []
        if "java" in checks:
            logger.info("Starting Java")
            java = Dataset("./data/RANDOM/search.java", ignore, kind="search")
            jsum = java.summarize()
            print(jsum)
        result.append(java)
        with open(pickler, "wb") as pickle_f:
            pickle.dump(result, pickle_f)

    # cs.analyze(CFGDriver)

    # line ="public virtual int Stem(char[] s, int len){for (int i = 0; i < len; i++){switch (s[i]){case 'ä':case 'à':case 'á':case 'â':s[i] = 'a';break;case 'ö':case 'ò':case 'ó':case 'ô':s[i] = 'o';break;case 'ï':case 'ì':case 'í':case 'î':s[i] = 'i';break;case 'ü':case 'ù':case 'ú':case 'û':s[i] = 'u';break;}}len = Step1(s, len);return Step2(s, len);}"
    # cs.pre_process_src("public class test {" + line + "}")

    # result = cs.run(CFGDriver, 1058)
    # postprocessor.write_to_dot(
    #     result.graph, "analyze_dataset_sample.dot", output_png=True
    # )
