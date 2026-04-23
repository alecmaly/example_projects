# Ruby cast / conversion catalogue.

# 1. Kernel conversion functions (strict).
def strict_conversions
  puts Integer("42")
  puts Float("3.14")
  puts String(123)
  puts Array([1,2,3])        # same array
  puts Hash([[:a, 1], [:b, 2]]).inspect
end

# 2. .to_X methods (lenient).
def lenient_conversions
  puts "42abc".to_i          # returns 42 — stops at first non-digit
  puts "hi".to_i             # returns 0
  puts 3.14.to_s
  puts [1, 2].to_a.inspect
  puts({a: 1}.to_h.inspect)
end

# 3. Runtime type test.
def type_tests(x)
  puts x.is_a?(String)       # most common
  puts x.kind_of?(Numeric)
  puts x.instance_of?(Integer)
  puts x.class
end

# 4. case/when uses === which is type-friendly for modules/classes.
def case_cast(x)
  case x
  when Integer then "int #{x}"
  when String  then "str len #{x.length}"
  when nil     then "nil"
  else              "other"
  end
end

# 5. Struct coercion via [].
def struct_cast
  Point = Struct.new(:x, :y) unless defined?(Point)
  p = Point.new(1, 2)
  puts "as array: #{p.to_a.inspect}"
  puts "as hash:  #{p.to_h.inspect}"
end

# 6. Coerce method protocol (used by Numeric).
class Dollar
  include Comparable
  attr_reader :cents
  def initialize(cents); @cents = cents; end
  def coerce(other); [Dollar.new((other * 100).to_i), self]; end
  def <=>(other); @cents <=> (other.is_a?(Dollar) ? other.cents : other * 100); end
  def to_s; "$#{'%.2f' % (@cents/100.0)}"; end
end

def run_casts_demo
  strict_conversions
  lenient_conversions
  type_tests("hi"); type_tests(42)
  puts case_cast(5); puts case_cast("hello"); puts case_cast(nil)
  struct_cast
  d = Dollar.new(1299)
  puts "#{d} > 10? #{d > 10}"    # triggers coerce
end
