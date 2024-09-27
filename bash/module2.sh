MODULE2_CONSTANT="I'm a constant in module2"
MODULE2_GLOBAL="I'm global in module2"

function2() {
    echo "This is function2 from module2"
    echo "Accessing module constant: $MODULE2_CONSTANT"
    internal_function
}

internal_function() {
    local INTERNAL_VAR="I'm local to internal_function"
    echo "This is an internal function in module2"
    echo "Internal var: $INTERNAL_VAR"
    echo "Accessing global: $MODULE2_GLOBAL"
}