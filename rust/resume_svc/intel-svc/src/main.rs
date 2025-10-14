use axum::{routing::get, routing::post, Router, Json};
use serde::{Deserialize, Serialize};
use tracing::info;

#[derive(Deserialize)]
struct LookupReq { domain: String, role_family: Option<String> }

#[derive(Serialize)]
struct LookupResp {
    domain: String,
    role_family: String,
    products: Vec<String>,
    people: Vec<Person>,
    signals: Vec<String>,
    sources: Vec<String>,
}

#[derive(Serialize)]
struct Person { name: String, title: String, linkedin: String }

async fn health() -> &'static str { "ok" }

async fn lookup_company(Json(req): Json<LookupReq>) -> Json<LookupResp> {
    let role = req.role_family.unwrap_or_else(|| "General".to_string());
    Json(LookupResp {
        domain: req.domain,
        role_family: role,
        products: vec!["ExampleProduct".into()],
        people: vec![Person { name: "Jane Doe".into(), title: "Hiring Manager".into(), linkedin: "https://linkedin.com/in/janedoe".into() }],
        signals: vec!["Recent funding".into(), "Hiring push".into()],
        sources: vec!["https://example.com".into()],
    })
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt().with_target(false).init();
    let app = Router::new()
        .route("/healthz", get(health))
        .route("/intel/lookup_company", post(lookup_company));
    let addr = std::net::SocketAddr::from(([0,0,0,0], 8081));
    info!("intel-svc listening on {}", addr);
    axum::serve(tokio::net::TcpListener::bind(addr).await.unwrap(), app).await.unwrap();
}
