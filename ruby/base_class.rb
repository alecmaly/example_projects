class BaseClass
  @@class_variable = "I'm a class variable in BaseClass"

  def initialize
    @base_var = "I'm a base class variable"
  end

  def base_method
    puts "This is a method from BaseClass"
    puts "Base var: #{@base_var}"
  end

  def self.class_variable
    @@class_variable
  end

  # Demonstrate metaprogramming
  def self.define_dynamic_method(method_name)
    define_method(method_name) do
      puts "This is a dynamically defined method: #{method_name}"
    end
  end
end