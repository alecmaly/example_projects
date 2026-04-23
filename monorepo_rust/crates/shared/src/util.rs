use crate::types::User;

pub fn format_user(u: &User) -> String {
    format!("{}:{}", u.id, u.name)
}

pub(crate) fn internal_only() -> &'static str {
    "crate-private"
}
