# Elixir feature coverage: pattern matching, pipe operator, structs,
# protocols, behaviours, guards, with-chains, comprehensions, Task/agent.

defmodule Features.User do
  @enforce_keys [:name]
  defstruct [:name, age: 0, role: :user]
end

defprotocol Features.Greeter do
  @doc "Returns a greeting for the given subject."
  def greet(subject)
end

defimpl Features.Greeter, for: Features.User do
  def greet(%Features.User{name: name}), do: "hello, #{name}"
end

defimpl Features.Greeter, for: BitString do
  def greet(s), do: "hello, " <> s
end

defmodule Features.Logger do
  @callback log(level :: atom, msg :: String.t()) :: :ok

  defmacro __using__(_opts) do
    quote do
      @behaviour Features.Logger
    end
  end
end

defmodule Features.StdOut do
  use Features.Logger
  @impl true
  def log(level, msg), do: IO.puts("[#{level}] #{msg}")
end

# `defoverridable` — module provides default impls that consumers can
# replace via their own `def` of the same name.
defmodule Features.Greetable do
  defmacro __using__(_opts) do
    quote do
      def greet_default(name), do: "hello, #{name}"
      def farewell(name), do: "goodbye, #{name}"
      defoverridable greet_default: 1, farewell: 1
    end
  end
end

defmodule Features.LoudGreeter do
  use Features.Greetable
  # Overrides the default implementation from Features.Greetable.
  def greet_default(name), do: "HELLO, #{String.upcase(name)}!"
end

defmodule Features do
  alias Features.{User, Greeter, StdOut}

  # Guards + multiple function clauses.
  def classify(n) when is_integer(n) and n > 0, do: :positive
  def classify(n) when is_integer(n) and n < 0, do: :negative
  def classify(0), do: :zero
  def classify(_), do: :other

  # Pipe operator chain.
  def describe(user) do
    user
    |> Map.from_struct()
    |> Map.put(:label, Greeter.greet(user))
    |> Map.to_list()
  end

  # `with` chain — railway pattern.
  def lookup(map, key) do
    with {:ok, v} <- Map.fetch(map, key),
         s when is_binary(s) <- v do
      {:ok, s}
    else
      :error -> {:error, :missing}
      _      -> {:error, :bad_type}
    end
  end

  # List / map comprehensions.
  def even_squares(n) do
    for x <- 0..n, rem(x, 2) == 0, do: x * x
  end

  # Spawn a lightweight process.
  def run_async do
    parent = self()
    pid = spawn_link(fn -> send(parent, {:hello, :from_spawn}) end)
    receive do
      {:hello, :from_spawn} -> StdOut.log(:info, "got hello from #{inspect(pid)}")
    after
      100 -> StdOut.log(:warn, "timeout")
    end
  end

  def run_feature_demo do
    user = %User{name: "alice", age: 30, role: :admin}
    StdOut.log(:info, Greeter.greet(user))
    StdOut.log(:info, Greeter.greet("bob"))
    StdOut.log(:info, "classify(5) = #{classify(5)}")
    StdOut.log(:info, "describe: #{inspect(describe(user))}")
    StdOut.log(:info, "lookup: #{inspect(lookup(%{"k" => "v"}, "k"))}")
    StdOut.log(:info, "even: #{inspect(even_squares(10))}")
    run_async()
  end

  # Multi-generator list comprehension with filter.
  def pairs do
    for x <- 1..3, y <- 1..3, x != y, do: {x, y}
  end
end

# `defmacro` — compile-time code expansion.
defmodule Features.MyMacros do
  defmacro unless_m(cond, do: body) do
    quote do
      if !unquote(cond), do: unquote(body)
    end
  end
end

# Minimal GenServer — OTP behaviour with callbacks.
defmodule Features.Counter do
  use GenServer

  def start_link(init \\ 0),
    do: GenServer.start_link(__MODULE__, init, name: __MODULE__)

  @impl true
  def init(n), do: {:ok, n}

  @impl true
  def handle_call(:inc, _from, n), do: {:reply, n + 1, n + 1}

  @impl true
  def handle_cast({:add, m}, n), do: {:noreply, n + m}
end

# Task.async / Task.await — parallel work.
defmodule Features.Workers do
  def parallel_sum(xs) do
    xs
    |> Enum.map(&Task.async(fn -> &1 * &1 end))
    |> Enum.map(&Task.await/1)
    |> Enum.sum()
  end
end
