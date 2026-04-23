# clean up .json files to ensure we are not using old data
find . -name "*.json" -type f ! -name launch.json ! -name tsconfig.json ! -path "*/_solidity-chainlink/*" ! -path "*/_vulnserver/*"  -delete

language_folders=( \
    # Languages with no monorepo analogue — flat fixtures retained.
    asm bash c lua powershell \
    # Additional single-dir language fixtures expanded from bare-bones to
    # cover features / imports / scopes (no monorepo tooling needed at this
    # fidelity level).
    cpp elixir groovy haskell ocaml scala swift zig \
    # Rust LSP-stress fixture (distinct from monorepo_rust — exercises the
    # LSP boot/ref-map path with a minimal single-crate shape).
    rust_lsp \
    # Web framework coverage (React TSX, Vue SFC, Angular component, vanilla JS).
    web \
    # Cross-dir / decompiler / no-build-file fixtures — retained.
    csharp_multi_dll c_multi_dir _ilspy_dump _jadx_dump \
    # Monorepo fixtures (replaced the former flat per-language dirs in the
    # consolidation pass — see VERIFICATION.md for the parity audit).
    monorepo_typescript monorepo_rust monorepo_python monorepo_go \
    monorepo_java monorepo_csharp monorepo_php monorepo_solidity \
    monorepo_kotlin monorepo_ruby \
)
BASE_DIR="`pwd`/"

# If sa-tool/ is present next to this script, mount its contents over the
# image's /app/*.py so patches to the extractor apply without rebuilding the
# 27 GB Docker image. This is the Phase 2/4/5 override mechanism described
# in EXTRACTOR_CHANGES_APPLIED.md. Unset SA_TOOL_OVERRIDE=0 to disable.
SA_TOOL_OVERRIDE="${SA_TOOL_OVERRIDE:-1}"
OVERRIDE_MOUNTS=""
if [ "$SA_TOOL_OVERRIDE" = "1" ] && [ -f "${BASE_DIR}sa-tool/1_extract_w_lsp.py" ]; then
    for f in 1_extract_w_lsp.py 0_detect_project_roots.py 2_build_callstacks.py; do
        if [ -f "${BASE_DIR}sa-tool/$f" ]; then
            OVERRIDE_MOUNTS="$OVERRIDE_MOUNTS -v ${BASE_DIR}sa-tool/$f:/app/$f:ro"
        fi
    done
    if [ -d "${BASE_DIR}sa-tool/modules" ]; then
        OVERRIDE_MOUNTS="$OVERRIDE_MOUNTS -v ${BASE_DIR}sa-tool/modules:/app/modules:ro"
    fi
    echo "sa-tool override active: $OVERRIDE_MOUNTS"
fi

for language in "${language_folders[@]}"
do
    echo "Scanning $language"
    src_dir="$BASE_DIR$language"
    cd $src_dir

    # translate folder name -> language identifier the extractor expects
    case "$language" in
        csharp_multi_dll|_ilspy_dump|monorepo_csharp) language="c#" ;;
        _jadx_dump|monorepo_java)                     language="java" ;;
        c_multi_dir|cpp)                              language="c" ;;   # clangd handles both .c and .cpp
        rust_lsp|monorepo_rust)                       language="rust" ;;
        web|monorepo_typescript)                      language="typescript" ;;
        monorepo_python)                              language="python" ;;
        monorepo_go)                                  language="go" ;;
        monorepo_php)                                 language="php" ;;
        monorepo_solidity)                            language="solidity" ;;
        monorepo_kotlin)                              language="kotlin" ;;
        monorepo_ruby)                                language="ruby" ;;
        # elixir / groovy / haskell / ocaml / scala / swift / zig / asm /
        # bash / lua / powershell use their folder name as-is.
    esac

    # step 1: parse codebase
    docker run --rm -it -v "$(pwd)":/app/output -v "$src_dir":$src_dir $OVERRIDE_MOUNTS alecmaly/sa-tool python3 /app/1_extract_w_lsp.py -d $src_dir -l $language

    docker run --rm -it -v $(pwd):/app/output $OVERRIDE_MOUNTS alecmaly/sa-tool python3 /app/2_build_callstacks.py

    # Step 3: move files to .vscode for extension
    mkdir -p .vscode/ext-static-analysis/graphs
    mv ./.vscode/ext-static-analysis/cache/functions_html.json ./.vscode/ext-static-analysis/functions_html.json
    mv ./.vscode/ext-static-analysis/cache/decorations.json ./.vscode/ext-static-analysis/decorations.json
    mv ./.vscode/ext-static-analysis/cache/callstacks.json ./.vscode/ext-static-analysis/callstacks.json
    mv ./.vscode/ext-static-analysis/cache/scope_summaries_html.json ./.vscode/ext-static-analysis/scope_summaries_html.json
    mv ./.vscode/ext-static-analysis/cache/inheritance_graph.json ./.vscode/ext-static-analysis/graphs/inheritance_graph.json


    src_dir=`pwd` && docker run --rm -it -v $(pwd):/app/output -v "$src_dir":"$src_dir" alecmaly/sa-tool semgrep scan --exclude sg-rules --json --config auto --json-output=semgrep.json # --config ../sg-rules  # removing custom rules to increase speed
    src_dir=`pwd` && docker run --rm -it -v $(pwd):/app/output -v "$src_dir":"$src_dir" alecmaly/sa-tool python3 /app/semgrep-to-detector-results.py -b "$src_dir" 


    ## Grep to Detectors:
            # Example: adding if and loops to detectors
    grep -rnEI --exclude-dir={.vscode,.git,node_modules,.json,target} "\bif\b" . | awk -F: '{print $1 ":" $2 ":" index($0, $4) ":" substr($0, index($0, $3))}' > grep-output.txt
    src_dir=`pwd` && docker run --rm -it -v $(pwd):/app/output -v "$src_dir":"$src_dir" alecmaly/sa-tool python3 /app/grep-to-detector-results.py -b "$src_dir" -c "grep-if statements" -a

    grep -rnEI --exclude-dir={.vscode,.git,node_modules,.json,target} "\b(while|for|until|do)\b" . | awk -F: '{print $1 ":" $2 ":" index($0, $4) ":" substr($0, index($0, $3))}' > grep-output.txt
    src_dir=`pwd` && docker run --rm -it -v $(pwd):/app/output -v "$src_dir":"$src_dir" alecmaly/sa-tool python3 /app/grep-to-detector-results.py -b "$src_dir" -c "grep-loops" -a

    # rust's was very large
    rm grep-output.txt

    code .
done

cd $BASE_DIR
# docker image currently runs as root, may need to change ownership of files to user or possibly set `chmod 777 {}` if vs code extensions do not have permission to read files
# sudo find . -exec chown $USER:$USER {} \;