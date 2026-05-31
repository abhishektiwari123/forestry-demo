# CDP-in-insurance — workflow diagrams

Mermaid diagrams (render natively on GitHub). Companion to `CDP-in-insurance-landscape.md` and `CDP-insurance-use-cases.xlsx`.

## 1. CDP operating loop (insurance)

How data flows through a CDP and back: sources → ingest → identity resolution → unified profile → intelligence → trigger → consent gate → activation → measurement → feedback.

```mermaid
flowchart LR
  subgraph SRC[Data sources]
    A1[Policy admin / PAS]
    A2[Claims]
    A3[Billing / payments]
    A4[Web + quote engine]
    A5[Mobile app]
    A6[Call center / IVR]
    A7[Agents / brokers]
    A8[3rd-party / LexID]
  end
  SRC --> ING[Ingest<br/>real-time + batch]
  ING --> IDR[Identity resolution<br/>deterministic + probabilistic<br/>household · agent-vs-direct]
  IDR --> PROF[(Unified customer profile)]
  PROF --> INT[Intelligence<br/>segments · propensity · churn · CLV · NBA]
  INT --> TRG{Trigger<br/>event or score threshold}
  TRG --> CON{Consent +<br/>governance gate}
  CON -->|allowed| ACT[Activation / orchestration]
  CON -->|blocked| STOP[Suppress]
  ACT --> C1[Email / SMS / WhatsApp]
  ACT --> C2[Web + app personalization]
  ACT --> C3[Push]
  ACT --> C4[Call-center screen pop]
  ACT --> C5[Ad platforms<br/>Customer Match / CAPI]
  C1 --> OUT[Outcomes + measurement<br/>conversion · retention · ROAS · LTV]
  C2 --> OUT
  C3 --> OUT
  C4 --> OUT
  C5 --> OUT
  OUT -. feedback + offline conversions .-> PROF
```

## 2. Quote-abandonment recovery + retargeting flow

The drop-off recovery loop: detect abandon → owned-channel recovery (resume link → escalate → call-center) in parallel with paid retargeting → on bind, fire offline conversion + suppress.

```mermaid
flowchart TD
  V[Visitor starts online quote] --> Q[Quote calculated / viewed]
  Q --> D{Completed / bound?}
  D -->|Yes| BIND[Policy bound]
  D -->|No - abandoned| CAP[CDP captures abandon event + saves quote to profile]
  CAP --> CONS{Consent to contact?}
  CAP --> AUD[Add to retargeting audience<br/>Meta / Google Customer Match]
  CONS -->|No| AUD
  CONS -->|Yes| SMS[SMS deep-link: resume where you left off]
  SMS --> ESC{Engaged?}
  ESC -->|No| WA[Escalate: WhatsApp / email]
  WA --> CALL[Route to call-center<br/>agent briefed on drop-off]
  ESC -->|Yes| RET[Return to funnel]
  CALL --> RET
  AUD --> RET
  RET --> BANNER[On-site personalized resume banner]
  BANNER --> D2{Completes?}
  D2 -->|Yes| BIND
  D2 -->|No| AUD
  BIND --> CAPI[Fire offline conversion via CAPI<br/>train value-based bidding]
  BIND --> SUP[Suppress from acquisition ads]
  BIND --> XS[Onboarding + cross-sell segment]
```
