//! Rust cast / conversion catalogue.

use std::convert::{From, Into, TryFrom, TryInto};

// 1. `as` primitive cast (may truncate/lose precision).
pub fn primitive_casts() {
    let x: i32 = 300;
    let y: u8 = x as u8;                 // truncating
    let z: f64 = x as f64;
    println!("as: {} {} {}", x, y, z);
}

// 2. From/Into — infallible conversion via trait.
pub struct Celsius(pub f64);
pub struct Fahrenheit(pub f64);

impl From<Celsius> for Fahrenheit {
    fn from(c: Celsius) -> Self { Fahrenheit(c.0 * 9.0 / 5.0 + 32.0) }
}

// `Into` is automatically implemented when `From` exists.
pub fn into_demo() {
    let c = Celsius(100.0);
    let f: Fahrenheit = c.into();
    println!("212F expected: {}", f.0);
}

// 3. TryFrom/TryInto — fallible conversion.
pub fn try_demo() -> Result<u8, std::num::TryFromIntError> {
    let n: i32 = 200;
    let b: u8 = u8::try_from(n)?;        // 200 fits in u8
    let big: i32 = 300;
    match u8::try_from(big) {
        Ok(v)  => println!("ok {}", v),
        Err(e) => println!("trunc err: {}", e),
    }
    Ok(b)
}

// 4. `.parse::<T>()` via FromStr.
pub fn parse_demo() {
    let n: i32 = "42".parse().unwrap();
    let p: Result<u16, _> = "notanumber".parse();
    println!("parsed {}, err? {}", n, p.is_err());
}

// 5. Pointer cast (unsafe).
pub fn ptr_demo() {
    let n: i32 = 42;
    let p: *const i32 = &n;
    let q: *const u8 = p as *const u8;   // reinterpret pointer
    let v: u8 = unsafe { *q };
    println!("ptr reinterpret: {}", v);
}

// 6. `std::mem::transmute` — unsafe bit-reinterpretation.
pub fn transmute_demo() {
    let f: f32 = 3.14;
    let bits: u32 = unsafe { std::mem::transmute::<f32, u32>(f) };
    println!("transmute bits: {:#x}", bits);
}

// 7. Trait object cast via `Box<dyn>`.
pub trait Shape { fn name(&self) -> &'static str; }
pub struct Circle;
impl Shape for Circle { fn name(&self) -> &'static str { "Circle" } }
pub fn as_trait_object() {
    let c: Box<dyn Shape> = Box::new(Circle);
    println!("dyn: {}", c.name());
}

// 8. `std::mem::size_of::<T>()` — compile-time type introspection.
pub fn sizeof_demo() {
    println!("sizeof(u64)={}", std::mem::size_of::<u64>());
}

pub fn run_casts_demo() {
    primitive_casts();
    into_demo();
    let _ = try_demo();
    parse_demo();
    ptr_demo();
    transmute_demo();
    as_trait_object();
    sizeof_demo();
}
