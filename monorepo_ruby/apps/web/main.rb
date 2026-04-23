require "bundler/setup"     # loads Gemfile path-deps
require "mono_shared"       # resolved via Bundler path
require "mono_utils"

include MonoShared           # bring the module's constants into global scope

user = User.new(1, "alice")
role = MonoShared::DEFAULT_ROLE
puts Util.format_user(user)
puts Util.hello("world")
puts "tag=#{MonoUtils::TAG} clamped=#{MonoUtils.clamp(42, 0, 10)}"

# autoload trigger
puts MonoUtils::Helper.greet

# Ported coverage from the flat ruby/ fixture.
require_relative "features"
require_relative "scopes"
require_relative "imports"
require_relative "advanced"
require_relative "casts"
require_relative "chain_deep"
run_feature_demo_mono
run_scope_demo_mono
imports_demo_mono
run_advanced_demo_mono
run_casts_demo

# T1 transitive chain — LSP must trace ChainDeep::VALUE_ALIAS back
# through ChainMiddle::MIDDLE_VALUE to ChainOrigin::ORIGIN_VALUE.
puts "transitive: #{ChainDeep::VALUE_ALIAS}"

# Cycle: CycleA ↔ CycleB via deferred require_relative.
require_relative "cycle_a"
puts "cycle: #{CycleA.kick_off}"
