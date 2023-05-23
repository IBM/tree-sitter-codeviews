import json
import os
import shutil
import traceback

from comex.codeviews.AST.AST_driver import ASTDriver
from comex.codeviews.CFG.CFG_driver import CFGDriver
from comex.codeviews.combined_graph.combined_driver import CombinedDriver
from comex.codeviews.SDFG.SDFG import DfgRda
from deepdiff import DeepDiff

dir_check = None
# "tests/data/RANDOM/codenet_fresh_run"
AST = "tests/data/AST"
CFG = "tests/data/CFG"
SDFG = "tests/data/SDFG"
COMBINED = "tests/data/COMBINED"


def test_ast(extension: str, test_folder: str, test_name: str):
    driver = ASTDriver
    invoke_driver(driver, extension, test_folder, test_name)


def test_cfg(extension: str, test_folder: str, test_name: str):
    driver = CFGDriver
    invoke_driver(driver, extension, test_folder, test_name)


def test_sdfg(extension: str, test_folder: str, test_name: str):
    driver = DfgRda
    invoke_driver(driver, extension, test_folder, test_name)


def test_combined(extension: str, test_folder: str, test_name: str):
    driver = CombinedDriver
    config_path = os.path.join(test_folder, test_name + "-config.json")
    invoke_driver(driver, extension, test_folder, test_name, config_path)


def test_dir(extension: str, test_folder: str, test_name: str):
    driver = CombinedDriver
    config_path = os.path.normpath(os.path.join(dir_check, "../config.json"))
    try:
        invoke_driver(driver, extension, test_folder, test_name, config_path, output_file=False)
    except Exception:
        error = traceback.format_exc()
        with open(os.path.join(test_folder, test_name + ".log"), "w") as f:
            f.write(error)


def invoke_driver(driver, extension, test_folder, test_name, configuration=None, output_file=True):
    test_file = os.path.join(test_folder, test_name + "." + extension)
    file_handle = open(test_file, "r")
    src_code = file_handle.read()
    file_handle.close()
    os.makedirs(os.path.join(test_folder, test_name), exist_ok=True)
    saving_path = os.path.join(test_folder, test_name, test_name + "-answer.json")
    gold_path = os.path.join(test_folder, test_name, test_name + "-gold.json")
    if configuration is None:
        result = driver(
            src_language=extension,
            src_code=src_code,
            output_file=saving_path,
            properties={},
        ).json
    else:
        input_file = open(configuration, "r")
        config = json.load(input_file)
        input_file.close()
        codeviews = config["combined_views"]
        result = driver(
            src_language=extension,
            src_code=src_code,
            output_file=saving_path,
            graph_format="all",
            codeviews=codeviews,
        ).json
    # Comment this out
    gold_exists = os.path.exists(gold_path)
    if not gold_exists:
        shutil.copyfile(saving_path, gold_path)
    assert gold_exists is True
    file_handle = open(gold_path, "r")
    gold_result = json.load(file_handle)
    file_handle.close()
    ddiff = DeepDiff(
        gold_result,
        result,
        ignore_order=True,
    )
    if not output_file:
        shutil.rmtree(os.path.join(test_folder, test_name))
        if ddiff == {}:
            os.remove(test_file)
    assert ddiff == {}


def pytest_generate_tests(metafunc):
    dynamic_tests = []
    local_run = False
    if "ast" in metafunc.function.__name__:
        test_folder = AST
    elif "cfg" in metafunc.function.__name__:
        test_folder = CFG
    elif "sdfg" in metafunc.function.__name__:
        test_folder = SDFG
    elif "dir" in metafunc.function.__name__:
        local_run = True
        test_folder = dir_check
    else:
        test_folder = COMBINED
    if test_folder and os.path.isdir(test_folder):
        folders = []
        if local_run:
            for test in os.listdir(test_folder):
                if os.path.isdir(os.path.join(test_folder, test)) and not test.startswith(".") and not test.isnumeric():
                    folders.append(os.path.join(test_folder, test))
        if not len(folders):
            folders = [test_folder]
        for folder in folders:
            for test in os.listdir(folder):
                if os.path.isfile(os.path.join(folder, test)) and not test.startswith("."):
                    test_name, test_extension = test.split(".")
                    if test_extension in ["cs", "java"]:
                        dynamic_tests.append((test_extension, folder, test_name))
    metafunc.parametrize(("extension", "test_folder", "test_name"), dynamic_tests)
