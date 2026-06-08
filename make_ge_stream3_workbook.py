#!/usr/bin/env python3
"""Great Eastern Stream 3 - B1/B3/C3 journey use-case workbook. Stdlib-only .xlsx."""
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

# ---- Sheet 1: Journeys overview ----
ov_h = ["Journey","Name","Sourcing","Conversion","One-line definition","Personas / profile","Why it matters","Target / north-star","Scope boundary (sequencing)"]
ov_w = [9,28,18,14,40,26,32,22,34]
ov = [
 ["B1","Marketing-led, converted digitally","Marketing-led","Digital (no FA)","New or anonymous prospect acquired via paid or organic media; completes purchase fully digitally (landing page, form, quote, payment) with no advisor touch","Self-directed buyers; young professionals and mass affluent (Project Clearwater); simpler standalone protection (e.g. Cancer Guard)","Cleanest test of digital-only economics; if conversion and cost-to-serve work here, the model scales to adjacent products","About 2-3% web-to-sale conversion","Out of scope: FA conversation, Great Planner, Great Advice, education/retention plays, data-science leads"],
 ["B3","Marketing-led, converted by FA","Marketing-led","FA (advisor)","Prospect acquired via paid or organic media; routes through Great Planner to an FA for the quote conversation and conversion; may be new or recognised as existing at landing page","Buyers of complex/higher-value advice products (whole life, term with riders, CI, ILP); family builders, pre-retirees; existing customers cross-buying","Volume journey for GE; most SEA insurance sales involve an advisor; balances digital efficiency with FA economics","Hot leads to FAs at low cost; minimal handoff leakage","Out of scope: purely digital self-served quote, data-science origination, retention/lapse treatment"],
 ["C3","Data science-led, converted by FA","Data-science-led","FA (advisor)","Existing customer surfaced to an FA by models (lapse risk, switch intent, maturity rollover, MHIT fit, cross-sell); FA runs the retention or cross-sell conversation","Existing GE customers; serves retention, switch-save, maturity rollover, cross-sell (esp. MHIT), and life-event up-sell","Highest-ROI journey; base is already owned so acquisition cost is near zero; retained premium streams compound","Lapse prevented; cross-sell and rollover capture on owned base","Out of scope: paid media at origination, new-customer acquisition, web-form lead creation, anonymous-to-known resolution"],
]

# ---- Sheet 2: Journey use cases (deep) ----
uc_h = ["Journey","Stage","#","Business use case","How the stack helps (data -> trigger -> action)","Technical use case","Data inputs needed","Capability layer (vendor-neutral)","Funnel metric","Business KPI (the vector)","How it makes money / moves KPI","Priority"]
uc_w = [9,16,6,27,40,28,24,26,14,22,26,7]
uc = [
 # ---------- B1 ----------
 ["B1","Paid media","B1-1","Lookalike prospecting from CDP seeds","Push high-value converter seeds to Meta/Google/DSP; refresh daily via Conversion API closed loop","Seed-audience export + Conversion API","Converters, value, hashed PII","CDP + Paid Media Activation","Reach","Prospect quality, ROAS","Higher-quality new business at lower cost","P1"],
 ["B1","Paid media","B1-2","Suppress existing policyholders and recent converters","Push exclusion audiences so spend goes to net-new prospects","Exclusion-audience sync","Policy holdings, recent bind events","CDP + Paid Media Activation","Reach","Wasted-spend %, CAC","Protects acquisition budget from day one","P1"],
 ["B1","Paid media","B1-3","Persona and intent audience build","Segment by Project Clearwater persona x intent x value-band","Audience segmentation","Persona, intent signals, value-band","CDP","Reach","Addressable reach, audience quality","Sharper targeting lifts efficiency","P1"],
 ["B1","Paid media","B1-4","Conversion-API closed loop","Feed bind events and value back to optimise bidding to value","Offline / Conversion API export","Bind event, premium value","CDP + Paid Media Activation","Reach (from Convert)","ROAS, value-based bidding","Compounds media efficiency over time","P1"],
 ["B1","Paid media","B1-5","Dynamic creative optimization","Optimise creative at persona x ad-cluster x product","Creative decisioning (DCO)","Persona, ad cluster, product","Campaign Management","Reach","Click-through, creative pass-through","Higher ad efficiency","P2"],
 ["B1","Landing page","B1-6","Creative-continuity landing-page personalization","Match the page to the ad creative, persona and intent in real time","Real-time on-page decisioning","Ad cluster, persona, intent, device","Real-time Personalization + CDP","Pass-through","Landing-page engagement, pass-through rate","More visitors progress to quote","P1"],
 ["B1","Landing page","B1-7","Identity resolution cookie to known","Resolve anonymous device to a known profile on PII capture","Identity resolution","Cookie/device id, PII (NRIC today; phone/email future)","CDP","Pass-through","Resolution / match rate","Enables 1:1 personalization and recovery","P1"],
 ["B1","Landing page","B1-8","Landing-page drop recovery via NBA channel pick","On drop, NBA fires channel 1 digital, then channel 2 FIIA, then channel 3 SkyBranch by value-adjusted propensity, cool-down, frequency cap, consent","Drop event + NBA arbitration + multichannel","Drop event, propensity, consent, contact","Decisioning + Campaign Management","Stop leakage","Landing-page drop recovery rate","Recovers prospects who would be lost","P1"],
 ["B1","Quote / form","B1-9","Form prefill (Singpass / KYC)","Prefill known data; Singpass in Singapore, guided KYC in Malaysia","Profile lookup + external prefill","Singpass data, known profile","CDP + Workflow Orchestration","Pass-through","Form completion rate","Less friction means more quotes","P1"],
 ["B1","Quote / form","B1-10","Form-drop recovery","On form drop, NBA fires channels 1-3 with saved state and a resume link","Drop event + saved state + NBA","Form state, contact, consent","Decisioning + Campaign Management","Stop leakage","Form completion / recovery rate","Recovers abandoned applications","P1"],
 ["B1","Quote / form","B1-11","Quote personalization","Tailor the quote presentation by persona and intent","Real-time personalization","Persona, quote inputs","Real-time Personalization","Convert","Quote-to-payment rate","Higher progression to payment","P2"],
 ["B1","Payment","B1-12","Payment-drop recovery (P0 urgency)","Payment drop is highest urgency; NBA fires channels 1-3 fast","Drop event (P0) + NBA + multichannel","Payment state, value, contact","Decisioning + Campaign Management","Stop leakage","Payment completion rate","Recovers near-won sales","P1"],
 ["B1","Payment","B1-13","Payment-method optimization","Offer card / PayNow / e-wallet by preference and market","Real-time personalization","Market, preference","Real-time Personalization","Convert","Payment success rate","Reduces payment friction","P2"],
 ["B1","Policy / onboarding","B1-14","Digital onboarding journey","On policy issue, fire welcome and activation sequence","Journey orchestration","Bind event, profile, channel pref","Campaign Management","Activate","Activation rate","Early value; builds the retention base","P1"],
 ["B1","Policy / onboarding","B1-15","Lifecycle handoff prospect to customer","Update lifecycle stage; set Account_Owner (or null if no FA); make eligible for C3","Profile update + workflow","Bind event, FA flag","CDP + CRM + Workflow","Retain / grow","Lifecycle data integrity","Enables future C3 lifetime value","P2"],
 ["B1","Cross-cutting","B1-16","Frequency capping across journeys","Prevent over-contact when other journeys also target the customer","Global frequency cap","Contact log across journeys","Campaign Management + Decisioning","Efficiency","Contact-fatigue, opt-out rate","Protects deliverability and trust","P1"],
 ["B1","Cross-cutting","B1-17","Propensity retrain loop","Conversion events refresh lookalike seeds and retrain the propensity model","Feedback loop","Conversion events, features","AI/ML Engine + CDP","Reach","Model lift over time","Compounding acquisition efficiency","P2"],
 ["B1","Cross-cutting","B1-18","Consent-state enforcement","Enforce consent and PDPA at each activation point","Consent gate","Consent state, purpose","CDP + Workflow","Efficiency","Compliance, deliverability","Avoids penalties; sustains trust","P1"],
 # ---------- B3 ----------
 ["B3","Paid media","B3-1","FA-acceptance propensity overlay","High-FA-acceptance customers see advice-led creative; low-acceptance see digital-first","Propensity overlay on audience + DCO","FA-acceptance score, persona","AI/ML Engine + Paid Media Activation + Campaign Management","Reach","Creative-fit, downstream FA acceptance","Routes the right customers to advice","P1"],
 ["B3","Paid media","B3-2","Shared acquisition mechanics with B1","Reuse lookalikes, suppression and persona audiences","Reuse of B1-1, B1-2, B1-3","As B1","CDP + Paid Media Activation","Reach","ROAS, audience quality","Efficient sourcing","P1"],
 ["B3","Landing page","B3-3","Existing-customer recognition at landing page","Cookies map a known or existing customer browsing anonymously; tailor and route accordingly","Identity resolution (cookies; NRIC today, phone/email future)","Cookie/device, NRIC","CDP","Pass-through","Recognition rate","Enables LSA continuity and a better offer","P1"],
 ["B3","Landing page","B3-4","Landing-page drop recovery (digital first, then FA)","NBA fires channels 1-3 first, then FA via Great Planner for advice-led recovery","Drop event + NBA + GP routing","Drop event, propensity, FA-acceptance","Decisioning + CRM + Great Planner","Stop leakage","Landing-page drop recovery rate","Recovers advice-led prospects","P1"],
 ["B3","RCB / consent","B3-5","Request-call-back, consent and LSA tagging","Capture RCB, consent and Last Servicing Agent preference","Form + consent + LSA tag","RCB inputs, consent, LSA","CRM + Workflow","Pass-through","RCB and consent completion","Clean advice handoff","P1"],
 ["B3","Lead creation","B3-6","Lead enrichment at creation","Enrich lead with purchase propensity, FA-acceptance, channel-fit and top-three predicted objections","Model scoring + objection classifier","Lead, behaviour, holdings","AI/ML Engine + CRM","Convert","Lead quality, FA acceptance","Better routing and close rates","P1"],
 ["B3","Lead creation","B3-7","Intent grading and next-best-channel","Grade intent (hot/medium/low); decide next best channel (digital vs agent)","Scoring + NBA","Engagement, propensity","Decisioning","Convert","Routing accuracy","Balances cost-to-serve with conversion","P1"],
 ["B3","GP routing","B3-8","Lead routing, new vs existing, LSA vs new agent","Great Planner tags the lead and assigns the LSA (existing) or a new agent (unassigned)","GP routing rules","Lead tags, LSA, capacity","Great Planner + CRM","Convert","Assignment SLA, leakage","Avoids lost leads at handoff","P1"],
 ["B3","GP routing","B3-9","Four-tier NBA routing arbitration","Tier 1 digital, tier 2 FIIA, tier 3 SkyBranch, tier 4 FA via GP when value-adjusted propensity x FA-acceptance crosses the threshold","NBA arbitration across tiers","Propensity, FA-acceptance, value, consent","Decisioning","Convert","Cost-to-serve, conversion","Spends FA time where it pays back","P1"],
 ["B3","GP routing","B3-10","FA-fit scoring (best advisor match)","Match the advisor by capacity, language and product specialisation","Agent-fit scoring","Advisor attributes, lead","AI/ML Engine + CRM","Convert","Match quality, close rate","Better conversion through fit","P1"],
 ["B3","GP routing","B3-11","Orphan-lead detection (SLA timer + grab pool)","Unactioned leads detected via SLA, routed to a grab pool; bot-assisted calling for low-value leads","SLA timer + grab-pool flow + bot calling","Lead status, SLA, value","Great Planner + Workflow + Decisioning","Stop leakage","Orphan rate, time-to-first-touch","Stops lead leakage in handoff","P1"],
 ["B3","Agent meeting","B3-12","Auto advisor briefing pack","Persona, lifestage, intent, holdings, top-three objections with responses and recommended next-best-offer land in Sales Cloud / FA Mobile App","Briefing generation","Profile, holdings, scores, objections","AI/ML Engine + CRM","Convert","FA prep time, close rate","Higher-quality advice meetings","P1"],
 ["B3","Agent meeting","B3-13","CVP tool Customer 360 integration (existing)","Great Advice pulls holdings, prior interactions and propensity live; recommends next-best-offer, cross-sell and talking points; refreshes in-meeting","Real-time Customer 360 to CVP","Customer 360, scores","CRM + CDP + Great Advice","Convert","In-meeting conversion, cross-sell","Deeper, faster advice conversations","P1"],
 ["B3","Agent meeting","B3-14","Unique FA-ID tagged URL (remote)","Remote meeting via a unique URL for attribution; payment via the same URL","URL generation + attribution","FA id, lead","Workflow + Attribution","Convert","Remote conversion, attribution accuracy","Enables remote sales and measurement","P2"],
 ["B3","Agent meeting","B3-15","SkyBranch sales-licensed action checklist","Assisted-sales rep checklist, similar to FA without advisor licensing","Guided checklist","Lead, context","CRM","Convert","Assisted close rate","Scales assisted sales","P2"],
 ["B3","Unhappy path","B3-16","Quote-not-accepted NBA","Decide nurture-with-alternative, re-engage-later, or senior-FA escalation","NBA arbitration","Quote outcome, propensity","Decisioning + Campaign Management","Stop leakage","Quote-accept rate","Recovers stalled deals","P1"],
 ["B3","Unhappy path","B3-17","Payment-drop P0 with FA priority callback","High-value payment drop triggers an FA priority callback","Drop event (P0) + FA callback","Payment state, value, FA","Decisioning + CRM + Great Planner","Stop leakage","Payment completion rate","Recovers high-value sales","P1"],
 ["B3","Policy / onboarding","B3-18","Policy issuance and onboarding handoff","Email policy issuance; hand off to onboarding","Journey orchestration","Bind event","Campaign Management","Activate","Onboarding rate","Builds the retention base","P2"],
 ["B3","Cross-cutting","B3-19","B3 to C3 lifecycle handoff","Account_Owner becomes the converting FA; future C3 triggers route to that FA via advisor continuity","Profile and ownership write","Bind, FA id","CDP + CRM","Retain / grow","Lifetime-value continuity","Strongest LTV motion in the model","P1"],
 # ---------- C3 ----------
 ["C3","Origination","C3-1","Multi-model propensity stack","Score the base for lapse (event on payment-failure, weekly otherwise), switch-intent (weekly), maturity rollover (90 days pre-maturity), MHIT fit (monthly), cross-sell per line (weekly), FA-acceptance (event)","Model stack in Decisioning / Studio","Base data, events, behaviour","AI/ML Engine + CDP","Origination","Model coverage, precision","Surfaces high-ROI opportunities on owned base","P1"],
 ["C3","Origination","C3-2","Score vector with SHAP reason codes","Each customer carries a vector of scores with reason codes, not a single label","Scoring + explainability","Features per customer","AI/ML Engine","Origination","Explainability, action quality","Trust and better treatment selection","P1"],
 ["C3","Origination","C3-3","NBA arbitration across firing models","When several models fire on one customer, resolve by value, urgency and fatigue limits; suppression prevents over-contact","NBA arbitration","Scores, value, fatigue","Decisioning","Convert","Action precision, fatigue","Right single action per customer","P1"],
 ["C3","Routing","C3-4","Advisor-continuity routing","CRM task defaults to the mapped FA (Account_Owner); grab-pool fallback after SLA via Flow","Routing + SLA flow","Account_Owner, SLA","CRM + Workflow","Convert","Actioned rate, SLA breach","Keeps relationship and recurring revenue","P1"],
 ["C3","Routing","C3-5","Grab-pool fallback","Unactioned tasks reassigned after SLA breach","SLA timer + flow","Task status, SLA","Workflow + CRM","Stop leakage","Task leakage rate","Prevents dropped opportunities","P1"],
 ["C3","Engagement","C3-6","NBA-selected engagement journey","Campaign journey indexed by persona x trigger x propensity x lifestage","Journey selection","Persona, trigger, propensity","Campaign Management","Pass-through","Engagement rate","Warms the customer before the FA","P1"],
 ["C3","Engagement","C3-7","Authenticated 1:1 personalization","Logged-in onsite and in-app personalization across home tile, sidebar, offers and notifications","Real-time personalization (authenticated)","Login, Customer 360","Real-time Personalization","Pass-through","Onsite engagement, conversion","Lifts conversion on the owned base","P1"],
 ["C3","Engagement","C3-8","Loss-if-lapse calculator (1:1)","Render real coverage figures and dependants from Customer 360, not a generic illustration","Dynamic content from Customer 360","Coverage, dependants","CDP + Real-time Personalization","Retain","Lapse-save rate","Prevents lapse; retains premium","P1"],
 ["C3","Engagement","C3-9","Comparison content vs current plan","Use the customer current plan as the baseline for switch defence","Dynamic content","Current plan data","Real-time Personalization + CDP","Retain","Switch-save rate","Defends against competitor churn","P1"],
 ["C3","Engagement","C3-10","Non-engagement escalation","Non-engagement triggers an escalation path","Trigger + escalation","Engagement signals","Decisioning + Campaign Management","Stop leakage","Escalation effectiveness","Recovers silent at-risk customers","P2"],
 ["C3","FA conversation","C3-11","FA briefing for retention and cross-sell","Briefing pack (holdings, scores, reason codes, next-best-offer) in Sales Cloud / FA Mobile App","Briefing generation","Customer 360, scores","AI/ML Engine + CRM","Convert","FA prep, close rate","Effective retention conversations","P1"],
 ["C3","FA conversation","C3-12","Maturity rollover next-best-product (90 days)","Surface the next-best-product for policies maturing within 90 days","Rollover model + journey","Maturity dates, propensity","AI/ML Engine + Campaign Management","Grow","Rollover capture rate","Retains maturing premium","P1"],
 ["C3","FA conversation","C3-13","MHIT cross-sell for coverage gaps","Identify coverage gaps and recommend MHIT","Gap model + next-best-offer","Holdings, gaps","AI/ML Engine + CRM","Grow","MHIT cross-sell rate","Closes protection gaps; adds premium","P1"],
 ["C3","FA conversation","C3-14","Closed-loop outcome capture","FA logs structured outcomes (interest, objection, follow-up, next step); streams to Data Cloud to refresh features and the NBA log","Structured capture + write-back","FA outcomes","CRM + CDP + AI/ML Engine","Convert","Model lift, data quality","Compounding intelligence over time","P1"],
 ["C3","Outcome","C3-15","Wait-state management","Not-ready outcomes set calibrated waits (7-14 days lapse, 30-90 days cross-sell) with content rotation","Wait-state rules + rotation","Outcome, trigger type","Decisioning + Campaign Management","Retain","Re-engage success, fatigue","Nurtures without over-contact","P2"],
 ["C3","Outcome","C3-16","Cool-down on conversion","On an adjacent-product purchase, suppress that product family during the cool-down window","Suppression rules","Purchase events","Decisioning + CDP","Efficiency","Over-contact rate","Protects trust and relevance","P2"],
 ["C3","FA conversation","C3-17","Up-sell on life events","Recommend a higher coverage tier on a life-event signal","Event trigger + next-best-offer","Life-event signals","AI/ML Engine + Campaign Management","Grow","Up-sell rate","Incremental premium","P2"],
]

# ---- Sheet 3: Funnel KPI ladder ----
fk_h = ["Funnel / value stage","What it answers","Example KPIs","Use cases that drive it"]
fk_w = [22,34,46,30]
fk = [
 ["Reach","Did we reach the right people?","Addressable reach, match rate, CAC, lead quality, wasted-spend %, ROAS","B1-1 to B1-5, B3-1, B3-2"],
 ["Pass-through","Did more people move to the next step?","Landing-page engagement, form/quote-start rate, recognition rate, RCB completion","B1-6, B1-7, B1-9, B3-3, B3-5, C3-6, C3-7"],
 ["Convert","Did more people convert or bind?","Quote-to-bind, contact rate, routing accuracy, in-meeting conversion, close rate","B1-11, B3-6 to B3-15, C3-3, C3-4, C3-11"],
 ["Stop leakage","Did we stop the drop-off and handoff loss?","Drop recovery rate (LP/form/payment), orphan rate, SLA breach, quote-accept rate","B1-8, B1-10, B1-12, B3-4, B3-11, B3-16, B3-17, C3-5, C3-10"],
 ["Retain and grow","Did we keep and deepen the relationship?","Lapse-save, switch-save, rollover capture, cross-sell/up-sell rate, CLV","C3-8, C3-9, C3-12, C3-13, C3-17, B1-15, B3-19"],
]

# ---- Sheet 4: SI use-case drop map ----
dm_h = ["SI use case / action","B1","B3","C3","Drop bucket / rationale"]
dm_w = [40,8,8,8,52]
dm = [
 ["1c Capture and auto-route leads to agents","Drop","Retain","Drop","Agent-dependent for B1; web-form lead-creation part drops for C3 (no web-form origination)"],
 ["1d Calendar booking and reminders","Drop","Retain","Retain","Agent-dependent action; not needed in B1 self-serve flow"],
 ["1e Ads-smarter / retargeting","Retain","Retain","Drop","Paid-media acquisition action; C3 originates from the model stack, not paid media"],
 ["2a-2e Education and Retention use case","Drop","Drop","Retain","Retention-only mechanics; belong to existing-base C3, not acquisition"],
 ["4e Lapse / switch scoring","Drop","Drop","Retain","Retention-only scoring; C3 core"],
 ["4f Maturity rollovers","Drop","Drop","Retain","Retention-only; C3 core"],
 ["5g Hot Lead alerts to advisors","Drop","Retain","Retain","Agent-dependent alert; not applicable to B1 (no FA)"],
 ["7 Young Gen Brand Affinity","Drop","Drop","Drop","Separate journey targeting children 7-17; outside these three"],
 ["Net effect","~","~","~","About 32 of the 45 SI actions retain across the three journeys collectively; drops are sequencing choices, not quality judgements; all 45 retain in the broader SI catalogue"],
]

# ---- Sheet 5: MarTech capability map ----
cm_h = ["Layer","Capability","What it does","Salesforce equivalent","Used by"]
cm_w = [22,30,42,30,12]
cm = [
 ["CDP","Unified profile + refresh","Create and refresh the single customer profile","Data Cloud","B1 B3 C3"],
 ["CDP","Identity resolution","Resolve cookies, hashed PII, CRM id, device (NRIC today; phone/email future)","Data Cloud","B1 B3"],
 ["CDP","Streaming event ingestion","Ingest form, drop, transaction and behavioural events","Data Cloud","B1 B3 C3"],
 ["CDP","Segmentation + suppression","Build persona x intent x value x lifestage x propensity audiences; manage suppression","Data Cloud","B1 B3 C3"],
 ["CDP","Audience activation","Activate audiences to downstream channels","Data Cloud","B1 B3 C3"],
 ["Campaign Management","Journey orchestration","Action-based, event-triggered journeys","Marketing Cloud Engagement","B1 B3 C3"],
 ["Campaign Management","Multichannel activation","Email, SMS, WhatsApp, push","Marketing Cloud Engagement","B1 B3 C3"],
 ["Campaign Management","Real-time personalization","Onsite and in-app 1:1 experiences","Marketing Cloud Personalization","B1 B3 C3"],
 ["Campaign Management","Paid media activation","Meta, Google, DSP via Conversion API","Marketing Cloud Advertising","B1 B3"],
 ["Campaign Management","Frequency capping","Cap contact across competing journeys","Marketing Cloud Engagement","B1 B3 C3"],
 ["AI/ML Engine","Propensity stack","8+ models per customer (purchase, lapse, switch, rollover, MHIT, cross-sell, FA-acceptance, no-show)","Einstein Studio","B3 C3"],
 ["AI/ML Engine","NBA / NBO arbitration","Rank competing actions by value, urgency, fatigue; suppress below threshold","Einstein Studio","B1 B3 C3"],
 ["AI/ML Engine","Objection classification","Predict top-three objections and response paths","Einstein Studio","B3"],
 ["AI/ML Engine","Agent-fit scoring","Match advisor by capacity, language, specialisation","Einstein Studio","B3"],
 ["AI/ML Engine","Explainability + RL loop","SHAP reason codes; reinforcement loop on NBA outcomes","Einstein Studio","B3 C3"],
 ["CRM","Advisor + service workflow","Lead, advisor and service workflow; outcome capture","Sales Cloud / Service Cloud","B1 B3 C3"],
 ["Workflow","Cross-system automation","Orchestrate flows, SLA timers, grab-pool reassignment","Salesforce Flow","B1 B3 C3"],
 ["CMS","Content + LP rendering","Manage content and render landing pages","AEM","B1 B3"],
 ["GE systems","Great Planner (GP)","Lead management, tagging and FA assignment","GE proprietary","B3"],
 ["GE systems","Great Advice (CVP)","Advisor client-facing engagement tool","GE proprietary","B3"],
 ["GE systems","FIIA / SkyBranch","Call centre and assisted-sales channels","GE proprietary","B1 B3"],
]

# ---- Sheet 6: Method and notes ----
mn_h = ["Item","Note"]
mn_w = [30,98]
mn = [
 ["Purpose","Great Eastern Stream 3 prep: business and technical use cases for the three priority journeys B1, B3, C3, with capability scope, data inputs and a funnel KPI vector per use case. Built as a workshop starting point."],
 ["Selection logic","From a 3x3 matrix (sourcing: marketing / sales / data-science x conversion: digital / FA / hybrid), three journeys were chosen: B1 tests pure digital economics, B3 represents volume (advisor-led), C3 tests the highest-ROI motion (existing-base retention and cross-sell). Together they cover all three sourcing types and both primary conversion modes."],
 ["The vector principle","Every use case carries a business KPI that ladders to a funnel or value stage: reach, pass-through, convert, stop leakage, retain and grow. See the Funnel KPI ladder tab. Each row also states how it makes money."],
 ["B1 to C3 lifecycle","B1 converters join the base; future cross-sell, lapse or maturity triggers move them into C3. Lifecycle stage updates from prospect to customer; Account_Owner is set, or left null if no FA was involved (C3 advisor-continuity then routes to grab pool)."],
 ["B3 to C3 lifecycle","B3 converters have an FA assigned at conversion (Account_Owner). Future C3 triggers route to that FA via advisor continuity, giving FAs recurring revenue and the customer continuity. This is the strongest lifetime-value motion."],
 ["Journey switching","A customer can be in several journeys at once. NBA arbitration ranks competing actions by value, urgency and customer-fatigue and picks one winner or suppresses all below the confidence threshold. Frequency capping prevents over-contact across journeys."],
 ["Identity note","GE currently identifies on NRIC only; phone and email-based identification is planned. B3 existing-customer recognition at landing page depends on this maturing."],
 ["Tool lens","Vendor-neutral layer names used in the use-case tabs; Salesforce equivalents listed in the MarTech capability map. Stack: Data Cloud, Marketing Cloud Engagement / Personalization / Advertising, Einstein Studio, Sales Cloud, Service Cloud, Salesforce Flow."],
 ["Style conventions applied","Sentence case; no em dashes; scope boundaries framed as sequencing choices; vendor-neutral naming with Salesforce equivalents."],
 ["Scale","54 journey use cases here plus framing and capability tabs. Expanding adjacent categories (claims, service, wellness, governance) and the SI catalogue depth gets to a 50-100+ workshop count."],
 ["Companion artefacts","Landscape research: CDP-in-insurance-landscape.md. Industry use cases + proof points: CDP-insurance-use-cases.xlsx. Flow diagrams: cdp-operating-loop.png, cdp-abandonment-recovery.png, CDP-insurance-workflow.md."],
]

sheets = [("Journeys overview", sheet_xml([ov_h]+ov, ov_w)),
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

out = "GE-Stream3-journey-usecases.xlsx"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", CT); z.writestr("_rels/.rels", RELS)
    z.writestr("xl/workbook.xml", WB); z.writestr("xl/_rels/workbook.xml.rels", WB_RELS)
    z.writestr("xl/styles.xml", STYLES)
    for i,(_,xml) in enumerate(sheets): z.writestr(f"xl/worksheets/sheet{i+1}.xml", xml)
print("wrote", out, "| use cases:", len(uc), "(B1/B3/C3)")
