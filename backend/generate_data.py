"""
Plum EMS — Synthetic Data Generator v2
1150+ realistic escalation records with realistic priority distribution.
Run: python generate_data.py
"""

import sqlite3, random, os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "plum_ems.db")

COMPANIES = [
    ("ABC Manufacturing Ltd","Enterprise",1200,"Manufacturing"),("GlobalLogic India","Enterprise",2800,"Technology"),
    ("Bharat Finance Corp","Enterprise",1800,"Finance"),("AlphaCorp Industries","Enterprise",3200,"Conglomerate"),
    ("Orion Technologies","Enterprise",950,"Technology"),("Metro Health Clinics","Enterprise",1500,"Healthcare"),
    ("Titan Forge Industries","Enterprise",2100,"Manufacturing"),("Prime Logistics","Enterprise",2400,"Logistics"),
    ("Hyperion Labs","Enterprise",880,"Pharma"),("Meridian Group","Enterprise",1900,"Conglomerate"),
    ("Cascade Retail","Enterprise",3400,"Retail"),("Vertex Systems","Enterprise",1100,"Technology"),
    ("Global Dynamics","Enterprise",2200,"Engineering"),("Omni Retail Chain","Enterprise",4100,"Retail"),
    ("Apex Pharma","Enterprise",1800,"Pharma"),("FastTrack Logistics","Enterprise",1350,"Logistics"),
    ("Zenith Corp","Enterprise",2600,"Conglomerate"),("Precision Engineering","Enterprise",980,"Engineering"),
    ("Horizon Capital","Enterprise",1600,"Finance"),("Star Manufacturing","Enterprise",1750,"Manufacturing"),
    ("TechSolutions Pvt Ltd","Mid-Market",350,"Technology"),("FinServe Ltd","Mid-Market",280,"Finance"),
    ("InnovaTech","Mid-Market",410,"Technology"),("SwiftPay Fintech","Mid-Market",190,"Fintech"),
    ("United Logistics","Mid-Market",320,"Logistics"),("Brightstar Textiles","Mid-Market",450,"Manufacturing"),
    ("CloudBase Technologies","Mid-Market",240,"Technology"),("NovaBuild","Mid-Market",380,"Construction"),
    ("Horizon Consulting","Mid-Market",210,"Consulting"),("FutureScape Technologies","Mid-Market",290,"Technology"),
    ("DataSurge Analytics","Mid-Market",175,"Analytics"),("IronCore Metals","Mid-Market",520,"Manufacturing"),
    ("PeakCommerce","Mid-Market",340,"E-commerce"),("Nuvama Wealth","Mid-Market",195,"Finance"),
    ("ClearVision Optics","Mid-Market",310,"Healthcare"),("Mosaic Media","Mid-Market",155,"Media"),
    ("TrustedCure Pharma","Mid-Market",480,"Pharma"),("ZestMart","Mid-Market",225,"Retail"),
    ("BlueSky Aviation","Mid-Market",430,"Aviation"),("Greenfield Farms","Mid-Market",260,"Agriculture"),
    ("Sunrise Retail","SME",45,"Retail"),("Nexus Startups","SME",28,"Technology"),
    ("Pixel Studios","SME",35,"Media"),("QuickCommerce","SME",62,"E-commerce"),
    ("AquaTech Solutions","SME",48,"Environment"),("EduFirst Academy","SME",72,"Education"),
    ("RoboWorks","SME",38,"Robotics"),("PureTech Labs","SME",55,"Technology"),
    ("Springboard Academy","SME",90,"Education"),("FreshMart","SME",44,"Food"),
    ("DataSys India","SME",67,"Technology"),("SwiftByte","SME",31,"Technology"),
    ("UrbanNest","SME",58,"Real Estate"),("GreenPath Organics","SME",42,"Food"),
    ("CraftCircle","SME",29,"Retail"),("ByteForge","SME",76,"Technology"),
    ("MindSpring Wellness","SME",33,"Healthcare"),("TalentBridge","SME",61,"HR"),
    ("QuickFix Services","SME",47,"Services"),("BoldBrew","SME",24,"Food"),
]

OWNERS = ["avik.bhandari","priya.menon","rahul.nair","neha.sharma","deepak.verma",
          "sunita.patel","ankit.joshi","ritu.gupta","karan.mehta","divya.krishnan",
          "rohan.sinha","swati.kapoor","manish.tiwari","pooja.agarwal","siddharth.rao"]

# (department, base_urgency 0-10, escalation_probability)
ISSUE_TYPES = {
    "Claims Delay":("Claims",7,0.88),"Cashless Denial":("Claims",9,0.94),
    "Claim Rejection":("Claims",8,0.90),"Maternity Claim Denied":("Claims",7,0.86),
    "Claims Expedite":("Claims",5,0.72),"Legal Notice":("Claims",10,0.99),
    "Social Media Risk":("Claims",9,0.97),"Health ID Not Issued":("Account Management",5,0.80),
    "Employee Addition Delay":("Account Management",5,0.76),"Policy Issuance Delay":("Account Management",6,0.80),
    "Policy Activation Failure":("Account Management",8,0.91),"Renewal Delay":("Account Management",7,0.85),
    "Communication Gap":("Account Management",3,0.60),"Super Top-Up Enrollment":("Account Management",3,0.55),
    "Data Integrity Issue":("Account Management",7,0.85),"Compliance Documentation":("Account Management",6,0.75),
    "Coverage Clarification":("Account Management",2,0.20),"Report Request":("Account Management",1,0.12),
    "Bulk Data Update":("Account Management",2,0.15),"Training Request":("Account Management",1,0.10),
    "Employee Deletion":("Account Management",2,0.18),"Tech/Portal Issue":("Engineering",6,0.80),
    "Tech/Integration Issue":("Engineering",7,0.84),"Document Upload Failure":("Engineering",5,0.75),
    "App Data Mismatch":("Engineering",6,0.78),"SSO Integration Broken":("Engineering",7,0.83),
    "Billing Dispute":("Finance",6,0.76),"Invoice/Tax Document":("Finance",3,0.55),
    "Wrong Premium Charged":("Finance",6,0.78),"Payment Confirmation Delay":("Finance",4,0.65),
    "New Business Lead":("Sales",0,0.04),"Positive Feedback":("Account Management",0,0.02),
    "Service Quality Feedback":("Operations",2,0.28),"Internal Data Update":("Operations",1,0.05),
}

HOSPITALS = ["Apollo Hospital","Fortis Healthcare","Max Hospital","AIIMS","Manipal Hospital",
             "Medanta","Columbia Asia","Narayana Health","Kokilaben Hospital","Sir Ganga Ram Hospital"]
PROCS = ["cardiac surgery","emergency appendectomy","chemotherapy","dialysis","ICU admission",
         "maternity delivery","neurological procedure","orthopedic surgery"]
REJECT_REASONS = ["pre-existing condition not disclosed","policy lapse","waiting period not completed",
                  "documents incomplete","treatment not covered","duplicate claim"]
DENIAL_REASONS = ["policy not active in system","employee not enrolled","network hospital not verified",
                  "pre-authorization expired","incorrect policy number"]

def rdate(start=90, end=0):
    now = datetime(2026,3,20,12,0,0)
    return now - timedelta(days=random.randint(end,start), hours=random.randint(8,19), minutes=random.randint(0,59))

def emp():
    f=random.choice(["Rahul","Priya","Suresh","Ananya","Deepak","Sunita","Karan","Divya","Amit","Neha",
                     "Ravi","Kavitha","Sanjay","Meena","Vikram","Pooja","Arun","Nisha","Ganesh","Anjali"])
    l=random.choice(["Kumar","Sharma","Patel","Nair","Singh","Gupta","Reddy","Iyer","Mehta","Joshi",
                     "Pillai","Rao","Verma","Kapoor","Mishra","Sinha","Bhat","Naik","Arora","Tiwari"])
    return f"{f} {l}"

def make_content(issue_type, company, owner_name):
    d = random.randint(3,45)
    cnt = random.randint(2,60)
    amt = random.randint(50,800)*1000
    hosp = random.choice(HOSPITALS)
    emp_name = emp()
    clm = f"CLM{random.randint(10000000,99999999)}"
    deny = random.choice(DENIAL_REASONS)
    rej = random.choice(REJECT_REASONS)

    templates = {
        "Claims Delay": [
            f"Dear {owner_name}, Claim #{clm} for employee {emp_name} has been pending {d} days with no update. Multiple follow-ups unanswered. Employee is in financial distress. Please escalate immediately.",
            f"Following up on claim #{clm} — this is our {random.randint(2,7)}th attempt. Still 'under process' after {d} days. We need a clear resolution timeline or will escalate to IRDAI.",
            f"Hi {owner_name}, this is regarding the claim we raised for {emp_name} back on {(datetime(2026,3,20)-timedelta(days=d)).strftime('%B %d')}. The TPA has not moved on this despite our reminders. Can you personally step in?",
        ],
        "Cashless Denial": [
            f"URGENT — {emp_name} admitted at {hosp} for emergency {random.choice(PROCS)}. Cashless request denied citing '{deny}'. This is factually incorrect. Please resolve within 2 hours or we will proceed with reimbursement and hold Plum accountable for delay.",
            f"Pre-auth rejected for {emp_name} at {hosp}. Patient in ICU. Denial reason is wrong per our active policy terms. Immediate escalation to insurer required. Please call me directly.",
        ],
        "Claim Rejection": [
            f"Claim #{clm} for {emp_name} has been rejected citing '{rej}'. We strongly dispute this. Please review policy clause {random.randint(3,15)}.{random.randint(1,8)} and reverse the decision.",
            f"Second rejection for claim #{clm}. All documents were submitted twice. This rejection is completely unacceptable. We are formally escalating.",
        ],
        "Policy Activation Failure": [
            f"Renewal payment of Rs {amt:,} was made {d} days ago. Policy still showing inactive. Two employees were denied cashless treatment this week because of this. Activate immediately — this is a breach of contract.",
            f"Policy inactive despite payment confirmation. One of our employees is scheduled for surgery tomorrow. Please activate by tonight, failing which we will pursue legal action.",
        ],
        "Health ID Not Issued": [
            f"{cnt} employees from our onboarding batch still don't have health IDs after {d} days. One employee was turned away at a network hospital last week. Please escalate to the onboarding team urgently.",
            f"Following up for the 4th time — health IDs not issued despite {d} days passing. The SLA is 3-5 working days. Our employees are currently uninsured in practice.",
        ],
        "Renewal Delay": [
            f"Policy expiring in {random.randint(3,10)} days. Renewal quote was requested {d} days ago — still no response. This puts {cnt} employees' coverage at risk. Please share the quote by EOD.",
            f"Critical: Policy lapse in {random.randint(3,8)} days. Renewal not initiated despite multiple follow-ups over {d} days. If not resolved by tomorrow, I am escalating to your CEO.",
        ],
        "Legal Notice": [
            f"We hereby serve formal legal notice regarding claim #{clm}. Despite {d} days and multiple escalations, the claim remains unresolved. If not addressed within 48 hours, we will file with IRDAI + Consumer Forum.",
            f"Final notice before IRDAI escalation. Claim #{clm} wrongfully rejected {d} days ago. 24-hour window to resolve. Please loop in your legal and compliance teams immediately.",
        ],
        "Social Media Risk": [
            f"Heads up — our {random.choice(['CFO','HR Director','CEO'])} is threatening to post about the {d}-day claim delay on LinkedIn. A draft post is circulating internally. Immediate resolution required to prevent viral escalation.",
            f"One of our employees has already started a thread about claim #{clm} on LinkedIn. 80+ engagements as of this morning. Please expedite this urgently and issue a direct client communication.",
        ],
        "Tech/Portal Issue": [
            f"Portal has been showing error code {random.choice(['503','AUTH_FAILED','TIMEOUT','DB_ERR'])} for the past {d} days. {cnt} employees cannot access their benefits. 3 tickets raised — still no resolution. Engineering team must be looped in.",
            f"Document upload has been failing on the Plum portal. Claim documents for {emp_name} cannot be submitted electronically. This is adding another {d}-day delay on top of the original claim issue.",
        ],
        "Billing Dispute": [
            f"The invoice received shows Rs {amt:,}, which is Rs {random.randint(5,80)*1000:,} more than the quoted premium. No prior communication about any change. Please send a detailed explanation and arrange a refund by month-end.",
            f"Premium auto-deducted this month is incorrect — overcharged by Rs {random.randint(10,60)*1000:,}. Our finance team has flagged this. Please investigate and reverse.",
        ],
        "Employee Addition Delay": [
            f"We made a payment {d} days ago to add {cnt} new employees to the policy. SLA is 3-5 business days. None of them have been added yet. One employee visited a hospital and was turned away uninsured. This needs to be resolved today.",
        ],
        "SSO Integration Broken": [
            f"After last week's Plum platform update, SSO is completely broken for our org. {cnt} employees cannot log in at all. Our IT team has confirmed it's a server-side issue. Please escalate to your engineering team with a 4-hour resolution target.",
        ],
        "Coverage Clarification": [
            f"One of our employees needs {random.choice(['mental health in-patient care','fertility treatment','dental surgery','physiotherapy'])}. Can you confirm if this is covered under our current plan before we advise them?",
        ],
        "Compliance Documentation": [
            f"We are under a regulatory audit. The auditors require all insurance policy documents and member data for {cnt} employees by {(datetime(2026,3,20)+timedelta(days=random.randint(2,5))).strftime('%b %d')}. Please coordinate with your documentation team immediately.",
        ],
        "Report Request": [
            f"The quarterly utilization report is pending. We have a board presentation next week. Please share Q{random.randint(1,4)} analysis with department-wise claims breakdown as soon as possible.",
        ],
        "Training Request": [
            f"The generic onboarding session last Thursday was not sufficient for our HR team. We need a dedicated 60-minute session covering the portal, claims process, and the wellness features. Please schedule.",
        ],
        "Positive Feedback": [
            f"Just wanted to share — {emp_name}'s claim was processed in just 3 days. The team was extremely responsive and helpful throughout. Great experience! Please pass on our appreciation.",
        ],
        "Service Quality Feedback": [
            f"{emp_name} was asked to submit the same document 4 different times by the TPA coordinator. The coordinator was also rude on call. Flagging this for your awareness and for process improvement.",
        ],
        "Internal Data Update": [
            f"@{owner_name} please update the GWP on Salesforce for the {company} renewal — INR {amt:,} + GST. Also update renewal date.",
        ],
        "Data Integrity Issue": [
            f"All employee data on the portal is showing incorrectly — wrong employee IDs, incorrect premium amounts, wrong policy dates. It appears to be a data migration error during onboarding. We need a full data audit immediately.",
        ],
        "Wrong Premium Charged": [
            f"This month's premium deduction does not match our policy documents. We are being overcharged by Rs {random.randint(10,60)*1000:,}. This is the second month this has happened. Please investigate and process a refund.",
        ],
    }
    options = templates.get(issue_type, [f"We have an issue regarding {issue_type} for our account. Multiple follow-ups have gone unanswered. Please resolve at the earliest."])
    return random.choice(options)

def make_subject(issue_type, d):
    subjects = {
        "Claims Delay": [f"Claim pending {d} days — urgent escalation needed","Follow-up: claim not resolved — 3rd reminder","Escalation: claim stuck at TPA for {d} days"],
        "Cashless Denial": ["URGENT: Cashless denied — patient admitted now","Emergency — cashless rejected, please intervene","Pre-auth rejected — patient in ICU"],
        "Claim Rejection": ["Claim wrongfully rejected — formal appeal","Rejection reason incorrect — please review","Dispute: claim rejection — policy clause violation"],
        "Policy Activation Failure": ["Policy inactive despite payment — urgent","Renewal done — still showing inactive","Coverage gap — activate immediately"],
        "Health ID Not Issued": [f"Health IDs not issued — {d} days since onboarding","Employee health cards still pending","New joiners without health ID — hospital visit failed"],
        "Renewal Delay": [f"Policy expiring in {random.randint(3,10)} days — no quote received","Renewal pending — coverage at risk","Urgent: policy lapse imminent"],
        "Legal Notice": ["Legal notice: unresolved claim — 48hr window","IRDAI complaint — final notice before filing","Consumer court filing — notice served"],
        "Social Media Risk": ["Client threatening LinkedIn post — urgent","Reputation risk: viral complaint starting","Urgent: social media escalation in progress"],
        "Tech/Portal Issue": ["Portal not accessible — {d} days","Error on document upload — claim delayed","App showing error — engineering needed now"],
        "Billing Dispute": ["Wrong premium charged this month","Invoice discrepancy — refund requested","Billing error — Rs {amt} overcharge"],
        "Employee Addition Delay": ["New employees not added to policy — SLA missed","Addition pending past deadline","New joiners uninsured — hospital visit failed"],
        "SSO Integration Broken": ["SSO broken after platform update","Portal login not working — mass failure","Authentication error — employees locked out"],
        "Coverage Clarification": ["Coverage query before scheduling treatment","Is this procedure covered under our plan?","Pre-authorization — coverage clarification needed"],
        "Compliance Documentation": ["Regulatory audit: insurance documents needed urgently","Policy documents for audit","Compliance documents request — deadline approaching"],
        "Report Request": ["Q4 utilization report needed for board","Quarterly claims analysis requested","Insurance data for board meeting"],
        "Training Request": ["Request: dedicated Plum portal training session","HR team training on claims process"],
        "Positive Feedback": ["Great experience — thank you Plum team!","Excellent service — claim resolved fast"],
        "Service Quality Feedback": ["TPA process feedback — document requested 4 times","Coordinator experience complaint — please review"],
        "Internal Data Update": ["SF update needed — renewal GWP","Salesforce GWP update for renewal"],
        "Data Integrity Issue": ["Wrong data across portal — urgent audit needed","Employee data mismatch — requires fix","Coverage amount incorrect — data error"],
        "Wrong Premium Charged": ["Premium overcharged — refund needed","Invoice amount incorrect — second month running"],
    }
    options = subjects.get(issue_type, [f"{issue_type} — action required"])
    subj = random.choice(options)
    return subj.replace("{d}", str(d)).replace("{amt}", str(random.randint(50,500)*1000))

ACTION_MAP = {
    "Claims Delay":"Escalate to TPA claims desk. Confirm all documents received. Set 24h resolution SLA. Give client written timeline.",
    "Cashless Denial":"Call TPA emergency line immediately. Override if policy is confirmed active. Coordinate directly with hospital authorization team.",
    "Claim Rejection":"Compare rejection reason against policy terms. If wrongful, raise formal reversal request with insurer with all supporting documents.",
    "Health ID Not Issued":"Raise bulk ID generation request with onboarding team. Set 24h ETA. Communicate progress to client daily.",
    "Policy Activation Failure":"Verify payment receipt. Trigger manual policy activation. Confirm coverage confirmation letter to client within 2h.",
    "Renewal Delay":"Share renewal quote by EOD. Issue temporary coverage confirmation. Confirm no gap in coverage.",
    "Legal Notice":"Immediately loop in Legal + Compliance. Assign senior POC. Resolve within 48h to avoid IRDAI escalation.",
    "Social Media Risk":"Resolve root cause urgently. Alert brand/communications team. Senior leadership to make personal client call.",
    "Tech/Portal Issue":"Raise P1 engineering ticket. Provide alternate document submission channel to client immediately. Set 4h resolution target.",
    "Billing Dispute":"Finance team to verify invoice vs contract. Reverse excess amount if confirmed. Issue written apology and credit note.",
    "Employee Addition Delay":"Verify payment receipt. Manual addition processing today. Confirm enrollment with policy card to client by EOD.",
    "Data Integrity Issue":"Freeze all account operations. Full data audit against master enrollment file. Re-process with correct data within 48h.",
    "Compliance Documentation":"Documentation team to compile full set. Share via secure link by regulatory deadline. Assign single POC.",
    "Coverage Clarification":"Review policy terms. Respond in writing within same business day. Do not leave client in ambiguity before treatment.",
    "Training Request":"Schedule dedicated 60-min session within 5 business days. Share calendar invite with agenda.",
    "Report Request":"Generate full utilization report from analytics dashboard. Share formatted PDF within 2 business days.",
    "SSO Integration Broken":"Raise P1 ticket with engineering. Investigate post-update regression. Communicate 4h ETA to client. Offer manual portal access as bridge.",
    "New Business Lead":"Forward to Sales team with account context. Follow up within 48h.",
    "Internal Data Update":"Update Salesforce opportunity fields. Confirm with account team lead.",
    "Positive Feedback":"Log feedback in CRM. Share appreciation note with TPA resolution team. Consider for team recognition.",
    "Service Quality Feedback":"Log formal complaint. Review call recording with TPA supervisor. Share corrective action plan within 3 days.",
    "Wrong Premium Charged":"Finance to verify premium calculation vs policy schedule. Reverse overcharge. Issue corrected invoice with apology.",
    "Document Upload Failure":"Raise portal bug ticket. Offer email submission as immediate workaround. Share resolution ETA.",
    "App Data Mismatch":"Engineering to investigate data sync issue. Verify correct coverage terms. Confirm to client in writing.",
    "Super Top-Up Enrollment":"Send enrollment communication to all employees immediately. Extend deadline if window is closing.",
    "Payment Confirmation Delay":"Finance to confirm payment receipt. Share official acknowledgment letter within 24h.",
    "Maternity Claim Denied":"Review maternity benefit clause in policy. If coverage confirmed, raise immediate reversal request with insurer.",
    "Claims Expedite":"Prioritize with TPA claims desk. Set daily status update cadence. Senior POC to track personally.",
    "Bulk Data Update":"Operations team to process in batch. Confirm completion with audit trail within 3 business days.",
    "Communication Gap":"Review all prior communication. Assign dedicated SPOC to client. Set weekly check-in cadence.",
    "Employee Deletion":"Process deletion in system today. Confirm with timestamp and policy endorsement to client.",
    "Policy Issuance Delay":"Check payment + KYC completeness. Manual issuance processing. Confirm policy document delivery within 24h.",
    "Invoice/Tax Document":"Finance to generate and share GST invoice within 48h.",
    "Tech/Integration Issue":"Engineering to check API sync logs. Identify integration break point. ETA to client within 6h.",
}

AI_SUMMARY_MAP = {
    "Claims Delay": lambda c,sz,d: f"{sz} client {c} reporting {d}-day claim processing delay. TPA escalation + written resolution timeline required within 24 hours.",
    "Cashless Denial": lambda c,sz,d: f"Emergency cashless denied for {c} employee at hospital. Patient admitted. Requires immediate TPA override — incorrect denial reason cited.",
    "Claim Rejection": lambda c,sz,d: f"{c} disputing claim rejection — reason cited does not align with policy terms. Likely wrongful rejection requiring insurer formal reversal.",
    "Policy Activation Failure": lambda c,sz,d: f"{c} policy inactive {d} days post renewal payment. Two employees already denied treatment. Manual activation + confirmation letter needed within 2h.",
    "Health ID Not Issued": lambda c,sz,d: f"Onboarding gap at {c} — health IDs unissued after {d} days. Employee turned away at hospital. Bulk issuance to onboarding team required today.",
    "Renewal Delay": lambda c,sz,d: f"{c} policy at risk of lapsing. Renewal quote not provided despite {d}-day wait. Coverage gap for entire workforce — senior escalation needed.",
    "Legal Notice": lambda c,sz,d: f"Formal legal notice from {c}. 48-hour window before IRDAI + Consumer Court filing. Legal + Compliance must engage immediately.",
    "Social Media Risk": lambda c,sz,d: f"{c} client threatening public LinkedIn post about {d}-day delay. Active brand damage risk. Immediate resolution + leadership outreach required.",
    "Tech/Portal Issue": lambda c,sz,d: f"Portal outage blocking {c} employees from claims and benefits. P1 engineering ticket + alternate channel for client needed within 4h.",
    "Billing Dispute": lambda c,sz,d: f"{c} overbilled without advance notice. Finance investigation + reversal needed. Risk of payment hold and relationship damage.",
    "Data Integrity Issue": lambda c,sz,d: f"Systemic data error across {c} account — wrong EIDs, premiums, policy dates. Full data audit + re-processing required before next hospital visit.",
    "SSO Integration Broken": lambda c,sz,d: f"SSO broken post platform update at {c}. Mass login failure for employees. P1 engineering ticket required with 4-hour resolution target.",
    "Employee Addition Delay": lambda c,sz,d: f"New employees at {c} uninsured {d} days post payment. One already denied at hospital. Operations must process manual addition today.",
    "Wrong Premium Charged": lambda c,sz,d: f"{c} overcharged on premium — second occurrence. Finance must verify and reverse. Risk of trust erosion + payment escalation.",
}

def get_summary(issue, company, size, delay):
    fn = AI_SUMMARY_MAP.get(issue)
    if fn: return fn(company, size, delay)
    dept,_,_ = ISSUE_TYPES.get(issue, ("Operations",3,0.4))
    return f"{company} raised a {issue} concern ({size} account) requiring prompt attention from the {dept} team. Assign and resolve within SLA."

def score(issue, size, delay, sentiment, is_esc):
    if not is_esc: return random.randint(0, 4)
    _,urg,_ = ISSUE_TYPES.get(issue, ("Ops",3,0.4))
    # Tighter weights to get realistic distribution
    sw = {"Enterprise":4,"Mid-Market":2.5,"SME":1.5}.get(size, 1.5)
    dw = 3 if delay>30 else 2 if delay>14 else 1 if delay>7 else 0.5 if delay>3 else 0
    mw = {"Angry":2.5,"Frustrated":1.5,"Neutral":0,"Positive":-1}.get(sentiment,0)
    raw = sw + urg*1.1 + dw + mw + random.uniform(-1.5, 1.5)
    return max(0, min(25, int(raw)))

def plabel(sc, is_esc):
    if not is_esc: return "Low"
    if sc >= 16: return "Critical"
    if sc >= 10: return "High"
    if sc >= 5: return "Medium"
    return "Low"

def generate():
    records = []
    now = datetime(2026,3,20,12,0,0)
    slack_users = ["ananya.nair","rajesh.mehta","vikram.sharma","priya.iyer","suresh.patel",
                   "kavitha.ram","deepak.joshi","nisha.kapoor","arun.chacko","manashi.roy",
                   "vidushi.m","mikhel.dhiman","smita.joshi","ankur.bansal","sonali.gupta"]
    wa_nums = [f"+91-{random.randint(7000000000,9999999999)}" for _ in range(60)]

    for _ in range(1150):
        comp, acc_size, emp_cnt, industry = random.choice(COMPANIES)
        issue, (dept, urg, esc_prob) = random.choice(list(ISSUE_TYPES.items()))
        source = random.choices(["Email","Slack","WhatsApp"],[0.45,0.35,0.20])[0]

        domain = comp.lower().replace(" ","").replace(",","")[:12].replace("/","") + ".com"
        roles = {"Enterprise":[("hr.head","HR Head"),("cfo","CFO"),("legal","Legal"),("it","IT Head"),("ceo","CEO")],
                 "Mid-Market":[("hr","HR Manager"),("finance","Finance"),("admin","Admin"),("operations","Ops")],
                 "SME":[("hr","HR"),("admin","Owner"),("info","Manager")]}
        r_email,_ = random.choice(roles.get(acc_size, roles["SME"]))

        if source=="Email":
            from_addr = f"{r_email}@{domain}"
            to_addr = f"{random.choice(OWNERS)}@plum.com"
            cc = f"hr@{domain}" if random.random()>0.6 else ""
        elif source=="Slack":
            from_addr = random.choice(slack_users)
            to_addr = random.choice(OWNERS)
            cc = random.choice(OWNERS) if random.random()>0.5 else ""
        else:
            from_addr = random.choice(wa_nums)
            to_addr = "+91-8765432109"
            cc = ""

        is_esc = random.random() < esc_prob
        delay = random.choices([0,1,3,7,14,21,30,45],[5,8,10,15,20,18,15,9])[0] + random.randint(0,4) if is_esc else random.choices([0,1,3],[60,25,15])[0]
        sentiment = random.choices(["Angry","Frustrated","Neutral"],[30,45,25])[0] if is_esc else random.choices(["Neutral","Positive","Frustrated"],[55,30,15])[0]
        ts = rdate(90,0)
        owner_name = to_addr.split("@")[0] if "@" in to_addr else to_addr
        content = make_content(issue, comp, owner_name.split(".")[0].capitalize())
        subject = make_subject(issue, delay)
        action = ACTION_MAP.get(issue, f"Review and resolve {issue} within SLA.")
        sc = score(issue, acc_size, delay, sentiment, is_esc)
        priority = plabel(sc, is_esc)

        age = (now-ts).days
        if age>14:
            sw = {"Critical":[0.1,0.2,0.1,0.6],"High":[0.2,0.2,0.1,0.5],"Medium":[0.15,0.3,0.05,0.5],"Low":[0.1,0.1,0.0,0.8]}
        elif age>7:
            sw = {"Critical":[0.25,0.4,0.2,0.15],"High":[0.3,0.4,0.1,0.2],"Medium":[0.3,0.4,0.05,0.25],"Low":[0.2,0.2,0.0,0.6]}
        else:
            sw = {"Critical":[0.5,0.3,0.15,0.05],"High":[0.5,0.3,0.1,0.1],"Medium":[0.5,0.3,0.05,0.15],"Low":[0.6,0.15,0.0,0.25]}
        status = random.choices(["Open","In Progress","Blocked","Closed"], sw.get(priority,[0.4,0.3,0.1,0.2]))[0]

        if status in ["Closed","In Progress"] or priority=="Critical" or random.random()>0.35:
            assigned_owner = random.choice(OWNERS)
        else:
            assigned_owner = None

        sla_t = {"Critical":1,"High":3,"Medium":7,"Low":14}.get(priority,7)
        sla_breach = is_esc and delay>sla_t and status!="Closed"

        if status=="Closed":
            res_days = random.randint(1, max(2, delay+3))
            resolved_at = (ts+timedelta(days=res_days)).strftime("%Y-%m-%d %H:%M:%S")
            tat = res_days*random.randint(6,20)
        else:
            resolved_at = None
            tat = (now-ts).days*random.randint(4,12) if status!="Open" else None

        ai_sum = get_summary(issue, comp, acc_size, delay)
        tags = ",".join(random.sample(["urgent","tpa","claim","renewal","tech","finance","hr","compliance","legal","billing"],k=random.randint(1,3)))

        records.append((source, ts.strftime("%Y-%m-%d %H:%M:%S"), from_addr, to_addr, cc,
            comp, acc_size, industry, emp_cnt, subject, content,
            1 if is_esc else 0, priority, sc, issue, dept,
            sentiment, delay, action, ai_sum, status, assigned_owner,
            1 if sla_breach else 0, resolved_at, tat,
            ts.strftime("%Y-%m-%d %H:%M:%S"), ts.strftime("%Y-%m-%d %H:%M:%S"), tags))
    return records

def create_db(records):
    if os.path.exists(DB_PATH): os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE escalations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT, timestamp TEXT, from_address TEXT, to_address TEXT, cc TEXT,
        account_name TEXT, account_size TEXT, industry TEXT, employee_count INTEGER,
        subject TEXT, content TEXT, is_escalation INTEGER, priority TEXT, priority_score INTEGER,
        issue_type TEXT, department TEXT, sentiment TEXT, delay_days INTEGER,
        action_required TEXT, ai_summary TEXT, status TEXT, assigned_owner TEXT,
        sla_breach INTEGER, resolved_at TEXT, tat_hours INTEGER,
        created_at TEXT, updated_at TEXT, tags TEXT
    )""")
    c.executemany("INSERT INTO escalations VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", records)
    conn.commit()
    for idx in ["priority","status","account_name","department","is_escalation","assigned_owner","timestamp","issue_type"]:
        c.execute(f"CREATE INDEX idx_{idx} ON escalations({idx})")

    # Create external data tables for Slack & Gmail integration
    c.execute("""CREATE TABLE oauth_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT UNIQUE,
        access_token TEXT,
        refresh_token TEXT,
        expires_at TEXT,
        created_at TEXT
    )""")

    c.execute("""CREATE TABLE slack_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_id TEXT,
        channel_name TEXT,
        user_id TEXT,
        user_name TEXT,
        message TEXT,
        timestamp TEXT,
        is_escalation INTEGER DEFAULT 0,
        escalation_type TEXT,
        priority TEXT,
        created_at TEXT
    )""")

    c.execute("""CREATE TABLE gmail_emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message_id TEXT UNIQUE,
        from_email TEXT,
        subject TEXT,
        body TEXT,
        labels TEXT,
        timestamp TEXT,
        is_escalation INTEGER DEFAULT 0,
        escalation_type TEXT,
        priority TEXT,
        created_at TEXT
    )""")

    conn.commit(); conn.close()
    esc = [r for r in records if r[11]]
    print(f"✅ Database: {DB_PATH}")
    print(f"   Total     : {len(records)}")
    print(f"   Escalation: {len(esc)}")
    for p in ["Critical","High","Medium","Low"]:
        print(f"   {p:10}: {sum(1 for r in records if r[13]==p)}")
    print(f"   SLA Breach: {sum(1 for r in records if r[23])}")
    print(f"   Open      : {sum(1 for r in records if r[21]=='Open')}")
    print(f"   Closed    : {sum(1 for r in records if r[21]=='Closed')}")

if __name__=="__main__":
    print("🔄 Generating 1150+ escalation records...")
    create_db(generate())
    print("✅ Done!")
