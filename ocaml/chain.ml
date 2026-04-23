(* OCaml transitive chain via 3 nested modules. *)

module Origin = struct
  let origin_value = "T1.origin"                         (* T1.origin.def *)
end

module Middle = struct
  let middle_value = Origin.origin_value                 (* T1.middle.reexport *)
end

module Deep = struct
  let value_alias = Middle.middle_value                  (* T1.deep.reexport *)
end

let run () = print_endline ("transitive: " ^ Deep.value_alias)
