local M = {}

function M.new(tag)                 return { tag = tag } end
function M.bounce_to_alpha(b)
    local cycle_a = require("cycle_a")         -- closes the cycle
    return cycle_a.describe({ name = "bounce-from-" .. b.tag })
end

return M
