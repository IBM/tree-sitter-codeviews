# Tree Sitter Multi Codeview Generator

Tree Sitter Multi Codeview Generator aims to generate combined multi-code view graphs that can be used with various types of machine learning models (sequence model neural networks, graph neural networks, etc). It is also designed to be easily extended to various source code languages. [tree-sitter](https://tree-sitter.github.io/tree-sitter/) is used for parsing which is highly efficient and has support for over 40+ languages. Currently, this repository supports codeviews for Java in over 40 possible combinations of codeviews. It has been structured such that support for other languages can be easily added. If you wish to add support for more languages, please refer to the [contributing](CONTRIBUTING.md) guide.

## Comex
`comex` is a rebuild of Tree Sitter Multi Codeview Generator for easier invocation as a Python package. 
This rebuild also includes a cli interface for easier usage.
It isolates the logic pertaining to the generation and combination of codeviews to better differentiate tasks involved in the `IBM OSCP Project`.

### Installation

`comex` is published on the Python Registry and can be easily installed via pip:

```console
pip install comex
```

**Note**: You would need to install GraphViz([dot](https://graphviz.org/download/)) so that the graph visualizations are generated

---
To setup `comex` for development using the source code in your python environment:

```console
pip install -r requirements-dev.txt
```
**Note**: Please clone recursively so sub-modules are setup correctly
```console
git clone --recursive {...}
```

This performs an editable install, meaning that comex would be available throughout your environment (particularly relevant if you use conda or something of the sort). This means now you can interact and import from `comex` just like any other package while remaining standalone but also reflecting any code side updates without any other manual steps

---
### Usage as a CLI

This is the recommended way to get started with `comex` as it is the most user friendly

The attributes and options supported by the CLI are well documented and can be viewed by running:
```console
comex --help
```

For example, to generate a combined CFG and DFG graph for a java file, you can run:
```console
comex --lang "java" --code-file ./test.java --graphs "cfg,dfg"
```

### Usage as a Python Package

The comex package can be used by importing required drivers as follows:

```python
from comex.codeviews.combined_graph.combined_driver import CombinedDriver

CombinedDriver(
    src_language=lang,
    src_code=code,
    output_file="output.json",
    graph_format=output,
    codeviews=codeviews
)
```
In most cases the required combination can be obtained via the `combined_driver` module as shown above.

````
src_language: denotes one of the supported languaged hence currently "java" or "cs"

src_code: denotes the source code to be parsed

output_file: denotes the output file to which the generated graph is written

graph_format: denotes the format of the output graph. Currently supported formats are "dot" and "json". To generate both pass "all"

codeviews: refers to the configuration passed for each codeview
````

### Output Example:

Combined simple AST+CFG+DFG for a simple Java program that finds the maximum among 2 numbers:

<img src="https://github.com/IBM/tree-sitter-codeviews/raw/main/sample.png" >


### Code Organization
The code is structured in the following way:
1. For each code-view, first the source code is parsed using the tree-sitter parser and then the various code-views are generated. In the [tree_parser](src/comex/tree_parser) directory, the Parser and ParserDriver is implemented with various funcitonalities commonly required by all code-views. Language-specific features are further developed in the language-specific parsers also placed in this directory.
2. The [codeviews](src/comex/codeviews) directory contains the core logic for the various codeviews. Each codeview has a driver class and a codeview class, which is further inherited and extended by language in case of code-views that require language-specific implementation.
3. The [cli.py](src/comex/cli.py) file is the CLI implementation. The drivers can also be directly imported and used like a python package. It is responsible for parsing the source code and generating the codeviews.

### Testing

The repo is setup to automatically perform CI tests on making pulls to main and development branches.
To test locally:

Run specific test 
- Say you wish to run `test_cfg` function
- Drop the `'[...]'` part to run all tests in a file
  - formatted as [extension-filename]
- no-cov prevents coverage report from being printed
```console
pytest -k 'test_cfg[cs-test7]' --no-cov
```

Run all tests and get coverage report
```console
pytest
```

Analyze the deviation report given by `deepdiff` by using the verbose output.
This will help quickly figure out difference from the gold file
```console
pytest -k 'test_cfg[cs-test7]' --no-cov -vv
```

### Publishing

Make sure to bump the version in `setup.cfg`.

Then run the following commands:

```bash
rm -rf build dist
python setup.py sdist bdist_wheel
```

Then upload it to PyPI using [twine](https://twine.readthedocs.io/en/latest/#installation) (`pip install twine` if not installed):

```bash
twine upload dist/*
```


### About the IBM OSCP Project
This tool was developed for research purposes as a part of the OSCP Project. Efficient representation of source code is essential for various software engineering tasks using AI pipelines such as code translation, code search and code clone detection. Code Representation aims at extracting the both syntactic and semantic features of source code and representing them by a vector which can be readily used for the downstream tasks. Multiple works exist that attempt to encode the code as sequential data to easily leverage state of art NN models like transformers. But it leads to a loss of information. Graphs are a natural representation for the code but very few works(MVG-AAAI’22) have tried to represent the different code features obtained from different code views like Program Dependency Graph, Data Flow Graph etc. as a multi-view graph. In this work, we want to explore more code views and its relevance to different code tasks as well as leverage transformers model for the multi-code view graphs. We believe such a work will help to 
1. Establish influence of specific code views for common tasks 
2. Demonstrate how graphs can combined with transformers 
3. Create re-usable models

### Team

This tool is based on the ongoing joint research effort between IBM and [Risha Lab](https://rishalab.in/) at [IIT Tirupati](https://www.iittp.ac.in/) to explore the effects of different code representations on code based tasks involving: 
 - [Srikanth Tamilselvam](https://www.linkedin.com/in/srikanth-tamilselvam-913a2ab/)
 - [Sridhar Chimalakonda](https://www.linkedin.com/in/sridharch/)
 - [Alex Mathai](https://www.linkedin.com/in/alex-mathai-403117131/)
 - [Debeshee Das](https://www.linkedin.com/in/debeshee-das/) 
 - [Noble Saji Mathews](https://www.linkedin.com/in/noble-saji-mathews/) 
 - [Kranthi Sedamaki](https://www.linkedin.com/in/kranthisedamaki/) 
 - [Atul Kumar](https://www.linkedin.com/in/atul-kumar-0ba442/) 
