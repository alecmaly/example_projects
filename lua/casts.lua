-- Lua cast / coercion catalogue.

local M = {}

-- 1. tostring / tonumber — stdlib conversions.
function M.converters()
    local s = tostring(42)
    local n = tonumber("3.14")
    local i = math.tointeger("10")     -- Lua 5.3+ integer-typed number
    return s, n, i
end

-- 2. type() — runtime type inspection.
function M.type_check(x)
    return type(x)    -- "string" / "number" / "table" / "boolean" / "function" / "nil" / "thread" / "userdata"
end

-- 3. Integer/float distinction (Lua 5.3+).
function M.int_float()
    local f = 3.0
    local i = math.floor(f)
    return f, i, math.type(f), math.type(i)   -- "float", "integer"
end

-- 4. String ↔ byte table.
function M.string_bytes()
    local s = "hi"
    local b1, b2 = string.byte(s, 1, 2)
    local back = string.char(b1, b2)
    return {b1, b2}, back
end

-- 5. Implicit string <-> number coercion in arithmetic.
function M.implicit_coercion()
    local n = "10" + 5       -- string coerced to number → 15
    local s = "count=" .. 42 -- number coerced to string
    return n, s
end

-- 6. setmetatable-based "cast" — attach a class-like metatable.
function M.as_class(t)
    local Class = { describe = function(self) return "described" end }
    Class.__index = Class
    return setmetatable(t, Class)
end

function M.run()
    local s, n, i = M.converters()
    print(s, n, i)
    print(M.type_check("foo"))
    print(M.int_float())
    local b, back = M.string_bytes()
    print(b[1], b[2], back)
    print(M.implicit_coercion())
    print(M.as_class({x = 1}):describe())
end

return M
