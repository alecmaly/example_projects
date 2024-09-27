local M = {}

M.MODULE1_GLOBAL = "I'm global in module1"

function M.function1()
    local localVar = "I'm local to function1"
    print("This is function1 from module1")
    print("Local var in function1: " .. localVar)
    print("Accessing global: " .. M.MODULE1_GLOBAL)
end

-- Demonstrate nested functions
function M.outerFunction()
    local outerVar = "I'm in the outer function"
    
    local function innerFunction()
        local innerVar = "I'm in the inner function"
        print("Inner accessing outer: " .. outerVar)
        print("Inner local: " .. innerVar)
    end
    
    innerFunction()
    print("Outer local: " .. outerVar)
end

return M