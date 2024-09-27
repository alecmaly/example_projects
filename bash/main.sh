#!/bin/bash

source ./module1.sh
source ./module2.sh

GLOBAL_VAR="I'm global in main"

main() {
    local LOCAL_VAR="I'm local to main"
    echo $GLOBAL_VAR
    echo $LOCAL_VAR
    echo "Imported constant: $MODULE2_CONSTANT"
    
    function1
    function2
    recursive_function 5
    
    # Accessing module-level variables
    echo "Module1 global: $MODULE1_GLOBAL"
    echo "Module2 global: $MODULE2_GLOBAL"
    
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