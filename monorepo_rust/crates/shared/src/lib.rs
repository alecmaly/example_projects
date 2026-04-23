// Multi-module crate root. `pub mod` exposes submodules; `pub use`
// re-exports individual items at the crate root so consumers can write
// `shared::User` as well as `shared::types::User`.
pub mod types;
pub mod util;

pub use types::{User, Role, DEFAULT_ROLE};
pub use util::format_user;

// Inline submodule (no separate file).
pub mod inline {
    pub fn tag() -> &'static str { "inline" }
}

// --- T1 transitive re-export chain (3 levels). Consumers pull
//     `VALUE_ALIAS` through 2 hops; LSP must resolve back to
//     `chain_origin::ORIGIN_VALUE`.
pub mod chain_origin {
    pub const ORIGIN_VALUE: &str = "T1.origin";                     // T1.origin.def
}
pub mod chain_middle {
    pub use super::chain_origin::*;                                  // T1.middle.reexport
}
pub mod chain_deep {
    pub use super::chain_middle::ORIGIN_VALUE as VALUE_ALIAS;        // T1.deep.reexport (renamed)
}
