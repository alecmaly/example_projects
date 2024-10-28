local module1 = require("module1")
local module2 = require("module2")
local os = require("os")  -- Added standard library import


GlobalVar = "I'm global in main"

local function main()
    local localVar = "I'm local to main"
    print(GlobalVar)
    print(localVar)
    print("Imported constant: " .. module2.MODULE2_CONSTANT)
    
    module1.function1()
    module2.function2()
    recursiveFunction(5)
    
    -- Accessing module-level variables
    print("Module1 global: " .. module1.MODULE1_GLOBAL)
    print("Module2 global: " .. module2.MODULE2_GLOBAL)
    
    -- Using a standard library function
    local current_time = os.time()
    print("Current timestamp: " .. current_time)
end

function recursiveFunction(n)
    if n <= 0 then
        return
    end
    print("Recursion level: " .. n)
    recursiveFunction(n - 1)
end

main()