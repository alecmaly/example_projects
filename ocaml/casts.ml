(* OCaml cast catalogue. *)

(* 1. Numeric conversions via stdlib helpers. *)
let to_float (i : int) : float = float_of_int i
let to_int   (f : float) : int = int_of_float f
let to_str   (i : int) : string = string_of_int i
let of_str   (s : string) : int = int_of_string s

(* 2. Variant "cast" via pattern match. *)
type shape = Circle of float | Square of float
let describe = function
  | Circle r -> Printf.sprintf "circle %f" r
  | Square s -> Printf.sprintf "square %f" s

(* 3. Subtype coercion — `:>` operator.
   Module A is a subtype of module B (via restriction); `x :> Ty` upcasts. *)
module Integer = struct
  type t = int
  let zero = 0
  let add x y = x + y
end

(* Opaque module type restriction — a form of "cast to narrower interface". *)
module type ADDABLE = sig
  type t
  val add : t -> t -> t
end
module IntegerAsAddable : ADDABLE = (Integer : ADDABLE)

(* 4. Polymorphic variant widening via :>. *)
let widen (v : [ `A ]) : [ `A | `B ] = (v :> [ `A | `B ])

(* 5. Unsafe magic cast — Obj.magic. *)
let unsafe_cast (x : 'a) : 'b = Obj.magic x

(* 6. Record type ascription — narrows inferred type. *)
type point = { x : int; y : int }
let origin : point = { x = 0; y = 0 }

let run () =
  Printf.printf "to_float 3 = %f\n" (to_float 3);
  Printf.printf "to_int 3.7 = %d\n" (to_int 3.7);
  Printf.printf "to_str 42  = %s\n" (to_str 42);
  Printf.printf "of_str 100 = %d\n" (of_str "100");
  print_endline (describe (Circle 2.0));
  let w = widen `A in
  (match w with `A -> print_endline "A" | `B -> print_endline "B");
  print_endline origin.x |> ignore;
  ignore (unsafe_cast origin : int)
