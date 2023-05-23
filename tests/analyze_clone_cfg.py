# from comex.codeviews.AST.AST_driver import ASTDriver
# from comex.codeviews.DFG.DFG_driver import DFGDriver
import json
import os
import pickle

from loguru import logger
from tqdm import tqdm

from antipatterns.cfg import Dataset

logger.remove()
logger.add(lambda msg: tqdm.write("\n" + msg, end="\n"), colorize=True)

ignore = {"java": [ 4119, 1572, 205,                # inline class definition
                    # 3249, 6758, 545, 1573, 2226, 2719, 2802, 2806, 2819, 3130, 3134, 3355, 4210, 4274, 4565, 5136, 5847, 6760, 8135, 8776, 8923, 8945, 80, 4712,                  # lambda functions (or constructor)
                    1464,               # empty cry -> unreachable catch
                    # 389, 1287,           # long (>5s)
                #    7345, 7459, 3487,    # very long
                   5283, 6370               # doesn't proceed
                   ]}

checks = [
    "java"
]


class Clone(Dataset):
    def read_src(self, line, ind, kind=""):
        json_snippet = json.loads(line)["func"]
        src = "public class test {\n" + json_snippet + "\n}"
        self.src[ind] = src
        return src


if __name__ == "__main__":
    pickler = "./data/RANDOM/clone.pkl"
    if os.path.exists(pickler):
        with open(pickler, "rb") as pickle_f:
            java, cs = pickle.load(pickle_f)
    else:
        java = {}
        cs = {}
        result = []
        if "java" in checks:
            logger.info("Starting Java")
            java = Clone("./data/RANDOM/clone.java", ignore)
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
