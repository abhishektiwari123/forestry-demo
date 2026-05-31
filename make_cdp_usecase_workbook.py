#!/usr/bin/env python3
"""CDP implementation-prep workbook (insurance) - stdlib-only .xlsx generator."""
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
    return round(min(lines, 24) * 14.6 + 5, 1)

def sheet_xml(rows, widths):
    n_cols, n_rows = len(widths), len(rows)
    cols = "".join(f'<col min="{i+1}" max="{i+1}" width="{w}" customWidth="1"/>' for i, w in enumerate(widths))
    body = []
    for r, row in enumerate(rows, start=1):
        style = 1 if r == 1 else 2
        ht = 32 if r == 1 else est_height(row, widths)
        cells = []
        for c, val in enumerate(row, start=1):
            cells.append(f'<c r="{col_letter(c)}{r}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{esc(val)}</t></is></c>')
        body.append(f'<row r="{r}" ht="{ht}" customHeight="1">{"".join(cells)}</row>')
    dim = f"A1:{col_letter(n_cols)}{n_rows}"
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            f'<dimension ref="{dim}"/>'
            '<sheetViews><sheetView workbookViewId="0">'
            '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
            '<selection pane="bottomLeft" activeCell="A2" sqref="A2"/></sheetView></sheetViews>'
            '<sheetFormatPr defaultRowHeight="15"/>'
            f'<cols>{cols}</cols><sheetData>{"".join(body)}</sheetData>'
            f'<autoFilter ref="{dim}"/></worksheet>')

# ============ Sheet 1: Business use-case categories ============
cat_h = ["#","Business use-case category","What it is","Example use cases","Primary KPI family","How CDP makes money / moves KPI","Journey deep-dive?"]
cat_w = [4,26,34,34,22,30,20]
cat = [
 ["1","Acquisition & paid-media efficiency","First-party data to target, retarget and suppress on ad platforms","Retargeting, suppression, lookalikes, offline-conversion loop","CAC, ROAS, lead quality","Lower acquisition cost; more qualified leads","Yes - Acquire journey"],
 ["2","Lead management & speed-to-lead","Score, route and recover leads in real time","Lead scoring, instant call routing, non-reachable recovery","Contact rate, lead-to-quote","More leads contacted and converted, faster","Yes - Acquire"],
 ["3","Drop-off / abandonment recovery","Detect funnel drop-off and trigger recovery","Quote / application / eKYC / checkout recovery","Completion rate, leakage","Recovered revenue from would-be drop-offs","Yes - Acquire"],
 ["4","Onboarding & activation","Activate new customers and complete profiles","Welcome journeys, eKYC, app adoption","Activation rate, time-to-active","Faster activation; higher early value","Yes - Default journey"],
 ["5","Cross-sell / upsell","Next-best-product on intent and life-event signals","Life-event triggers, cross-LOB bundles","Products/customer, cross-sell rate","More products per customer","Yes - Default journey"],
 ["6","Retention / renewal / churn","Predict and prevent lapse; win back","Pre-renewal nudges, churn save, win-back","Renewal rate, churn, CLV","Retained premium; higher CLV","Yes - Default journey"],
 ["7","Personalization & experience","1:1 web/app/next-best-action from the unified profile","Returning-customer offers, NBA, send-time optimization","Engagement, conversion","Higher conversion and satisfaction","Cuts across journeys"],
 ["8","Claims & service experience","Proactive, contextual servicing","Claim-status comms, agent screen pops, de-escalation","NPS, cost-to-serve, post-claim churn","Lower churn and service cost","Cuts across journeys"],
 ["9","Consent, governance & data foundation (enabler)","Identity resolution + enforced consent","Single profile, consent enforcement, suppression","Compliance, deliverability, match rate","Enables everything; avoids fines/penalties","Enabler"],
 ["10","Member engagement & wellness (life/health)","Behavioural data for engagement and risk","Wellness programs, app engagement, telematics","Engagement, loss ratio","Better risk selection and loyalty","Cuts across journeys"],
]

# ============ Sheet 2: Journey use cases (deep) ============
uc_h = ["Journey","Stage","#","Business use case","How the CDP helps (data -> trigger -> action)","Technical use case (what the stack does)","Data inputs needed","CDP capability needed (feature scope)","Funnel metric","Business KPI (the vector)","How it makes money","Priority"]
uc_w = [22,15,4,26,40,30,26,26,14,22,28,8]
AQ="Acquire / quote-to-buy"
ON="Onboard & cross-sell [DEFAULT - replace w/ GE]"
RN="Renew & retain [DEFAULT - replace w/ GE]"
uc = [
 [AQ,"Bid media","A1","High lead-quality feedback loop","Push converters + bound-policy value back to ad platforms so they optimise to quality, not clicks","Offline-conversion / CAPI export of conversion events + value","Bound policy, premium/value, hashed PII, lead source","Audience sync + offline-conversion API","Reach","Cost per qualified lead; lead-quality score","Lower CAC; higher-quality pipeline","P1"],
 [AQ,"Bid media","A2","Suppress existing customers","Exclude current policyholders from prospecting; reallocate budget","Exclusion-audience sync to ad platforms","Policy holdings, hashed PII","Audience sync (exclusion)","Reach","Wasted-spend %, CAC","Stops paying to reach owned customers","P1"],
 [AQ,"Bid media","A3","High-LTV lookalike prospecting","Seed from top-LTV / multi-policy customers; platform finds similar","Predictive LTV score + seed-audience export","Policy, premium, tenure, claims history","ML scoring + audience sync","Reach","Prospect quality, ROAS","Higher-quality new business","P2"],
 [AQ,"Bid media","A4","Cookieless first-party activation","Activate consented first-party IDs as cookies fade","Identity resolution + hashed match (e.g. UID2)","Email/phone, consent, web events","Identity resolution + activation","Reach","Addressable reach, match rate","Protects acquisition post-cookie","P2"],
 [AQ,"Landing page","A5","Returning-customer recognition -> sweeter offer","Recognise the returning/known visitor (only you know they returned) and show a better offer","Real-time profile lookup + on-site decisioning","Device/cookie -> profile link, prior visits, offers seen","Identity resolution + real-time personalization","Convert","Returning-visitor conversion rate","Higher conversion on warm traffic","P1"],
 [AQ,"Landing page","A6","Pass-through personalization","Personalize the page by source, segment and recently-viewed product","Real-time content decisioning","Traffic source, segment, recently-viewed","Real-time personalization","Pass-through","Landing-page engagement / pass-through rate","More visitors progress to quote","P1"],
 [AQ,"Landing page","A7","Drop-off management (known customer)","Detect the drop, identify the customer, trigger a resume nudge","Real-time drop event + journey trigger","Page/scroll events, profile, quote state","Real-time triggers + orchestration","Stop leakage","Bounce / drop-off rate","Recovers would-be lost visitors","P1"],
 [AQ,"Landing page","A8","Exit-intent capture + progressive profiling","Exit survey/coupon to capture and enrich the profile","Exit-intent trigger + form + profile write-back","Exit signal, zero-party answers","Real-time triggers + profile unification","Pass-through","Lead-capture rate","Turns anonymous traffic into leads","P2"],
 [AQ,"Quote / form","A9","Quote-abandonment recovery","Save the quote, send a resume deep-link (SMS/WhatsApp/email), escalate","Abandon event + saved-state + orchestration","Quote inputs, contact, consent","Real-time triggers + orchestration","Stop leakage","Quote completion rate","Recovers abandoned quotes","P1"],
 [AQ,"Quote / form","A10","Dynamic form / prefill","Prefill known data and shorten the form","Profile lookup + external data enrichment","Known customer data, 3rd-party prefill","Identity resolution + integration","Pass-through","Form completion rate","Less friction -> more quotes","P2"],
 [AQ,"Quote / form","A11","Speed-to-lead routing","Route a hot quote to a call-center agent within minutes","Real-time score + route to agent","Quote, propensity score, agent availability","Real-time triggers + activation to contact centre","Convert","Contact rate; quote-to-bind","First-to-respond wins the sale","P1"],
 [AQ,"Quote / form","A12","Price-reveal reassurance","Detect the price-reveal drop and trigger an explainer / flexible option","Event trigger + treatment","Price-shown event, segment","Real-time triggers + personalization","Stop leakage","Post-price drop-off rate","Rescues sticker-shock leavers","P2"],
 [AQ,"eKYC / verify","A13","eKYC drop-off recovery","Re-engage failed/abandoned KYC on the preferred channel","Drop event + re-engagement journey","KYC step status, contact, consent","Real-time triggers + orchestration","Stop leakage","eKYC completion rate","Recovers stalled applications","P1"],
 [AQ,"eKYC / verify","A14","OTP-assisted completion","Agent triggers an OTP at a preferred time to complete the purchase","Event + assisted-channel trigger","Application state, phone","Orchestration + contact-centre integration","Convert","Assisted-completion rate","Converts stuck applicants","P2"],
 [AQ,"Checkout / bind","A15","Checkout / payment abandonment recovery","Reminder + human call for high-value carts","Abandon event + escalation journey","Checkout state, value, contact","Real-time triggers + orchestration","Stop leakage","Checkout completion rate","Recovers near-won policies","P1"],
 [AQ,"Checkout / bind","A16","Offline-conversion feedback on bind","Fire the bound-policy value back to ad platforms","Offline-conversion export","Bound policy + value, hashed PII","Offline-conversion API","Convert -> Reach","ROAS; value-based bidding","Compounds media efficiency","P1"],
 [AQ,"Checkout / bind","A17","Suppress on conversion","Remove the buyer from acquisition ads at bind","Exclusion sync on bind event","Bind event, hashed PII","Audience sync","Efficiency","Wasted-spend %","Stops post-purchase ad waste","P1"],
 [AQ,"Post-bind","A18","Handoff to onboarding + cross-sell","Move the new customer into onboarding and cross-sell segments","Segment membership on bind","Bind event, profile","Segmentation","Retain / grow","Activation handoff rate","Bridges to lifetime value","P2"],
 [ON,"Onboard","O1","Welcome / activation journey","Orchestrate a first-90-day welcome sequence","Journey orchestration","Bind, profile, channel preference","Orchestration","Activate","Activation rate","Faster value realisation","P1"],
 [ON,"Onboard","O2","Profile / data completion","Progressive profiling to enrich the customer record","Forms + profile write-back","Profile gaps","Profile unification","Activate","Profile completeness","Enables targeting & personalization","P2"],
 [ON,"Onboard","O3","App / portal adoption","Nudge self-serve digital adoption","Triggers + push/in-app","App install/login events","Triggers + orchestration","Engage","Digital-adoption rate","Lower cost-to-serve","P2"],
 [ON,"Onboard","O4","Channel-preference & consent capture","Learn best channel and capture opt-ins","Preference centre + propensity","Engagement history, consent","Consent + ML","Engage","Reachability, opt-in rate","Better deliverability & compliance","P2"],
 [ON,"Cross-sell","O5","Life-event cross-sell trigger","New home/marriage/child -> next-best-product","Event trigger + next-best-action","Life-event signals, holdings","Triggers + ML scoring","Grow","Cross-sell rate; products/customer","More products per customer","P1"],
 [ON,"Cross-sell","O6","Cross-LOB bundle (auto->home->life)","Surface the second-LOB opportunity on a signal","NBA + segmentation","Holdings, behaviour","ML + orchestration","Grow","Bundle rate","Deeper share of wallet","P1"],
 [ON,"Cross-sell","O7","Anniversary / maturity upsell","Anniversary or maturity trigger -> upgrade","Scheduled + event trigger","Policy dates, holdings","Triggers","Grow","Upsell rate","Incremental premium","P2"],
 [ON,"Cross-sell","O8","Agent / RM cross-sell copilot","Surface recommendations + context to the agent","Profile API to agent desktop","Profile, drop-offs, recommendations","Identity + activation to contact centre","Grow","Agent cross-sell rate","Lifts assisted sales","P2"],
 [RN,"Renew","R1","Pre-renewal nudge sequence","Timed multi-channel sequence ~45 days before renewal","Scheduled journey","Renewal date, channel preference","Orchestration","Retain","Renewal rate","Retained premium","P1"],
 [RN,"Churn","R2","Predictive churn / at-risk save","Score risk on rate-shopping / claim signals, trigger a save offer","Churn model + save journey","Behaviour, claims, payment history","ML scoring + orchestration","Retain","Churn rate; save rate","Prevents lapse","P1"],
 [RN,"Win-back","R3","Win-back lapsed policies","Re-engage lapsed customers within the revival window","Lapsed segment + journey","Lapse date, profile","Segmentation + orchestration","Re-acquire","Win-back rate","Recovers lost customers","P2"],
 [RN,"Renew","R4","Payment-failure dunning","Recover failed/late payments to avoid involuntary lapse","Event trigger + reminder sequence","Payment status","Triggers","Retain (involuntary)","Involuntary churn rate","Reduces avoidable lapse","P1"],
 [RN,"Retain","R5","CLV-based retention prioritization","Focus retention spend on high-CLV at-risk customers","CLV model + segmentation","Revenue, tenure, holdings","ML scoring","Retain","CLV retained","Protects the best customers","P2"],
 [RN,"Claims","R6","Post-claim experience save","Proactive comms + survey after a claim","Claim event + journey","Claim status, NPS","Triggers + orchestration","Retain","Post-claim churn; NPS","Reduces churn-after-claim","P1"],
 [RN,"Renew","R7","Renewal upsell injection","Vary the upsell within the renewal journey per customer","NBA inside the renewal journey","Holdings, propensity","ML + orchestration","Grow","Renewal-upsell rate","More value at renewal","P2"],
 [RN,"Retain","R8","Loyalty / wellness engagement","Ongoing engagement program (life/health)","Program + triggers","Wellness/app/telematics data","Triggers + orchestration","Retain","Engagement; loss ratio","Loyalty plus better risk","P2"],
]

# ============ Sheet 3: Funnel KPI ladder ============
fk_h = ["Funnel stage (the 'vector')","What it answers","Example KPIs","Use cases that drive it"]
fk_w = [22,34,46,28]
fk = [
 ["Reach","Did we reach the right people?","Addressable reach, match rate, CAC, lead-quality score, wasted-spend %","A1, A2, A3, A4"],
 ["Pass-through","Did more people move to the next step?","Landing-page engagement, form/quote-start rate, pass-through rate, lead-capture rate","A6, A8, A10"],
 ["Convert","Did more people convert / bind?","Quote-to-bind, conversion rate, contact rate, returning-visitor conversion","A5, A11, A14, A16, O5, O6"],
 ["Stop leakage","Did we stop the drop-off?","Quote / application / eKYC / checkout completion, drop-off recovery rate","A7, A9, A12, A13, A15"],
 ["Retain & grow","Did we keep and deepen the relationship?","Renewal rate, churn, CLV, products/customer, cross-sell rate","R1, R2, R5, O5, O6"],
]

# ============ Sheet 4: Method & notes ============
mn_h = ["Item","Note"]
mn_w = [28,98]
mn = [
 ["PURPOSE","CDP implementation-prep pack for an insurance client - a workshop-ready starting point that pre-empts the SI's 'ocean-mode' use-case dump. Built 2026-05-31."],
 ["STRUCTURE (the four bullets)",""],
 ["1A Business use cases","'Journey use cases' tab, column 'Business use case'. The hard, creative part - go 1-2 layers deeper per journey stage."],
 ["1B Technical use cases","'Journey use cases' tab, column 'Technical use case' - mapped 1:1 to each business use case."],
 ["2 Feature activation scope","'Journey use cases' tab, column 'CDP capability needed' - the capabilities each use case requires (tool-agnostic, per your instruction). Swap for named Data Cloud features if the tool is fixed."],
 ["3 Integration design / data flow","'Journey use cases' tab, column 'Data inputs needed' - the inputs/feeds per use case. The full interlink-architecture + data diagram is a separate one-pager to build for the P1 use cases."],
 ["4 Implementation / operating model / release plan","Standardised - pull from prior assets (per the discussion, ~half a day). Not duplicated here."],
 ["THE 'VECTOR' PRINCIPLE","Every use case carries a business KPI that ladders to a funnel metric: Reach -> Pass-through -> Convert -> Stop leakage -> Retain & grow. See the 'Funnel KPI ladder' tab. Each row also states 'how it makes money'."],
 ["ASSUMPTIONS",""],
 ["Journey 1 = Acquire / quote-to-buy","CONFIRMED by you. Built deep (18 use cases across 6 stages: bid media, landing page, quote/form, eKYC, checkout/bind, post-bind). This is your Facebook-retargeting / sweeter-returning-offer example, expanded."],
 ["Journeys 2 & 3 = DEFAULTS","Onboard & cross-sell, and Renew & retain are PLACEHOLDERS. You pointed me to your 'GE' Claude chat for the real three journeys - I cannot access other chats. Paste the GE journey names/definitions and I will replace these and re-deep them."],
 ["Tool lens","Tool-agnostic, per your selection. Feature scope is expressed as CDP capabilities (identity resolution, segmentation, real-time triggers, audience sync, ML scoring, journey orchestration, consent enforcement, offline-conversion API)."],
 ["SCALE","~34 journey use cases + 10 categories here. Expanding the non-journey categories (claims, service, wellness, governance) gets you to the 50-100 'workshop-respectable' count."],
 ["COMPANION ARTEFACTS","Named real-world deployments + ROI evidence: CDP-insurance-use-cases.xlsx. Landscape report: CDP-in-insurance-landscape.md. Flow diagrams: cdp-operating-loop.png, cdp-abandonment-recovery.png."],
]

# ============ package ============
sheets = [("Use-case categories", sheet_xml([cat_h]+cat, cat_w)),
          ("Journey use cases", sheet_xml([uc_h]+uc, uc_w)),
          ("Funnel KPI ladder", sheet_xml([fk_h]+fk, fk_w)),
          ("Method & notes", sheet_xml([mn_h]+mn, mn_w))]

CT = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
 '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
 '<Default Extension="xml" ContentType="application/xml"/>'
 '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
 '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
 + "".join(f'<Override PartName="/xl/worksheets/sheet{i+1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(len(sheets)))
 + '</Types>')
RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
 '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
WB = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
 + "".join(f'<sheet name="{esc(n)}" sheetId="{i+1}" r:id="rId{i+1}"/>' for i,(n,_) in enumerate(sheets))
 + '</sheets></workbook>')
WB_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
 + "".join(f'<Relationship Id="rId{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i+1}.xml"/>' for i in range(len(sheets)))
 + f'<Relationship Id="rId{len(sheets)+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
STYLES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
 '<fonts count="2"><font><sz val="11"/><color theme="1"/><name val="Calibri"/><family val="2"/></font>'
 '<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/><family val="2"/></font></fonts>'
 '<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>'
 '<fill><patternFill patternType="solid"><fgColor rgb="FF2F5496"/><bgColor indexed="64"/></patternFill></fill></fills>'
 '<borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border>'
 '<border><left/><right/><top/><bottom style="thin"><color rgb="FFBFBFBF"/></bottom><diagonal/></border></borders>'
 '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
 '<cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
 '<xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="left" vertical="center" wrapText="1"/></xf>'
 '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf></cellXfs>'
 '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')

out = "CDP-insurance-usecase-prep.xlsx"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", CT)
    z.writestr("_rels/.rels", RELS)
    z.writestr("xl/workbook.xml", WB)
    z.writestr("xl/_rels/workbook.xml.rels", WB_RELS)
    z.writestr("xl/styles.xml", STYLES)
    for i,(_,xml) in enumerate(sheets):
        z.writestr(f"xl/worksheets/sheet{i+1}.xml", xml)
print("wrote", out, "| categories:", len(cat), "| journey use cases:", len(uc))
