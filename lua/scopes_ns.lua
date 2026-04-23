-- S10 middle hop (re-exports) + S14 stand-in (namespace-like table).
local reexport = require("scopes_reexport")

local M = {}

-- Re-exported value: reader in scopes.lua consumes `scopes_ns.re_exported_value`,
-- which resolves back to scopes_reexport's definition.
M.re_exported_value = reexport.value

-- S14 stand-in: Widget as a "nested namespace" table member.
M.Widget = {}                                   -- S14.Widget.def
M.Widget.__index = M.Widget
function M.Widget.new(label)
    return setmetatable({ label = label }, M.Widget)
end

return M
