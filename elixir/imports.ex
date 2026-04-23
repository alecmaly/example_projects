# Elixir's four module-reference forms.

defmodule Imports.HelperA do
  def a_func, do: :a
  defmacro shout(s), do: quote(do: IO.puts(unquote(s)))
end

defmodule Imports.HelperB do
  def b_func, do: :b
end

defmodule Imports do
  # 1. `alias` — rename a module short-form.
  alias Imports.HelperA, as: A
  # 2. `alias` multi-form.
  alias Imports.{HelperB}
  # 3. `import` — pull functions into local scope.
  import IO, only: [puts: 1]
  # 4. `require` — enable macros from another module.
  require Imports.HelperA
  # 5. `use` — runs __using__ macro (custom DSL hook).
  #    See features.ex `Features.StdOut` for a real `use` consumer.

  def run do
    puts("via import IO")                         # 3
    Imports.HelperA.shout("via require+macro")    # 4
    A.a_func()                                    # 1
    HelperB.b_func()                              # 2
  end
end
