# 1. require — searches $LOAD_PATH and bundler-resolved gems
require "json"

# 2. require_relative — path relative to this file
require_relative "scopes_reexport"

# 3. load — re-executes the file every time (shape-only).
# load "scopes_reexport.rb"

# 4. autoload — deferred constant resolution.
autoload :CSV, "csv"

# 5. Bundler setup + workspace gem
require "bundler/setup"
require "mono_shared"
require "mono_utils"

def imports_demo_mono
  puts JSON.parse("[1,2]").length
  puts RE_EXPORTED_VALUE
  puts MonoShared::Util.format_user(MonoShared::User.new(1, "alice"))
  puts MonoUtils::TAG
  puts MonoUtils.clamp(42, 0, 10)
  puts CSV.new("").class.name       # autoload trigger
end
