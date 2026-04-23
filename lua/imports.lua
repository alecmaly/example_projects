-- 1. Plain require, returning the module's value (usually a table).
local m1 = require("module1")

-- 2. Require with aliased local binding.
local m2table = require("module2")
local MOD2 = m2table   -- rename for clarity

-- 3. Require a submodule via dotted path (package.path).
-- local deep = require("pkg.sub.helper")   -- shape-only

-- 4. Direct access to `package.loaded` (Lua's module cache).
local alreadyLoaded = package.loaded["module1"]

-- 5. dofile / loadfile — direct file execution, bypassing package cache.
-- dofile("module1.lua")       -- shape-only; would re-execute

-- 6. _G access — the global environment table.
_G.EXPORTED_GLOBAL = "from-imports"

local M = {}

function M.demo()
    print(m1.MODULE1_GLOBAL, MOD2.MODULE2_CONSTANT)
    if alreadyLoaded then print("was cached") end
    print("global reachable:", _G.EXPORTED_GLOBAL)
end

return M
