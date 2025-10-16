# AI Resume Assistant – Web-First Product Specification

**Prepared by:** Terry Yodaiken  
**Role:** Founder & CEO, POVIEW.AI  
**Audience:** Engineering, Product, and Ops teams

---

## 1. Overview

The AI Resume Assistant is a **web-based SaaS** that automates resume and cover letter tailoring using AI-powered contextual research. Users interact entirely through a web interface — no desktop app required.

### Stack

Frontend: Next.js (React + TailwindCSS)  
Backend: FastAPI + Claude Agent SDK  
Microservices: Rust (Axum) for high-performance research and rendering  
Storage: Google Drive (user files), Qdrant (vector store), Postgres (metadata)

---

## 2. Architecture

**Browser (Next.js)** → **FastAPI Gateway** → **Claude Agent SDK** → **Rust Microservices** → **Google Drive / Qdrant / Postgres**

| Component     | Technology                     | Function                                                     |
| ------------- | ------------------------------ | ------------------------------------------------------------ |
| Frontend      | Next.js                        | User dashboard, uploads, analytics                           |
| Gateway       | FastAPI                        | Auth, routing, orchestration                                 |
| Agents        | Claude Agent SDK               | Profile, Research, Compose, Review                           |
| Rust Services | Axum                           | `intel-svc` (company research), `render-svc` (PDF rendering) |
| Storage       | Postgres, Qdrant, Google Drive | Data, embeddings, files                                      |

---

## 3. Web App Features

- Job description upload or LinkedIn scrape
- Resume tailoring and cover letter generation
- Interview brief (company insights and people)
- Feedback loop for self-learning
- Google Drive integration for storage
- Secure web authentication (OAuth)

---

## 4. Observability & Cost Control

- Metrics: tokens_in/out, cost/run, latency, cache hit %, error rate
- CostLimiter enforces per-user budget
- Grafana dashboards for metrics & alerts

---

## 5. Development Phases

| Phase                  | Goal                      | Deliverables                         |
| ---------------------- | ------------------------- | ------------------------------------ |
| **Closed Alpha (Web)** | Validate workflow         | Web interface, auth, working backend |
| **Public Beta**        | UX optimisation, feedback | Dashboard, payments, analytics       |
| **Launch (SaaS)**      | Scale & monetise          | Stable SaaS with metrics dashboards  |

---

## 6. Security & Compliance

- OAuth for login (Google sign-in)
- User data encrypted; stored only in Drive
- `/purge` endpoint for full account deletion
- GDPR & CCPA compliant by design

---

## 7. Timeline

```
Month 1–2   Closed Alpha (Web)
Month 3–4   Public Beta + pricing
Month 5–6   Launch (SaaS)
Month 7–12  Optimise cost + analytics
```

---

## 8. Key Metrics

- p50 runtime < 60s
- avg £/run < £0.25
- interview conversion ≥ 25%
- cache hit rate ≥ 50%

---

**End of Web-First Product Specification**
