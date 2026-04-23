// C1.a — mutually-referential types via Box.
// Rust requires indirection (Box / Rc / &) to compile cyclic types.

use crate::cycle_b::Bravo;

pub struct Alpha {
    pub name: String,
    pub child: Option<Box<Bravo>>,          // C1.a.type_ref → cycle_b::Bravo
}

impl Alpha {
    pub fn new(name: &str) -> Self {
        Alpha { name: name.into(), child: None }
    }

    pub fn spawn_bravo(&self) -> Box<Bravo> {
        Box::new(Bravo::new(&format!("{}/b", self.name)))
    }

    pub fn describe(&self) -> String { format!("Alpha({})", self.name) }
}

pub fn kick_off() -> String {
    let a = Alpha::new("root");
    let b = a.spawn_bravo();
    b.bounce_to_alpha()
}
