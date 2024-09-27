local M = {}

M.MODULE2_CONSTANT = "I'm a constant in module2"
M.MODULE2_GLOBAL = "I'm global in module2"

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

return M