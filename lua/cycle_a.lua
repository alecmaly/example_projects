-- C1.a — Lua cycle via package.loaded caching.
-- When cycle_a requires cycle_b and cycle_b tries to require cycle_a,
-- Lua returns the partially-initialised module table of cycle_a.
-- The LSP has to handle that partial-load state gracefully.

local M = {}

function M.describe(a)    return "Alpha(" .. a.name .. ")" end
function M.spawn_bravo(a)
    local cycle_b = require("cycle_b")        -- lazy require inside fn
    return cycle_b.new(a.name .. "/b")
end
function M.kick_off()
    local a = { name = "root" }
    local b = M.spawn_bravo(a)
    local cycle_b = require("cycle_b")
    return cycle_b.bounce_to_alpha(b)
end

return M
