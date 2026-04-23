# Labeled scope test cases for Ruby — monorepo edition.
# Cross-module refs target mono_shared (workspace gem) and
# MonoShared::ScopesNs::Widget.

require "mono_shared"
require "mono_shared/scopes_ns"
require_relative "scopes_reexport"

$MONO_MODULE_VAR = "mod-initial"                  # S04.def

def mono_s01_local
  local_a = "S01.local"                           # S01.def
  puts local_a                                    # S01.read
end

def mono_s02_closure_read
  outer_a = "S02.outer"                           # S02.outer.def
  inner = -> { puts outer_a }                     # S02.inner.read
  inner.call
end

def mono_s03_closure_write
  counter = 0                                     # S03.outer.def
  bump = -> { counter += 1 }                      # S03.inner.write
  bump.call; bump.call
  counter                                         # S03.outer.read
end

def mono_s05_same_module_write
  $MONO_MODULE_VAR = "rotated"                    # S05.write
  puts $MONO_MODULE_VAR                           # S05.read
end

def mono_s06_cross_read
  MonoShared::DEFAULT_ROLE                        # S06.read
end

def mono_s07_cross_write
  MonoShared.const_set(:DEFAULT_ROLE, :new_value) # S07.write
end

def mono_s08_shadowing
  mono_module_var = "shadowed"                    # S08.shadow.def
  puts mono_module_var                            # S08.shadow.read
end

def mono_s10_reexport
  puts RE_EXPORTED_VALUE                          # S10.consumer.read
end

class MonoScopeBase
  @@class_var = 1                                 # S12.static.def
  attr_reader :x                                  # S11.instance.def via @x
  def initialize(x); @x = x; end
  def read_instance(x); [x, @x]; end              # S11.param.read + S11.instance.read
  def self.class_var; @@class_var; end
end

class MonoScopeDerived < MonoScopeBase
  def read_inherited
    self.class.class_var                          # S13.derived.read
  end
end

def mono_s14_qualified
  MonoShared::ScopesNs::Widget.new("hi").label    # S14.read
end

def run_scope_demo_mono
  mono_s01_local
  mono_s02_closure_read
  puts mono_s03_closure_write
  mono_s05_same_module_write
  puts mono_s06_cross_read
  mono_s07_cross_write rescue nil
  mono_s08_shadowing
  mono_s10_reexport
  puts MonoScopeBase.new(42).read_instance(100).inspect
  puts MonoScopeDerived.new(1).read_inherited
  puts mono_s14_qualified
end
