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
    
    -- Accessing module-level variables (reads)
    print("Module1 global: " .. module1.MODULE1_GLOBAL)
    print("Module2 global: " .. module2.MODULE2_GLOBAL)

    -- Cross-module WRITES
    module2.MODULE2_GLOBAL = "rotated-from-main"
    module2.set_global("rotated-via-helper")
    print("Module2 global after: " .. module2.MODULE2_GLOBAL)

    -- Metatable-based "class" dispatch
    local c = module2.Circle.new(2.5)
    print("Circle area: " .. c:area())

    -- Error handling with pcall
    local ok, err = pcall(function() error("boom") end)
    print("pcall -> ok=" .. tostring(ok) .. " err=" .. tostring(err))

    -- Coroutines: first 8 Fibonacci numbers
    local fibs = module1.fibTake(8)
    print("fibs: " .. table.concat(fibs, ", "))

    -- Labeled scope test cases
    local scopes = require("scopes")
    scopes.run_scope_demo()
    
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

-- Coroutine: producer yields 3 values, consumer drains via resume.
local function producer()
    for i = 1, 3 do
        coroutine.yield(i * 10)
    end
end

local co = coroutine.create(producer)
while true do
    local ok, value = coroutine.resume(co)
    if not ok or value == nil then break end
    print("co value: " .. tostring(value))
end

-- coroutine.wrap variant: wrapped generator returns a callable.
local gen = coroutine.wrap(function()
    for i = 1, 3 do
        coroutine.yield(i)
    end
end)

for _ = 1, 3 do
    print("wrap value: " .. tostring(gen()))
end

-- pcall around a function that throws via error(...).
local function boomy()
    error("boomy-failed")
end

local ok_p, err_p = pcall(boomy)
print("pcall -> ok=" .. tostring(ok_p) .. " err=" .. tostring(err_p))

-- xpcall with a custom error handler that formats the error.
local function formatErr(e)
    return "[handled] " .. tostring(e)
end

local ok_x, err_x = xpcall(boomy, formatErr)
print("xpcall -> ok=" .. tostring(ok_x) .. " err=" .. tostring(err_x))