local M = {}

M.MODULE2_CONSTANT = "I'm a constant in module2"
M.MODULE2_GLOBAL = "I'm global in module2"

-- Phase 1 addition: metatable-based "class" for OO/dispatch coverage.
local Circle = {}
Circle.__index = Circle
function Circle.new(r)
    return setmetatable({ r = r }, Circle)
end
function Circle:area() return 3.141592653589793 * self.r * self.r end
M.Circle = Circle

function M.set_global(v)
    M.MODULE2_GLOBAL = v -- cross-module WRITE target
end

function M.function2()
    print("This is function2 from module2")
    print("Accessing module constant: " .. M.MODULE2_CONSTANT)
    M.internalFunction()
end

function M.internalFunction()
    local internalVar = "I'm local to internalFunction"
    print("This is an internal function in module2")
    print("Internal var: " .. internalVar)
    print("Accessing global: " .. M.MODULE2_GLOBAL)
end

-- Demonstrate table and closure usage
M.counter = {
    value = 0,
    increment = function(self)
        self.value = self.value + 1
        return self.value
    end
}

-- Function literal assigned directly to a module field — exercises the
-- ``M.fn = function(...) end`` shape (distinct from the declarative
-- ``function M.fn(...) end`` form also used elsewhere in this fixture).
M.describe = function(x)
    return "circle r=" .. tostring(x)
end

return M