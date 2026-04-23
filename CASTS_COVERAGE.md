# Casts / type-conversion coverage matrix

One `casts.<ext>` (or `Casts.<ext>`) per language, each cataloguing the
native cast / coercion forms the LSP needs to recognise. This
complements `IMPORTS_COVERAGE.md` (import forms) and
`SCOPE_TEST_SPEC.md` (variable scope).

## Location & forms per language

| Lang       | File                                                                   | Cast forms covered |
|------------|------------------------------------------------------------------------|---------------------|
| Python     | `monorepo_python/packages/app/src/mono_app/casts.py`                   | `int()` / `float()` / `str()` / `list()` / `bool()` / `bytes()` builtin constructors • `isinstance` narrowing • `typing.cast` • `__int__` / `__float__` / `__str__` / `__bool__` dunders • `__index__` • `Optional` unwrap • `typing.Protocol` structural cast |
| TypeScript | `monorepo_typescript/apps/web/src/casts.ts`                            | `as T` • `<T>x` legacy • non-null `!` • `as const` • `satisfies` • `typeof` narrowing • `instanceof` narrowing • discriminated-union narrowing • `in`-operator narrowing • user-defined `is T` type guard • indexed access • `JSON.parse as T` |
| Rust       | `monorepo_rust/crates/app/src/casts.rs`                                | `as` primitive • `From`/`Into` • `TryFrom`/`TryInto` • `.parse::<T>()` via `FromStr` • pointer cast (unsafe) • `std::mem::transmute` • `Box<dyn Trait>` trait-object cast • `std::mem::size_of::<T>()` |
| Go         | `monorepo_go/apps/web/casts.go`                                        | `T(x)` numeric conversion • `strconv` • type assertion `x.(T)` • type switch • interface satisfaction • slice→array conversion (Go 1.20+) • bytes↔string |
| Java       | `monorepo_java/apps/web/src/main/java/mono/web/Casts.java`             | primitive narrow/widen cast • reference downcast • `instanceof` (legacy + pattern) • autoboxing/unboxing • generic wildcard cast (unchecked) • `Integer.parseInt`/`Double.parseDouble` • downcast in `instanceof T t` pattern |
| C#         | `monorepo_csharp/apps/Web/Casts.cs`                                    | `(T)x` explicit cast • `as T` (null-on-fail) • `is T` / `is T t` pattern • `switch`-expression type narrowing • `checked`/`unchecked` • user-defined implicit/explicit conversion operators • `Convert.ToInt32` • boxing/unboxing • nullable `GetValueOrDefault` |
| Kotlin     | `monorepo_kotlin/apps/web/src/main/kotlin/mono/web/Casts.kt`           | `as` • `as?` safe • `is` / `!is` smart cast • `!!` non-null assert • `.toInt()`/`.toDouble()` etc. • `inline fun <reified T>` runtime cast • `data class.copy` • sealed exhaustive `when` |
| Ruby       | `monorepo_ruby/apps/web/casts.rb`                                      | `Integer()` / `Float()` / `String()` strict • `.to_i` / `.to_s` / `.to_f` lenient • `is_a?` / `kind_of?` / `instance_of?` • `case`/`when` with class •  `Struct#to_a`/`#to_h` • `coerce` protocol |
| PHP        | `monorepo_php/apps/web/src/Casts.php`                                  | `(int)` / `(float)` / `(bool)` / `(array)` / `(object)` / `(string)` cast operators • `settype` • `intval`/`floatval`/`strval`/`boolval` • `instanceof` • `__toString` magic method • union-type param narrowing |
| Solidity   | `monorepo_solidity/src/Casts.sol`                                      | `uint8(x)` numeric narrowing • signed↔unsigned • `bytes32(uint)` • `address(x)` / `payable(x)` / `uint160(addr)` • contract→address • enum↔uint |
| Scala      | `scala/casts.scala`                                                    | `asInstanceOf[T]` unchecked downcast • `isInstanceOf[T]` • pattern match with type ascription • `.toInt`/`.toDouble`/etc. • `Try` safe parse • `implicit def` conversion |
| Swift      | `swift/casts.swift`                                                    | `as!` forced • `as?` optional downcast • `is` type test • pattern match `case let x as T` • `Int(...)`/`Double(...)` initializer casts • `String ↔ NSString` bridging • enum `rawValue` cast |
| Haskell    | `haskell/Casts.hs`                                                     | `fromIntegral` (Num narrowing) • `read :: String -> T` via Read • `readMaybe` total parse • `show` via Show • `toEnum`/`fromEnum` • `Data.Typeable.cast` • `toRational`/`fromRational` |
| OCaml      | `ocaml/casts.ml`                                                       | `int_of_float`/`float_of_int`/`string_of_int`/`int_of_string` • pattern match over variants • module signature restriction • `:>` polymorphic-variant upcast • `Obj.magic` unsafe • record type ascription |
| Elixir     | `elixir/casts.ex`                                                      | `Integer.parse` / `String.to_integer` • `to_string` via String.Chars protocol • `Atom.to_string` / `String.to_existing_atom` • charlist↔binary • struct `Map.from_struct` / `struct!` • `is_integer`/`is_binary`/... guards |
| Zig        | `zig/casts.zig`                                                        | `@as(T, x)` • `@intCast` • `@floatCast` • `@intFromFloat` / `@floatFromInt` • `@ptrCast` • `@bitCast` • `@truncate` • `@enumFromInt` / `@intFromEnum` • error-set widening |
| Lua        | `lua/casts.lua`                                                        | `tostring` / `tonumber` • `type()` inspect • `math.tointeger` / `math.type` (Lua 5.3+) • `string.byte` / `string.char` • implicit string↔number in arithmetic/concat • metatable-based "class cast" |
| Bash       | `bash/casts.sh`                                                        | `$((x))` arithmetic expansion • `printf '%d\|%.2f\|%s'` formatting • `declare -i`/`-a`/`-A` • `[[ =~ ]]` regex narrow |
| PowerShell | `powershell/Casts.ps1`                                                 | `[int]$x` / `[double]$x` / `[datetime]$x` type-accelerator cast • `-as [Type]` (null on fail) • `[int]::Parse` / `::TryParse` • `[Type]::new()` ctor • `-f` format • enum cast • `PSCustomObject` tagging |
| Groovy     | `groovy/Casts.groovy`                                                  | `as T` operator • `.asType(T)` method • C-style `(int) x` • duck-type implicit coercion • `instanceof` • GString↔String • `collectEntries` list→map |
| C          | `c/casts.c`                                                            | C-style `(T)x` • pointer reinterpret via `memcpy` (strict-aliasing safe) • compound literal `(T){...}` (C99) • union-based reinterpret • `void *` erasure • function-pointer cast • implicit numeric promotion |
| C++        | `cpp/casts.cpp`                                                        | `static_cast<T>` • `dynamic_cast<T*>` • `const_cast<T*>` • `reinterpret_cast<T*>` • C-style `(T)x` • functional-style `T(x)` • `std::bit_cast<T>` (C++20) • user-defined `operator T()` implicit + `explicit operator T()` • `unique_ptr` ownership transfer via `static_cast` |
| ASM (NASM) | `asm/casts.asm`                                                        | `movzx` zero-extend • `movsx` sign-extend • `cdq` 32→64 sign-extend (EAX→EDX:EAX) • `cqo` 64→128 sign-extend (RAX→RDX:RAX) • `cvtsi2sd` int→double • `cvttsd2si` truncating double→int • `cvtps2pd` float→double |

## Wiring

Each `casts.*` file is called from its language's entry point so the
extractor sees a complete call graph from `main` → the cast demos.
Calls are added alongside the existing `features` / `scopes` /
`imports` / `advanced` invocations.

## What's not covered

- Compile-time-only type coercion in languages where the LSP discards
  it (e.g., TypeScript `satisfies` has runtime-equivalent output; only
  the type-checker sees it). The LSP still surfaces the syntax, so
  these are documented shape-only.
- Exotic / deprecated forms (`Obj.magic` in OCaml, `std::mem::transmute`
  in Rust) are included as shape-only — marked `unsafe` / commented in
  the fixture.
