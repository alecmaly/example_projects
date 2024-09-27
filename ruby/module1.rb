module Module1
  class Class1
    @@class_variable = "I'm a class variable"

    def initialize
      @instance_var = "I'm an instance variable"
    end

    def method1
      puts "This is method1 from Class1"
      private_method
    end

    def self.class_variable
      @@class_variable
    end

    private

    def private_method
      puts "This is a private method in Class1"
      puts "Instance var: #{@instance_var}"
      puts "Class var: #{@@class_variable}"
    end
  end
end