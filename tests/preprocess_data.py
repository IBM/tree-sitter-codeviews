import json
import os

from loguru import logger
from tqdm import tqdm

from comex.utils import src_parser

logger.remove()
logger.add(lambda msg: tqdm.write("\n" + msg, end="\n"), colorize=True)

ignore = {"cs": [], "java": []}

checks = [
    "cs",
    "java"
]


if __name__ == "__main__":
    file_location = "/Volumes/Samsung_T5/GitHub/Enhanced-GraphCodeBERT/GraphCodeBERT/translation/data"
    new_file_location = f"{file_location}/processed"
    os.makedirs(new_file_location, exist_ok=True)
    files = ["test.java-cs.txt.cs","test.java-cs.txt.java","train.java-cs.txt.cs","train.java-cs.txt.java","valid.java-cs.txt.cs","valid.java-cs.txt.java"]
    for file in files:
        name, extension = file.rsplit(".", 1)
        with open(os.path.join(new_file_location, file), "w") as w:
            with open(os.path.join(file_location, file), "r") as f:
                lines = f.read().splitlines()
                for line in lines:
                    processed_line = src_parser.pre_process_src(extension, line, wrap_class=False, ignore_error=True)
                    w.write(json.dumps(processed_line)+"\n")