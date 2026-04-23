//! Exhaustive Rust import forms — monorepo edition. Biased toward
//! cross-crate imports (shared, utils).

// 1. Plain `use` — one item.
use shared::User;
// 2. Braced list.
use shared::{Role, DEFAULT_ROLE};
// 3. Renamed.
use shared::format_user as fmt_user;
// 4. Glob — brings every pub name.
use shared::inline::*;
// 5. Self + braced combo.
use std::io::{self, Read};
// 6. Super — module-hierarchy-relative (app crate root -> sibling mod).
use super::scopes::ScopeBase as ScopeBaseSuper;
// 7. Crate-absolute.
use crate::features::Shape;
// 8. Re-exported / pub-used.
pub use utils::clamp;

// 9. `extern crate` — legacy 2015 style. Shape-only.
// extern crate utils as _utils_legacy;

// 10. Inline module.
pub mod inline_here {
    pub const NAME: &str = "inline";
    pub fn greet() -> &'static str { NAME }
}

// 11. Conditional compile import (gated off).
#[cfg(feature = "json")]
use std::io::Write;

pub fn demo() {
    let u = User { id: 1, name: "alice".into() };
    let _r: Role = DEFAULT_ROLE;
    println!("{}", fmt_user(&u));
    println!("tag = {}", tag());                    // via shared::inline::*
    let _ = io::stdin();
    let _: Option<Box<dyn Read>> = None;
    let _ = ScopeBaseSuper { x: 1 };
    let _ = Shape::Circle(1.0);
    let _ = inline_here::greet();
    let _ = clamp(5, 0, 10);
}
