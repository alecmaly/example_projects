# Ruby feature coverage — ported from ruby/features.rb. Self-contained.

class String
  def shout_mono
    upcase + "!"
  end
end

class MonoCounter
  @count = 0
  class << self
    attr_accessor :count
    def bump; @count += 1; end
    def reset; @count = 0; end
  end
end

def mono_dispatch(symbol_name, *args, **kwargs)
  case symbol_name
  when :add    then args.sum
  when :concat then args.join(kwargs.fetch(:sep, " "))
  else              "unknown op"
  end
end

MonoPoint = Struct.new(:x, :y) do
  def magnitude; Math.sqrt(x * x + y * y); end
end

def mono_block_caller
  yield 10
end

def mono_wrap_proc(p)
  p.call(20)
end

def run_feature_demo_mono
  puts "shout: #{'hello'.shout_mono}"
  MonoCounter.reset
  3.times { MonoCounter.bump }
  puts "counter = #{MonoCounter.count}"
  puts mono_dispatch(:add, 1, 2, 3)
  puts mono_dispatch(:concat, "a", "b", "c", sep: "-")
  p = MonoPoint.new(3, 4)
  puts "magnitude = #{p.magnitude}"
  puts mono_block_caller { |n| n * 2 }
  puts mono_wrap_proc(->(n) { n + 5 })
  puts [1, 2, 3, 4].map(&:to_s).inspect
end
