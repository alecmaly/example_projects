module MonoUtils
  TAG = "utils"

  def self.clamp(n, lo, hi)
    [[n, hi].min, lo].max
  end

  # Autoload — Ruby's deferred constant resolution. When Helper is first
  # referenced, Ruby loads mono_utils/helper.rb on demand.
  autoload :Helper, "mono_utils/helper"
end
