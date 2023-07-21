"""CLI for depend."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from loguru import logger

from .codeviews.combined_graph.combined_driver import CombinedDriver
from . import get_language_map

get_language_map()
app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(
        lang: str = typer.Option(..., help="java, cs"),
        code: Optional[str] = typer.Option(None, help="""
    public class Max2 {
        public static void main(String[] args) {
            int x= 3;
            x = x + 3;
            int y = 4;
            y += 1;
        }
    }
    """),
        code_file: Optional[Path] = typer.Option(None, help="./test_file,java"),
        graphs: str = typer.Option("ast,dfg", help="ast, cfg, dfg"),
        output: str = typer.Option("dot", help="all/json/dot (dot generates png as well)"),
        blacklisted: str = typer.Option("", help="Nodes to be removed from the AST"),
        collapsed: bool = typer.Option(False, help="Collapses all occurrences of a variable into one node"),
        # statements: bool = typer.Option(True, help="Converts DFG output to statement level and uses RDA"),
        last_def: bool = typer.Option(False, help="Adds last definition information to the DFG"),
        last_use: bool = typer.Option(False, help="Adds last use information to the DFG"),
        throw_parse_error: bool = typer.Option(False, help="Throws an error if the code cannot be parsed"),
        debug: bool = typer.Option(False, help="Enables debug logs"),
):
    """
    Comex

    Generates, customizes and combines multiple source code representations (AST, CFG, DFG)


    """
    if debug:
        level = "DEBUG"
    else:
        level = "WARNING"

    config = {
        "handlers": [{"sink": sys.stderr, "level": level}],
    }
    logger.configure(**config)

    codeviews = {
        "AST": {
            "exists": False,
            "collapsed": collapsed,
            "minimized": bool(blacklisted),
            "blacklisted": blacklisted.split(",")
        },
        "DFG": {
            "exists": False,
            "collapsed": collapsed,
            "minimized": False,
            "statements": True,
            "last_def": last_def,
            "last_use": last_use
        },
        "CFG": {
            "exists": False,
        }
    }

    if "ast" in graphs.lower():
        codeviews["AST"] = {
            "exists": True,
            "collapsed": collapsed,
            "minimized": bool(blacklisted),
            "blacklisted": blacklisted.split(",")
        }
    if "dfg" in graphs.lower():
        codeviews["DFG"] = {
            "exists": True,
            "collapsed": collapsed,
            "minimized": False,
            "statements": True,
            "last_def": last_def,
            "last_use": last_use
        }
    if "cfg" in graphs.lower():
        codeviews["CFG"] = {
            "exists": True,
        }

    try:
        if code_file:
            file_handle = open(code_file, "r")
            src_code = file_handle.read()
            file_handle.close()
            CombinedDriver(src_language=lang, src_code=src_code, output_file="output.json",
                           graph_format=output, codeviews=codeviews)
        else:
            if not code:
                raise Exception("No code provided")
            CombinedDriver(src_language=lang, src_code=code, output_file="output.json", graph_format=output,
                           codeviews=codeviews)
    except (
            Exception
    ) as e:
        try:
            logger.error(e.msg)
        except AttributeError:
            logger.error(e)
        sys.exit(-1)
