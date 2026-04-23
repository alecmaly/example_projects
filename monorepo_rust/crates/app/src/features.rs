//! Rust feature coverage — ported from rust/src/features.rs.
//! Self-contained; exercises enum-with-data, match, `?`, Box<dyn>,
//! iterator chain, capturing closure.

use std::fmt;

#[derive(Debug)]
pub enum Shape {
    Circle(f64),
    Square(f64),
    Rectangle { w: f64, h: f64 },
}

impl Shape {
    pub fn area(&self) -> f64 {
        match self {
            Shape::Circle(r) => std::f64::consts::PI * r * r,
            Shape::Square(s) => s * s,
            Shape::Rectangle { w, h } => w * h,
        }
    }
}

pub trait Greeter: fmt::Debug {
    fn greet(&self) -> String;
}

#[derive(Debug)]
pub struct English;
#[derive(Debug)]
pub struct Spanish;

impl Greeter for English { fn greet(&self) -> String { "hello".into() } }
impl Greeter for Spanish { fn greet(&self) -> String { "hola".into() } }

pub fn make_greeter(lang: &str) -> Box<dyn Greeter> {
    match lang {
        "es" => Box::new(Spanish),
        _    => Box::new(English),
    }
}

pub fn parse_pair(s: &str) -> Result<(i32, i32), Box<dyn std::error::Error>> {
    let mut it = s.split(',');
    let a = it.next().ok_or("missing a")?.trim().parse::<i32>()?;
    let b = it.next().ok_or("missing b")?.trim().parse::<i32>()?;
    Ok((a, b))
}

pub fn sum_even_squares(n: i32) -> i64 {
    (0..=n)
        .filter(|x| x % 2 == 0)
        .map(|x| (x as i64) * (x as i64))
        .sum()
}

pub fn make_counter() -> impl FnMut() -> i32 {
    let mut n = 0;
    move || { n += 1; n }
}

pub fn run_feature_demo() {
    for s in [Shape::Circle(2.0), Shape::Square(3.0), Shape::Rectangle { w: 2.0, h: 5.0 }] {
        println!("{:?} area = {:.3}", s, s.area());
    }
    for lang in ["en", "es"] {
        let g = make_greeter(lang);
        println!("{lang}: {}", g.greet());
    }
    match parse_pair("3, 4") {
        Ok(p)  => println!("parsed {:?}", p),
        Err(e) => println!("error: {}", e),
    }
    println!("sum of even squares 0..10 = {}", sum_even_squares(10));
    let mut c = make_counter();
    println!("counter: {} {} {}", c(), c(), c());
}
