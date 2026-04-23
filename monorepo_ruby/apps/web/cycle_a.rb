# C1.a — Ruby's late binding makes cycles trivial at runtime.
require_relative "cycle_b"       # WILL require cycle_b.rb which will require us back

class CycleA
  def initialize(name); @name = name; end
  def describe; "CycleA(#{@name})"; end
  def spawn_bravo; CycleB.new("#{@name}/b"); end

  def self.kick_off
    a = new("root")
    a.spawn_bravo.bounce_to_alpha
  end
end
