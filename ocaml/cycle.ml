(* OCaml — mutually recursive modules / types require `module rec`
   or `type ... and ...`. Below demonstrates both forms. *)

(* Mutually recursive TYPES via `and`. *)
type alpha = { a_name : string; mutable a_child : bravo option }
and  bravo = { b_tag  : string; mutable b_owner : alpha option }

(* Mutually recursive FUNCTIONS via `let rec ... and`. *)
let rec describe a = "Alpha(" ^ a.a_name ^ ")"
and     spawn_bravo a = { b_tag = a.a_name ^ "/b"; b_owner = Some a }
and     bounce b = describe { a_name = "bounce-from-" ^ b.b_tag; a_child = None }

(* Mutually recursive MODULES via `module rec`. *)
module rec A : sig
  val greet : unit -> string
end = struct
  let greet () = "A via " ^ B.echo "x"
end
and B : sig
  val echo : string -> string
end = struct
  let echo s = s ^ "!"
end

let run () =
  let a = { a_name = "root"; a_child = None } in
  let b = spawn_bravo a in
  print_endline ("cycle: " ^ bounce b);
  print_endline ("module rec: " ^ A.greet ())
