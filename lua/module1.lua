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

-- Coroutine-based producer. Yields successive Fibonacci numbers.
function M.fibProducer()
    return coroutine.create(function()
        local a, b = 0, 1
        while true do
            coroutine.yield(a)
            a, b = b, a + b
        end
    end)
end

-- Drives the coroutine N times and returns a list of values.
function M.fibTake(n)
    local co = M.fibProducer()
    local out = {}
    for i = 1, n do
        local ok, v = coroutine.resume(co)
        if not ok then break end
        out[#out + 1] = v
    end
    return out
end

return M