module Greeter = struct
  let prefix = "hi"
  let greet name = prefix ^ " " ^ name
end
let main () = print_endline (Greeter.greet "world")
let _ = main ()
