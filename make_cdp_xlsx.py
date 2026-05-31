#!/usr/bin/env python3
"""Generate a formatted multi-sheet .xlsx (CDP-in-insurance use cases) using only the stdlib."""
import math, zipfile

def esc(s):
    s = "" if s is None else str(s)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def col_letter(i):  # 1-based -> A, B, ...
    s = ""
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s

def est_height(values, widths):
    lines = 1
    for v, w in zip(values, widths):
        v = "" if v is None else str(v)
        lines = max(lines, math.ceil((len(v) + 1) / max(w - 1, 6)))
    return round(min(lines, 22) * 14.6 + 4, 1)

def sheet_xml(rows, widths):
    n_cols, n_rows = len(widths), len(rows)
    cols = "".join(
        f'<col min="{i+1}" max="{i+1}" width="{w}" customWidth="1"/>' for i, w in enumerate(widths)
    )
    body = []
    for r, row in enumerate(rows, start=1):
        style = 1 if r == 1 else 2
        ht = 30 if r == 1 else est_height(row, widths)
        cells = []
        for c, val in enumerate(row, start=1):
            ref = f"{col_letter(c)}{r}"
            cells.append(
                f'<c r="{ref}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{esc(val)}</t></is></c>'
            )
        body.append(f'<row r="{r}" ht="{ht}" customHeight="1">{"".join(cells)}</row>')
    dim = f"A1:{col_letter(n_cols)}{n_rows}"
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<dimension ref="{dim}"/>'
        '<sheetViews><sheetView workbookViewId="0">'
        '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
        '<selection pane="bottomLeft" activeCell="A2" sqref="A2"/>'
        '</sheetView></sheetViews>'
        '<sheetFormatPr defaultRowHeight="15"/>'
        f'<cols>{cols}</cols>'
        f'<sheetData>{"".join(body)}</sheetData>'
        f'<autoFilter ref="{dim}"/>'
        '</worksheet>'
    )

# ---------------- Sheet 1: Use Cases ----------------
uc_headers = ["#", "Lifecycle stage", "Use case", "Business problem",
              "How the CDP helps (data -> trigger -> action)", "Activation channel(s)",
              "Named insurer example(s)", "Vendor / platform", "Reported outcome / metric", "Evidence quality"]
uc_widths = [4, 19, 25, 38, 58, 22, 24, 18, 30, 17]

uc = [
 ["1","Acquisition & paid media","First-party audience activation (retargeting)","Digital acquisition leaned on declining 3rd-party cookies; warm prospects not re-engaged","Unify policy/quote/web data -> build segments (quote-started-no-bind, browsed product) -> hash PII -> sync to ad platforms; auto-refresh","Google Customer Match, Meta, TikTok, LinkedIn, Amazon DSP","Toggle (Farmers digital brand)","Twilio Segment","-67% CPA","Vendor"],
 ["2","Acquisition & paid media","Customer suppression","Budget wasted advertising to existing/converted customers","Push current-policyholder segment as an exclusion list to ad platforms; reallocate to prospecting","Google/Meta exclusion lists","(general)","Hightouch / Zeotap / Tealium","~10-20% wasted budget removed","Benchmark (uncorroborated)"],
 ["3","Acquisition & paid media","High-LTV lookalike seeding","Low-quality prospecting wastes spend","Seed from top-decile predicted-LTV / multi-policy bundlers -> platform expands to lookalikes","Meta, Google","LexisNexis property->auto","various","directional","Capability"],
 ["4","Acquisition & paid media","Cookieless / UID2 activation","Signal loss from Safari/Firefox/iOS + privacy regulation (NOT Chrome)","Resolve anonymous -> consented first-party profile -> activate via Unified ID 2.0","The Trade Desk","Metricon (adjacent, home builder)","Hightouch ID Express","+72% leads (adjacent)","Vendor / adjacent"],
 ["5","Acquisition & paid media","Offline-conversion feedback loop","Policy binds offline days after the click; pixels miss it, so bidding optimizes to the wrong signal","Fire qualified-lead + bound-policy + value server-side to ad platforms to train value-based bidding","Meta CAPI, Google Enhanced Conversions for Leads","(general)","Adobe RT-CDP, Hightouch, mParticle","~15-35% lower CPL (unverified)","Vendor"],
 ["6","Acquisition & paid media","MMM + LTV-based budget allocation","Last-click under-credits brand/upper-funnel; spend misallocated","Combine marketing-mix modeling + CLV to shift spend from low- to high-LTV channels","(planning / all)","Legal & General","Tealium + Snowflake","Reallocated majority of marketing spend","Vendor"],
 ["7","Lead mgmt & speed-to-lead","AI / predictive lead scoring","Agents waste effort on low-readiness leads","Real-time scoring on behavior -> prioritize and route hot leads to agents","Call center / CRM","Generali","Insider","3x leads, -20% sales cycle","Vendor"],
 ["8","Lead mgmt & speed-to-lead","Speed-to-lead call routing","Online leads go cold; sold to 3-8 carriers, first-to-respond wins","Abandon/enquiry event -> instant dialer connects an agent within ~1 min","Phone","Insurance Choice (Optilead)","Optilead","+150% policies, ~80% abandoned quotes connected","Vendor (indep. anchor: Velocify 25-carrier audit)"],
 ["9","Lead mgmt & speed-to-lead","Non-reachable lead recovery","Call center can't reach a share of leads by phone","Export non-reachable lists from CRM -> target online on preferred channel/device","Web / push / email","(unnamed insurer)","Lemnisk / FirstHive","-","Vendor"],
 ["10","Lead mgmt & speed-to-lead","Missed-call -> WhatsApp journey","Low outbound answer rates lose intent","Missed call sent real-time to CDP -> triggers WhatsApp journey to book a slot","WhatsApp","(unnamed insurer)","Lemnisk","-","Vendor"],
 ["11","Drop-off / abandonment","Quote abandonment recovery","~84% abandon quotes; second spike at price reveal","Detect funnel step + save quote to profile -> SMS deep-link 'resume' -> escalate SMS->WhatsApp->voice","SMS, WhatsApp, email, web push, voice","Optilead clients (recover ~21%, best 47%)","Optilead / Lemnisk","~21% of abandoned quotes recovered","Vendor / benchmark"],
 ["12","Drop-off / abandonment","Application / form abandonment","Long static forms; security & length friction","Detect stall -> triggered nudge + pre-filled resume link; route abandoners to a briefed agent","Email, SMS, banner, agent","Legal & General","Tealium + Snowflake","+15% completions, +54% call-to-lead","Vendor"],
 ["13","Drop-off / abandonment","eKYC / identity-verification drop-off","Heavy onboarding drop at the KYC step","Cross-channel scoring -> re-engage low-score/inactive users (Early-Month-on-Book)","Email, SMS, web push","Generali","Insider","-17% eKYC drop-offs","Vendor"],
 ["14","Drop-off / abandonment","Checkout / payment abandonment","Drop at the final payment page for online purchase","Detect final-page drop -> reminder via banner/onsite/email/SMS; high-value -> immediate human call","Banner, email, SMS, call","(thin; bank-loan analog)","Tealium","+11% conv (bank-loan analog)","Vendor / adjacent"],
 ["15","Drop-off / abandonment","Browsing / product-page retargeting","Prospect browses a product page and leaves","Web activity updates profile -> later web-push offer for that exact product","Web push, banner","(unnamed insurer)","Lemnisk","-","Vendor"],
 ["16","Drop-off / abandonment","High-value abandoner segmentation","Treating all abandoners the same is inefficient","Split into 'high-value' / 'high-propensity-to-return' segments + on-site personalization + social retargeting","Onsite, social","(general)","Tealium","-","Vendor"],
 ["17","Onboarding & activation","Welcome / activation journeys","Fragmented onboarding experience","Map journey from first contact -> orchestrate welcome sequence; segment-driven dashboards/tasks","Email, app, push","AIA Philam Life (pilot)","Lemnisk","Qualitative (pilot)","Vendor PR"],
 ["18","Onboarding & activation","OTP-assisted purchase completion","Prospects stall in online purchase; agents can't expedite","Agent triggers a valid OTP to the prospect's phone at a preferred time to complete the buy","SMS / assisted","(unnamed insurer)","FirstHive","-","Vendor"],
 ["19","Cross-sell / upsell","Life-event / milestone cross-sell","Generic offers miss the moment of need","Life-event/anniversary/maturing-deposit triggers -> next-best-product on preferred channel","Omnichannel","(Affinity FCU bank analog)","Hightouch / NGDATA","'up to 25% cross-sell increase' (aggregator)","Benchmark"],
 ["20","Cross-sell / upsell","Cross-LOB bundling (auto->home->life->health)","Siloed lines of business miss cross-sell","Unified intent signals across online+offline surface the 2nd-LOB opportunity; equip brokers","Agent, CRM, web","LexisNexis property->auto","LexisNexis","-","Vendor"],
 ["21","Cross-sell / upsell","Upsell injected into renewal","One-size renewal messaging leaves revenue on the table","Per-customer logic varies the upsell offer within a single renewal campaign","Omnichannel","FirstHive 'leading insurer'","FirstHive","(paired with +23% renewal)","Vendor"],
 ["22","Cross-sell / upsell","Agent / RM cross-sell copilot","Agents lack live context during a call","CDP surfaces drop-off points, history and AI recs to the agent in real time","Agent desktop","(unnamed insurer)","FirstHive / NGDATA","-","Capability"],
 ["23","Cross-sell / upsell","Seasonal cross-sell","Demand for some products is time-sensitive","Calendar/seasonal triggers (life insurance at tax season, home pre-disaster season)","Omnichannel","(general)","Hightouch","-","Capability"],
 ["24","Retention / renewal / churn","Offline->online renewal migration","Renewals stuck in offline / branch channels","Unified data drives self-serve digital renewal nudges; right message/person/time","Email, SMS, app","Income Insurance","Tealium + Merkle","Car renewal 44->72%, motorcycle 52->68%","Vendor + Drum Award"],
 ["25","Retention / renewal / churn","Pre-renewal nudge sequences","Customers lapse at renewal","Timed multi-channel sequence ~45 days out (call->email->text) + early-renewal discount","Call, email, SMS, app","Allianz","Insider","80% app-push opt-in","Vendor"],
 ["26","Retention / renewal / churn","Predictive churn / at-risk save","Customers leave before being engaged","Churn model on rate-shopping / competitor-quote / claim-dissatisfaction -> save journey / flexible payment","Omnichannel","Liberty Mutual","predictive segmentation","+15% retention","3rd-party aggregator"],
 ["27","Retention / renewal / churn","Risk-tier -> NBA retention engine","Retention actions are ad hoc","Policy engine maps risk tiers to per-channel NBAs (pricing, coverage review, payment plan, concierge)","Omnichannel, agent","(general)","NGDATA","-","Capability"],
 ["28","Retention / renewal / churn","Renewal / payment-issue notifications","Failed/late payments drive involuntary churn","CDP triggers renewal and payment-update communications","SMS, email, app","(unnamed insurer)","Lemnisk","-","Vendor"],
 ["29","Retention / renewal / churn","Win-back / dormant reactivation","Lapsed and dormant customers are lost value","Lifecycle stages (lapsed/dormant) trigger re-engagement journeys","Omnichannel","(general)","BlueConic / Zeotap","- (thinly evidenced)","Under-evidenced"],
 ["30","Retention / renewal / churn","CLV modeling for retention targeting","Can't tell which customers to protect","Model CLV from revenue/usage/churn -> prioritize high-value retention","(targeting)","(general)","BlueConic","-","Capability"],
 ["31","Personalization & decisioning","On-site / app individualization","Generic web/app experiences convert poorly","Real-time profile drives recently-viewed banners and dynamic content (behavior-driven, not rules)","Web, app","Etiqa; Generali; Prudential","Insider; Zeta; Adobe","4.74% vs 2.17%; +24% close; +135% engagement","Vendor (+ indep. press: Prudential)"],
 ["32","Personalization & decisioning","Next-Best-Action arbitration","Which offer, when, and whether to act at all","Decision engine ranks actions via P x C x V x L (Pega) / Einstein / Agentforce on the unified profile","Omnichannel","(capability)","Pega / Salesforce","-","Capability"],
 ["33","Personalization & decisioning","Channel-propensity orchestration","Right message, wrong channel","Model picks each user's best channel -> per-individual journeys (thousands of unique paths)","Omnichannel","Aegon Life","Lemnisk (Ramanujan)","+19% web conversions","Vendor PR"],
 ["34","Personalization & decisioning","Send-Time Optimization","Messages sent at the wrong time","Predict optimal per-recipient send time from open/click history","Email, push","(capability)","Adobe Journey Optimizer","-","Capability"],
 ["35","Personalization & decisioning","Geofence-triggered offers","Missing location-based moments of relevance","Enter geofence (e.g., a hospital) -> real-time 1:1 SMS offer (e.g., health checkup)","SMS","(unnamed insurer)","Lemnisk","-","Vendor"],
 ["36","Claims & service","Real-time contact-center screen pops","Agents lack caller context at pickup","Sub-100ms CDP API feeds IVR/agent the profile + active-claim status + recent activity; intent-based routing","Call center (Amazon Connect, Diabolocom)","(capability)","Tealium","-","Vendor / capability"],
 ["37","Claims & service","Proactive claims-status comms","Claims anxiety drives dissatisfaction & service churn","Claim-event/status-change triggers updates + post-settlement NPS + de-escalation routing","Email, SMS, push, agent","(general)","Hightouch / CDP.com","-","Capability"],
 ["38","Fraud & risk","Real-time fraud signals","Quote manipulation and fraudulent applications","Stream cross-channel behavioral signals to a fraud model in real time","(backend / agent)","USAA; (ForMotiv)","Tealium EventStream; ForMotiv","Latency 1hr -> <1s; agent quote-manipulation -18%","Vendor anecdote"],
 ["39","Member engagement & wellness","Wellness / engagement programs","Low ongoing engagement; risk & cost","Wearables + points + status tiers + premium discounts; activity data flows back to the insurer","App, wearables","John Hancock Vitality (AIA Vitality)","Vitality + wearables","20+ engagements/mo; Apple Watch 7x; ~90% earned premium savings","Company-direct + Conference Board (independent)"],
 ["40","Bancassurance / embedded","Embedded insurance with partner-data pre-fill","Friction in distribution; thin first-party profiles","Bank/partner data pre-fills the application at point of sale inside the partner app","Partner app","Chubb via DBS; Nubank Vida","Chubb Studio (NB: embedded API platform, not a CDP)","Nubank Vida 560k+ active policies","Company"],
 ["41","Consent / governance","Enforced consent & preference management","Client-side tags can't be trusted to honor opt-outs; regulatory fines","Server-side per-event consent check vs purpose rules + Global Privacy Control -> block non-compliant events before activation; DSARs, audit logs, opt-out propagation","All channels","(capability)","Tealium","- (strong GLBA/PIPEDA rationale; $100M+ pixel fines)","Vendor / capability"],
 ["42","Data foundation / identity","Identity resolution / single customer view","Fragmented identifiers; agent-vs-direct attribution","Deterministic anchors + probabilistic fills; household resolution; often augmented by LexisNexis LexID","(foundation)","LexID for Insurance","CDP + LexisNexis","-","Capability / vendor"],
]
sheet1 = sheet_xml([uc_headers] + uc, uc_widths)

# ---------------- Sheet 2: Named Deployments ----------------
nd_headers = ["Insurer", "Region", "Vendor / stack", "Headline use case", "Reported metric", "Evidence quality"]
nd_widths = [20, 9, 23, 33, 42, 30]
nd = [
 ["Income Insurance","SG","Tealium + Merkle","Offline->online renewal migration","Car renewal 44->72%, -40% CPA, +452% online revenue YoY","Vendor + Drum Award (partial independent)"],
 ["Legal & General","UK","Tealium + Snowflake","Abandoned-application recovery + LTV spend","+54% call-to-lead, +15% application completions","Vendor (on newswires)"],
 ["Prudential Financial","US","Adobe Real-Time CDP","Personalization at scale","+135% engagement in <30 days","Vendor + independent press"],
 ["Generali (entity A)","EU","Zeta Global","AI website individualization","+24% close rate","Vendor"],
 ["Generali (entity B)","EU","Insider","Cross-channel lead scoring / eKYC","3x leads, -17% eKYC drop-off, -20% sales cycle","Vendor - DO NOT merge with entity A"],
 ["Etiqa","MY/SG","Insider","Homepage banner personalization","Conversion 4.74% vs 2.17% average","Vendor"],
 ["AIA Singapore","SG","Lemnisk","Lead gen / app engagement","+63% lead generation, 2.3x CTR","Vendor"],
 ["AIA Philam Life","PH","Lemnisk","Digital onboarding (pilot)","Qualitative","Vendor PR"],
 ["Aegon Life","IN","Lemnisk (Ramanujan)","Channel-propensity orchestration","+19% website conversions","Vendor PR"],
 ["Tawuniya","SA","Lemnisk","Acquisition/retention; application-starter recovery","Claims 62x ROI, 75% ops efficiency","Vendor - treat cautiously"],
 ["nib","AU","Tealium + The Lumery","Unified profiles / personalization","+175% marketable leads (113M+ events)","Vendor"],
 ["USAA","US","Tealium EventStream","Real-time fraud signals","Data latency 1hr -> <1s","Vendor anecdote (no fraud-$ metric)"],
 ["Toggle (Farmers)","US","Twilio Segment","First-party audiences / lookalikes / retargeting","-67% CPA","Vendor"],
 ["The Zebra","US","Hightouch + Snowflake + Iterable","Conversion-event enrichment","+170% Facebook match rate, +50% email CTR","Vendor"],
 ["Liberty Mutual","US","(unspecified)","Predictive segmentation / retention","+15% retention","3rd-party aggregator"],
 ["Insurance Choice","UK","Optilead","Speed-to-lead dialer","+150% policies; ~80% abandoned quotes connected","Vendor"],
 ["John Hancock","US","Vitality + wearables","App engagement / wellness","20+ engagements/mo; Apple Watch users 7x more engaged","Company-direct + Conference Board (independent)"],
 ["Sedgwick","US","Microsoft (Sidekick agent)","Agentic claims processing","+30% claims-processing efficiency","Vendor blog"],
]
sheet2 = sheet_xml([nd_headers] + nd, nd_widths)

# ---------------- Sheet 3: Legend & Notes ----------------
lg_headers = ["Item", "Meaning / note"]
lg_widths = [30, 96]
lg = [
 ["PURPOSE","CDP-in-insurance use-case catalog + named deployments. Compiled 2026-05-31 from multi-source web research."],
 ["EVIDENCE LABELS",""],
 ["Vendor","Self-reported vendor/agency case study or marketing page. Treat metrics as directional marketing claims."],
 ["Vendor + independent","Vendor claim corroborated by an independent outlet or industry award (e.g., The Drum)."],
 ["Company-direct","Reported by the insurer itself (first-party; self-interested but not vendor marketing)."],
 ["3rd-party aggregator","Reported by a non-primary aggregator/listicle, not the insurer or vendor directly. Lower confidence."],
 ["Capability","A documented product mechanic - what the platform CAN do - not a measured insurer outcome."],
 ["Benchmark","Industry/vendor benchmark figure, frequently repeated across blogs without primary sourcing."],
 ["Adjacent","Banking/other-industry example included for mechanics; NOT an insurance result."],
 ["Under-evidenced","Use case asserted by vendors but with few named, quantified insurer deployments."],
 ["KEY CAVEATS",""],
 ["Page-fetch was blocked","Findings rest on search-result snippets, not full-page reads. Treat exact figures as 'as reported'."],
 ["Generali caveat","Insider AND Zeta both claim Generali with non-overlapping metrics - almost certainly different regional units. Never aggregate into one 'Generali result'."],
 ["Cookieless correction","Google did NOT kill third-party cookies; it retired most Privacy Sandbox APIs (Oct 2025). The shift is driven by Safari/Firefox/iOS + regulation."],
 ["Quarantined claims","The flashiest 'propensity routing -> call center' numbers (57.97%, 58%, 2x contactability) are TELCO/BANKING, not insurers. A 'Geico -20% cost-per-quote' claim has no primary source (likely fabricated)."],
 ["Salesforce note","Most 'Salesforce + insurer' relationships are CRM (Service/Marketing/Financial Services Cloud), NOT the Data Cloud CDP. Data Cloud is emerging in insurance (FSC for Insurance Brokerages); at Prudential it is 'in the future' while Adobe RT-CDP is the live CDP."],
 ["Most credible metrics","John Hancock Vitality (independent corroboration); Income Insurance operational renewal-rate shifts; the Velocify 25-carrier audit (2.3-day avg callback, ~40% never called)."],
]
sheet3 = sheet_xml([lg_headers] + lg, lg_widths)

# ---------------- Package ----------------
CT = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
 '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
 '<Default Extension="xml" ContentType="application/xml"/>'
 '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
 '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
 '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
 '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
 '<Override PartName="/xl/worksheets/sheet3.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
 '</Types>')

RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
 '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
 '</Relationships>')

WB = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
 '<sheets>'
 '<sheet name="Use Cases" sheetId="1" r:id="rId1"/>'
 '<sheet name="Named Deployments" sheetId="2" r:id="rId2"/>'
 '<sheet name="Legend &amp; Notes" sheetId="3" r:id="rId3"/>'
 '</sheets></workbook>')

WB_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
 '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
 '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>'
 '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet3.xml"/>'
 '<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
 '</Relationships>')

STYLES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
 '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
 '<fonts count="2">'
 '<font><sz val="11"/><color theme="1"/><name val="Calibri"/><family val="2"/></font>'
 '<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/><family val="2"/></font>'
 '</fonts>'
 '<fills count="3">'
 '<fill><patternFill patternType="none"/></fill>'
 '<fill><patternFill patternType="gray125"/></fill>'
 '<fill><patternFill patternType="solid"><fgColor rgb="FF305496"/><bgColor indexed="64"/></patternFill></fill>'
 '</fills>'
 '<borders count="2">'
 '<border><left/><right/><top/><bottom/><diagonal/></border>'
 '<border><left/><right/><top/><bottom style="thin"><color rgb="FFBFBFBF"/></bottom><diagonal/></border>'
 '</borders>'
 '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
 '<cellXfs count="3">'
 '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
 '<xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="left" vertical="center" wrapText="1"/></xf>'
 '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>'
 '</cellXfs>'
 '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
 '</styleSheet>')

out = "CDP-insurance-use-cases.xlsx"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", CT)
    z.writestr("_rels/.rels", RELS)
    z.writestr("xl/workbook.xml", WB)
    z.writestr("xl/_rels/workbook.xml.rels", WB_RELS)
    z.writestr("xl/styles.xml", STYLES)
    z.writestr("xl/worksheets/sheet1.xml", sheet1)
    z.writestr("xl/worksheets/sheet2.xml", sheet2)
    z.writestr("xl/worksheets/sheet3.xml", sheet3)
print("wrote", out, "rows:", len(uc), "deployments:", len(nd))
