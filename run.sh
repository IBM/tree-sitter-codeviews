# Use this script to run various commands and test out the repo
# Each set of commands is preceeded by a comment that describes what it does. 
# Uncomment the command you wish to run and then run this script bash run.sh in your terminal in the root directory

export PYTHONPATH="$PYTHONPATH:$PWD"

# ----------------------------------------------------------------
# To run a set of miscellaneous test cases covering multiple codeviews
# Expected output is "JSON test Passed" on all the cases

# python3 testing/test_AST/AST_test.py
# python3 testing/test_DFG/test_script_DFG.py
# ----------------------------------------------------------------

# To generate CFG for all data points in the code clone detection dataset 
# python3 experiments/scripts/CFG_clone_test.py
# ----------------------------------------------------------------

# To generate various codeviews and save their outputs in dot format and/json format
# modify the config.json file before running the following
python3 example_files/main.py

# python3 masking_experiments/generate_context.py

# python3 masking_experiments/GCBMask.py
# python3 src/comex/masking_experiments/GCBMask.py
# python3 experiment/experiment_script.py