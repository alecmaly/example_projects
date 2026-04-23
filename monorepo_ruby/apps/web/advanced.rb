# Ruby advanced-feature coverage ported from the flat ruby/. Covers:
# Fiber, method_missing + respond_to_missing?, define_method,
# include mixin, class variable (@@var), module as mixin.

# --- module as mixin (include inside a class).
module Greeter
  def greet
    "hello, #{name}"
  end
end

# --- class variable @@var + include mixin + define_method.
class AnimalAdv
  @@population = 0                             # class variable
  include Greeter

  attr_reader :name

  def initialize(name)
    @name = name
    @@population += 1
  end

  def self.population
    @@population
  end

  # define_method — dynamic method definition.
  define_method(:describe) do
    "#{@name} exists"
  end

  # Deferred dynamic method generation — class-level define_method.
  def self.define_greeting(style)
    define_method(:"greet_#{style}") do
      "#{style.to_s.upcase}: hello, #{@name}"
    end
  end
end

AnimalAdv.define_greeting(:shout)
AnimalAdv.define_greeting(:whisper)

# --- inheritance using super + method_missing + respond_to_missing?
class DogAdv < AnimalAdv
  def initialize(name, breed)
    super(name)                                # super call
    @breed = breed
  end

  def speak
    "#{@name} (woof, #{@breed})"
  end

  # method_missing — metaprogramming fallback.
  def method_missing(name, *args, &block)
    if name.to_s.start_with?("dynamic_")
      "dynamic method #{name} called with #{args.inspect}"
    else
      super
    end
  end

  def respond_to_missing?(name, include_private = false)
    name.to_s.start_with?("dynamic_") || super
  end
end

# --- prepend — inserts a module BEFORE the class in the MRO,
# so the module's method wraps the class's via super.
module AuditPrepend
  def speak
    "[audited] #{super}"
  end
end

class AuditedDog < DogAdv
  prepend AuditPrepend
end

# --- Fiber — lightweight concurrency.
def fibonacci_fiber
  Fiber.new do
    a, b = 0, 1
    loop do
      Fiber.yield a
      a, b = b, a + b
    end
  end
end

def run_advanced_demo_mono
  a = AnimalAdv.new("Kira")
  puts a.greet                                 # via mixin
  puts a.describe                              # via define_method
  puts a.greet_shout                           # via class-level define_greeting
  puts a.greet_whisper

  d = DogAdv.new("Rex", "collie")
  puts d.speak
  puts d.greet                                 # still from mixin via inheritance
  puts d.dynamic_hello("x", "y")               # method_missing
  puts d.respond_to?(:dynamic_anything)        # respond_to_missing?

  puts "population=#{AnimalAdv.population}"    # @@class var

  ad = AuditedDog.new("Rex", "collie")
  puts ad.speak                                # prepended audit wrapper

  fib = fibonacci_fiber
  10.times { print "#{fib.resume} " }
  puts
end

# --- case/in pattern matching (Ruby 3+): hash, array, class/deconstruct.
Point = Struct.new(:x, :y) do
  def deconstruct_keys(keys)
    { x: x, y: y }
  end
end

def describe_shape(value)
  case value
  in {name: String => n, age: Integer => a}
    "#{n} is #{a}"
  in [Integer, *rest]
    "int-head rest=#{rest.inspect}"
  in Point(x: 0, y: 0)
    "origin point"
  else
    "unknown"
  end
end

# --- &:symbol shorthand — Symbol#to_proc style.
def shout_all(words)
  words.map(&:upcase)
end

# --- numbered block parameters (_1, _2 ...).
def double_each(nums)
  nums.each { puts _1 * 2 }
end

# --- refinement module — scoped method extension of a core class.
module StringRefine
  refine String do
    def shout
      self.upcase + "!"
    end
  end
end

class RefineUser
  using StringRefine

  def yell
    "x".shout
  end
end
