defmodule Greeter do
  @greeting "hi"
  def greet(name), do: "#{@greeting} #{name}"
  defp internal(n), do: n * 2
end
defmodule Main do
  def run do
    Greeter.greet("world")
  end
end
