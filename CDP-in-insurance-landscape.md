# Customer Data Platforms (CDP) in Insurance — A Global Landscape

*Research report · compiled 2026-05-31 · scope: successful CDP deployments and use cases at major insurers worldwide · vendor-agnostic with extra attention to Salesforce Data Cloud.*

---

## Method & evidence caveat

This report was produced by fanning out parallel web-research sweeps (Salesforce-focused, Europe, North America, Asia-Pacific, and cross-cutting patterns), followed by a verification pass that cross-checked the highest-stakes claims against independent sources.

Two limitations shape how much to trust each figure:

1. **Page-level fetching was blocked in the research environment**, so findings rest on search-result extracts of the underlying pages rather than full-text reads.
2. **Most published CDP-in-insurance ROI figures are vendor-sourced** (self-reported case studies). Each claim below is labeled by source type, and corroboration by an independent outlet is noted where it exists.

A definitional discipline runs throughout: a **CDP** is a packaged software platform that unifies first-party customer data into persistent profiles for marketing/CX activation. Customer-relationship management (CRM), master data management (MDM), and cloud data warehouses are **excluded** even when insurers market them as "customer 360" or "data platform."

---

## Executive summary

- **Real, named CDP deployments at big insurers are rarer than the marketing noise suggests.** Much insurer "CDP" press is actually CRM (Salesforce Service/Marketing Cloud), MDM (Reltio), or a data warehouse (Snowflake/Databricks).
- **Best-documented deployments cluster in two pockets:** (1) Singapore + India + SEA, dominated by specialist CDPs **Lemnisk** and **Tealium**; and (2) a few Western flagships — **Prudential (Adobe), Legal & General (Tealium), USAA (Tealium)**.
- **Tealium and Lemnisk — not the household-name platforms — power most confirmable insurer CDPs.** Salesforce Data Cloud is *emerging* in insurance (via "FSC for Insurance Brokerages") but has thin proven-ROI evidence so far.
- **The single most metric-rich, independently-recognized case is Income Insurance (Singapore) on Tealium:** +452% online-generated revenue YoY, –40% cost-per-acquisition, +92% CTR — and it won a Drum Award.
- **Hard, independent ROI is essentially absent.** The only independent economics are McKinsey's personalization figures (~50% lower acquisition cost, 5–10% revenue lift), which describe personalization broadly, not "the CDP."

---

## 1. What insurers use a CDP for

| Use case | Business problem it solves |
|---|---|
| Unified profile / single customer view (360) | Data fragmented across policy admin, CRM, claims, billing, web/app, call center — and siloed per line of business. |
| Cross-sell / next-best-product | Insurers under-monetize their book; an auto customer is never offered home/life because the signal is trapped in another silo. |
| Retention / churn prevention | A renewal-driven model means churn hits revenue directly; at-risk signals aren't seen early enough. |
| Omnichannel personalization | Generic web/app/email converts poorly; "quote-and-bounce" behavior goes unaddressed. |
| Lead scoring & acquisition efficiency | High customer-acquisition cost; spend wasted on poor leads; quote/eKYC drop-offs. |
| Cookieless first-party activation | Third-party cookie deprecation threatens digital acquisition; insurers need first-party identity. |
| Consent-governed activation | Must personalize while honoring GDPR/CCPA/GLBA with granular, auditable, real-time consent. |

---

## 2. The deployments — global landscape

### At a glance

| Insurer | Region | CDP platform | Headline outcome (source type) | Confidence |
|---|---|---|---|---|
| Income Insurance | Singapore | Tealium | +452% online revenue, –40% CPA, +92% CTR (vendor + Drum Award) | ★★★ Strong |
| Prudential Financial | US | Adobe Real-Time CDP | +135% engagement lift (vendor + independent press) | ★★★ Strong |
| Legal & General | UK | Tealium + Snowflake | +54% call-to-lead, +15% conversion (vendor, on newswires) | ★★★ Strong |
| AIA Singapore | Singapore | Lemnisk | +63% lead-gen growth, 2.3× CTR (vendor + Forrester ref) | ★★☆ Solid |
| Generali | EU/global | Zeta & Insider | +24% close rate; 3× leads, +25% LTV (vendor) | ★★☆ Solid |
| Etiqa | Malaysia/SG | Insider | 4.74% vs 2.17% conversion (vendor) | ★★☆ Solid |
| USAA | US | Tealium | Data latency 1 hr → <30 sec (vendor) | ★★☆ Solid |
| Partenamut | Belgium | Tealium | +16.6% email CTR (vendor + integrator) | ★★☆ Solid |
| Aegon Life | India | Lemnisk | +19% website conversions (vendor, syndicated) | ★★☆ Solid |
| AIA Philam Life | Philippines | Lemnisk | Qualitative (vendor PR) | ★★☆ Solid |
| Royal Sundaram / Tata AIA | India | Lemnisk | Conversions lifted (vendor) | ★★☆ Solid |
| Baldwin Group, AssuredPartners | US | Salesforce Data Cloud (via FSC for Brokerages) | Qualitative (vendor PR) | ★☆☆ Emerging |
| IAG / NRMA | Australia | Adobe Experience Cloud | Announced Oct 2025, CDP product not named, no results yet | ★☆☆ Announced |
| NN Group | Netherlands | BlueConic | None disclosed (~2015, thin source) | ★☆☆ Weak |

### Tier 1 — Strongest cases

**Income Insurance (NTUC Income), Singapore — Tealium AudienceStream.** Implemented by agency Merkle; built a 360° single customer view and reported +452% online-generated revenue YoY, –40% cost-per-acquisition, +92% CTR, and higher early online renewals (car 44%→72%, motorcycle 52%→68%). Won 'Brilliant Use of Data/Insight' at The Drum Awards for Marketing APAC 2023 — meaningful independent recognition.

**Prudential Financial, US — Adobe Real-Time CDP.** The "Prudential Personalization Platform" runs on Adobe Real-Time CDP atop Adobe Experience Platform (with AEM, Target, Marketo), unifying profiles to personalize journeys for consumers, advisors and employers. Adobe's 2025 Summit cites a 135% engagement lift in under 30 days (via Adobe Target). Independently echoed by MediaPost.

**Legal & General, UK — Tealium + Snowflake.** L&G Retail built a "marketing data zone"/single customer view on Tealium AudienceStream integrated with Snowflake — zero-party data capture, predictive models, real-time call-center routing, abandoned-application intervention. Reported +54% call-to-lead conversion and +15% banner conversion. Distributed via newswires (GlobeNewswire, Aug 2025).

**AIA Singapore — Lemnisk.** Defined 30 CDP use cases; reported 63% growth in lead generation and 2.3× CTR uplift. Corroborated as a CDP example by Marketing-Interactive citing a Forrester study.

### Tier 2 — Solid but vendor-sourced

- **Generali (Europe/global)** runs two CDPs in different markets: Zeta Global (+24% close rate) and Insider (3× leads, 20% faster sales cycle, +25% LTV).
- **Etiqa (Malaysia/Singapore)** — Insider: conversion 4.74% vs 2.17% average.
- **USAA (US)** — Tealium AudienceStream + EventStream: cut data latency from ~1 hour to <30 seconds for fraud/intent use cases.
- **Partenamut (Belgium)** — Tealium: +16.6% email CTR, corroborated by integrator MultiMinds.
- **India life insurers on Lemnisk** — Aegon Life (+19% website conversions, syndicated to Business Standard), Royal Sundaram, Tata AIA (vendor-listed). AIA Philam Life (Philippines) — Lemnisk, qualitative.

### Tier 3 — Emerging, announced, or weakly sourced

- **The Baldwin Group & AssuredPartners (US)** adopted Salesforce's "Financial Services Cloud for Insurance Brokerages," which embeds Data Cloud — vendor PR, no isolated ROI.
- **IAG / NRMA (Australia)** announced an Adobe Experience Cloud partnership (Oct 2025) for a unified customer view — but sources don't explicitly name Adobe Real-Time CDP, and there are no results yet.
- **NN Group / Nationale-Nederlanden (Netherlands)** — BlueConic (~2015); only a tech-spend tracker as evidence. Treat as unconfirmed.

---

## 3. Salesforce Data Cloud in insurance

Salesforce's insurance presence is huge — but mostly CRM, not CDP.

- **Genuinely Data Cloud (the CDP):**
  - The Baldwin Group, AssuredPartners — via *FSC for Insurance Brokerages* (Data Cloud-powered client profiles). Vendor PR, no measured ROI yet.
  - Prudential — important nuance: Salesforce's own customer story says Prudential "already has a single platform anchored by Financial Services Cloud, and *in the future, Data Cloud*." So Data Cloud is **planned, not yet live** at Prudential; the live Salesforce deployment is **Agentforce** (agentic AI for retirement-strategy wholesalers, projected to save ~½ day/week) on Financial Services Cloud + third-party data lakes. (Prudential's live *CDP* is Adobe's.)
- **Frequently mis-attributed to Data Cloud — actually CRM/Marketing Cloud:** Farmers (Service Cloud; the "75% faster loss reporting" is a Service Cloud result), AXA (Service Cloud + MuleSoft), Allianz Direct (Marketing Cloud + Personalization), Manulife/John Hancock, State Farm, Sun Life, Tokio Marine, Prudential Singapore (Customer 360 + Marketing Cloud), Humana (Health Cloud). None are confirmable Data Cloud/CDP wins.
- **A debunked claim:** an SEO aggregator lists Highmark as a Data Cloud customer, but independent reporting shows Highmark's member platform runs on Google Cloud + League, not Salesforce.

**Bottom line:** Data Cloud is the analyst-anointed market leader (below) and is clearly moving into insurance via the brokerage product, but its proven, metric-backed insurer deployments currently lag Tealium's and Lemnisk's.

---

## 4. Vendor landscape

**Analyst rankings (cross-industry, not insurance-specific):**
- **2026 Gartner Magic Quadrant for CDPs:** Salesforce positioned as a Leader (characterized by CXToday as the sole *returning* Leader); Oracle, Uniphore, and Hightouch new to the quadrant (Oracle and Uniphore announced Leader placement); Adobe the sole Visionary; Tealium dropped Leader → Challenger, joining Treasure Data as Challengers; ActionIQ, Redpoint, mParticle, and Zeta Global dropped off entirely. Gartner frames a "platformization vs. agentification" split, arguing regulated industries benefit from platformization with enforced consent.
- **Forrester Wave B2C CDPs, Q3 2025:** Treasure Data named a Leader.

**Who actually shows up in insurance (practitioner reality):**
- **Tealium** — dominates confirmable Western insurer deployments (Income, L&G, USAA, Partenamut).
- **Lemnisk** — dominates India/SEA insurer deployments (AIA Singapore, AIA Philam, Aegon, Royal Sundaram, Tata AIA); positions explicitly as a BFSI/insurance CDP.
- **Insider** — strong in personalization-led cases (Generali, Etiqa, Allianz).
- **Adobe Real-Time CDP** — Prudential; IAG (announced).
- **Salesforce Data Cloud** — emerging via FSC for Insurance Brokerages.
- **Other FS/insurance specialists:** Celebrus (D4T4), NGDATA, FirstHive, BlueConic, Hightouch (composable/warehouse-native; e.g., The Zebra +170% match rate).

---

## 5. ROI reality check

| Figure | Source | Trust level |
|---|---|---|
| Personalization → ~50% lower acquisition cost, 5–10% revenue lift, 5–10× marketing ROI | McKinsey | Independent — but about personalization broadly, not "the CDP" |
| Income Insurance +452% online revenue | Tealium/Merkle + Drum Award | Vendor + independent award |
| L&G +54% call-to-lead; AIA SG +63% leads; Generali +24% close; Etiqa 4.74%; Aegon +19% | Respective vendors | Vendor-sourced, single-client |
| "802% ROI" | Forrester TEI commissioned by Treasure Data (2019) | Discount — composite, non-insurance, 6+ years old |
| "36% higher cross-sell / 28% better retention," "55% of BFSI use CDPs" | Marketing blogs | Untraceable to a primary source — don't cite |

There is no rigorous, independent, insurance-specific CDP ROI benchmark.

---

## 6. Why CDP deployment is hard in insurance

- **Legacy core / policy-admin systems** — claims and billing data trapped in systems modern tools can't easily reach. The #1 practical blocker.
- **Line-of-business silos** — auto/home/life/health each with its own stack → missed cross-sell, inconsistent experience.
- **Regulation + consent** — overlapping regimes (GDPR, CCPA, GLBA, PIPEDA); consent must be granular, auditable, and enforced in real time at every activation.
- **Identity resolution at enterprise scale** — wrong stitching corrupts every segment and personalization.
- **Agent/broker vs. direct channels** — an under-documented identity problem; insurers often don't "own" the end-customer relationship the way a D2C brand does.

---

## 7. What to trust vs. discount

- **Trust:** McKinsey's personalization economics (independent); the *structure* of Gartner/Forrester rankings; Income Insurance/Tealium (independent award); Prudential/Adobe (independent press).
- **Treat as directional:** all single-client vendor lift figures (Generali, Etiqa, AIA SG, L&G, Aegon).
- **Discount/discard:** the Forrester "802%" as an insurance number; "36%/28%/55%" benchmark-blog stats; any "Salesforce + insurer = Data Cloud" assumption (mostly CRM); the Highmark Data Cloud claim (it's Google Cloud/League).
- **Biggest myth busted:** that household-name CDPs power most insurer deployments. In practice, Tealium and Lemnisk — plus Adobe at Prudential — carry the best-evidenced insurance CDP stories, while Salesforce Data Cloud is still early in insurance despite leading the analyst quadrant.

---

## Sources (selected)

**Strongest cases**
- Income Insurance / Tealium: https://tealium.com/resource/case-study/income-insurance-limited-forges-the-future-of-insurance-cx-with-tealium-cdp/ · Merkle/Dentsu: https://www.dentsu.com/sg/en/our-work/merkle-singapore-income-insurance · The Drum: https://www.thedrum.com/news/2023/05/30/singaporean-broker-income-insurance-united-its-distant-data-silos-heres-how
- Prudential / Adobe: https://blog.adobe.com/en/publish/2023/03/31/prudential-financial-collaborates-with-adobe-deliver-personalized-financial-experiences · Adobe Summit 2025: https://business.adobe.com/summit/2025/sessions/aipowered-personalization-prudentials-secret-s530.html · MediaPost: https://www.mediapost.com/publications/article/383938/adobe-ai-tech-for-prudential-financial-means-perso.html
- Legal & General / Tealium: https://tealium.com/resource/case-study/legal-general-transforms-customer-engagement-through-real-time-data-and-insight/ · GlobeNewswire: https://www.globenewswire.com/news-release/2025/08/12/3131444/0/en/legal-general-taps-tealium-snowflake-to-accelerate-ai-powered-cx-and-business-growth.html
- AIA Singapore / Lemnisk: https://www.lemnisk.co/ · Marketing-Interactive: https://www.marketing-interactive.com/sea-greater-china-hottest-cdp-markets

**Solid (vendor-sourced)**
- Generali / Zeta: https://zetaglobal.com/resource-center/how-generali-leveraged-ai-based-website-individualization-to-increase-close-rates-by-24/ · Generali / Insider: https://useinsider.com/case-studies/generali/
- Etiqa / Insider: https://insiderone.com/cdp-for-insurance/
- Partenamut / Tealium: https://tealium.com/resource/case-study/the-foundations-of-a-long-term-marketing-strategy/ · MultiMinds: https://www.multiminds.eu/case/partenamut
- Aegon Life / Lemnisk: https://www.prnewswire.com/news-releases/aegon-life-boosts-website-conversions-with-lemnisks-customer-data-platform-300878403.html
- AIA Philam Life / Lemnisk: https://www.cdpinstitute.org/resources/aia-philippines-accelerates-digital-transformation-with-lemnisks-customer-data-platform/

**Salesforce Data Cloud**
- Prudential / Salesforce: https://www.salesforce.com/customer-stories/prudential/ · diginomica: https://diginomica.com/ai-and-financial-services-how-prudential-insurance-putting-humans-and-agents-work-agentforce-better · Prudential newsroom: https://news.prudential.com/latest-news/feature-stories/feature-stories-details/2025/Prudential-explores-the-art-of-the-possible-with-agentic-AI-/default.aspx
- FSC for Insurance Brokerages: https://www.salesforce.com/news/stories/financial-services-cloud-for-insurance-brokerages/

**Announced / weak / excluded**
- IAG / Adobe: https://www.iag.com.au/newsroom/innovation/iag-partners-with-adobe · https://www.insurancebusinessmag.com/au/news/technology/iag-and-adobe-team-up-for-personalised-insurance-growth-554189.aspx
- Aviva / Reltio (MDM, excluded): https://www.reltio.com/resources/press-releases/multinational-insurer-aviva-goes-live-with-reltio-data-cloud-for-real-time-data-intelligence-to-personalize-customer-experiences/
- AXA / Snowflake (data platform, excluded): https://www.snowflake.com/en/customers/all-customers/case-study/axa/

**Vendor landscape & ROI**
- Gartner MQ 2026 (CXToday): https://www.cxtoday.com/customer-analytics-intelligence/gartner-magic-quadrant-cdp-2026/ · Salesforce: https://www.salesforce.com/data/gartner-magic-quadrant-cdp-2026/ · Oracle: https://www.oracle.com/cx/marketing/gartner-mq-customer-data-platforms/
- McKinsey personalization: https://www.mckinsey.com/industries/financial-services/our-insights/how-traditional-insurance-carriers-can-disrupt-through-personalized-marketing
- CDP Institute (FS & insurance): https://www.cdpinstitute.org/resourcesindustry/financial-services-and-insurance/

*Note: most quantitative figures are vendor-sourced marketing unless an independent corroborating outlet is listed. Figures were extracted from search-result summaries; for citation-grade verbatim quotes, the primary URLs above should be retrieved through an unblocked browser or scraper.*

---

# Part II — Operational use-case catalog (deep dive)

*Added from a second research wave (five parallel use-case-focused sweeps). Every metric is labeled by source quality; vendor case-study numbers are self-reported unless an independent outlet is noted.*

## How a CDP runs operationally

The loop: **ingest → resolve identity → score/segment → trigger → activate → measure → feed back.** Three things make the insurance version distinctive:

1. **Identity resolution must solve agent-vs-direct.** A lead arrives via agent, web self-serve, aggregator, or social; the CDP stitches them so suppression/attribution work regardless of channel. LexisNexis **LexID** (household-level, ~2.3B records) is the real workhorse, often augmenting the CDP.
2. **The sale closes offline, days later** — so the high-leverage tactic is the **offline-conversion feedback loop**: fire `bound-policy` + value back to Meta CAPI / Google Enhanced Conversions for Leads so value-based bidding optimizes to real policies, not clicks.
3. **Consent must be enforced, not just captured.** Client-side tags can't be trusted to honor opt-outs (healthcare paid $100M+ in pixel-tracking fines since 2023; FTC is expanding GLBA reach). CDPs evaluate each event server-side against purpose rules + the Global Privacy Control signal and block non-compliant events before activation.

## Catalog by lifecycle stage

**1. Acquisition & paid media** — retargeting on hashed first-party audiences (Google Customer Match / Meta / TikTok / LinkedIn); suppression of current customers (fastest ROI; "10–20% budget waste" is vendor-repeated/uncorroborated); high-LTV/multi-policy lookalike seeds; cookieless/UID2 on The Trade Desk; offline-conversion loop via CAPI / Enhanced Conversions for Leads; lead scoring + speed-to-lead. *Toggle (Farmers) / Twilio Segment: –67% CPA. Insurance Choice / Optilead: connect ~1 min → +150% policies, ~80% abandoned quotes connected.* Contact within 60s → +391% conversion (Velocify). Independent anchor: Velocify audit of 25 carriers — 2.3-day avg callback, ~40% never called.

**2. Drop-off / abandonment recovery** — quote (≈84% abandon; second spike at price reveal), application, eKYC, checkout, renewal. Mechanic: detect funnel step → SMS deep link → "resume where you left off" with prefilled data → escalate SMS (~42 min) → WhatsApp → voice. *L&G (Tealium+Snowflake): abandoners routed to a briefed agent → +54% call-to-lead, +15% completions. Generali (Insider): –17% eKYC drop-offs.* Checkout recovery for high-value carts = immediate human call.

**3. Onboarding & activation** — welcome journeys, OTP-assisted purchase completion, app install/engagement. *AIA Singapore (Lemnisk): +63% lead gen; AIA Philam Life: digital-onboarding pilot.*

**4. Cross-sell / upsell / next-best-product** — life-event/milestone triggers (new home, marriage, child, anniversary, maturing deposit), cross-LOB (auto→home→life→health), agent/RM copilot with live recs. Act on demonstrated intent. Realistic cross-sell ML ≈75% accuracy (the "0.99" claims = likely leakage); Insider's "85% save / 27% upsell" triple is unattributed.

**5. Retention / renewal / churn / win-back** — offline→online renewal migration; predictive churn scored 30–60 days pre-renewal on rate-shopping/competitor-quote/claim-dissatisfaction signals; risk-tier→NBA retention engine (NGDATA). *Income Insurance: car early-online renewal 44%→72%, motorcycle 52%→68% (best operational metric). Liberty Mutual: +15% retention via predictive segmentation (3rd-party-sourced).* Win-back/lapsed is thinly evidenced.

**6. Personalization & decisioning** — on-site/app individualization (recently-viewed, behavior-driven banners); NBA arbitration via Pega's **P×C×V×L** (Propensity×Context×Value×Levers), Salesforce Einstein/Agentforce, Adobe Journey Optimizer; channel-propensity + Send-Time Optimization. *Generali/Zeta: +24% close rate; Prudential/Adobe: +135% engagement <30 days; Etiqa/Insider: 4.74% vs 2.17%; Aegon Life/Lemnisk "Ramanujan": +19% web conv.*

**7. Claims & service** — sub-100ms contact-center screen pops (Tealium → Amazon Connect/Diabolocom) with active-claim status before pickup; intent-based routing; proactive status comms + post-settlement NPS + de-escalation; fraud signals. *USAA (Tealium EventStream): real-time fraud signals, latency 1hr→<1s (anecdotal, no fraud-$ metric). ForMotiv behavioral biometrics: agent quote-manipulation –18%.*

**8. Member/app engagement & wellness** — *John Hancock Vitality (wearables + points + premium discounts): 20+ engagements/month, Apple Watch users 7× more engaged, ~90% earned premium savings — **company-direct + independent Conference Board corroboration** (strongest independent engagement data).* Same model underpins AIA's "Healthier, Longer, Better Lives."

**9. Bancassurance / embedded** — partner (bank) data pre-fills the application. *Chubb Studio via DBS app; Nubank Vida 560k+ active policies* — note Chubb Studio is an embedded-insurance API platform, not a CDP.

**10. Consent / governance** — centralized opt-in/out, DSARs, suppression lists, audit logs, server-side opt-out propagation downstream, do-not-call/channel-specific rules. GLBA (opt-out + ban on sharing account numbers for marketing), PIPEDA (meaningful consent).

## Consolidated named-deployment table (deep dive)

| Insurer | Region | Stack | Use case | Metric | Evidence |
|---|---|---|---|---|---|
| Income Insurance | SG | Tealium+Merkle | Offline→online renewal | renewal 44→72%, –40% CPA, +452% online rev | Vendor + Drum Award |
| Legal & General | UK | Tealium+Snowflake | Abandoned-app recovery | +54% call-to-lead, +15% completions | Vendor (newswires) |
| Prudential | US | Adobe RT-CDP | Personalization at scale | +135% engagement <30 days | Vendor + indep. press |
| Generali (A) | EU | Zeta | Website individualization | +24% close rate | Vendor |
| Generali (B) | EU | Insider | Lead scoring / eKYC | 3× leads, –17% eKYC drop-off | Vendor — do not merge with A |
| Etiqa | MY/SG | Insider | Banner personalization | 4.74% vs 2.17% | Vendor |
| AIA Singapore | SG | Lemnisk | Lead gen / app | +63% leads, 2.3× CTR | Vendor |
| Aegon Life | IN | Lemnisk | Channel propensity | +19% web conv | Vendor PR |
| nib | AU | Tealium | Unified profiles | +175% marketable leads | Vendor |
| USAA | US | Tealium | Real-time fraud signals | latency 1hr→<1s | Vendor anecdote |
| Toggle (Farmers) | US | Twilio Segment | Retargeting / lookalikes | –67% CPA | Vendor |
| The Zebra | US | Hightouch+Snowflake | Conversion enrichment | +170% FB match, +50% email CTR | Vendor |
| Liberty Mutual | US | unspecified | Predictive retention | +15% retention | 3rd-party |
| Insurance Choice | UK | Optilead | Speed-to-lead | +150% policies | Vendor |
| John Hancock | US | Vitality+wearables | Engagement / wellness | 20+/mo, Apple Watch 7× | Company + Conference Board |
| Sedgwick | US | MS Sidekick | Agentic claims | +30% efficiency | Vendor |

## What's real vs. marketing
- **Most credible:** John Hancock Vitality (independent corroboration); Income Insurance's operational renewal-rate shifts; the Velocify carrier audit (proves insurers execute speed-to-lead poorly).
- **Quarantined:** the flashiest "propensity routing → call center" numbers (57.97%, 58%, 2× contactability) are **telco/banking**, not insurers; a "Geico –20% cost-per-quote" claim with no primary source (likely fabricated).
- **Generali caveat:** Insider and Zeta both claim Generali with non-overlapping metrics — different regional units; never aggregate.
- **Under-evidenced if pitched:** win-back/lapsed-policy and bancassurance-CDP.

### Additional source URLs (Part II)
- Lemnisk insurance use cases: https://www.lemnisk.co/blog/cdp-use-cases-for-insurance/ · https://www.lemnisk.co/ramanujan/
- Tealium: contact centers https://tealium.com/tealium-for-contact-centers/ · L&G https://tealium.com/resource/case-study/legal-general-transforms-customer-engagement-through-real-time-data-and-insight/ · consent https://docs.tealium.com/consent/consent-overview/
- Insider Generali: https://useinsider.com/case-studies/generali/ · Zeta Generali: https://zetaglobal.com/resource-center/how-generali-leveraged-ai-based-website-individualization-to-increase-close-rates-by-24/
- Twilio Segment Toggle: https://segment.com/customers/toggle/ · Hightouch The Zebra: https://hightouch.com/customers/the-zebra
- Optilead Insurance Choice: https://www.optilead.co.uk/case-studies/insurance-choice/ · Velocify carrier study: https://www.prnewswire.com/news-releases/biggest-insurance-companies-keep-their-customers-waiting-velocify-study-finds-258281391.html
- Pega NBA arbitration: https://academy.pega.com/topic/action-arbitration/v3 · Salesforce Agentforce: https://www.salesforce.com/news/stories/how-data-cloud-powers-agentforce/
- John Hancock Vitality (company): https://www.johnhancock.com/about-us/newsroom.html · Conference Board (independent): https://www.conference-board.org/research/economy-strategy-finance-briefs/John-Hancock-Customer-Engagement-Increase
- Chubb Studio embedded: https://about.chubb.com/stories/banks-and-the-digital-wallet-race-the-embedded-insurance-strategy.html
- LexisNexis LexID for insurance: https://risk.lexisnexis.co.uk/products/lexid-for-insurance · GLBA (FTC): https://www.ftc.gov/business-guidance/resources/how-comply-privacy-consumer-financial-information-rule-gramm-leach-bliley-act
