from flask import Flask, jsonify, request, send_from_directory, redirect
import sqlite3, os, tempfile, json, uuid
from datetime import datetime, timedelta
import sys
try:
    import pandas as pd
    HAS_PANDAS = True
except:
    HAS_PANDAS = False

from integrations import fetch_slack_data, fetch_gmail_data, get_slack_messages, get_gmail_emails, get_external_escalations, save_token, start_scheduler, get_sync_status

# Initialize Flask WITHOUT automatic static folder
app = Flask(__name__, static_folder=None, static_url_path=None)
DB_PATH = os.path.join(os.path.dirname(__file__), "plum_ems.db")
UPLOAD_DATA = {}  # temp storage for uploaded file data: {file_id: dataframe}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def q(sql, params=(), one=False):
    conn = get_db()
    try:
        cur = conn.execute(sql, params)
        rows = cur.fetchall()
        return (dict(rows[0]) if rows else None) if one else [dict(r) for r in rows]
    finally:
        conn.close()

def ex(sql, params=()):
    conn = get_db()
    try: conn.execute(sql, params); conn.commit()
    finally: conn.close()

@app.after_request
def cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp

@app.route("/")
def index():
    return send_from_directory(os.path.join(os.path.dirname(__file__), "../frontend"), "index.html")

@app.route("/api/dashboard/stats")
def dash_stats():
    s = {}
    s["total"] = q("SELECT COUNT(*) c FROM escalations", one=True)["c"]
    s["escalations"] = q("SELECT COUNT(*) c FROM escalations WHERE is_escalation=1", one=True)["c"]
    s["open"] = q("SELECT COUNT(*) c FROM escalations WHERE status='Open' AND is_escalation=1", one=True)["c"]
    s["in_progress"] = q("SELECT COUNT(*) c FROM escalations WHERE status='In Progress' AND is_escalation=1", one=True)["c"]
    s["blocked"] = q("SELECT COUNT(*) c FROM escalations WHERE status='Blocked' AND is_escalation=1", one=True)["c"]
    s["closed"] = q("SELECT COUNT(*) c FROM escalations WHERE status='Closed' AND is_escalation=1", one=True)["c"]
    s["critical_open"] = q("SELECT COUNT(*) c FROM escalations WHERE priority='Critical' AND status!='Closed' AND is_escalation=1", one=True)["c"]
    s["sla_breaches"] = q("SELECT COUNT(*) c FROM escalations WHERE sla_breach=1 AND status!='Closed'", one=True)["c"]
    s["avg_delay"] = round(q("SELECT AVG(delay_days) a FROM escalations WHERE is_escalation=1", one=True)["a"] or 0, 1)
    s["avg_tat_hours"] = round(q("SELECT AVG(tat_hours) a FROM escalations WHERE status='Closed' AND tat_hours IS NOT NULL", one=True)["a"] or 0)
    for p in ["Critical","High","Medium","Low"]:
        s[f"priority_{p.lower()}"] = q("SELECT COUNT(*) c FROM escalations WHERE priority=? AND is_escalation=1",(p,),one=True)["c"]
    for src in ["Email","Slack","WhatsApp"]:
        s[f"source_{src.lower()}"] = q("SELECT COUNT(*) c FROM escalations WHERE source=? AND is_escalation=1",(src,),one=True)["c"]
    today = "2026-03-20"
    yesterday = "2026-03-19"
    s["today_new"] = q("SELECT COUNT(*) c FROM escalations WHERE timestamp LIKE ? AND is_escalation=1",(f"{today}%",),one=True)["c"]
    s["yesterday_new"] = q("SELECT COUNT(*) c FROM escalations WHERE timestamp LIKE ? AND is_escalation=1",(f"{yesterday}%",),one=True)["c"]
    s["unassigned_critical"] = q("SELECT COUNT(*) c FROM escalations WHERE priority='Critical' AND assigned_owner IS NULL AND status!='Closed'",one=True)["c"]
    return jsonify(s)

@app.route("/api/dashboard/top")
def dash_top():
    limit = int(request.args.get("limit", 15))
    return jsonify(q("""SELECT id,account_name,account_size,subject,priority,priority_score,
        issue_type,department,sentiment,delay_days,status,assigned_owner,
        source,timestamp,sla_breach,action_required,ai_summary
        FROM escalations WHERE is_escalation=1 AND status!='Closed'
        ORDER BY priority_score DESC, delay_days DESC LIMIT ?""",(limit,)))

@app.route("/api/dashboard/trend")
def dash_trend():
    days = int(request.args.get("days", 30))
    base = datetime(2026,3,20)
    rows = []
    for d in range(days,-1,-1):
        date = (base - timedelta(days=d)).strftime("%Y-%m-%d")
        total = q("SELECT COUNT(*) c FROM escalations WHERE timestamp LIKE ?",(f"{date}%",),one=True)["c"]
        esc   = q("SELECT COUNT(*) c FROM escalations WHERE timestamp LIKE ? AND is_escalation=1",(f"{date}%",),one=True)["c"]
        crit  = q("SELECT COUNT(*) c FROM escalations WHERE timestamp LIKE ? AND priority='Critical'",(f"{date}%",),one=True)["c"]
        rows.append({"date":date,"total":total,"escalations":esc,"critical":crit})
    return jsonify(rows)

@app.route("/api/dashboard/owner-workload")
def owner_workload():
    return jsonify(q("""SELECT assigned_owner,COUNT(*) total,
        SUM(CASE WHEN status='Open' THEN 1 ELSE 0 END) open_count,
        SUM(CASE WHEN status='In Progress' THEN 1 ELSE 0 END) in_progress,
        SUM(CASE WHEN status='Blocked' THEN 1 ELSE 0 END) blocked,
        SUM(CASE WHEN priority='Critical' AND status!='Closed' THEN 1 ELSE 0 END) critical_open,
        SUM(CASE WHEN sla_breach=1 THEN 1 ELSE 0 END) sla_breaches
        FROM escalations WHERE assigned_owner IS NOT NULL AND is_escalation=1 AND status!='Closed'
        GROUP BY assigned_owner ORDER BY total DESC"""))

@app.route("/api/dashboard/dept-summary")
def dept_summary():
    return jsonify(q("""SELECT department,COUNT(*) total,
        SUM(CASE WHEN status!='Closed' THEN 1 ELSE 0 END) open_total,
        SUM(CASE WHEN priority='Critical' THEN 1 ELSE 0 END) critical,
        SUM(CASE WHEN sla_breach=1 THEN 1 ELSE 0 END) sla_breaches,
        ROUND(AVG(delay_days),1) avg_delay
        FROM escalations WHERE is_escalation=1 GROUP BY department ORDER BY open_total DESC"""))

@app.route("/api/escalations")
def get_escalations():
    page = int(request.args.get("page",1))
    per_page = int(request.args.get("per_page",25))
    where, params = [], []
    for col,arg in [("source","source"),("priority","priority"),("status","status"),
                    ("department","department"),("account_size","account_size"),("assigned_owner","owner")]:
        v = request.args.get(arg,"")
        if v: where.append(f"{col}=?"); params.append(v)
    if request.args.get("is_escalation"):
        where.append("is_escalation=?"); params.append(1 if request.args.get("is_escalation").lower()=="yes" else 0)
    if request.args.get("sla_breach"): where.append("sla_breach=1")
    if request.args.get("search"):
        srch = f"%{request.args.get('search')}%"
        where.append("(account_name LIKE ? OR subject LIKE ? OR content LIKE ? OR issue_type LIKE ?)")
        params.extend([srch,srch,srch,srch])
    wsql = ("WHERE "+" AND ".join(where)) if where else ""
    sort = request.args.get("sort_by","priority_score")
    if sort not in ["priority_score","delay_days","timestamp","account_name","priority","status"]: sort="priority_score"
    dir_ = "DESC" if request.args.get("sort_dir","desc").upper()=="DESC" else "ASC"
    total = q(f"SELECT COUNT(*) c FROM escalations {wsql}",params,one=True)["c"]
    offset = (page-1)*per_page
    rows = q(f"""SELECT id,source,timestamp,from_address,account_name,account_size,industry,
        subject,is_escalation,priority,priority_score,issue_type,department,
        sentiment,delay_days,status,assigned_owner,sla_breach,ai_summary,action_required,created_at
        FROM escalations {wsql} ORDER BY {sort} {dir_} LIMIT ? OFFSET ?""",params+[per_page,offset])
    return jsonify({"total":total,"page":page,"per_page":per_page,"pages":(total+per_page-1)//per_page,"data":rows})

@app.route("/api/escalations/<int:eid>")
def get_esc(eid):
    row = q("SELECT * FROM escalations WHERE id=?", (eid,), one=True)
    if not row: return jsonify({"error":"Not found"}),404
    return jsonify(row)

@app.route("/api/escalations/<int:eid>", methods=["PUT","OPTIONS"])
def update_esc(eid):
    if request.method=="OPTIONS": return jsonify({}),200
    data = request.get_json() or {}
    allowed = {k:v for k,v in data.items() if k in ["status","assigned_owner","priority"]}
    if not allowed: return jsonify({"error":"No valid fields"}),400
    allowed["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if allowed.get("status")=="Closed": allowed["resolved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ex(f"UPDATE escalations SET {', '.join(f'{k}=?' for k in allowed)} WHERE id=?", list(allowed.values())+[eid])
    return jsonify({"success":True})

@app.route("/api/escalations/<int:eid>/ai-process", methods=["POST","OPTIONS"])
def ai_process(eid):
    if request.method=="OPTIONS": return jsonify({}),200
    row = q("SELECT * FROM escalations WHERE id=?", (eid,), one=True)
    if not row: return jsonify({"error":"Not found"}),404
    flags = []
    if row["delay_days"]>30: flags.append(f"⚠️ {row['delay_days']}-day delay — critical SLA breach")
    if row["sentiment"]=="Angry": flags.append("⚠️ Angry sentiment — churn / legal risk")
    if row["sla_breach"]: flags.append("🚨 SLA breached — escalate to leadership")
    if row["priority"]=="Critical": flags.append("🔴 Critical — requires same-day resolution")
    if row["account_size"]=="Enterprise" and row["priority"] in ["Critical","High"]: flags.append("🏢 Enterprise account — senior POC assignment needed")
    return jsonify({"summary":row["ai_summary"],"urgency_flags":flags,
        "key_entities":{"account":row["account_name"],"issue":row["issue_type"],"dept":row["department"],"sentiment":row["sentiment"],"delay":f"{row['delay_days']} days"},
        "recommended_action":row["action_required"],"escalate_to":row["department"],
        "priority_justification":f"Score {row['priority_score']}/25 — {row['account_size']} account, {row['issue_type']}, {row['delay_days']}d delay, {row['sentiment'].lower()} sentiment."})

@app.route("/api/analytics/issue-types")
def a_issues():
    return jsonify(q("""SELECT issue_type,COUNT(*) total,
        SUM(CASE WHEN status='Closed' THEN 1 ELSE 0 END) resolved,
        SUM(CASE WHEN priority='Critical' THEN 1 ELSE 0 END) critical,
        SUM(CASE WHEN sla_breach=1 THEN 1 ELSE 0 END) sla_breaches,
        ROUND(AVG(delay_days),1) avg_delay,ROUND(AVG(tat_hours),0) avg_tat_hours
        FROM escalations WHERE is_escalation=1 GROUP BY issue_type ORDER BY total DESC"""))

@app.route("/api/analytics/accounts")
def a_accounts():
    return jsonify(q("""SELECT account_name,account_size,industry,COUNT(*) total,
        SUM(CASE WHEN is_escalation=1 THEN 1 ELSE 0 END) escalations,
        SUM(CASE WHEN priority='Critical' THEN 1 ELSE 0 END) critical,
        SUM(CASE WHEN status!='Closed' AND is_escalation=1 THEN 1 ELSE 0 END) open_escalations,
        SUM(CASE WHEN sla_breach=1 THEN 1 ELSE 0 END) sla_breaches,
        ROUND(AVG(delay_days),1) avg_delay,MAX(priority_score) max_score
        FROM escalations GROUP BY account_name ORDER BY escalations DESC LIMIT 25"""))

@app.route("/api/analytics/resolution")
def a_resolution():
    return jsonify(q("""SELECT department,COUNT(*) total,
        SUM(CASE WHEN status='Closed' THEN 1 ELSE 0 END) closed,
        SUM(CASE WHEN status!='Closed' THEN 1 ELSE 0 END) open_count,
        SUM(CASE WHEN sla_breach=1 THEN 1 ELSE 0 END) sla_breaches,
        ROUND(AVG(CASE WHEN status='Closed' AND tat_hours IS NOT NULL THEN tat_hours END),0) avg_tat_hours,
        ROUND(CAST(SUM(CASE WHEN status='Closed' THEN 1 ELSE 0 END) AS FLOAT)/COUNT(*)*100,1) resolution_rate
        FROM escalations WHERE is_escalation=1 GROUP BY department ORDER BY total DESC"""))

@app.route("/api/analytics/priority-age")
def a_age():
    buckets = [("0-3 days",0,3),("4-7 days",4,7),("8-14 days",8,14),("15-30 days",15,30),("30+ days",31,999)]
    result = []
    for label,lo,hi in buckets:
        row = {"bucket":label}
        for p in ["Critical","High","Medium","Low"]:
            row[p] = q("SELECT COUNT(*) c FROM escalations WHERE delay_days BETWEEN ? AND ? AND priority=? AND is_escalation=1 AND status!='Closed'",(lo,hi,p),one=True)["c"]
        row["total"] = sum(row[p] for p in ["Critical","High","Medium","Low"])
        result.append(row)
    return jsonify(result)

@app.route("/api/analytics/sla-performance")
def a_sla():
    return jsonify(q("""SELECT priority,COUNT(*) total,
        SUM(CASE WHEN sla_breach=0 THEN 1 ELSE 0 END) within_sla,
        SUM(CASE WHEN sla_breach=1 THEN 1 ELSE 0 END) breached,
        ROUND(AVG(delay_days),1) avg_delay
        FROM escalations WHERE is_escalation=1 GROUP BY priority
        ORDER BY CASE priority WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END"""))

@app.route("/api/meta/filters")
def meta():
    def vals(col): return [r[col] for r in q(f"SELECT DISTINCT {col} FROM escalations WHERE {col} IS NOT NULL ORDER BY {col}")]
    return jsonify({"sources":vals("source"),"priorities":["Critical","High","Medium","Low"],
        "statuses":["Open","In Progress","Blocked","Closed"],"departments":vals("department"),
        "account_sizes":["Enterprise","Mid-Market","SME"],"owners":vals("assigned_owner"),
        "issue_types":vals("issue_type"),"industries":vals("industry")})

# ─── Slack & Gmail Integration ────────────────────────────────────────────────────
@app.route("/api/integrations/slack/auth")
def slack_auth():
    """Start Slack OAuth flow"""
    scope = "channels:read,messages:read,users:read"
    auth_url = f"https://slack.com/oauth/v2/authorize?client_id={os.getenv('SLACK_CLIENT_ID')}&scope={scope}&redirect_uri={os.getenv('SLACK_REDIRECT_URI','http://localhost:5000/api/integrations/slack/callback')}"
    return jsonify({"auth_url": auth_url})

@app.route("/api/integrations/slack/callback")
def slack_callback():
    """Slack OAuth callback"""
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "No code provided"}), 400

    import requests
    token_resp = requests.post("https://slack.com/api/oauth.v2.access", data={
        "client_id": os.getenv("SLACK_CLIENT_ID"),
        "client_secret": os.getenv("SLACK_CLIENT_SECRET"),
        "code": code,
        "redirect_uri": os.getenv("SLACK_REDIRECT_URI", "http://localhost:5000/api/integrations/slack/callback")
    })

    if token_resp.json().get("ok"):
        access_token = token_resp.json().get("access_token")
        save_token("slack", access_token)
        return redirect("/?integration=slack&status=connected")
    return jsonify({"error": "Failed to get token"}), 400

@app.route("/api/integrations/gmail/auth")
def gmail_auth():
    """Start Gmail OAuth flow"""
    scope = "https://www.googleapis.com/auth/gmail.readonly"
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={os.getenv('GMAIL_CLIENT_ID')}&redirect_uri={os.getenv('GMAIL_REDIRECT_URI','http://localhost:5000/api/integrations/gmail/callback')}&response_type=code&scope={scope}"
    return jsonify({"auth_url": auth_url})

@app.route("/api/integrations/gmail/callback")
def gmail_callback():
    """Gmail OAuth callback"""
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "No code provided"}), 400

    import requests
    token_resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": os.getenv("GMAIL_CLIENT_ID"),
        "client_secret": os.getenv("GMAIL_CLIENT_SECRET"),
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": os.getenv("GMAIL_REDIRECT_URI", "http://localhost:5000/api/integrations/gmail/callback")
    })

    if token_resp.status_code == 200:
        access_token = token_resp.json().get("access_token")
        save_token("gmail", access_token)
        return redirect("/?integration=gmail&status=connected")
    return jsonify({"error": "Failed to get token"}), 400

@app.route("/api/integrations/sync")
def sync_integrations():
    """Manually sync Slack and Gmail data"""
    results = {}
    results["slack"] = fetch_slack_data()
    results["gmail"] = fetch_gmail_data()
    return jsonify(results)

@app.route("/api/integrations/data")
def get_integrations_data():
    """Get all synced external data"""
    return jsonify({
        "slack_messages": get_slack_messages(50),
        "gmail_emails": get_gmail_emails(50),
        "escalations": get_external_escalations()
    })

@app.route("/api/integrations/status")
def integrations_status():
    """Get integration sync status"""
    return jsonify(get_sync_status())

if __name__=="__main__":
    # Start background scheduler for auto-sync
    start_scheduler()

    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    print(f"[*] Plum EMS >> http://localhost:{port}")
    app.run(debug=debug, port=port, host="0.0.0.0")

# ─── Classifier data (for intake endpoint) ───────────────────────────────────
_ISSUE_DEPT = {
    "Claims Delay":"Claims","Cashless Denial":"Claims","Claim Rejection":"Claims",
    "Maternity Claim Denied":"Claims","Legal Notice":"Claims","Social Media Risk":"Claims",
    "Claims Expedite":"Claims","Policy Activation Failure":"Account Management",
    "Health ID Not Issued":"Account Management","Employee Addition Delay":"Account Management",
    "Renewal Delay":"Account Management","Data Integrity Issue":"Account Management",
    "Policy Issuance Delay":"Account Management","Compliance Documentation":"Account Management",
    "Communication Gap":"Account Management","Tech/Portal Issue":"Engineering",
    "SSO Integration Broken":"Engineering","Tech/Integration Issue":"Engineering",
    "Document Upload Failure":"Engineering","App Data Mismatch":"Engineering",
    "Billing Dispute":"Finance","Wrong Premium Charged":"Finance",
    "Invoice/Tax Document":"Finance","Payment Confirmation Delay":"Finance",
}
_ISSUE_URG = {
    "Legal Notice":10,"Social Media Risk":9,"Cashless Denial":9,"Policy Activation Failure":8,
    "Claim Rejection":8,"Claims Delay":7,"Renewal Delay":7,"SSO Integration Broken":7,
    "Data Integrity Issue":7,"Tech/Integration Issue":7,"Tech/Portal Issue":6,
    "Billing Dispute":6,"Wrong Premium Charged":6,"Employee Addition Delay":5,
    "Health ID Not Issued":5,"Policy Issuance Delay":6,"Maternity Claim Denied":7,
    "Claims Expedite":5,"Compliance Documentation":6,"Communication Gap":3,
}
_INTAKE_KEYWORDS = {
    "Legal Notice":["legal notice","irdai","consumer court","court filing"],
    "Social Media Risk":["linkedin","twitter","social media","post about","viral"],
    "Cashless Denial":["cashless denied","cashless rejection","pre-auth","hospital denied","pre auth"],
    "Claims Delay":["claim pending","claim delay","clm","claim stuck","not processed"],
    "Claim Rejection":["claim rejected","rejection reason","wrongfully rejected","formal appeal"],
    "Policy Activation Failure":["policy inactive","not activated","showing inactive","coverage gap","still inactive"],
    "Renewal Delay":["renewal","expiring","policy lapse","lapse","quote not received"],
    "Tech/Portal Issue":["portal","error 5","not accessible","login issue","document upload"],
    "SSO Integration Broken":["sso","single sign-on","authentication broken","login broken","cant log in"],
    "Billing Dispute":["overcharged","wrong amount","invoice discrepancy","billing error","refund"],
    "Employee Addition Delay":["new employee","not added","addition pending","joiners uninsured"],
    "Data Integrity Issue":["wrong data","incorrect data","data error","data mismatch","portal shows wrong"],
    "Health ID Not Issued":["health id","health card","id not issued","card not received"],
    "Maternity Claim Denied":["maternity","delivery","pregnancy","maternity claim"],
    "Wrong Premium Charged":["overcharged","wrong premium","premium incorrect","excess charged"],
}
_ACTION_MAP = {
    "Claims Delay":"Escalate to TPA claims desk. Confirm all documents received. Set 24h resolution SLA. Give client written timeline.",
    "Cashless Denial":"Call TPA emergency line immediately. Override if policy is confirmed active. Coordinate directly with hospital authorization team.",
    "Claim Rejection":"Compare rejection reason against policy terms. If wrongful, raise formal reversal request with insurer.",
    "Health ID Not Issued":"Raise bulk ID generation request with onboarding team. Set 24h ETA. Communicate progress to client daily.",
    "Policy Activation Failure":"Verify payment receipt. Trigger manual policy activation. Confirm coverage confirmation letter to client within 2h.",
    "Renewal Delay":"Share renewal quote by EOD. Issue temporary coverage confirmation. Confirm no gap in coverage.",
    "Legal Notice":"Immediately loop in Legal + Compliance. Assign senior POC. Resolve within 48h to avoid IRDAI escalation.",
    "Social Media Risk":"Resolve root cause urgently. Alert brand/communications team. Senior leadership to make personal client call.",
    "Tech/Portal Issue":"Raise P1 engineering ticket. Provide alternate document submission channel to client immediately. Set 4h resolution target.",
    "Billing Dispute":"Finance team to verify invoice vs contract. Reverse excess amount if confirmed. Issue written apology and credit note.",
    "Employee Addition Delay":"Verify payment receipt. Manual addition processing today. Confirm enrollment with policy card to client by EOD.",
    "SSO Integration Broken":"Raise P1 ticket with engineering. Investigate post-update regression. Communicate 4h ETA to client.",
    "Maternity Claim Denied":"Review maternity benefit clause in policy. If coverage confirmed, raise immediate reversal request with insurer.",
    "Wrong Premium Charged":"Finance to verify premium calculation vs policy schedule. Reverse and reissue corrected invoice.",
    "Data Integrity Issue":"Freeze all account operations. Full data audit against master enrollment file. Re-process with correct data within 48h.",
}


def _classify_intake(subject, content):
    text = (subject + " " + content).lower()
    for issue, keywords in _INTAKE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return issue
    return "General Escalation"


def _intake_summary(issue, account, size):
    summaries = {
        "Legal Notice": f"Formal legal notice from {account} ({size}). IRDAI/Consumer Court filing threatened. Legal + Compliance must engage immediately.",
        "Social Media Risk": f"{account} threatening social media post. Active brand damage risk. Immediate resolution + leadership outreach required.",
        "Cashless Denial": f"Emergency cashless denied for {account} ({size}) employee. Patient admitted at hospital. Requires immediate TPA override.",
        "Claims Delay": f"{account} ({size}) reporting claim processing delay. TPA escalation + written resolution timeline required within 24h.",
        "Claim Rejection": f"{account} disputing claim rejection. Likely wrongful rejection requiring insurer formal reversal.",
        "Policy Activation Failure": f"{account} policy inactive post-renewal. Employees being denied treatment. Manual activation + confirmation letter needed within 2h.",
        "Renewal Delay": f"{account} policy at risk of lapsing. Renewal quote not provided. Coverage gap for entire workforce — senior escalation needed.",
        "Tech/Portal Issue": f"Portal outage blocking {account} employees from claims and benefits. P1 engineering ticket + alternate channel needed within 4h.",
        "Billing Dispute": f"{account} overbilled without notice. Finance investigation + reversal needed.",
        "Employee Addition Delay": f"New employees at {account} uninsured post-payment. Employees being turned away at hospitals. Operations must act today.",
        "SSO Integration Broken": f"SSO broken for {account}. Mass login failure for employees. P1 engineering ticket required with 4-hour resolution target.",
        "Maternity Claim Denied": f"{account} employee maternity claim wrongfully denied. Policy review + insurer reversal required urgently.",
        "Wrong Premium Charged": f"{account} overcharged on premium. Finance must verify and reverse. Risk of trust erosion and payment escalation.",
        "Data Integrity Issue": f"Systemic data error across {account} account. Full data audit required before next hospital visit.",
        "Health ID Not Issued": f"Onboarding gap at {account} — health IDs unissued. Employees being turned away. Bulk issuance request required today.",
    }
    return summaries.get(issue, f"{account} ({size}) raised a {issue} concern requiring prompt attention and ownership assignment.")


# ─── VP Daily Brief ───────────────────────────────────────────────────────────
@app.route("/api/morning/brief")
def brief():
    critical_open = q("""SELECT id,account_name,account_size,subject,priority_score,
        issue_type,department,sentiment,delay_days,status,assigned_owner,sla_breach,ai_summary,action_required
        FROM escalations WHERE priority='Critical' AND status!='Closed' AND is_escalation=1
        ORDER BY priority_score DESC, delay_days DESC LIMIT 10""")

    unassigned = q("""SELECT id,account_name,priority,issue_type,delay_days
        FROM escalations WHERE assigned_owner IS NULL AND status!='Closed' AND is_escalation=1
        AND priority IN ('Critical','High') ORDER BY priority_score DESC LIMIT 8""")

    blocked = q("""SELECT id,account_name,priority,issue_type,department,delay_days,assigned_owner
        FROM escalations WHERE status='Blocked' AND is_escalation=1
        ORDER BY delay_days DESC LIMIT 8""")

    sla_heat = q("""SELECT department,
        SUM(CASE WHEN sla_breach=1 THEN 1 ELSE 0 END) breaches,
        ROUND(AVG(delay_days),1) avg_delay,
        SUM(CASE WHEN priority='Critical' AND status!='Closed' THEN 1 ELSE 0 END) critical_open,
        COUNT(*) total
        FROM escalations WHERE is_escalation=1 GROUP BY department ORDER BY breaches DESC""")

    risk_accounts = q("""SELECT account_name,account_size,
        SUM(CASE WHEN status!='Closed' AND is_escalation=1 THEN 1 ELSE 0 END) open_esc,
        SUM(CASE WHEN priority='Critical' THEN 1 ELSE 0 END) critical,
        SUM(CASE WHEN sla_breach=1 THEN 1 ELSE 0 END) sla,
        MAX(delay_days) max_delay, MAX(priority_score) risk_score
        FROM escalations WHERE is_escalation=1
        GROUP BY account_name HAVING (critical>0 OR sla>2) AND open_esc>0
        ORDER BY risk_score DESC, critical DESC LIMIT 8""")

    totals = q("""SELECT
        COALESCE(SUM(CASE WHEN status='Open' AND is_escalation=1 THEN 1 ELSE 0 END),0) open,
        COALESCE(SUM(CASE WHEN status='Blocked' AND is_escalation=1 THEN 1 ELSE 0 END),0) blocked,
        COALESCE(SUM(CASE WHEN priority='Critical' AND status!='Closed' AND is_escalation=1 THEN 1 ELSE 0 END),0) crit_open,
        COALESCE(SUM(CASE WHEN sla_breach=1 AND status!='Closed' THEN 1 ELSE 0 END),0) sla_active,
        COALESCE(SUM(CASE WHEN assigned_owner IS NULL AND status!='Closed' AND is_escalation=1
            AND priority IN ('Critical','High') THEN 1 ELSE 0 END),0) unassigned_ch
        FROM escalations""", one=True)

    bullets = []
    if totals.get("crit_open", 0) > 0:
        top_dept = max(sla_heat, key=lambda x: x["critical_open"]) if sla_heat else {"department":"Claims"}
        bullets.append(f"[CRITICAL] {totals.get('crit_open', 0)} Critical escalations remain unresolved — {top_dept['department']} has the highest backlog.")
    if totals.get("sla_active", 0) > 0:
        bullets.append(f"[SLA] {totals.get('sla_active', 0)} active escalations have breached SLA — legal and reputational risk is elevated.")
    if totals.get("blocked", 0) > 0:
        bullets.append(f"[BLOCKED] {totals.get('blocked', 0)} escalations are Blocked — review ownership and unblock by EOD.")
    if totals.get("unassigned_ch", 0) > 0:
        bullets.append(f"[UNASSIGNED] {totals.get('unassigned_ch', 0)} Critical/High priority escalations have no owner — assign immediately.")
    if risk_accounts:
        top = risk_accounts[0]
        bullets.append(f"[RISK] {top['account_name']} ({top['account_size']}) is your highest-risk account — {top['critical']} critical, {top['sla']} SLA breaches, {top['max_delay']}d max delay.")

    return jsonify({"generated_at":"2026-03-20 09:00:00","summary_bullets":bullets,
        "critical_open":critical_open,"unassigned_high":unassigned,
        "blocked_escalations":blocked,"dept_sla_heatmap":sla_heat,
        "risk_accounts":risk_accounts,"totals":totals})


# ─── Intake: Simulate new escalation ─────────────────────────────────────────
@app.route("/api/intake", methods=["POST","OPTIONS"])
def intake():
    if request.method=="OPTIONS": return jsonify({}),200
    data = request.get_json() or {}
    for f in ["source","from_address","subject","content","account_name"]:
        if not data.get(f): return jsonify({"error":f"Missing field: {f}"}),400

    text = data.get("subject","") + " " + data.get("content","")
    detected_issue = _classify_intake(data["subject"], data["content"])
    urgency_words = ["urgent","emergency","asap","immediate","today","irdai","legal","patient","icu","surgery","hospital","critical","threat","social media","linkedin"]
    urg_count = sum(1 for w in urgency_words if w in text.lower())
    sentiment = "Angry" if urg_count>=4 else "Frustrated" if urg_count>=2 else "Neutral"

    acc_row = q("SELECT account_size,industry,employee_count FROM escalations WHERE account_name=? LIMIT 1",(data["account_name"],),one=True)
    acc_size = acc_row["account_size"] if acc_row else "Mid-Market"
    industry = acc_row["industry"] if acc_row else "Unknown"
    emp_count = acc_row["employee_count"] if acc_row else 0

    dept = _ISSUE_DEPT.get(detected_issue,"Account Management")
    urg = _ISSUE_URG.get(detected_issue, 5)
    sw = {"Enterprise":4,"Mid-Market":2.5,"SME":1.5}.get(acc_size,2.5)
    mw = {"Angry":2.5,"Frustrated":1.5,"Neutral":0}.get(sentiment,0)
    sc = max(0, min(25, int(sw + urg*1.1 + mw)))
    priority = "Critical" if sc>=16 else "High" if sc>=10 else "Medium" if sc>=5 else "Low"
    action = _ACTION_MAP.get(detected_issue, f"Review and assign to {dept} team immediately.")
    ai_sum = _intake_summary(detected_issue, data["account_name"], acc_size)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    try:
        cur = conn.execute("""INSERT INTO escalations
            (source,timestamp,from_address,to_address,cc,account_name,account_size,industry,employee_count,
             subject,content,is_escalation,priority,priority_score,issue_type,department,sentiment,
             delay_days,action_required,ai_summary,status,assigned_owner,sla_breach,resolved_at,tat_hours,created_at,updated_at,tags)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (data["source"],now,data["from_address"],data.get("to_address","avik.bhandari@plum.com"),"",
             data["account_name"],acc_size,industry,emp_count,
             data["subject"],data["content"],1,priority,sc,
             detected_issue,dept,sentiment,0,action,ai_sum,"Open",None,0,None,None,now,now,"intake,new"))
        new_id = cur.lastrowid
        conn.commit()
    finally: conn.close()

    return jsonify({"id":new_id,"detected_issue":detected_issue,"priority":priority,"priority_score":sc,
        "department":dept,"sentiment":sentiment,"ai_summary":ai_sum,"action_required":action,
        "urgency_signals":urg_count,"message":"Escalation created and classified."})

# ─── File Upload & Custom Data Analysis ─────────────────────────────────────
@app.route("/api/upload", methods=["POST","OPTIONS"])
def upload():
    if request.method=="OPTIONS": return jsonify({}),200
    if not HAS_PANDAS: return jsonify({"error":"pandas not installed"}),500
    if "file" not in request.files: return jsonify({"error":"No file provided"}),400

    file = request.files["file"]
    if not file.filename: return jsonify({"error":"Empty filename"}),400
    if not (file.filename.endswith(".csv") or file.filename.endswith(".xlsx")):
        return jsonify({"error":"Only .csv and .xlsx files supported"}),400

    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.stream)
        else:
            df = pd.read_excel(file.stream)

        if df.empty: return jsonify({"error":"File is empty"}),400

        file_id = str(uuid.uuid4())[:8]
        UPLOAD_DATA[file_id] = df

        return jsonify({"file_id":file_id,"rows":len(df),"columns":list(df.columns),
            "message":f"Uploaded {len(df)} rows successfully"})
    except Exception as e:
        return jsonify({"error":str(e)}),400


@app.route("/api/analysis/<file_id>")
def custom_analysis(file_id):
    if file_id not in UPLOAD_DATA: return jsonify({"error":"File not found or expired"}),404

    df = UPLOAD_DATA[file_id]
    cols = list(df.columns)

    # Flexible column mapping — try common variations
    def find_col(names):
        for n in names:
            if any(n.lower() in c.lower() for c in cols): return next(c for c in cols if n.lower() in c.lower())
        return None

    priority_col = find_col(["priority"]) or "priority"
    status_col = find_col(["status"]) or "status"
    dept_col = find_col(["department","dept"]) or "department"
    issue_col = find_col(["issue","type","issue_type"]) or "issue_type"
    delay_col = find_col(["delay","days","delay_days"]) or "delay_days"

    # Build summary stats
    try:
        total = len(df)
        by_priority = df[priority_col].value_counts().to_dict() if priority_col in cols else {}
        by_status = df[status_col].value_counts().to_dict() if status_col in cols else {}
        by_dept = df[dept_col].value_counts().to_dict() if dept_col in cols else {}
        by_issue = df[issue_col].value_counts().head(10).to_dict() if issue_col in cols else {}

        avg_delay = float(df[delay_col].mean()) if delay_col in cols and pd.api.types.is_numeric_dtype(df[delay_col]) else 0

        return jsonify({
            "file_id":file_id,
            "total_rows":total,
            "columns":cols,
            "priority_distribution":by_priority,
            "status_distribution":by_status,
            "department_distribution":by_dept,
            "top_issues":by_issue,
            "avg_delay_days":round(avg_delay, 1),
            "sample_rows":df.head(5).to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error":str(e)}),400


@app.route("/api/morning/brief/<file_id>")
def custom_brief(file_id):
    if file_id not in UPLOAD_DATA: return jsonify({"error":"File not found"}),404

    df = UPLOAD_DATA[file_id]
    cols = list(df.columns)

    priority_col = next((c for c in cols if "priority" in c.lower()), None)
    status_col = next((c for c in cols if "status" in c.lower()), None)
    dept_col = next((c for c in cols if "dept" in c.lower()), None)

    bullets = []

    if priority_col and "Critical" in df[priority_col].values:
        crit_count = len(df[df[priority_col]=="Critical"])
        bullets.append(f"[CUSTOM DATA] {crit_count} records marked Critical priority in your uploaded file.")

    if status_col:
        status_counts = df[status_col].value_counts()
        top_status = status_counts.index[0] if len(status_counts) > 0 else "Unknown"
        bullets.append(f"[CUSTOM DATA] Most records have status '{top_status}' ({status_counts.iloc[0]} records).")

    if dept_col:
        dept_counts = df[dept_col].value_counts()
        if len(dept_counts) > 0:
            bullets.append(f"[CUSTOM DATA] Top department: {dept_counts.index[0]} with {dept_counts.iloc[0]} records.")

    bullets.append(f"[CUSTOM DATA] Total records analyzed: {len(df)}")

    if len(bullets) < 5:
        bullets.append("[CUSTOM DATA] More detailed analysis available in the Analytics view.")

    return jsonify({
        "file_id":file_id,
        "generated_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary_bullets":bullets,
        "data_summary":{"total_rows":len(df),"columns":len(cols),"column_names":cols}
    })


# ─── Serve static files (MUST be BEFORE SPA fallback) ────────────────────────────
@app.route("/css/<path:filename>")
def serve_css(filename):
    frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
    return send_from_directory(frontend_path, f"css/{filename}")

@app.route("/js/<path:filename>")
def serve_js(filename):
    frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
    return send_from_directory(frontend_path, f"js/{filename}")

@app.route("/assets/<path:filename>")
def serve_assets(filename):
    frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
    return send_from_directory(frontend_path, f"assets/{filename}")

# ─── SPA fallback route (MUST be LAST) ──────────────────────────────────────────
# This fallback serves index.html for SPA routing (but NOT for /api routes)
@app.route("/<path:path>", defaults={"path": ""})
def spa_fallback(path=""):
    # NEVER serve SPA for /api routes - let them 404 properly
    if path.startswith("api/"):
        return jsonify({"error": "Not found"}), 404
    # For everything else, serve index.html for SPA client-side routing
    try:
        return send_from_directory(os.path.join(os.path.dirname(__file__), "../frontend"), "index.html")
    except:
        return jsonify({"error": "Not found"}), 404


if __name__=="__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    print(f"[*] Plum EMS >> http://localhost:{port}")
    app.run(debug=debug, port=port, host="0.0.0.0")
