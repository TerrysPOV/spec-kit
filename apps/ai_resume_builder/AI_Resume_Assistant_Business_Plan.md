# AI Resume Assistant – Business Plan

**Prepared by:** Terry Yodaiken
**Role:** Founder & CEO, POVIEW.AI
**Document type:** Business Plan

---

## 1. Executive Summary

The **AI Resume Assistant** is an intelligent workflow automation product that customises job applications using users' real experience, prior outcomes, and company-specific research. It replaces generic CV tailoring with a personalised, adaptive engine that learns from feedback to improve each application.

The product is initially delivered as a **desktop app** (PoC) and evolves into a full **web-based SaaS** platform. It integrates with Google Drive for data storage, orchestrated by a production-grade **FastAPI + Claude Agent SDK** backend with intelligent multi-model routing for cost optimization. The service will monetise via tiered monthly subscriptions and B2B white-label versions.

Within 24 months, the goal is to reach **5,000+ paying users**, generating **£1.9M ARR** with gross margins above 65% (improved through intelligent model routing). Early validation through Alpha/Beta cohorts will determine conversion, churn, and LTV/CAC ratios to inform scale-up funding.

---

## 2. Market Opportunity

### Addressable Market
- **Target audience:** Mid- to senior-level job seekers, career transitioners, and professionals using LinkedIn/Indeed.
- **Total addressable market (TAM):** ~50M active job seekers in English-speaking markets.
- **Serviceable available market (SAM):** ~2M users adopting AI-driven CV services.
- **Serviceable obtainable market (SOM):** 5,000–20,000 paying users in 2 years via direct channels.

### Competitive Landscape
| Competitor | Focus | Pricing | Gap |
|-------------|--------|----------|------|
| Kickresume | CV builder | £10–£25/mo | No adaptive feedback or research |
| Teal | Job tracking + templates | £10–£20/mo | No personalised tailoring |
| ResumAI / Rezi | AI CV generator | £15–£25/mo | No real-time research or outcome learning |
| AI Resume Assistant | Personalised agent | £19–£49/mo | Outcome learning, company research |

---

## 3. Product & Go-To-Market

### Positioning
**Tagline:** "Smarter applications. Fewer rejections."
**Core message:** Your AI assistant that learns your story and applies it to every role intelligently.

### Go-To-Market Strategy
| Phase | Users | Channel | Notes |
|-------|--------|----------|--------|
| PoC | 100 | LinkedIn DMs, network outreach | Free testers |
| Alpha | 300 | Referral invites | Feedback-for-access model |
| Beta | 1,000 | LinkedIn Ads + content marketing | Paid conversion tracking |
| Launch | 5,000+ | Paid search, affiliates, partnerships | Tiered pricing rollout |

### Pricing & Feature Gates

**Subscription tiers with usage limits:**

| Tier | Monthly (£) | Job Runs/Day | Features |
|------|-------------|--------------|-----------|
| **Starter** | £19 | 1 compose/day | CV + cover letter generation only |
| **Pro** | £49 | 3 composes/day | + Company research + interview brief |
| **Premium** | £99 | Unmetered (fair-use) | + Job tracking + auto-apply + networking insights |

**Feature gate enforcement:**
- **Starter:** Limited to Parser + Composer agents only (no Research agent)
- **Pro:** Full agent pipeline (Parser + Research + Composer + Quality)
- **Premium:** Priority queue + advanced caching + personalized recommendations

**Fair-use policy (Premium):**
- Daily limit: 20 job runs/day (soft cap)
- Monthly limit: 400 job runs/month
- Abuse threshold: >50 runs/day triggers manual review

**ARPU optimization scenarios:**

| Tier | Target Mix | Weighted ARPU | Monthly Cost/User | Gross Margin |
|------|------------|---------------|-------------------|--------------|
| Base Case | 40% Starter, 45% Pro, 15% Premium | £49 | £17 | 65% |
| Conservative | 50% Starter, 40% Pro, 10% Premium | £42 | £15 | 64% |
| Aggressive | 30% Starter, 50% Pro, 20% Premium | £56 | £19 | 66% |

**Pricing telemetry tracking:**
- Daily active users by tier
- Average runs/user/day by tier
- Tier upgrade/downgrade events
- Cost/run by tier (validates pricing assumptions)
- Churn rate by tier

**Margin protection mechanisms:**
- Starter tier: 1 run/day = ~£0.20/day cost = £6/month (68% margin at £19/mo)
- Pro tier: 3 runs/day = ~£0.60/day cost = £18/month (63% margin at £49/mo)
- Premium tier: Fair-use avg 10 runs/day = £2/day = £60/month (40% margin at £99/mo)
- Cost overrun alerts trigger automatic tier re-evaluation

---

## 4. Financial Forecasts (24 Months)

All values in **GBP (£)**.

### Key Assumptions
| Metric | Base Case | Slow Case | Aggressive Case |
|---------|------------|-------------|------------------|
| Starting Users | 1,000 | 1,000 | 1,000 |
| Monthly Growth | 15% | 8% | 25% |
| Monthly Churn | 5% | 8% | 3% |
| ARPU | £49 | £45 | £59 |
| Variable Cost/User | £17 | £15 | £19 |
| Fixed Monthly Cost | £60,000 | £50,000 | £75,000 |

### Summary Forecast Table (Base Case)
| Month | Active Users | Revenue (£) | Profit (£) |
|--------|---------------|--------------|-------------|
| 1 | 1,000 | 49,000 | -11,000 |
| 6 | 1,949 | 95,501 | 14,021 |
| 12 | 3,799 | 186,151 | 57,163 |
| 18 | 7,405 | 352,844 | 137,788 |
| 24 | 14,431 | 707,119 | 342,962 |

**Breakeven:** Month 10–12 (Base Case)

### Sensitivity Analysis
| Scenario | Revenue @ 24mo (£) | Profit (£) | Breakeven |
|-----------|---------------------|-------------|-----------|
| Slow (8% growth, 8% churn) | 382,000 | -48,000 | >24mo |
| Base (15% growth, 5% churn) | 707,000 | 343,000 | 11mo |
| Aggressive (25% growth, 3% churn) | 1,590,000 | 890,000 | 7mo |

### ASCII Revenue Projection (Base Case)
```
£k
800 |                                ▇
700 |                              ▇▇▇
600 |                             ▇▇▇▇
500 |                          ▇▇▇▇▇▇
400 |                       ▇▇▇▇▇▇▇▇
300 |                    ▇▇▇▇▇▇▇▇▇▇
200 |                ▇▇▇▇▇▇▇▇▇▇▇▇▇
100 |          ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇
    -------------------------------------------------
     1   6   12   18   24 (Months)
```

---

## 5. Operating Assumptions
| Category | Detail |
|-----------|---------|
| LLM cost (blended) | £0.012 per 1k tokens (intelligent routing: 60% small models, 40% frontier) |
| Avg tokens per run | 15k |
| Cost per job run | £0.18–£0.25 (target: £0.20 with caching) |
| Caching benefit | 50% reduction on cached prompts (manifest, company data) |
| Users per month | 1–5 job runs average |
| Marketing spend | 20% of monthly revenue |
| Team cost | £40k–£60k/month (founders + engineers + infra) |
| Hosting | £1.5k/month (Render + DB + Qdrant + Redis) |
| Payment processor fee | 3% |

**Cost Optimization Strategy:**
- **Parser Agent**: GPT-4o-mini/Gemini Flash (£0.005/1k tokens) - 30% of tokens
- **Research Agent**: Perplexity/smaller models (£0.01/1k tokens) - 30% of tokens
- **Composer Agent**: Claude 3.5-4.5 Sonnet (£0.015/1k tokens) - 40% of tokens
- **Caching**: 50% cost reduction on repeated CV/company data
- **Result**: £0.20/run average vs £0.30 with single-model approach

**Cost per tier breakdown:**

| Tier | Avg Runs/Day | Monthly Runs | Cost/Month (£0.20/run) | Revenue | Margin |
|------|--------------|--------------|------------------------|---------|---------|
| Starter | 1 | 30 | £6 | £19 | 68% |
| Pro | 3 | 90 | £18 | £49 | 63% |
| Premium | 10 (fair-use avg) | 300 | £60 | £99 | 39% |

**Margin protection:**
- Real-time cost tracking per user
- Automatic tier re-evaluation if usage exceeds projections
- Premium fair-use enforcement (20 runs/day soft cap)
- Circuit breaker on high-cost users (>£5/day)

---

## 6. Key Metrics & Milestones

### Performance KPIs
| KPI | Target |
|-----|---------|
| CAC Payback | < 2 months |
| Gross Margin | > 60% |
| LTV/CAC | > 3.5 |
| DAU/MAU | > 30% |
| NPS | > 30 |

### Milestone Timeline
```
Month 1–2   PoC launch, 100 users
Month 3–4   Alpha, Drive + telemetry integration
Month 5–6   Beta, web dashboard + payments
Month 7–9   Public launch, 1k–5k users
Month 10–12 Monetisation + partnership pipeline
Month 12+   Scale & automate marketing channels
```

---

## 7. Risk & Mitigation Summary
| Risk | Impact | Mitigation |
|-------|---------|-------------|
| Slow adoption | Medium | Free PoC cohort + referral growth |
| LLM cost volatility | Medium | Multi-model routing + caching + token budgets |
| LLM provider outages | Low | Multi-provider fallback (Anthropic → OpenRouter → alternatives) |
| Agent orchestration complexity | Low | Claude SDK abstracts complexity, comprehensive testing |
| Compliance/PII risk | High | Google Drive storage only, hashed telemetry |
| Competitive saturation | Medium | Focus on adaptive feedback + research edge |
| Funding gap | Medium | Bootstrap until positive unit economics |
| Premium tier margin erosion | Medium | Fair-use enforcement + real-time cost monitoring |

---

## 8. Funding Outlook (Optional)
- **Pre-seed requirement:** £250k to scale from Alpha → Beta.
- **Use of funds:** Infra scaling (25%), team expansion (50%), marketing (25%).
- **Runway:** ~12 months at base burn rate (~£60k/month).

---

**End of Document**
