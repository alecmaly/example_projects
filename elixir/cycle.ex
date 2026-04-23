# Elixir handles cross-module cycles at runtime via protocol/behaviour
# indirection — direct compile-time cycles between two modules would be
# detected. The idiomatic workaround is a shared behaviour:

defmodule CycleBehaviour do
  @callback describe() :: String.t()
end

defmodule CycleA do
  @behaviour CycleBehaviour
  def describe, do: "CycleA"
  def bounce, do: CycleB.describe()       # cross-ref through the behaviour
end

defmodule CycleB do
  @behaviour CycleBehaviour
  def describe, do: "CycleB"
  def bounce, do: CycleA.describe()       # cross-ref back
end

defmodule CycleDemo do
  def run do
    IO.puts("cycle A→B: #{CycleA.bounce()}")
    IO.puts("cycle B→A: #{CycleB.bounce()}")
  end
end
