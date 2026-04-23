defmodule Chain.Origin do
  @origin_value "T1.origin"                              # T1.origin.def
  def value, do: @origin_value
end

defmodule Chain.Middle do
  # Re-export — Elixir has no symbol re-export; we delegate.
  defdelegate value, to: Chain.Origin                    # T1.middle.reexport
end

defmodule Chain.Deep do
  defdelegate value_alias, to: Chain.Middle, as: :value  # T1.deep.reexport
end

defmodule Chain do
  def run do
    IO.puts("transitive: #{Chain.Deep.value_alias()}")
  end
end
