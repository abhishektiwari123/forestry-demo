#!/usr/bin/env python3
"""GE Stream 3 CDP use-case bank, v2 (post-review). Stdlib-only .xlsx."""
import math, zipfile

def esc(s):
    s = "" if s is None else str(s)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def col_letter(i):
    s = ""
    while i:
        i, r = divmod(i - 1, 26); s = chr(65 + r) + s
    return s

def est_height(values, widths):
    lines = 1
    for v, w in zip(values, widths):
        v = "" if v is None else str(v)
        lines = max(lines, math.ceil((len(v) + 1) / max(w - 1, 6)))
    return round(min(lines, 26) * 14.6 + 5, 1)

def sheet_xml(rows, widths):
    n_cols, n_rows = len(widths), len(rows)
    cols = "".join(f'<col min="{i+1}" max="{i+1}" width="{w}" customWidth="1"/>' for i, w in enumerate(widths))
    body = []
    for r, row in enumerate(rows, start=1):
        style = 1 if r == 1 else 2
        ht = 30 if r == 1 else est_height(row, widths)
        cells = "".join(f'<c r="{col_letter(c)}{r}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{esc(v)}</t></is></c>' for c, v in enumerate(row, start=1))
        body.append(f'<row r="{r}" ht="{ht}" customHeight="1">{cells}</row>')
    dim = f"A1:{col_letter(n_cols)}{n_rows}"
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            f'<dimension ref="{dim}"/><sheetViews><sheetView workbookViewId="0">'
            '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
            '<selection pane="bottomLeft" activeCell="A2" sqref="A2"/></sheetView></sheetViews>'
            f'<sheetFormatPr defaultRowHeight="15"/><cols>{cols}</cols><sheetData>{"".join(body)}</sheetData>'
            f'<autoFilter ref="{dim}"/></worksheet>')

# ===== Sheet 1: Read me and change log =====
rd_h = ["Item","Detail"]
rd_w = [34,96]
rd = [
 ["What this is","Great Eastern Stream 3 CDP business use-case bank, version 2.1. Plain-English business use cases for B1, B3, C3, re-structured after the working-team review and aligned to the Project Clearwater GE journey. This is the bank that everything downstream is built on (Data Cloud mapping, then prioritization, then the SI build)."],
 ["What changed in v2 (structure rebuild)",""],
 ["1. Re-staged to the GE end-to-end journey","Replaced the generic funnel stages (paid media, landing page, form, payment, onboarding) with the GE January end-to-end journey: outreach, awareness, exploration, quotation, KYC, eligibility check, payment, issuance, post-purchase, claims management. Outreach was added before awareness to hold paid and own media."],
 ["2. Two-tier structure","Added a Tier column. Journey-level use cases sit on a stage; foundational use cases are the always-on CDP enablers that underpin every stage. Ten foundational use cases were added from the MSB enabler layer; the former cross-cutting rows (frequency capping, propensity retrain, consent) were folded into the foundational tier."],
 ["3. Use-case group tag","Added a use-case group column using the MSB taxonomy (acquisition, onboarding, engagement, retention, cross-sell / upsell, channel execution, data enablement). Applied best-fit; will align to the official grouping when the team sends it."],
 ["4. End-to-end coverage","Added eligibility and claims use cases so no GE journey stage is empty."],
 ["What was kept (validated in the review)","The columns, especially how the stack helps, the funnel or value metric, the business KPI, and how it makes money. The plain-English business framing for an SI audience. The B1 / B3 / C3 mapping; the three client objectives (enforced, new business acceleration, retention) are already covered by these three journeys."],
 ["What is deliberately NOT here yet",""],
 ["Data Cloud feature mapping","Deferred to the next stage, owned by Jose and Nerea. This bank is the business-English hurdle before the tool mapping."],
 ["The how (integrations, settings)","SI scope. We define the what; the SI defines the how."],
 ["Prioritization","Comes after Data Cloud mapping, scored against the three journeys, the MarTech backlog, and what Data Cloud actually supports. Anything Data Cloud cannot support drops automatically at that stage."],
 ["What changed in v2.1 (this version)",""],
 ["Stages aligned to the GE Project Clearwater slide","Merged payment and issuance into one stage (payment / policy issuance) to match the GE journey; the eight GE stages are now awareness, exploration, quotation, KYC, eligibility check, payment / policy issuance, post-purchase servicing, claims management. Outreach is retained before awareness to hold paid and own media; flagged as a Clearwater addition."],
 ["Added Rose and Skybranch as journey-wide layers","Rose (the Gen-AI chatbot running across the journey) and Skybranch (assisted support across the journey) are added as foundational use cases, since the slide shows both as throughout-journey layers, not single-stage steps."],
 ["Added CDP-relevant signature moments","Itemised the Clearwater signature moments that the CDP genuinely drives: future-self / needs-assessment to 8 segments and model portfolio, modular quote with save-for-later, vulnerability and competency capture, pre-qualified eligibility, medical-document reuse, AI scam scan, marketing-consent capture (planted-tree reward), personalized policy snapshot and benefits video, wellness-to-reduce-premium. Pure experience and ops features (digital-avatar dialogue, one-day reimbursement, in-app camera capture) are noted as GE journey features the CDP supports but does not own."],
 ["Pending inputs to finalize v3",""],
 ["Official MSB use-case grouping","The roughly seven groups, to replace the best-fit tags in column B."],
 ["MSB 29 use cases + Word enabler doc","To add any obvious missing use cases and enabler layers."],
 ["MarTech backlog","To run the 80 to 90 percent comprehensiveness check the client will ask about."],
 ["Counts","75 use cases total: B1 15, B3 19, C3 17, GE signature and shared 12, foundational 12."],
]

# ===== Sheet 2: Journeys overview =====
ov_h = ["Journey","Name","Sourcing","Conversion","One-line definition","Why it matters","Scope boundary (sequencing)"]
ov_w = [9,28,18,16,42,34,36]
ov = [
 ["B1","Marketing-led, converted digitally","Marketing-led","Digital (no FA)","Prospect acquired via paid or organic media; completes purchase fully digitally with no advisor touch","Cleanest test of digital-only economics; about 2 to 3 percent web-to-sale","Out of scope: FA conversation, Great Planner, education and retention plays, data-science leads"],
 ["B3","Marketing-led, converted by FA","Marketing-led","FA (advisor)","Prospect acquired via media; routes through Great Planner to an FA for the quote conversation; may be new or recognised as existing","Volume journey; most SEA insurance sales involve an advisor; balances digital efficiency with FA economics","Out of scope: purely digital self-served quote, data-science origination, retention treatment"],
 ["C3","Data science-led, converted by FA","Data-science-led","FA (advisor)","Existing customer surfaced to an FA by models (lapse, switch, maturity, MHIT, cross-sell); FA runs the conversation","Highest-ROI journey; base is already owned, so acquisition cost is near zero; retained premium compounds","Out of scope: paid media at origination, new-customer acquisition, web-form lead creation"],
]

# ===== Sheet 3: GE journey stages =====
st_h = ["Order","GE journey stage","What happens","Journeys that touch it","Note"]
st_w = [7,22,40,20,40]
st = [
 ["0","Outreach","Paid and own media reaches the prospect","B1, B3","Clearwater addition before awareness, to hold media use cases"],
 ["1","Awareness","Prospect sees hyper-personalized campaign and lands on a hyper-personalized page","B1, B3","GE slide stage 1; signature moment is the personalized landing"],
 ["2","Exploration","Future-self interactive experience, needs assessment to 8 segments, model portfolios, AI explainer, reroute to Skybranch for complex queries","B1, B3","GE slide stage 2; richest signature-moment stage"],
 ["3","Quotation","Instant tailored quote; modular portfolio add and remove; alternative pricing via sliders; save-quote for later","B1, B3","GE slide stage 3; B1 self-served, B3 via FA through Great Planner"],
 ["4","KYC","Human-like digital-avatar account opening; progress indicators; Singpass retrieval in Singapore; vulnerability and competency capture","B1, B3","GE slide stage 4"],
 ["5","Eligibility check","Minimal info to underwrite, one question per page; pre-qualified journeys in 3-4 clicks; upload existing medical documents; AI scam scan; reroute to Skybranch","B1, B3","GE slide stage 5; instant outcome where possible"],
 ["6","Payment / policy issuance","Multiple payment options (Apple Pay, OCBC BNPL, PayNow); automatic rewards; welcome message and app invitation; personalized policy snapshot and benefits video","B1, B3","GE slide stage 6; payment and issuance are one GE stage; highest-urgency drop recovery, P0"],
 ["7","Post-purchase servicing","Self-serve amend and renew; automated renewal nudges via app, web or WA; wellness programs to reduce premiums; marketing-consent capture (planted-tree reward); cross and upsell prompts","B1, B3, C3","GE slide stage 7; C3 lives here; the largest opportunity"],
 ["8","Claims management","Claims handled with clear, empathetic support; submit via digital-avatar dialogue; integrated camera capture; reimbursement in about 1 day; reach out to Skybranch on rejection","All","GE slide stage 8"],
 ["L1","Rose, Gen-AI chatbot (journey-wide)","Real-time humanized chat support across the whole journey; saves chat history for the customer's next visit","All","GE slide shows Rose as a throughout-journey layer; CDP feeds profile and history"],
 ["L2","Skybranch (journey-wide)","Assisted support across the journey via chat, phone and video for complex queries (trade-offs, deductible, premium, claim-rejection reasons)","All","GE slide shows Skybranch as a throughout-journey layer"],
 ["F","Cross-journey (foundational)","Always-on CDP capabilities that underpin every stage","All","Data, identity, consent, arbitration, frequency, retrain"],
]

# ===== Sheet 4: Journey use cases (the bank) =====
uc_h = ["Tier","Use-case group","GE journey stage","Journey","ID","Business use case","How the stack helps (data -> trigger -> action)","Technical use case","Data inputs needed","Capability layer (vendor-neutral)","Funnel / value metric","Business KPI (the vector)","How it makes money / moves KPI","Priority"]
uc_w = [13,18,17,9,7,25,38,27,23,25,15,21,26,8]
J="Journey-level"; F="Foundational"
uc = [
 # ---- B1 ----
 [J,"Acquisition","Outreach","B1","B1-1","Lookalike prospecting from CDP seeds","Push high-value converter seeds to Meta/Google/DSP; refresh daily via Conversion API closed loop","Seed-audience export + Conversion API","Converters, value, hashed PII","CDP + Paid Media Activation","Reach","Prospect quality, ROAS","Higher-quality new business at lower cost","P1"],
 [J,"Acquisition","Outreach","B1","B1-2","Suppress existing policyholders and recent converters","Push exclusion audiences so spend goes to net-new prospects","Exclusion-audience sync","Policy holdings, recent bind events","CDP + Paid Media Activation","Reach","Wasted-spend %, CAC","Protects acquisition budget from day one","P1"],
 [J,"Acquisition","Outreach","B1","B1-3","Persona and intent audience build","Segment by Project Clearwater persona x intent x value-band","Audience segmentation","Persona, intent signals, value-band","CDP","Reach","Addressable reach, audience quality","Sharper targeting lifts efficiency","P1"],
 [J,"Acquisition","Outreach","B1","B1-4","Conversion-API closed loop","Feed bind events and value back to optimise bidding to value","Offline / Conversion API export","Bind event, premium value","CDP + Paid Media Activation","Reach (from Convert)","ROAS, value-based bidding","Compounds media efficiency over time","P1"],
 [J,"Channel execution","Outreach","B1","B1-5","Dynamic creative optimization","Optimise creative at persona x ad-cluster x product","Creative decisioning (DCO)","Persona, ad cluster, product","Campaign Management","Reach","Click-through, creative pass-through","Higher ad efficiency","P2"],
 [J,"Engagement","Exploration","B1","B1-6","Creative-continuity landing-page personalization","Match the page to the ad creative, persona and intent in real time","Real-time on-page decisioning","Ad cluster, persona, intent, device","Real-time Personalization + CDP","Pass-through","Landing-page engagement, pass-through rate","More visitors progress to quote","P1"],
 [J,"Data enablement","Exploration","B1","B1-7","Identity resolution cookie to known","Resolve anonymous device to a known profile on PII capture","Identity resolution","Cookie/device id, PII (NRIC today; phone/email future)","CDP","Pass-through","Resolution / match rate","Enables 1:1 personalization and recovery","P1"],
 [J,"Channel execution","Exploration","B1","B1-8","Landing-page drop recovery via NBA channel pick","On drop, NBA fires channel 1 digital, then channel 2 FIIA, then channel 3 SkyBranch by value-adjusted propensity, cool-down, frequency cap, consent","Drop event + NBA arbitration + multichannel","Drop event, propensity, consent, contact","Decisioning + Campaign Management","Stop leakage","Landing-page drop recovery rate","Recovers prospects who would be lost","P1"],
 [J,"Acquisition","KYC","B1","B1-9","Form prefill (Singpass / KYC)","Prefill known data; Singpass in Singapore, guided KYC in Malaysia","Profile lookup + external prefill","Singpass data, known profile","CDP + Workflow Orchestration","Pass-through","Form completion rate","Less friction means more quotes","P1"],
 [J,"Channel execution","Quotation","B1","B1-10","Form-drop recovery","On form drop, NBA fires channels 1-3 with saved state and a resume link","Drop event + saved state + NBA","Form state, contact, consent","Decisioning + Campaign Management","Stop leakage","Form completion / recovery rate","Recovers abandoned applications","P1"],
 [J,"Engagement","Quotation","B1","B1-11","Quote personalization","Tailor the quote presentation by persona and intent","Real-time personalization","Persona, quote inputs","Real-time Personalization","Convert","Quote-to-payment rate","Higher progression to payment","P2"],
 [J,"Channel execution","Payment / policy issuance","B1","B1-12","Payment-drop recovery (P0 urgency)","Payment drop is highest urgency; NBA fires channels 1-3 fast","Drop event (P0) + NBA + multichannel","Payment state, value, contact","Decisioning + Campaign Management","Stop leakage","Payment completion rate","Recovers near-won sales","P1"],
 [J,"Channel execution","Payment / policy issuance","B1","B1-13","Payment-method optimization","Offer card / PayNow / e-wallet by preference and market","Real-time personalization","Market, preference","Real-time Personalization","Convert","Payment success rate","Reduces payment friction","P2"],
 [J,"Onboarding","Post-purchase servicing","B1","B1-14","Digital onboarding journey","On policy issue, fire welcome and activation sequence","Journey orchestration","Bind event, profile, channel pref","Campaign Management","Activate","Activation rate","Early value; builds the retention base","P1"],
 [J,"Data enablement","Post-purchase servicing","B1","B1-15","Lifecycle handoff prospect to customer","Update lifecycle stage; set Account_Owner (or null if no FA); make eligible for C3","Profile update + workflow","Bind event, FA flag","CDP + CRM + Workflow","Retain and grow","Lifecycle data integrity","Enables future C3 lifetime value","P2"],
 # ---- B3 ----
 [J,"Acquisition","Outreach","B3","B3-1","FA-acceptance propensity overlay","High-FA-acceptance customers see advice-led creative; low-acceptance see digital-first","Propensity overlay on audience + DCO","FA-acceptance score, persona","AI/ML Engine + Paid Media Activation","Reach","Creative-fit, downstream FA acceptance","Routes the right customers to advice","P1"],
 [J,"Acquisition","Outreach","B3","B3-2","Shared acquisition mechanics with B1","Reuse lookalikes, suppression and persona audiences","Reuse of B1-1, B1-2, B1-3","As B1","CDP + Paid Media Activation","Reach","ROAS, audience quality","Efficient sourcing","P1"],
 [J,"Data enablement","Exploration","B3","B3-3","Existing-customer recognition at landing page","Cookies map a known or existing customer browsing anonymously; tailor and route accordingly","Identity resolution (cookies; NRIC today, phone/email future)","Cookie/device, NRIC","CDP","Pass-through","Recognition rate","Enables LSA continuity and a better offer","P1"],
 [J,"Channel execution","Exploration","B3","B3-4","Landing-page drop recovery (digital first, then FA)","NBA fires channels 1-3 first, then FA via Great Planner for advice-led recovery","Drop event + NBA + GP routing","Drop event, propensity, FA-acceptance","Decisioning + CRM + Great Planner","Stop leakage","Landing-page drop recovery rate","Recovers advice-led prospects","P1"],
 [J,"Acquisition","Exploration","B3","B3-5","Request-call-back, consent and LSA tagging","Capture RCB, consent and Last Servicing Agent preference","Form + consent + LSA tag","RCB inputs, consent, LSA","CRM + Workflow","Pass-through","RCB and consent completion","Clean advice handoff","P1"],
 [J,"Acquisition","Quotation","B3","B3-6","Lead enrichment at creation","Enrich lead with purchase propensity, FA-acceptance, channel-fit and top-three predicted objections","Model scoring + objection classifier","Lead, behaviour, holdings","AI/ML Engine + CRM","Convert","Lead quality, FA acceptance","Better routing and close rates","P1"],
 [J,"Channel execution","Quotation","B3","B3-7","Intent grading and next-best-channel","Grade intent (hot/medium/low); decide next best channel (digital vs agent)","Scoring + NBA","Engagement, propensity","Decisioning","Convert","Routing accuracy","Balances cost-to-serve with conversion","P1"],
 [J,"Channel execution","Quotation","B3","B3-8","Lead routing, new vs existing, LSA vs new agent","Great Planner tags the lead and assigns the LSA (existing) or a new agent (unassigned)","GP routing rules","Lead tags, LSA, capacity","Great Planner + CRM","Convert","Assignment SLA, leakage","Avoids lost leads at handoff","P1"],
 [J,"Channel execution","Quotation","B3","B3-9","Four-tier NBA routing arbitration","Tier 1 digital, tier 2 FIIA, tier 3 SkyBranch, tier 4 FA via GP when value-adjusted propensity x FA-acceptance crosses the threshold","NBA arbitration across tiers","Propensity, FA-acceptance, value, consent","Decisioning","Convert","Cost-to-serve, conversion","Spends FA time where it pays back","P1"],
 [J,"Channel execution","Quotation","B3","B3-10","FA-fit scoring (best advisor match)","Match the advisor by capacity, language and product specialisation","Agent-fit scoring","Advisor attributes, lead","AI/ML Engine + CRM","Convert","Match quality, close rate","Better conversion through fit","P1"],
 [J,"Channel execution","Quotation","B3","B3-11","Orphan-lead detection (SLA timer + grab pool)","Unactioned leads detected via SLA, routed to a grab pool; bot-assisted calling for low-value leads","SLA timer + grab-pool flow + bot calling","Lead status, SLA, value","Great Planner + Workflow + Decisioning","Stop leakage","Orphan rate, time-to-first-touch","Stops lead leakage in handoff","P1"],
 [J,"Engagement","Quotation","B3","B3-12","Auto advisor briefing pack","Persona, lifestage, intent, holdings, top-three objections with responses and recommended next-best-offer land in Sales Cloud / FA Mobile App","Briefing generation","Profile, holdings, scores, objections","AI/ML Engine + CRM","Convert","FA prep time, close rate","Higher-quality advice meetings","P1"],
 [J,"Cross-sell / upsell","Quotation","B3","B3-13","CVP tool Customer 360 integration (existing)","Great Advice pulls holdings, prior interactions and propensity live; recommends next-best-offer, cross-sell and talking points; refreshes in-meeting","Real-time Customer 360 to CVP","Customer 360, scores","CRM + CDP + Great Advice","Convert","In-meeting conversion, cross-sell","Deeper, faster advice conversations","P1"],
 [J,"Channel execution","Quotation","B3","B3-14","Unique FA-ID tagged URL (remote)","Remote meeting via a unique URL for attribution; payment via the same URL","URL generation + attribution","FA id, lead","Workflow + Attribution","Convert","Remote conversion, attribution accuracy","Enables remote sales and measurement","P2"],
 [J,"Channel execution","Quotation","B3","B3-15","SkyBranch sales-licensed action checklist","Assisted-sales rep checklist, similar to FA without advisor licensing","Guided checklist","Lead, context","CRM","Convert","Assisted close rate","Scales assisted sales","P2"],
 [J,"Channel execution","Quotation","B3","B3-16","Quote-not-accepted NBA","Decide nurture-with-alternative, re-engage-later, or senior-FA escalation","NBA arbitration","Quote outcome, propensity","Decisioning + Campaign Management","Stop leakage","Quote-accept rate","Recovers stalled deals","P1"],
 [J,"Channel execution","Payment / policy issuance","B3","B3-17","Payment-drop P0 with FA priority callback","High-value payment drop triggers an FA priority callback","Drop event (P0) + FA callback","Payment state, value, FA","Decisioning + CRM + Great Planner","Stop leakage","Payment completion rate","Recovers high-value sales","P1"],
 [J,"Onboarding","Payment / policy issuance","B3","B3-18","Policy issuance and onboarding handoff","Email policy issuance; hand off to onboarding","Journey orchestration","Bind event","Campaign Management","Activate","Onboarding rate","Builds the retention base","P2"],
 [J,"Data enablement","Post-purchase servicing","B3","B3-19","B3 to C3 lifecycle handoff","Account_Owner becomes the converting FA; future C3 triggers route to that FA via advisor continuity","Profile and ownership write","Bind, FA id","CDP + CRM","Retain and grow","Lifetime-value continuity","Strongest LTV motion in the model","P1"],
 # ---- eligibility + claims (end-to-end coverage) ----
 [J,"Channel execution","Eligibility check","B1, B3","GEN-1","Eligibility-decision communication","On the eligibility result, trigger a clear next-step message or an alternative-product path","Decision event + journey","Eligibility result","Decisioning + Campaign Management","Stop leakage","Eligibility pass-through","Keeps eligible customers moving; redirects declines","P2"],
 [J,"Retention","Claims management","All","GEN-2","Proactive claims-status communication","On a claim event or status change, send proactive updates, a satisfaction survey and de-escalation routing","Claim event + journey + routing","Claim status, NPS","Campaign Management + CRM","Retain and grow","Post-claim churn, NPS","Reduces churn after a claim","P2"],
 # ---- C3 (post-purchase) ----
 [J,"Retention","Post-purchase servicing","C3","C3-1","Multi-model propensity stack","Score the base for lapse (event on payment-failure, weekly otherwise), switch-intent (weekly), maturity rollover (90 days pre-maturity), MHIT fit (monthly), cross-sell per line (weekly), FA-acceptance (event)","Model stack in Decisioning / Studio","Base data, events, behaviour","AI/ML Engine + CDP","Retain and grow","Model coverage, precision","Surfaces high-ROI opportunities on owned base","P1"],
 [J,"Data enablement","Post-purchase servicing","C3","C3-2","Score vector with SHAP reason codes","Each customer carries a vector of scores with reason codes, not a single label","Scoring + explainability","Features per customer","AI/ML Engine","Retain and grow","Explainability, action quality","Trust and better treatment selection","P1"],
 [J,"Channel execution","Post-purchase servicing","C3","C3-3","NBA arbitration across firing models","When several models fire on one customer, resolve by value, urgency and fatigue limits; suppression prevents over-contact","NBA arbitration","Scores, value, fatigue","Decisioning","Retain and grow","Action precision, fatigue","Right single action per customer","P1"],
 [J,"Channel execution","Post-purchase servicing","C3","C3-4","Advisor-continuity routing","CRM task defaults to the mapped FA (Account_Owner); grab-pool fallback after SLA via Flow","Routing + SLA flow","Account_Owner, SLA","CRM + Workflow","Convert","Actioned rate, SLA breach","Keeps relationship and recurring revenue","P1"],
 [J,"Channel execution","Post-purchase servicing","C3","C3-5","Grab-pool fallback","Unactioned tasks reassigned after SLA breach","SLA timer + flow","Task status, SLA","Workflow + CRM","Stop leakage","Task leakage rate","Prevents dropped opportunities","P1"],
 [J,"Engagement","Post-purchase servicing","C3","C3-6","NBA-selected engagement journey","Campaign journey indexed by persona x trigger x propensity x lifestage","Journey selection","Persona, trigger, propensity","Campaign Management","Pass-through","Engagement rate","Warms the customer before the FA","P1"],
 [J,"Engagement","Post-purchase servicing","C3","C3-7","Authenticated 1:1 personalization","Logged-in onsite and in-app personalization across home tile, sidebar, offers and notifications","Real-time personalization (authenticated)","Login, Customer 360","Real-time Personalization","Pass-through","Onsite engagement, conversion","Lifts conversion on the owned base","P1"],
 [J,"Retention","Post-purchase servicing","C3","C3-8","Loss-if-lapse calculator (1:1)","Render real coverage figures and dependants from Customer 360, not a generic illustration","Dynamic content from Customer 360","Coverage, dependants","CDP + Real-time Personalization","Retain and grow","Lapse-save rate","Prevents lapse; retains premium","P1"],
 [J,"Retention","Post-purchase servicing","C3","C3-9","Comparison content vs current plan","Use the customer current plan as the baseline for switch defence","Dynamic content","Current plan data","Real-time Personalization + CDP","Retain and grow","Switch-save rate","Defends against competitor churn","P1"],
 [J,"Channel execution","Post-purchase servicing","C3","C3-10","Non-engagement escalation","Non-engagement triggers an escalation path","Trigger + escalation","Engagement signals","Decisioning + Campaign Management","Stop leakage","Escalation effectiveness","Recovers silent at-risk customers","P2"],
 [J,"Engagement","Post-purchase servicing","C3","C3-11","FA briefing for retention and cross-sell","Briefing pack (holdings, scores, reason codes, next-best-offer) in Sales Cloud / FA Mobile App","Briefing generation","Customer 360, scores","AI/ML Engine + CRM","Convert","FA prep, close rate","Effective retention conversations","P1"],
 [J,"Cross-sell / upsell","Post-purchase servicing","C3","C3-12","Maturity rollover next-best-product (90 days)","Surface the next-best-product for policies maturing within 90 days","Rollover model + journey","Maturity dates, propensity","AI/ML Engine + Campaign Management","Retain and grow","Rollover capture rate","Retains maturing premium","P1"],
 [J,"Cross-sell / upsell","Post-purchase servicing","C3","C3-13","MHIT cross-sell for coverage gaps","Identify coverage gaps and recommend MHIT","Gap model + next-best-offer","Holdings, gaps","AI/ML Engine + CRM","Retain and grow","MHIT cross-sell rate","Closes protection gaps; adds premium","P1"],
 [J,"Data enablement","Post-purchase servicing","C3","C3-14","Closed-loop outcome capture","FA logs structured outcomes (interest, objection, follow-up, next step); streams to Data Cloud to refresh features and the NBA log","Structured capture + write-back","FA outcomes","CRM + CDP + AI/ML Engine","Retain and grow","Model lift, data quality","Compounding intelligence over time","P1"],
 [J,"Channel execution","Post-purchase servicing","C3","C3-15","Wait-state management","Not-ready outcomes set calibrated waits (7-14 days lapse, 30-90 days cross-sell) with content rotation","Wait-state rules + rotation","Outcome, trigger type","Decisioning + Campaign Management","Retain and grow","Re-engage success, fatigue","Nurtures without over-contact","P2"],
 [J,"Channel execution","Post-purchase servicing","C3","C3-16","Cool-down on conversion","On an adjacent-product purchase, suppress that product family during the cool-down window","Suppression rules","Purchase events","Decisioning + CDP","Retain and grow","Over-contact rate","Protects trust and relevance","P2"],
 [J,"Cross-sell / upsell","Post-purchase servicing","C3","C3-17","Up-sell on life events","Recommend a higher coverage tier on a life-event signal","Event trigger + next-best-offer","Life-event signals","AI/ML Engine + Campaign Management","Retain and grow","Up-sell rate","Incremental premium","P2"],
 # ---- GE signature moments (Project Clearwater); CDP-driven elements only ----
 [J,"Engagement","Awareness","B1, B3","GE-S1","Hyper-personalized awareness landing","Land the prospect on a hyper-personalized page built from persona, ad cluster and intent; show products and messages relevant to their needs","Real-time on-page decisioning","Persona, ad cluster, intent, device","CDP + Real-time Personalization","Pass-through","Landing-page relevance, pass-through","More relevant arrivals progress","P1"],
 [J,"Engagement","Exploration","B1, B3","GE-S2","Future-self interactive experience","Power the future-self life-journey visualisation with profile and life-stage data; feed interactions back to the profile","Profile-fed interactive experience + write-back","Life-stage, profile, interaction events","CDP + Real-time Personalization","Pass-through","Experience engagement, profile enrichment","Deeper engagement and richer first-party data","P1"],
 [J,"Engagement","Exploration","B1, B3","GE-S3","Needs assessment to 8 segments and model portfolio","Map the customer to 1 of 8 segments from the needs assessment and recommend model portfolios on needs and profile","Segmentation + recommendation","Assessment answers, profile, goals","CDP + AI/ML Engine","Pass-through","Assessment completion, recommendation take-up","Right-fit products lift conversion","P1"],
 [J,"Cross-sell / upsell","Exploration","B1, B3","GE-S4","Personalized product information via WhatsApp","Send personalized product information on the explored products via WhatsApp","Profile-triggered messaging","Explored products, contact, consent","Campaign Management","Pass-through","WhatsApp engagement","Keeps warm prospects moving","P2"],
 [J,"Engagement","Quotation","B1, B3","GE-S5","Modular quote with save-for-later","Persist the modular quote (add and remove cover, slider pricing) to the profile so the customer can save and resume","Quote-state persistence + resume","Quote configuration, profile","CDP + Real-time Personalization","Convert","Quote save and resume rate","Recovers considered buyers","P1"],
 [J,"Data enablement","KYC","B1, B3","GE-S6","Vulnerability and competency capture","Capture vulnerability and competency signals at KYC and store on the profile for compliant treatment downstream","Profile capture + governance flag","Vulnerability and competency inputs","CDP + Workflow","Enabler","Capture completeness, compliance","Compliant, duty-of-care treatment","P2"],
 [J,"Channel execution","Eligibility check","B1, B3","GE-S7","Pre-qualified eligibility in 3-4 clicks","Use known profile and prior data to pre-qualify and minimise questions; instant outcome where possible","Profile prefill + decisioning","Known profile, minimal inputs","CDP + Decisioning","Stop leakage","Eligibility completion, time-to-outcome","Less friction lifts completion","P1"],
 [J,"Data enablement","Eligibility check","B1, B3","GE-S8","Medical-document reuse","Reuse uploaded or held medical documents instead of a fresh medical exam where possible","Document linkage to profile","Held or uploaded medical documents","CDP + Workflow","Stop leakage","Exam-avoidance rate","Removes a major drop-off point","P2"],
 [F,"Data enablement","Eligibility check","All","GE-S9","AI scam scan across the journey","Score interactions for scam and fraud signals consistently across the journey; reroute to Skybranch if needed","Real-time fraud scoring","Behavioural and interaction signals","AI/ML Engine + CDP","Enabler","Scam detection rate","Reduces fraud loss and protects customers","P2"],
 [J,"Engagement","Payment / policy issuance","B1, B3","GE-S10","Personalized policy snapshot and benefits video","Generate a plain-language policy snapshot and a personalized benefits and claims-process video from policy data","Dynamic content from policy data","Policy data, profile","CDP + Real-time Personalization","Activate","Snapshot and video engagement","Builds confidence; reduces early churn","P2"],
 [J,"Retention","Post-purchase servicing","C3","GE-S11","Wellness program to reduce premiums","Run wellness programs that reward healthy actions with premium reductions; activity data flows back to the profile","Program + triggers + write-back","Wellness and app activity, consent","Campaign Management + CDP","Retain and grow","Wellness enrolment, engagement","Loyalty plus better risk and retention","P2"],
 [F,"Data enablement","Post-purchase servicing","All","GE-S12","Marketing-consent capture via reward","Capture marketing consent in exchange for a reward (for example a planted tree in the customer's name)","Consent capture + reward trigger","Consent grant, reward event","CDP + Campaign Management","Enabler","Marketing-consent opt-in rate","Grows the addressable, consented base","P1"],
 # ---- Foundational ----
 [F,"Data enablement","Cross-journey","All","F-1","Unified customer profile and refresh","Ingest streaming and batch events into one profile; refresh in real time","Profile unification + streaming ingestion","Web SDK, form/drop/transaction events, source systems","CDP","Enabler","Profile coverage, freshness","Enables every downstream use case","P1"],
 [F,"Data enablement","Cross-journey","All","F-2","Identity resolution graph","Stitch cookies, hashed PII, CRM ID and device into one identity (NRIC today; phone and email planned)","Identity resolution","Cookie/device, NRIC, phone, email, CRM ID","CDP","Enabler","Match rate, identity coverage","Accuracy of every segment and personalization","P1"],
 [F,"Channel execution","Cross-journey","All","F-3","Audience segmentation and activation","Build persona x intent x value x lifestage x propensity audiences and activate downstream","Segmentation + activation","Profile, scores, consent","CDP + Campaign Management","Enabler","Audience quality, activation latency","Powers targeting across journeys","P1"],
 [F,"Channel execution","Cross-journey","All","F-4","Suppression audience management","Maintain suppression and exclusion audiences across channels","Suppression lists","Holdings, conversion, consent","CDP + Campaign Management","Enabler","Wasted-spend %, over-contact","Protects spend and trust","P1"],
 [F,"Data enablement","Cross-journey","All","F-5","Consent and preference enforcement","Enforce consent and PDPA at each activation; honour Global Privacy Control; block non-compliant events server-side","Consent gate (server-side)","Consent state, purpose, channel preference","CDP + Workflow","Enabler","Compliance, deliverability","Avoids penalties; sustains trust","P1"],
 [F,"Channel execution","Cross-journey","All","F-6","Frequency capping across journeys","Cap contact across competing journeys so a customer is not over-contacted","Global frequency cap","Contact log across journeys","Campaign Management + Decisioning","Enabler","Contact-fatigue, opt-out rate","Protects deliverability and trust","P1"],
 [F,"Channel execution","Cross-journey","All","F-7","NBA / NBO arbitration engine","Rank competing actions by value, urgency and fatigue; pick one winner or suppress below threshold","Arbitration engine","Scores, value, fatigue, consent","Decisioning","Enabler","Action precision","Right action per customer across journeys","P1"],
 [F,"Data enablement","Cross-journey","All","F-8","Propensity model retrain and feedback loop","Conversion and outcome events refresh seeds and retrain models","Feedback loop","Conversion events, outcomes, features","AI/ML Engine + CDP","Enabler","Model lift over time","Compounding performance","P2"],
 [F,"Data enablement","Cross-journey","All","F-9","Closed-loop outcome capture to profile","Structured outcomes from FA and channels stream back to the profile and the decision log","Structured capture + write-back","Outcomes, interactions","CRM + CDP + AI/ML Engine","Enabler","Data quality, model lift","Improves every future decision","P1"],
 [F,"Data enablement","Cross-journey","All","F-10","Calculated insights and derived features","Compute derived features (value-band, lifestage, tenure) for segmentation and scoring","Feature engineering","Raw profile and event data","CDP","Enabler","Feature availability","Sharper segments and models","P2"],
 [F,"Channel execution","Rose, journey-wide","All","F-11","Rose Gen-AI chatbot, profile-aware across the journey","Give Rose the unified profile and saved chat history so support is humanized and continuous when the customer returns","Profile and history to conversational layer","Profile, chat history, intent","CDP + Campaign Management","Enabler","Containment, return-visit continuity","Lowers cost-to-serve; sustains engagement","P1"],
 [F,"Channel execution","Skybranch, journey-wide","All","F-12","Skybranch assisted support across the journey","Surface the profile and journey context to Skybranch for complex queries (trade-offs, deductible, premium, claim-rejection reasons) via chat, phone and video","Profile and context to assisted desktop","Profile, journey state, query","CDP + CRM","Enabler","Assisted resolution, conversion","Converts complex cases that would drop","P1"],
]

# ===== Sheet 5: Funnel KPI ladder =====
fk_h = ["Funnel / value stage","What it answers","Example KPIs","Use cases that drive it"]
fk_w = [22,34,46,30]
fk = [
 ["Reach","Did we reach the right people?","Addressable reach, match rate, CAC, lead quality, wasted-spend %, ROAS","B1-1 to B1-5, B3-1, B3-2"],
 ["Pass-through","Did more people move to the next step?","Landing-page engagement, form/quote-start rate, recognition rate, RCB completion","B1-6, B1-7, B1-9, B3-3, B3-5, C3-6, C3-7"],
 ["Convert","Did more people convert or bind?","Quote-to-bind, contact rate, routing accuracy, in-meeting conversion, close rate","B1-11, B3-6 to B3-15, C3-4, C3-11"],
 ["Stop leakage","Did we stop the drop-off and handoff loss?","Drop recovery (LP/form/payment), orphan rate, SLA breach, quote-accept rate","B1-8, B1-10, B1-12, B3-4, B3-11, B3-16, B3-17, C3-5, C3-10, GEN-1"],
 ["Retain and grow","Did we keep and deepen the relationship?","Lapse-save, switch-save, rollover capture, cross-sell/up-sell rate, CLV","C3-8, C3-9, C3-12, C3-13, C3-17, B1-15, B3-19, GEN-2"],
 ["Enabler (foundational)","Is the always-on machinery in place?","Match rate, profile freshness, consent compliance, action precision, model lift","F-1 to F-10"],
]

# ===== Sheet 6: SI use-case drop map =====
dm_h = ["SI use case / action","B1","B3","C3","Drop bucket / rationale"]
dm_w = [40,8,8,8,52]
dm = [
 ["1c Capture and auto-route leads to agents","Drop","Retain","Drop","Agent-dependent for B1; web-form lead-creation part drops for C3"],
 ["1d Calendar booking and reminders","Drop","Retain","Retain","Agent-dependent; not needed in B1 self-serve"],
 ["1e Ads-smarter / retargeting","Retain","Retain","Drop","Paid-media acquisition action; C3 originates from the model stack"],
 ["2a-2e Education and Retention use case","Drop","Drop","Retain","Retention-only mechanics; belong to existing-base C3"],
 ["4e Lapse / switch scoring","Drop","Drop","Retain","Retention-only scoring; C3 core"],
 ["4f Maturity rollovers","Drop","Drop","Retain","Retention-only; C3 core"],
 ["5g Hot Lead alerts to advisors","Drop","Retain","Retain","Agent-dependent alert; not applicable to B1"],
 ["7 Young Gen Brand Affinity","Drop","Drop","Drop","Separate journey for children 7-17; outside these three"],
 ["Net effect","~","~","~","About 32 of 45 SI actions retain across the three journeys collectively; drops are sequencing choices, not quality judgements; all 45 retain in the broader SI catalogue"],
]

# ===== Sheet 7: MarTech capability map =====
cm_h = ["Layer","Capability","What it does","Salesforce equivalent","Used by"]
cm_w = [22,30,42,30,12]
cm = [
 ["CDP","Unified profile + refresh","Create and refresh the single customer profile","Data Cloud","B1 B3 C3"],
 ["CDP","Identity resolution","Resolve cookies, hashed PII, CRM id, device (NRIC today; phone/email future)","Data Cloud","B1 B3"],
 ["CDP","Streaming event ingestion","Ingest form, drop, transaction and behavioural events","Data Cloud","B1 B3 C3"],
 ["CDP","Segmentation + suppression","Build audiences; manage suppression","Data Cloud","B1 B3 C3"],
 ["CDP","Audience activation","Activate audiences to downstream channels","Data Cloud","B1 B3 C3"],
 ["Campaign Management","Journey orchestration","Action-based, event-triggered journeys","Marketing Cloud Engagement","B1 B3 C3"],
 ["Campaign Management","Multichannel activation","Email, SMS, WhatsApp, push","Marketing Cloud Engagement","B1 B3 C3"],
 ["Campaign Management","Real-time personalization","Onsite and in-app 1:1 experiences","Marketing Cloud Personalization","B1 B3 C3"],
 ["Campaign Management","Paid media activation","Meta, Google, DSP via Conversion API","Marketing Cloud Advertising","B1 B3"],
 ["Campaign Management","Frequency capping","Cap contact across competing journeys","Marketing Cloud Engagement","B1 B3 C3"],
 ["AI/ML Engine","Propensity stack","8+ models per customer","Einstein Studio","B3 C3"],
 ["AI/ML Engine","NBA / NBO arbitration","Rank competing actions; suppress below threshold","Einstein Studio","B1 B3 C3"],
 ["AI/ML Engine","Objection classification","Predict top-three objections and responses","Einstein Studio","B3"],
 ["AI/ML Engine","Agent-fit scoring","Match advisor by capacity, language, specialisation","Einstein Studio","B3"],
 ["AI/ML Engine","Explainability + RL loop","SHAP reason codes; reinforcement loop on outcomes","Einstein Studio","B3 C3"],
 ["CRM","Advisor + service workflow","Lead, advisor and service workflow; outcome capture","Sales Cloud / Service Cloud","B1 B3 C3"],
 ["Workflow","Cross-system automation","Flows, SLA timers, grab-pool reassignment","Salesforce Flow","B1 B3 C3"],
 ["CMS","Content + LP rendering","Manage content and render landing pages","AEM","B1 B3"],
 ["GE systems","Great Planner (GP)","Lead management, tagging and FA assignment","GE proprietary","B3"],
 ["GE systems","Great Advice (CVP)","Advisor client-facing engagement tool","GE proprietary","B3"],
 ["GE systems","FIIA / SkyBranch","Call centre and assisted-sales channels","GE proprietary","B1 B3"],
]

# ===== Sheet 8: Method and notes =====
mn_h = ["Item","Note"]
mn_w = [30,98]
mn = [
 ["Sequence","CDP use-case bank (this, business English) then Data Cloud feature mapping (Jose, Nerea) then prioritization (against the three journeys, the MarTech backlog, and Data Cloud support) then SI defines the how. Everything downstream is built on this bank, so it is locked first."],
 ["Why not structure by outcome","The three client objectives (enforced, new business acceleration, retention) map onto B1, B3, C3 already; the CDP machinery under each outcome is the same, so an outcome structure adds nothing."],
 ["Why not the campaign or segment lens","Campaign lens does not work for this deliverable; the customer-segment lifecycle view was judged too high level. The journey-stage plus foundational structure was chosen."],
 ["Two tiers","Journey-level use cases sit on a GE stage. Foundational use cases are always-on CDP enablers used across journeys. Filter on the Tier column to separate them."],
 ["Vector principle","Every use case carries a business KPI that ladders to a funnel or value stage: reach, pass-through, convert, stop leakage, retain and grow; foundational rows are enablers. See the Funnel KPI ladder tab."],
 ["Lifecycle links","B1 and B3 converters join the base and become eligible for C3. B3 sets Account_Owner to the converting FA, so future C3 triggers route back via advisor continuity; this is the strongest lifetime-value motion."],
 ["Journey switching","A customer can sit in several journeys at once; NBA arbitration picks one winning action or suppresses all below threshold, and frequency capping prevents over-contact."],
 ["Identity caveat","GE currently identifies on NRIC only; phone and email identification is planned. B3 existing-customer recognition depends on this maturing."],
 ["Style conventions","Sentence case; no em dashes; vendor-neutral layer names with Salesforce equivalents in the MarTech capability map; scope boundaries framed as sequencing."],
 ["Companion artefacts","Industry research: CDP-in-insurance-landscape.md. Industry use cases and proof points: CDP-insurance-use-cases.xlsx. Flow diagrams: cdp-operating-loop.png, cdp-abandonment-recovery.png."],
]

sheets = [("Read me and change log", sheet_xml([rd_h]+rd, rd_w)),
          ("Journeys overview", sheet_xml([ov_h]+ov, ov_w)),
          ("GE journey stages", sheet_xml([st_h]+st, st_w)),
          ("Journey use cases", sheet_xml([uc_h]+uc, uc_w)),
          ("Funnel KPI ladder", sheet_xml([fk_h]+fk, fk_w)),
          ("SI use-case drop map", sheet_xml([dm_h]+dm, dm_w)),
          ("MarTech capability map", sheet_xml([cm_h]+cm, cm_w)),
          ("Method and notes", sheet_xml([mn_h]+mn, mn_w))]

CT = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
 '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
 '<Default Extension="xml" ContentType="application/xml"/>'
 '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
 '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
 + "".join(f'<Override PartName="/xl/worksheets/sheet{i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(len(sheets))) + '</Types>')
RELS = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'
WB = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
 + "".join(f'<sheet name="{esc(n)}" sheetId="{i+1}" r:id="rId{i+1}"/>' for i,(n,_) in enumerate(sheets)) + '</sheets></workbook>')
WB_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
 + "".join(f'<Relationship Id="rId{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i+1}.xml"/>' for i in range(len(sheets)))
 + f'<Relationship Id="rId{len(sheets)+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
STYLES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
 '<fonts count="2"><font><sz val="11"/><color theme="1"/><name val="Calibri"/><family val="2"/></font>'
 '<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/><family val="2"/></font></fonts>'
 '<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>'
 '<fill><patternFill patternType="solid"><fgColor rgb="FF1F3864"/><bgColor indexed="64"/></patternFill></fill></fills>'
 '<borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border>'
 '<border><left/><right/><top/><bottom style="thin"><color rgb="FFBFBFBF"/></bottom><diagonal/></border></borders>'
 '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
 '<cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
 '<xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="left" vertical="center" wrapText="1"/></xf>'
 '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf></cellXfs>'
 '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')

out = "GE-Stream3-CDP-usecase-bank-v2.1.xlsx"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", CT); z.writestr("_rels/.rels", RELS)
    z.writestr("xl/workbook.xml", WB); z.writestr("xl/_rels/workbook.xml.rels", WB_RELS)
    z.writestr("xl/styles.xml", STYLES)
    for i,(_,xml) in enumerate(sheets): z.writestr(f"xl/worksheets/sheet{i+1}.xml", xml)
print("wrote", out, "| journey use cases rows:", len(uc))
