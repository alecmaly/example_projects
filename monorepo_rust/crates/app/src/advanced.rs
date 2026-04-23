//! Rust advanced-feature coverage ported from the flat rust/. Covers:
//! macro_rules!, async fn (via blocking adapter), unsafe fn + raw
//! pointer deref, lifetime-carrying function signatures, #[derive],
//! and trait-object double dispatch.

// --- macro_rules! definition + invocation ---
#[macro_export]
macro_rules! logln {
    ($($arg:tt)*) => {{
        println!("[log] {}", format!($($arg)*));
    }};
}

// --- lifetimes in signatures ---
pub fn first_word<'a>(s: &'a str) -> &'a str {
    s.split_whitespace().next().unwrap_or("")
}

pub fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() > b.len() { a } else { b }
}

// --- unsafe fn + unsafe block ---
pub unsafe fn read_raw(p: *const i32) -> i32 {
    *p
}

pub fn unsafe_demo() -> i32 {
    let x: i32 = 42;
    let p: *const i32 = &x;
    unsafe { read_raw(p) }
}

// --- async fn — using a simple blocking executor to avoid pulling tokio
//     into this crate. The shape (async signature + .await) is what the
//     LSP needs to see.
pub async fn compute_async(x: i32) -> i32 {
    x + 1
}

pub async fn chain_async(x: i32) -> i32 {
    let a = compute_async(x).await;
    let b = compute_async(a).await;
    a + b
}

fn block_on<F: std::future::Future>(mut fut: F) -> F::Output {
    use std::pin::Pin;
    use std::task::{Context, Poll, Waker, RawWaker, RawWakerVTable};

    // minimal no-op waker
    fn raw_waker() -> RawWaker {
        fn no_op(_: *const ()) {}
        fn clone(_: *const ()) -> RawWaker { raw_waker() }
        static VT: RawWakerVTable = RawWakerVTable::new(clone, no_op, no_op, no_op);
        RawWaker::new(std::ptr::null(), &VT)
    }
    let waker = unsafe { Waker::from_raw(raw_waker()) };
    let mut cx = Context::from_waker(&waker);
    let mut fut = unsafe { Pin::new_unchecked(&mut fut) };
    loop {
        match fut.as_mut().poll(&mut cx) {
            Poll::Ready(v) => return v,
            Poll::Pending => continue,
        }
    }
}

// --- trait objects w/ double dispatch ---
pub trait Animal: std::fmt::Debug {
    fn speak(&self) -> String;
}

#[derive(Debug)]
pub struct Duck;
#[derive(Debug)]
pub struct Fox;

impl Animal for Duck { fn speak(&self) -> String { "quack".into() } }
impl Animal for Fox  { fn speak(&self) -> String { "what does the fox say?".into() } }

// Trait with a *default method*. Implementors inherit it or override it.
pub trait Describable: Animal {
    fn describe(&self) -> String {
        format!("a creature that says {}", self.speak())
    }
}

impl Describable for Duck {}                     // inherits default `describe`
impl Describable for Fox {
    fn describe(&self) -> String {                 // overrides the default
        format!("mysterious fox: {}", self.speak())
    }
}

pub fn animals() -> Vec<Box<dyn Animal>> {
    vec![Box::new(Duck), Box::new(Fox)]
}

pub fn run_advanced_demo() {
    logln!("hello from macro, value = {}", 42);

    let s = String::from("first word here");
    logln!("first_word = {}", first_word(&s));
    logln!("longest = {}", longest("short", "longest"));

    logln!("unsafe deref -> {}", unsafe_demo());

    let result = block_on(chain_async(10));
    logln!("chain_async(10) = {}", result);

    for a in animals() {
        logln!("{:?}: {}", a, a.speak());
    }
}

// --- const-generic function ---
pub fn sum_array<const N: usize>(arr: [i32; N]) -> i32 {
    arr.iter().sum()
}

// --- const-generic struct with inherent impl ---
pub struct FixedBuf<const N: usize> {
    pub data: [u8; N],
}

impl<const N: usize> FixedBuf<N> {
    pub fn new() -> Self {
        FixedBuf { data: [0u8; N] }
    }
    pub fn len(&self) -> usize {
        N
    }
}

// --- GAT (generic associated type) ---
pub trait Container {
    type Item<'a> where Self: 'a;
    fn first_item<'a>(&'a self) -> Option<Self::Item<'a>>;
}

impl Container for Vec<i32> {
    type Item<'a> = &'a i32;
    fn first_item<'a>(&'a self) -> Option<Self::Item<'a>> {
        self.first()
    }
}

// --- function returning `impl Iterator` ---
pub fn even_counter(n: usize) -> impl Iterator<Item = usize> {
    (0..n).filter(|x| x % 2 == 0)
}

// --- async block used inside a non-async function ---
pub fn make_future_demo() {
    let fut = async { 1 + 2 };
    // Pretend we're handing this off to some executor somewhere.
    let _ = fut;
}

// --- unsafe impl for Send/Sync marker traits ---
pub struct RawHandle {
    pub ptr: *mut u8,
}

unsafe impl Send for RawHandle {}
unsafe impl Sync for RawHandle {}
