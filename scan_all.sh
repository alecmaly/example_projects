
# c# is broken (OmniSharp) 
language_folders=(asm bash c go java kotlin lua php powershell python ruby rust solidity typescript)
BASE_DIR="`pwd`/"

for language in "${language_folders[@]}"
do
    echo "Scanning $language"
    src_dir="$BASE_DIR$language"
    cd $src_dir

    # step 1: parse codebase
    # docker run --rm -it -p 5678:5678 -v "$(pwd)":/app/output -v "$src_dir":$src_dir alecmaly/sa-tool python3 /app/1_extract_w_lsp.py -d $src_dir -l $language -it 5
    
    # # step 2: build callstacks
    # docker run --rm -it -v $(pwd):/app/output sa-tool python3 /app/2_build_callstacks.py

    # Step 3: move files to .vscode for extension
    mkdir -p .vscode/ext-static-analysis/graphs
    mv ./functions_html.json ./.vscode/ext-static-analysis/functions_html.json
    mv ./callstacks.json ./.vscode/ext-static-analysis/callstacks.json
    mv ./scope_summaries_html.json ./.vscode/ext-static-analysis/scope_summaries_html.json
    mv ./inheritance_graph.json ./.vscode/ext-static-analysis/graphs/inheritance_graph.json
done
