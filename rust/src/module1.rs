use std::sync::Arc;
use tokio::sync::Mutex;

pub trait Trait1 {
    fn trait_method(&self);
}

pub trait Trait2 {
    fn another_trait_method(&self);
}

pub struct BaseStruct {
    base_var: String,
}

impl BaseStruct {
    pub fn new() -> Self {
        BaseStruct {
            base_var: String::from("I'm a base struct variable"),
        }
    }

    pub async fn base_method(&self) -> Result<(), Box<dyn std::error::Error>> {
        println!("This is a method from BaseStruct");
        println!("Base var: {}", self.base_var);
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        Ok(())
    }
}

pub struct DerivedStruct {
    base: BaseStruct,
    derived_var: String,
}

impl DerivedStruct {
    pub fn new() -> Self {
        DerivedStruct {
            base: BaseStruct::new(),
            derived_var: String::from("I'm a derived struct variable"),
        }
    }

    pub async fn derived_method(&self) -> Result<(), Box<dyn std::error::Error>> {
        println!("This is a method from DerivedStruct");
        println!("Derived var: {}", self.derived_var);
        self.base_method().await?;
        Ok(())
    }

    pub async fn base_method(&self) -> Result<(), Box<dyn std::error::Error>> {
        self.base.base_method().await?;
        println!("This is an overridden method in DerivedStruct");
        Ok(())
    }
}

impl Trait1 for BaseStruct {
    fn trait_method(&self) {
        println!("Trait1 method implemented for BaseStruct");
    }
}

impl Trait2 for BaseStruct {
    fn another_trait_method(&self) {
        println!("Trait2 method implemented for BaseStruct");
    }
}

impl Trait1 for DerivedStruct {
    fn trait_method(&self) {
        println!("Trait1 method implemented for DerivedStruct");
    }
}

impl Trait2 for DerivedStruct {
    fn another_trait_method(&self) {
        println!("Trait2 method implemented for DerivedStruct");
    }
}

pub async fn use_struct1() -> Result<(), Box<dyn std::error::Error>> {
    let obj = Arc::new(Mutex::new(Struct1::new()));
    obj.lock().await.method1().await?;
    Ok(())
}