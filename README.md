# Plum EMS — Escalation Management System

### Production-Grade AI-Enabled Escalation Management for Plum Group Health Insurance

A full-stack system for VP of Account Management overseeing 4000+ corporate health insurance accounts. Consolidates escalations from Email, Slack, and WhatsApp, auto-classifies them, prioritizes by business impact, tracks ownership, and surfaces critical issues at a glance.

**Built with:** Python Flask (backend) · Vanilla JS (frontend) · SQLite · Chart.js

---

## Quick Start

### Prerequisites
- Python 3.7+
- Flask >= 3.0.0

### Installation & Run
```bash
cd backend

# Install dependencies
pip install flask

# Generate 1150+ synthetic escalation records
python generate_data.py

# Start Flask server
python app.py
```

Then visit: **http://localhost:5000**

---

## Key Features

### 📊 VP Daily Brief (Default View)
- Morning digest with 5 auto-generated narrative bullets
- Top 10 critical open escalations
- 8 unassigned Critical/High priority items
- Blocked escalations requiring unblocking
- Highest-risk accounts with metrics
- Department SLA heatmap

### 🎯 Dashboard
- **10 KPI Cards:** Critical Open, SLA Breaches, Open Queue, Avg Delay, In Progress, Blocked, Resolved, Avg TAT, Total Records, New Today
- **Charts:** 30-day escalation trend, department breakdown, priority mix, source distribution
- **Owner Workload:** Grid view of all 15 account owners with active escalation counts, critical items, blocked count, and SLA breaches
- **Top 15 Priority Queue:** Sortable by score and delay, clickable for detail panel

### 📋 Escalations Table
- Full paginated view of all 1152 records (25/50/100 per page)
- **Filters:** Source (Email/Slack/WhatsApp), Priority, Status, Department, Account Size, SLA Breach Only, Owner
- **Search:** Account name, subject, content, issue type
- **Sortable Columns:** Time, Account, Subject, Source, Priority, Score, Issue, Dept, Sentiment, Status, Owner, Delay, SLA
- **Click Row → Detail Panel** with full escalation info, AI summary, recommended action
- **Live Inline Updates:** Change status or owner directly — saves to API with toast notification

### 📈 Analytics (5 Tabs)
1. **Issue Types** — Bar chart of total vs resolved, full breakdown table with resolution %, SLA breach count, avg delay, avg TAT
2. **Top Accounts** — Top 25 accounts by risk, showing total, escalations, open, critical, SLA breaches, avg delay, risk badge
3. **Resolution** — 2 side-by-side bar charts (resolution rate %, avg TAT hours), per-department performance with progress bars
4. **SLA Performance** — 4 KPI cards (one per priority) with within-SLA count, breach count, %, avg delay, bar chart comparison
5. **Escalation Aging** — Stacked bar chart of 5 age buckets × 4 priorities, aging breakdown table

### ➕ Escalation Intake Simulator
- Form to simulate new escalations from Email/Slack/WhatsApp
- Auto-detects issue type from message content
- Auto-scores priority (0-25)
- Detects sentiment from urgency signal count
- Looks up account size from existing data
- **6 Pre-Built Scenarios:** Cashless Denied, Legal Notice, Social Media Risk, Portal Outage, Renewal Lapse, Billing Overcharge
- Result card shows detected issue, priority badge, score, routed department, sentiment, AI summary, recommended action
- "Open Record →" button links to detail panel of newly created escalation

---

## Data Structure

### Database (SQLite: plum_ems.db)
**1152 Records** across:
- **60 Companies:** 20 Enterprise (800–4000 emp), 20 Mid-Market (150–550 emp), 20 SME (20–100 emp)
- **35+ Issue Types:** Claims Delay, Cashless Denial, Legal Notice, Policy Activation, SSO Broken, Billing Dispute, etc.
- **6 Departments:** Claims, Account Management, Engineering, Finance, Sales, Operations
- **15 Account Owners:** avik.bhandari, priya.menon, rahul.nair, neha.sharma, deepak.verma, sunita.patel, ankit.joshi, ritu.gupta, karan.mehta, divya.krishnan, rohan.sinha, swati.kapoor, manish.tiwari, pooja.agarwal, siddharth.rao

### Priority Scoring Formula
```
base_urgency = issue_type_urgency (0-10)
size_weight = {"Enterprise": 4, "Mid-Market": 2.5, "SME": 1.5}[account_size]
delay_weight = 3 if delay>30d else 2 if delay>14d else 1 if delay>7d else 0.5 if delay>3d else 0
sentiment_weight = {"Angry": 2.5, "Frustrated": 1.5, "Neutral": 0, "Positive": -1}[sentiment]
score = size_weight + (urgency × 1.1) + delay_weight + sentiment_weight + random_noise(-1.5, +1.5)
priority = "Critical" if score>=16 else "High" if score>=10 else "Medium" if score>=5 else "Low"
```

### SLA Thresholds
- **Critical:** 1 day (24 hours)
- **High:** 3 days (72 hours)
- **Medium:** 7 days
- **Low:** 14 days

---

## API Endpoints (17 Total)

### Dashboard & Stats
- `GET /api/dashboard/stats` — Overall KPI counts
- `GET /api/dashboard/top?limit=15` — Top N escalations by priority + delay
- `GET /api/dashboard/trend?days=30` — Daily counts for trend chart
- `GET /api/dashboard/owner-workload` — Per-owner escalation counts (open/critical/SLA)
- `GET /api/dashboard/dept-summary` — Per-dept metrics (total/open/critical/SLA/avg_delay)

### Escalations CRUD
- `GET /api/escalations` — Paginated + filtered list (params: page, per_page, sort_by, sort_dir, filters...)
- `GET /api/escalations/:id` — Full record detail
- `PUT /api/escalations/:id` — Update status, owner, priority
- `POST /api/escalations/:id/ai-process` — Regenerate AI summary, flags, and action

### Analytics
- `GET /api/analytics/issue-types` — Total/resolved/critical/SLA/avg_delay per issue
- `GET /api/analytics/accounts` — Top 25 accounts by risk
- `GET /api/analytics/resolution` — Per-dept resolution rate and TAT
- `GET /api/analytics/priority-age` — 5 age buckets × 4 priorities (open only)
- `GET /api/analytics/sla-performance` — Per-priority SLA compliance metrics

### Meta & Features
- `GET /api/meta/filters` — All distinct filter values (sources, priorities, statuses, depts, sizes, owners, issues, industries)
- `POST /api/intake` — Create new escalation from form submission, auto-classify and score
- `GET /api/brief` — VP Daily Brief with narrative bullets, critical items, risk accounts, dept heatmap

---

## Frontend Architecture

### File Organization
```
frontend/
├── index.html                    # Single entry point
├── css/
│   └── styles.css               # Complete dark theme design system
└── js/
    ├── utils.js                 # Badge renderers, formatters, ChartRegistry
    ├── api.js                   # Fetch wrappers for all endpoints
    ├── components.js            # Sidebar, Topbar, DetailPanel
    ├── app.js                   # Router, App.boot(), App.navigate()
    └── views/
        ├── brief.js             # VP Daily Brief view
        ├── dashboard.js         # KPI Dashboard with charts
        ├── escalations.js       # Filterable table + pagination
        ├── analytics.js         # 5-tab analytics panels
        └── intake.js            # Escalation intake form + scenarios
```

### Script Load Order
1. Chart.js (CDN)
2. utils.js (badge renderers, color maps, utilities)
3. api.js (fetch wrappers)
4. components.js (sidebar, topbar, detail panel HTML generators)
5. views/*.js (individual view renderers)
6. app.js (router + boot)

### Design System
- **Theme:** Professional dark (Slack-inspired)
- **Colors:** Plum (#e8563a), Critical (#ff4d4d), High (#f97316), Medium (#eab308), Low (#22c55e)
- **Fonts:** Inter (sans-serif) · JetBrains Mono (monospace)
- **Layout:** 220px fixed sidebar + responsive main content
- **Responsive:** 520px right-slide detail panel, mobile-friendly tables

---

## Key Implementation Details

### Auto-Classification (Intake)
- 15 issue types with keyword matching (e.g., "cashless denied", "social media", "legal notice")
- Sentiment detection from urgency word count (angry=4+ words, frustrated=2-3, neutral<2)
- Account size lookup from existing data
- Department routing based on issue type
- VP-ready AI summary generation with specific action recommendations

### SLA Breach Detection
- Compares delay_days against priority-based SLA threshold
- Tracked on escalations WHERE priority IN (Critical/High/Medium/Low) and status != Closed
- Displayed as red "SLA" badge in tables and detail panels

### Live Updates
- Status/owner changes save immediately via PUT /api/escalations/:id
- Toast notification appears after each update
- No save button — onChange fires API call directly
- Detail panel reflects updates in real-time

### Chart Management
- ChartRegistry singleton prevents canvas reuse errors
- Destroys previous chart before re-rendering
- Shared dark-themed chart defaults (grid color, tick labels, tooltip styling)

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.7+ · Flask 3.0.0+ |
| **Database** | SQLite (single file: plum_ems.db) |
| **Frontend** | Vanilla JavaScript (ES6) · HTML5 · CSS3 |
| **Charts** | Chart.js 4.4.1 (via CDN) |
| **Fonts** | Google Fonts (Inter + JetBrains Mono) |
| **Server** | Flask development server (production: use WSGI) |

**Zero Build Tools:** No npm, no webpack, no TypeScript, no build step. Run with just `python app.py`.

---

## Deployment

### Development
```bash
python app.py
```

### Production
Use a WSGI server (Gunicorn, uWSGI, etc.):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Database
SQLite file persists at `backend/plum_ems.db`. For large-scale deployments (>100K records), migrate to PostgreSQL or MySQL.

---

## Features & Workflow

### For VP of Account Management
1. **Morning:** Open "Daily Brief" — see top priorities, risk accounts, unassigned critical items
2. **Throughout Day:** Switch to Dashboard for real-time KPIs and owner workload
3. **Triage:** Use Escalations table to search, filter, sort, and bulk view
4. **Detail:** Click any row to see full message, AI summary, recommended action
5. **Assign:** Update owner directly in detail panel — auto-saves
6. **Analyze:** Switch to Analytics to spot trends, issue hotspots, dept performance, aging issues
7. **New Intake:** Use Intake simulator to classify and score inbound escalations before creating

### For Operations/Support
1. Receive escalations via Email, Slack, or WhatsApp
2. Forward/copy to intake form with message content
3. System auto-classifies and routes to correct department
4. Auto-calculates priority based on account size, urgency, sentiment
5. Escalation appears in DB and surfaces to VP immediately

---

## Metrics Tracked

- **Counts:** Total records, escalations, open, in progress, blocked, closed, critical open, SLA breaches
- **Averages:** Delay days, TAT hours
- **Distributions:** By priority, source, department, account size, status, sentiment, owner
- **Risk Scoring:** Per account (critical count + SLA breach count + max delay + risk_score)
- **Resolution Rate:** Per department, issue type
- **SLA Compliance:** Per priority, per department, overall

---

## Known Limitations

- SQLite not suitable for 100K+ records; use PostgreSQL for scale
- No authentication/authorization (add Flask-Login for multi-user)
- No email/Slack integration (dummy intake form only)
- Data is synthetically generated (not real customer data)
- Charts re-render on every navigation (optimization: cache rendered views)

---

## Development Notes

### Adding a New Issue Type
1. Add to `ISSUE_TYPES` dict in `generate_data.py` with (department, base_urgency, escalation_prob)
2. Add keyword matching to `_INTAKE_KEYWORDS` in `app.py`
3. Add department mapping to `_ISSUE_DEPT`
4. Add urgency weight to `_ISSUE_URG`
5. Add action template to `_ACTION_MAP`
6. Add summary template to `_intake_summary()`
7. Re-run `python generate_data.py` to regenerate data

### Customizing Dashboard KPIs
- Edit `DashboardView.kpis()` in `frontend/js/views/dashboard.js`
- Add/remove stat cards, edit queries in `backend/app.py` → `dash_stats()` endpoint

### Extending Analytics Tabs
- Add new tab markup to `AnalyticsView.render()` in `frontend/js/views/analytics.js`
- Create API endpoint in `backend/app.py` (e.g., `/api/analytics/custom-metric`)
- Call endpoint and render chart/table in view

---

## Author & License

Built as a take-home assignment prototype. Production deployments should add authentication, audit logging, error handling, monitoring, and multi-tenant support.

**Version:** 1.0.0 | **Last Updated:** March 2026
