# C1.b — the `require_relative "cycle_a"` here would deadlock if loaded
# first, but Ruby's require caching makes the cycle safe as long as the
# CycleA constant is referenced LAZILY inside the method body.

class CycleB
  def initialize(tag); @tag = tag; end
  def bounce_to_alpha
    require_relative "cycle_a"     # lazy — avoids top-level cycle deadlock
    CycleA.new("bounce-from-#{@tag}").describe
  end
end
