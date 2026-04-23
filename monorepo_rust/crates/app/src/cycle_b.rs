// C1.b — closes the cycle back to Alpha.

use crate::cycle_a::Alpha;

pub struct Bravo {
    pub tag: String,
}

impl Bravo {
    pub fn new(tag: &str) -> Self { Bravo { tag: tag.into() } }

    pub fn bounce_to_alpha(&self) -> String {
        Alpha::new(&format!("bounce-from-{}", self.tag)).describe()
    }
}
