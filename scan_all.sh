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

# This driver runs the predecessor LSP-based extractor in the
# ``alecmaly/sa-tool`` Docker image. The current production pipeline
# uses tree-sitter — see ``alecmaly/source-mapper`` (built from the
# alecmaly/static-analysis-tooling repo) and run with
# ``docker run --rm -v "$PWD:$PWD" alecmaly/source-mapper scan "$PWD"``.
# This script is kept for users who still want LSP-pipeline output
# against these fixtures, or for diff'ing the two extractors.

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

    # step 1: parse codebase. The unified ``scan`` entrypoint
    # auto-detects input shape and runs the right extract +
    # postprocess pipeline. ``_process_static_analysis.sh`` (called
    # by scan) handles the cache → top-level file copies the
    # legacy two-step (``1_extract_w_lsp.py`` + ``2_build_callstacks.py``)
    # used to do manually here.
    docker run --rm -it -v "$src_dir":"$src_dir" alecmaly/source-mapper scan "$src_dir"


    src_dir=`pwd` && docker run --rm -it -v ~/.semgrep:/root/.semgrep -v $(pwd):/app/output -v "$src_dir":"$src_dir" alecmaly/source-mapper semgrep scan --exclude sg-rules --no-git-ignore --json --config /app/sg-rules --config auto --json-output=semgrep.json "$src_dir"
    src_dir=`pwd` && docker run --rm -it -v $(pwd):/app/output -v "$src_dir":"$src_dir" alecmaly/source-mapper python3 /app/postprocess/detectors_to_results.py -s semgrep -b "$src_dir" -c "semgrep"


    ## Grep to Detectors:
            # Example: adding if and loops to detectors
    src_dir=`pwd` && docker run --rm -it -v $(pwd):/app/output -v "$src_dir":"$src_dir" alecmaly/source-mapper sh -c "cd \"$src_dir\" && grep -rnEI --exclude-dir={.vscode,.git,node_modules,.json,target} '\bif\b' . | awk -F: '{print \$1\":\"\$2\":\"index(\$0,\$4)\":\"substr(\$0,index(\$0,\$3))}'" > grep-output.txt
    src_dir=`pwd` && docker run --rm -it -v $(pwd):/app/output -v "$src_dir":"$src_dir" alecmaly/source-mapper python3 /app/postprocess/detectors_to_results.py -s grep -b "$src_dir" -c "grep-if statements" -a

    src_dir=`pwd` && docker run --rm -it -v $(pwd):/app/output -v "$src_dir":"$src_dir" alecmaly/source-mapper sh -c "cd \"$src_dir\" && grep -rnEI --exclude-dir={.vscode,.git,node_modules,.json,target} '\b(while|for|until|do)\b' . | awk -F: '{print \$1\":\"\$2\":\"index(\$0,\$4)\":\"substr(\$0,index(\$0,\$3))}'" > grep-output.txt
    src_dir=`pwd` && docker run --rm -it -v $(pwd):/app/output -v "$src_dir":"$src_dir" alecmaly/source-mapper python3 /app/postprocess/detectors_to_results.py -s grep -b "$src_dir" -c "grep-loops" -a

    # rust's was very large
    rm grep-output.txt

    code .
done

cd $BASE_DIR
# docker image currently runs as root, may need to change ownership of files to user or possibly set `chmod 777 {}` if vs code extensions do not have permission to read files
# sudo find . -exec chown $USER:$USER {} \;