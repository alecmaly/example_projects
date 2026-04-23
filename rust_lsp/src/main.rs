mod module1;
mod module2;

use module1::{BaseStruct, DerivedStruct, Trait1, Trait2};
use module2::{function1, MODULE2_CONSTANT, ComplexStruct};
use std::sync::Arc;
use tokio::sync::Mutex;
use futures::stream::{self, StreamExt};

static GLOBAL_VAR: &str = "I'm global in main";


fn test() {
    let local_var = "I'm local to test";
    println!("{}", GLOBAL_VAR);
    println!("{}", local_var);
    test2();
}

fn test2() {
    let local_var = "I'm local to test2";
    println!("{}", GLOBAL_VAR);
    println!("{}", local_var);
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let local_var = "I'm local to main";
    println!("{}", GLOBAL_VAR);
    println!("{}", local_var);
    println!("Imported constant: {}", MODULE2_CONSTANT);

    let base_obj = BaseStruct::new();
    let derived_obj = DerivedStruct::new();

    base_obj.base_method().await?;
    derived_obj.base_method().await?;
    derived_obj.derived_method().await?;

    // Using traits
    let trait_obj: Box<dyn Trait1> = Box::new(BaseStruct::new());
    trait_obj.trait_method();

    let complex_obj = ComplexStruct::new("Complex".to_string(), 42);
    complex_obj.complex_method().await?;

    function1().await?;
    recursive_function(5).await?;

    // Accessing module-level variables
    println!("Module1 static var: {}", BaseStruct::static_var());
    println!("Module2 public var: {}", module2::public_var());

    // Demonstrate generic function
    let numbers = vec![1, 2, 3, 4, 5];
    println!("Sum of numbers: {}", sum(&numbers));

    // Demonstrate async closure
    let async_closure = async {
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        println!("Async closure executed");
    };
    async_closure.await;

    // Demonstrate async stream
    let mut stream = stream::iter(0..5)
        .then(|i| async move {
            tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
            i
        });

    while let Some(i) = stream.next().await {
        println!("Stream item: {}", i);
    }

    Ok(())
}

async fn recursive_function(n: i32) -> Result<(), Box<dyn std::error::Error>> {
    if n <= 0 {
        return Ok(());
    }
    println!("Recursion level: {}", n);
    tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
    recursive_function(n - 1).await
}

// Generic function
fn sum<T: std::iter::Sum>(items: &[T]) -> T
where
    T: Copy,
{
    items.iter().copied().sum()
}