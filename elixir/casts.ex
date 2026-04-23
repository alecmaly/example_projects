# Elixir cast / conversion catalogue.

defmodule Casts do
  # 1. Integer.parse / String.to_integer — parsing.
  def parse_int(s) do
    case Integer.parse(s) do
      {n, ""}  -> {:ok, n}
      _        -> {:error, :bad}
    end
  end

  # 2. to_string — Protocol-based (String.Chars).
  def to_str(x), do: to_string(x)

  # 3. Integer -> String conversions.
  def int_to_str(n), do: Integer.to_string(n)
  def str_to_int(s), do: String.to_integer(s)

  # 4. Atom <-> String (use to_existing_atom to avoid atom-table exhaustion).
  def atom_to_str(a), do: Atom.to_string(a)
  def str_to_atom(s), do: String.to_existing_atom(s)

  # 5. Charlist <-> binary.
  def str_to_charlist(s), do: String.to_charlist(s)
  def charlist_to_str(c), do: List.to_string(c)

  # 6. Struct -> Map coercion.
  defmodule User do
    defstruct [:name, :age]
  end
  def user_to_map(u), do: Map.from_struct(u)
  def map_to_user(m), do: struct!(User, m)

  # 7. Type-check helpers.
  def is_what(x) do
    cond do
      is_integer(x) -> :int
      is_binary(x)  -> :string
      is_list(x)    -> :list
      is_atom(x)    -> :atom
      true          -> :other
    end
  end

  def run_casts_demo do
    IO.inspect(parse_int("42"))
    IO.inspect(to_str(:hello))
    IO.inspect(int_to_str(42))
    IO.inspect(str_to_int("123"))
    IO.inspect(atom_to_str(:alice))
    IO.inspect(str_to_charlist("hi"))
    u = %User{name: "alice", age: 30}
    IO.inspect(user_to_map(u))
    IO.inspect(map_to_user(%{name: "bob", age: 40}))
    IO.inspect(is_what(42))
  end
end
