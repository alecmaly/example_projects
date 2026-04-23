-- Labeled scope test cases for Lua. See SCOPE_TEST_SPEC.md at repo root.
-- N/A for Lua: S09 (require returns values, no `import as`), S12 (metatable
-- emulation rather than real statics), S14 (tables, not namespaces).

local M = {}

local module2 = require("module2")              -- same-pattern cross-module access
local scopes_ns = require("scopes_ns")          -- S14 stand-in (table member)

-- S04 def / S05 write target. Using a module-local means it's "private" to
-- this file; _G.GlobalVar is the true "global" for cross-module scenarios.
M.MODULE_VAR = "mod-initial"                    -- S04.def

function M.s01_local()
    local local_a = "S01.local"                 -- S01.def
    print(local_a)                              -- S01.read
end

function M.s02_closure_read()
    local outer_a = "S02.outer"                 -- S02.outer.def
    local inner = function() print(outer_a) end -- S02.inner.read (upvalue)
    inner()
end

function M.s03_closure_write()
    local counter = 0                           -- S03.outer.def
    local bump = function() counter = counter + 1 end  -- S03.inner.write (upvalue)
    bump(); bump()
    return counter                              -- S03.outer.read
end

function M.s05_same_module_write()
    M.MODULE_VAR = "rotated"                    -- S05.write
    print(M.MODULE_VAR)                         -- S05.read
end

function M.s06_cross_read()
    return module2.MODULE2_GLOBAL               -- S06.read
end

function M.s07_cross_write()
    module2.set_global("S07")                   -- S07.write (indirect)
end

function M.s08_shadowing()
    local MODULE_VAR = "shadowed"               -- S08.shadow.def — local shadows M.MODULE_VAR
    print(MODULE_VAR)                           -- S08.shadow.read
end

-- S10 re-export stand-in: scopes_reexport defines a value, scopes_ns
-- re-exports it via its own module table. Reader goes through scopes_ns.
function M.s10_reexport()
    print(scopes_ns.re_exported_value)          -- S10.consumer.read
end

-- S11/S13 — metatable-based "class" inheritance.
local ScopeBase = {}
ScopeBase.__index = ScopeBase
function ScopeBase.new(x)
    return setmetatable({ x = x }, ScopeBase)   -- S11.instance.def (field x)
end
function ScopeBase:read_instance(x)
    return x + self.x                           -- S11.param.read + S11.instance.read
end

local ScopeDerived = setmetatable({}, { __index = ScopeBase })
ScopeDerived.__index = ScopeDerived
function ScopeDerived.new()
    return setmetatable({ x = 7 }, ScopeDerived)
end
function ScopeDerived:read_inherited()
    return self:read_instance(100)              -- S13.derived.read — routes to ScopeBase
end

function M.run_scope_demo()
    M.s01_local()
    M.s02_closure_read()
    print(M.s03_closure_write())
    M.s05_same_module_write()
    print(M.s06_cross_read())
    M.s07_cross_write()
    M.s08_shadowing()
    M.s10_reexport()
    print(ScopeBase.new(42):read_instance(100))
    print(ScopeDerived.new():read_inherited())
end

return M
