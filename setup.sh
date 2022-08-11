# This setup script installs are rdependencies

# Part 1: Clones the required repositories that contain the grammars of the source languages.
# These grammar repositories are required for tree-sitter to work
# --------------------------------------------------------------------------------------------
printf "Running setup script...\n"
rmdir vendor
mkdir vendor
cd vendor
pwd
git clone https://github.com/tree-sitter/tree-sitter-java.git
git clone https://github.com/tree-sitter/tree-sitter-python.git


# Uncomment the following lines according to the source languages you want to work with using tree-sitter
# Currently this repository supports only Java source code
git clone https://github.com/tree-sitter/tree-sitter-c-sharp.git
git clone https://github.com/tree-sitter/tree-sitter-go.git
git clone https://github.com/tree-sitter/tree-sitter-javascript.git
git clone https://github.com/tree-sitter/tree-sitter-php.git
git clone https://github.com/tree-sitter/tree-sitter-ruby.git

cd ..

# Part 2: Install dependencies from requirements.txt
pip install -r requirements.txt

