// Ported coverage from the flat rust/ fixture.
mod features;
mod scopes;
mod imports;
mod advanced;
mod casts;
mod cycle_a;
mod cycle_b;

// `use` re-exported items from the shared crate root.
use shared::{User, Role, DEFAULT_ROLE, format_user};
// Explicit path through the submodule.
use shared::util;
// Aliased import.
use utils::{clamp as bounded, TAG as UTILS_TAG};
// Glob import — brings every pub name from inline module into scope.
use shared::inline::*;

fn main() {
    let u = User { id: 1, name: "alice".into() };
    let role: Role = DEFAULT_ROLE;
    println!("{} ({:?})", format_user(&u), role);
    println!("tag={} clamped={}", UTILS_TAG, bounded(42, 0, 10));
    println!("inline.tag={}", tag());

    // Explicit through-path call.
    let s = util::format_user(&u);
    println!("via util: {}", s);

    // Exercise ported coverage.
    features::run_feature_demo();
    scopes::run_scope_demo();
    imports::demo();
    advanced::run_advanced_demo();
    casts::run_casts_demo();

    // T1 transitive chain — `VALUE_ALIAS` resolved through 2 hops of pub use.
    println!("transitive: {}", shared::chain_deep::VALUE_ALIAS);

    // Cycle: Alpha ↔ Bravo.
    println!("cycle: {}", cycle_a::kick_off());
}
