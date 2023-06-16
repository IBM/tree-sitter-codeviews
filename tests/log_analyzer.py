import glob
import os.path
import re
import sys

if len(sys.argv) < 2:
    print("Usage: python log_stats.py <directory>")
    sys.exit()

directory = sys.argv[1]
logs = {}
samples = {}

if "java" in directory:
    lang = "java"
else:
    lang = "cs"

for file in glob.glob(directory + "/*.log"):
    with open(file, "r") as f:
        lines = f.readlines()
        if not lines:
            continue
        last_line = lines[-1].strip()
        category = last_line.split()
        category = category[0] + category[-1]
        category = re.sub('[^0-9a-zA-Z]+', '_', category)
        if category.startswith("TimeoutError"):
            # write filename without extension to a file timeout.txt
            with open("timeout.txt", "a") as f:
                f.write(file.split("/")[-1].rsplit('.', 1)[0] + ", ")
        category = f"classified_logs/{category}"
        if not os.path.exists(category):
            os.makedirs(category)
        os.system(f"cp {file} {category}")
        os.system(f"cp {file.rsplit('.',1)[0]}.{lang} {category}")
        if category in logs:
            logs[category] += 1
        else:
            logs[category] = 1
            samples[category] = file

for category in logs:
    print(f"{category}: {logs[category]} logs, sample file: {samples[category]}")
