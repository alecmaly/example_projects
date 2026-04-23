(* OCaml feature coverage: variants, records, modules, functors,
   pattern matching, labelled args, refs (mutable cells). *)

(* Variant with data. *)
type shape =
  | Circle of float
  | Square of float
  | Rectangle of { w : float; h : float }

let area = function
  | Circle r -> 3.14159 *. r *. r
  | Square s -> s *. s
  | Rectangle { w; h } -> w *. h

(* Module with private fields. *)
module Box : sig
  type 'a t
  val make   : 'a -> 'a t
  val get    : 'a t -> 'a
end = struct
  type 'a t = { value : 'a }
  let make v = { value = v }
  let get b  = b.value
end

(* Functor — parameterised module. *)
module type COMPARABLE = sig
  type t
  val compare : t -> t -> int
end

module MakeSet (C : COMPARABLE) = struct
  type elt = C.t
  let empty = []
  let add x xs = if List.exists (fun y -> C.compare x y = 0) xs then xs else x :: xs
end

module IntCmp = struct type t = int let compare = Stdlib.compare end
module IntSet = MakeSet (IntCmp)

(* Labelled + optional args. *)
let greet ?(greeting = "hello") ~name () = greeting ^ ", " ^ name

(* Mutable ref. *)
let counter = ref 0
let bump () = incr counter

(* Tail-recursive with accumulator. *)
let rec fibs_into acc a b = function
  | 0 -> List.rev acc
  | n -> fibs_into (a :: acc) b (a + b) (n - 1)

let fibs n = fibs_into [] 0 1 n

(* Entry. *)
let run_feature_demo () =
  Printf.printf "area circle = %f\n" (area (Circle 2.0));
  let b = Box.make "hi" in
  Printf.printf "box = %s\n" (Box.get b);
  let s = IntSet.add 1 (IntSet.add 2 IntSet.empty) in
  Printf.printf "set len = %d\n" (List.length s);
  print_endline (greet ~name:"world" ());
  bump (); bump ();
  Printf.printf "counter = %d\n" !counter;
  Printf.printf "fibs 8 = %s\n"
    (String.concat "," (List.map string_of_int (fibs 8)))
