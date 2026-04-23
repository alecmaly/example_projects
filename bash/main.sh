#!/bin/bash

source ./module1.sh
source ./module2.sh
source ./features.sh
source ./scopes.sh

GLOBAL_VAR="I'm global in main"

# Phase 1: error handling constructs
set -u
trap 'echo "caught signal, cleaning up"' EXIT

# Higher-order-ish function: takes a command name and invokes it.
invoke() { "$1"; }

main() {
    local LOCAL_VAR="I'm local to main"
    echo $GLOBAL_VAR
    echo $LOCAL_VAR
    echo "Imported constant: $MODULE2_CONSTANT"
    
    function1
    function2
    recursive_function 5
    
    # Accessing module-level variables (reads)
    echo "Module1 global: $MODULE1_GLOBAL"
    echo "Module2 global: $MODULE2_GLOBAL"

    # Cross-module WRITE + helper invocation
    MODULE2_GLOBAL="rotated-from-main"
    set_module1_global "rotated-via-helper"
    echo "Module1 global after: $MODULE1_GLOBAL"
    echo "Module2 global after: $MODULE2_GLOBAL"
    invoke function1

    # Arrays, associative arrays, heredoc, process substitution
    run_feature_demo

    # Labeled scope test cases
    run_scope_demo_bash
    
    # Using a standard command
    current_date=$(date +"%Y-%m-%d")
    echo "Current date: $current_date"
}

recursive_function() {
    if [ $1 -le 0 ]; then
        return
    fi
    echo "Recursion level: $1"
    recursive_function $(($1 - 1))
}

main