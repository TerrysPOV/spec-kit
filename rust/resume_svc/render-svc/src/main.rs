use axum::{routing::post, Router, Json, response::IntoResponse};
use serde::Deserialize;
use tracing::info;

#[derive(Deserialize)]
struct RenderReq { cv_json: serde_json::Value }

async fn render(Json(_req): Json<RenderReq>) -> impl IntoResponse {
    Json(serde_json::json!({ "pdf_url": "s3://bucket/fake.pdf" }))
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt().with_target(false).init();
    let app = Router::new().route("/render/resume", post(render));
    let addr = std::net::SocketAddr::from(([0,0,0,0], 8082));
    info!("render-svc listening on {}", addr);
    axum::serve(tokio::net::TcpListener::bind(addr).await.unwrap(), app).await.unwrap();
}
