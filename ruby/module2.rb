module Module2
  MODULE2_CONSTANT = "I'm a constant in Module2"
  @module_variable = "I'm a module instance variable"

  def self.function1
    puts "This is function1 from Module2"
    puts "Accessing module constant: #{MODULE2_CONSTANT}"
    internal_function
  end

  def self.internal_function
    local_var = "I'm local to internal_function"
    puts "This is an internal function in Module2"
    puts "Local var: #{local_var}"
    puts "Module var: #{@module_variable}"
  end

  def self.module_variable
    @module_variable
  end
end