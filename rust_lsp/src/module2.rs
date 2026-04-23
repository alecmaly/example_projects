use tokio::time::sleep;
use std::time::Duration;

pub const MODULE2_CONSTANT: &str = "I'm a constant in module2";
pub static PUBLIC_VAR: &str = "I'm a public static variable in module2";

pub struct ComplexStruct {
    name: String,
    value: i32,
}

impl ComplexStruct {
    pub fn new(name: String, value: i32) -> Self {
        ComplexStruct { name, value }
    }

    pub async fn complex_method(&self) -> Result<(), Box<dyn std::error::Error>> {
        println!("Complex method called on {} with value {}", self.name, self.value);
        sleep(Duration::from_millis(100)).await;
        Ok(())
    }
}

pub async fn function1() -> Result<(), Box<dyn std::error::Error>> {
    println!("This is function1 from module2");
    println!("Accessing module constant: {}", MODULE2_CONSTANT);
    internal_function().await?;
    Ok(())
}

async fn internal_function() -> Result<(), Box<dyn std::error::Error>> {
    let local_var = "I'm local to internal_function";
    println!("This is an internal function in module2");
    println!("Local var: {}", local_var);
    println!("Public var: {}", PUBLIC_VAR);
    sleep(Duration::from_millis(100)).await;
    Ok(())
}

pub fn public_var() -> &'static str {
    PUBLIC_VAR
}