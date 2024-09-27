MODULE1_GLOBAL="I'm global in module1"

function1() {
    local LOCAL_VAR="I'm local to function1"
    echo "This is function1 from module1"
    echo "Local var in function1: $LOCAL_VAR"
    echo "Accessing global: $MODULE1_GLOBAL"
}

# Demonstrate nested functions
outer_function() {
    local OUTER_VAR="I'm in the outer function"
    
    inner_function() {
        local INNER_VAR="I'm in the inner function"
        echo "Inner accessing outer: $OUTER_VAR"
        echo "Inner local: $INNER_VAR"
    }
    
    inner_function
    echo "Outer local: $OUTER_VAR"
}