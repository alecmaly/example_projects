(* Labeled scope test cases for OCaml. See SCOPE_TEST_SPEC.md. *)

let module_var = ref "mod-initial"                    (* S04.def — mutable ref *)

let s01_local () =
  let local_a = "S01.local" in                        (* S01.def *)
  print_endline local_a                               (* S01.read *)

let s02_closure_read () =
  let outer_a = "S02.outer" in                        (* S02.outer.def *)
  let inner () = print_endline outer_a in             (* S02.inner.read *)
  inner ()

let s03_closure_write () =
  let counter = ref 0 in                              (* S03.outer.def *)
  let bump () = incr counter in                       (* S03.inner.write *)
  bump (); bump ();
  !counter                                            (* S03.outer.read *)

let s05_same_module_write () =
  module_var := "rotated";                            (* S05.write *)
  print_endline !module_var                           (* S05.read *)

let s08_shadowing () =
  let module_var = "shadowed" in                      (* S08.shadow.def *)
  print_endline module_var                            (* S08.shadow.read *)

(* S11: record field vs function param. *)
type scope_base = { x : int }
let read_instance x b = x + b.x                       (* S11.param.read + S11.instance.read *)

module Ns = struct
  type widget = { label : string }                    (* S14.Widget.def *)
  let mk_widget label = { label }
end

let s14_qualified () = (Ns.mk_widget "hi").label      (* S14.read *)

let run_scope_demo () =
  s01_local ();
  s02_closure_read ();
  Printf.printf "counter=%d\n" (s03_closure_write ());
  s05_same_module_write ();
  s08_shadowing ();
  Printf.printf "s11=%d\n" (read_instance 100 { x = 42 });
  Printf.printf "s14=%s\n" (s14_qualified ())
