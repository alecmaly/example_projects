//! Labeled scope test cases for Rust — monorepo edition.
//! Ported from rust/src/scopes.rs. Cross-module refs now target the
//! sibling workspace crates `shared` / `utils`.
//! See SCOPE_TEST_SPEC.md at repo root.

use std::sync::atomic::{AtomicI32, Ordering};

// ------------------------------------------------ S04 def / S05 write target
static MODULE_VAR: AtomicI32 = AtomicI32::new(1);     // S04.def

// S09 aliased import from sibling workspace crate.
use shared::format_user as shared_format_user;       // S09.def
use shared::User;
use crate::scopes_ns::Widget;                         // S14.import

pub mod scopes_ns {
    pub struct Widget {                              // S14.Widget.def
        pub label: String,
    }
    impl Widget {
        pub fn new(label: &str) -> Self { Widget { label: label.into() } }
    }
}

pub fn s01_local() {
    let local_a = "S01.local";                       // S01.def
    println!("{}", local_a);                         // S01.read
}

pub fn s02_closure_read() {
    let outer_a = String::from("S02.outer");         // S02.outer.def
    let inner = || println!("{}", outer_a);          // S02.inner.read
    inner();
}

pub fn s03_closure_write() -> i32 {
    let mut counter = 0;                             // S03.outer.def
    let mut bump = || counter += 1;                  // S03.inner.write
    bump(); bump();
    counter                                          // S03.outer.read
}

pub fn s05_same_module_write() {
    MODULE_VAR.store(2, Ordering::SeqCst);           // S05.write
    println!("{}", MODULE_VAR.load(Ordering::SeqCst));// S05.read
}

pub fn s06_cross_read() -> shared::Role {
    shared::DEFAULT_ROLE                             // S06.read — cross-crate
}

pub fn s07_cross_write() {
    // Rust won't let us mutate a shared const, so we exercise the
    // write path through a utils helper that mutates its own state.
    // Covers "cross-crate call that results in a write" semantics.
    let mut c = utils::clamp(1, 0, 1);                // S07.write (indirect)
    c = utils::clamp(c, 0, 1);
    let _ = c;
}

pub fn s08_shadowing() {
    let module_var = "shadowed";                      // S08.shadow.def
    println!("{}", module_var);                       // S08.shadow.read
}

pub fn s09_aliased_import() {
    let u = User { id: 1, name: "alice".into() };
    println!("{}", shared_format_user(&u));           // S09.read
}

pub struct ScopeBase {
    pub x: i32,                                       // S11.instance.def / S13.base.def
}
impl ScopeBase {
    pub fn read_instance(&self, x: i32) -> i32 {
        x + self.x                                    // S11.param.read + S11.instance.read
    }
}

pub struct ScopeDerived {
    pub base: ScopeBase,
    pub y: i32,
}
impl ScopeDerived {
    pub fn read_inherited(&self) -> i32 {
        self.base.x                                   // S13.derived.read
    }
}

pub fn s14_qualified() -> String {
    Widget::new("hi").label                           // S14.read
}

pub fn run_scope_demo() {
    s01_local();
    s02_closure_read();
    println!("{}", s03_closure_write());
    s05_same_module_write();
    println!("{:?}", s06_cross_read());
    s07_cross_write();
    s08_shadowing();
    s09_aliased_import();
    println!("{}", ScopeBase { x: 42 }.read_instance(100));
    println!("{}", ScopeDerived { base: ScopeBase { x: 7 }, y: 0 }.read_inherited());
    println!("{}", s14_qualified());
}
