require_relative 'base_class'
require_relative 'derived_class'
require_relative 'module2'

$global_var = "I'm global in main"

def main
  local_var = "I'm local to main"
  puts $global_var
  puts local_var
  puts "Imported constant: #{Module2::MODULE2_CONSTANT}"

  base_obj = BaseClass.new
  derived_obj = DerivedClass.new

  base_obj.base_method
  derived_obj.base_method
  derived_obj.derived_method

  Module2.function1
  recursive_function(5)

  # Accessing class-level variables
  puts "BaseClass class var: #{BaseClass.class_variable}"
  puts "Module2 var: #{Module2.module_variable}"

  # Demonstrate blocks and procs
  multiplier = Proc.new { |x| x * 2 }
  puts "Result of multiplier: #{multiplier.call(5)}"

  # Demonstrate exception handling
  begin
    result = 10 / 0
  rescue ZeroDivisionError => e
    puts "Caught exception: #{e.message}"
  end

  # Demonstrate metaprogramming
  BaseClass.define_method(:dynamic_method) do
    puts "This method was dynamically defined"
  end
  base_obj.dynamic_method

  # Demonstrate fiber
  fib = Fiber.new do
    a, b = 0, 1
    loop do
      Fiber.yield a
      a, b = b, a + b
    end
  end

  10.times { puts "Fibonacci number: #{fib.resume}" }
end

def recursive_function(n)
  return if n <= 0
  puts "Recursion level: #{n}"
  recursive_function(n - 1)
end

main