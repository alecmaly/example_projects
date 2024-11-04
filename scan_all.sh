# clean up .json files to ensure we are not using old data
find . -name "*.json" -type f ! -name launch.json ! -name tsconfig.json -delete

# c# is broken (OmniSharp) 
language_folders=(asm bash c go java kotlin lua php powershell python ruby rust solidity typescript)
BASE_DIR="`pwd`/"

for language in "${language_folders[@]}"
do
    echo "Scanning $language"
    src_dir="$BASE_DIR$language"
    cd $src_dir

    # step 1: parse codebase
    docker run --rm -it -p 5678:5678 -v "$(pwd)":/app/output -v "$src_dir":$src_dir alecmaly/sa-tool python3 /app/1_extract_w_lsp.py -d $src_dir -l $language 
    

    docker run --rm -it -v $(pwd):/app/output alecmaly/sa-tool python3 /app/2_build_callstacks.py

    # Step 3: move files to .vscode for extension
    mkdir -p .vscode/ext-static-analysis/graphs
    mv ./functions_html.json ./.vscode/ext-static-analysis/functions_html.json
    mv ./callstacks.json ./.vscode/ext-static-analysis/callstacks.json
    mv ./scope_summaries_html.json ./.vscode/ext-static-analysis/scope_summaries_html.json
    mv ./inheritance_graph.json ./.vscode/ext-static-analysis/graphs/inheritance_graph.json


    src_dir=`pwd` && docker run --rm -it -v $(pwd):/app/output -v "$src_dir":"$src_dir" alecmaly/sa-tool semgrep scan --exclude sg-rules --json --config auto --json-output=semgrep.json # --config ../sg-rules  # removing custom rules to increase speed
    src_dir=`pwd` && docker run --rm -it -v $(pwd):/app/output -v "$src_dir":"$src_dir" alecmaly/sa-tool python3 /app/semgrep-to-detector-results.py -b "$src_dir" 

    # rust's was very large
    rm grep-output.txt

    ## Grep to Detectors:
            # Example: adding if and loops to detectors
    grep -rnEI --exclude-dir={.vscode,.git,node_modules,.json} "\bif\b" . | awk -F: '{print $1 ":" $2 ":" index($0, $4) ":" substr($0, index($0, $3))}' > grep-output.txt
    src_dir=`pwd` && docker run --rm -it -v $(pwd):/app/output -v "$src_dir":"$src_dir" alecmaly/sa-tool python3 /app/grep-to-detector-results.py -b "$src_dir" -c "grep-if statements" -a

    grep -rnEI --exclude-dir={.vscode,.git,node_modules,.json} "\b(while|for|until|do)\b" . | awk -F: '{print $1 ":" $2 ":" index($0, $4) ":" substr($0, index($0, $3))}' > grep-output.txt
    src_dir=`pwd` && docker run --rm -it -v $(pwd):/app/output -v "$src_dir":"$src_dir" alecmaly/sa-tool python3 /app/grep-to-detector-results.py -b "$src_dir" -c "grep-loops" -a

    # code .
done

# docker image currently runs as root, may need to change ownership of files to user or possibly set `chmod 777 {}` if vs code extensions do not have permission to read files
# sudo find . -exec chown $USER:$USER {} \;