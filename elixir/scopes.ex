# Elixir scope test cases. See SCOPE_TEST_SPEC.md.
# N/A: S02/S03 closures are expressions, not captured local writes the
# way mutable-language closures work; immutable + process state model.
# S10 (re-export) — Elixir doesn't have a native re-export syntax.

defmodule Scopes.Reexport do
  @value "S10.origin"                             # S10.origin.def (passes through Scopes)
  def value, do: @value
end

defmodule Scopes.Ns do
  defmodule Widget do                             # S14.Widget.def
    defstruct [:label]
    def new(label), do: %__MODULE__{label: label}
  end
end

defmodule Scopes do
  # --- S04.def — module attribute acts as "module var" for Elixir.
  @module_var "mod-initial"

  # --- S09: aliased import.
  alias Scopes.Ns.Widget                          # S09.def
  alias Scopes.Reexport                           # for S10

  def s01_local do
    local_a = "S01.local"                         # S01.def
    IO.puts(local_a)                              # S01.read
  end

  # Same-module "write" in Elixir is a new variable binding, or Agent/ETS.
  # Use an Agent to give a real cross-process mutable cell.
  def start_var do
    {:ok, _} = Agent.start_link(fn -> @module_var end, name: __MODULE__)
  end

  def s05_same_module_write do
    Agent.update(__MODULE__, fn _ -> "rotated" end)      # S05.write
    IO.puts(Agent.get(__MODULE__, & &1))                 # S05.read
  end

  def s06_cross_read, do: Reexport.value                 # S06.read
  def s07_cross_write, do: send(self(), {:cross, "S07"}) # S07.write (message-passing analogue)

  def s08_shadowing do
    module_var = "shadowed"                              # S08.shadow.def
    IO.puts(module_var)                                  # S08.shadow.read
  end

  def s09_aliased_import do
    Widget.new("via-alias")                              # S09.read
  end

  def s10_reexport_chain, do: Reexport.value             # S10.consumer.read

  def s14_qualified, do: Widget.new("hi").label          # S14.read

  def run_scope_demo do
    start_var()
    s01_local()
    s05_same_module_write()
    IO.puts(s06_cross_read())
    s07_cross_write()
    s08_shadowing()
    _ = s09_aliased_import()
    IO.puts(s10_reexport_chain())
    IO.puts(s14_qualified())
  end
end
