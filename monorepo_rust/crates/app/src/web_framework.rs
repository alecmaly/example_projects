//! Axum framework idioms: Router::new().route(...), extractor types
//! (Path, Query, State, Json), async handlers, custom error type
//! implementing IntoResponse, middleware via tower_layer, tokio runtime.
//!
//! Uses in this fixture are for static-analysis only; crates are not
//! expected to resolve.

use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::{IntoResponse, Response},
    routing::{delete, get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use tower::ServiceBuilder;
use tower_http::trace::TraceLayer;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AxumUser {
    pub id: u64,
    pub email: String,
    pub name: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct CreateUser {
    pub email: String,
    pub name: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct ListParams {
    #[serde(default = "default_limit")]
    pub limit: usize,
    pub search: Option<String>,
}
fn default_limit() -> usize { 10 }

#[derive(Clone)]
pub struct AppState {
    pub users: Arc<RwLock<HashMap<u64, AxumUser>>>,
}

// --- custom error + IntoResponse ---
#[derive(Debug)]
pub enum ApiError {
    NotFound(String),
    BadRequest(String),
    Internal(String),
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let (status, msg) = match self {
            ApiError::NotFound(m)   => (StatusCode::NOT_FOUND, m),
            ApiError::BadRequest(m) => (StatusCode::BAD_REQUEST, m),
            ApiError::Internal(m)   => (StatusCode::INTERNAL_SERVER_ERROR, m),
        };
        (status, Json(serde_json::json!({ "error": msg }))).into_response()
    }
}

// --- handlers ---
pub async fn get_user(
    State(state): State<AppState>,
    Path(id): Path<u64>,
) -> Result<Json<AxumUser>, ApiError> {
    let users = state.users.read().await;
    users.get(&id)
        .cloned()
        .map(Json)
        .ok_or_else(|| ApiError::NotFound(format!("user {id}")))
}

pub async fn list_users(
    State(state): State<AppState>,
    Query(params): Query<ListParams>,
) -> Json<Vec<AxumUser>> {
    let users = state.users.read().await;
    let iter = users.values().filter(|u| {
        params.search.as_ref().map_or(true, |s| u.email.contains(s))
    });
    Json(iter.take(params.limit).cloned().collect())
}

pub async fn create_user(
    State(state): State<AppState>,
    Json(req): Json<CreateUser>,
) -> Result<(StatusCode, Json<AxumUser>), ApiError> {
    if !req.email.contains('@') {
        return Err(ApiError::BadRequest("bad email".into()));
    }
    let mut users = state.users.write().await;
    let id = users.len() as u64 + 1;
    let u = AxumUser { id, email: req.email, name: req.name };
    users.insert(id, u.clone());
    Ok((StatusCode::CREATED, Json(u)))
}

pub async fn delete_user(
    State(state): State<AppState>,
    Path(id): Path<u64>,
) -> Result<StatusCode, ApiError> {
    let mut users = state.users.write().await;
    users.remove(&id)
        .map(|_| StatusCode::NO_CONTENT)
        .ok_or_else(|| ApiError::NotFound(format!("user {id}")))
}

pub fn build_router(state: AppState) -> Router {
    Router::new()
        .route("/api/users",       get(list_users).post(create_user))
        .route("/api/users/:id",   get(get_user).delete(delete_user))
        .route("/api/users",       post(create_user))
        .route("/api/users/:id",   delete(delete_user))
        .layer(ServiceBuilder::new().layer(TraceLayer::new_for_http()))
        .with_state(state)
}

#[tokio::main]
pub async fn run_axum_server() {
    let state = AppState { users: Arc::new(RwLock::new(HashMap::new())) };
    let app = build_router(state);
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
