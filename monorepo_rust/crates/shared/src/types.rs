#[derive(Debug, Clone)]
pub struct User {
    pub id: u64,
    pub name: String,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Role {
    Admin,
    User,
    Guest,
}

pub const DEFAULT_ROLE: Role = Role::User;
