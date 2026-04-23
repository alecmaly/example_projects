(* OCaml's module-reference forms. *)

(* 1. Plain open — brings every name into scope. *)
open Printf

(* 2. Local open inside expression. *)
let use_local () =
  let open List in
  length [1; 2; 3]

(* 3. Module alias. *)
module L = List

(* 4. Rebinding with restrictions (module inclusion). *)
module type SHOWABLE = sig val describe : unit -> string end
module M : SHOWABLE = struct let describe () = "described" end

(* 5. Include — merges another module's bindings into this one. *)
module Derived = struct
  include M
  let extra () = "extra"
end

let run () =
  printf "open Printf → %s\n" "ok";
  printf "local List → %d\n" (use_local ());
  printf "alias L.length → %d\n" (L.length [1;2;3]);
  printf "include chain → %s / %s\n" (Derived.describe ()) (Derived.extra ())
