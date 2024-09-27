require_relative 'base_class'

class DerivedClass < BaseClass
  def initialize
    super
    @derived_var = "I'm a derived class variable"
  end

  def base_method
    super
    puts "This is an overridden method in DerivedClass"
  end

  def derived_method
    puts "This is a method from DerivedClass"
    puts "Derived var: #{@derived_var}"
    base_method
  end

  # Demonstrate Ruby's method_missing
  def method_missing(method_name, *args, &block)
    puts "You called a non-existent method: #{method_name}"
    puts "Arguments: #{args.join(', ')}"
  end

  # Demonstrate Ruby's respond_to_missing?
  def respond_to_missing?(method_name, include_private = false)
    method_name.to_s.start_with?('dynamic_') || super
  end
end