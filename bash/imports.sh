#!/bin/bash
# Bash has three shapes for pulling in external code:

# 1. `source path` — runs path in the current shell (shares vars/funcs).
source ./module1.sh

# 2. `. path` — identical to `source` (POSIX name).
. ./module2.sh

# 3. Env-path-relative via $PATH — rare; the invoked script runs in a subshell
#    and cannot mutate the parent. Shown here shape-only.
# path/to/helper.sh

# 4. `export` — promotes a variable to the environment so subprocesses see it.
export SHARED_EXPORT="from-imports"

imports_demo() {
    echo "MODULE1_GLOBAL=$MODULE1_GLOBAL"
    echo "MODULE2_GLOBAL=$MODULE2_GLOBAL"
    ( echo "subshell sees SHARED_EXPORT=$SHARED_EXPORT" )
}
