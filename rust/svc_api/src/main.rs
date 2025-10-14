use axum::{routing::get, Router};
use std::net::SocketAddr;

#[tokio::main]
async fn main() {
    let app = Router::new().route("/", get(|| async { "ok" }));
    let addr = SocketAddr::from(([127, 0, 0, 1], 3001));
    println!("svc_api listening on http://{addr}");
    axum::serve(tokio::net::TcpListener::bind(addr).await.unwrap(), app)
        .await
        .unwrap();
}
