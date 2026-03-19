# Plum EMS — Quick Start Guide

## ✅ What's Fixed & New

### 1. Daily Brief Now Works!
The "VP Daily Brief" view was stuck. **Fixed!**
- Generates 5 narrative bullets from real data
- Shows critical open escalations
- Displays unassigned Critical/High items
- SLA heatmap by department
- Highest-risk accounts with metrics

### 2. Upload Your Own Data Feature ✨
**NEW: Analyze your custom CSV/Excel files!**

Click **"Upload Data"** in the sidebar to:
- Upload your own CSV or Excel file
- Auto-detect columns (priority, status, department, issue_type, delay_days)
- Get instant analysis with distribution charts
- See AI-generated summary bullets for your data
- View sample rows and statistics

---

## How to Run

### Step 1: Install Dependencies
```bash
cd plum-ems/backend
pip install -q flask pandas openpyxl
```

### Step 2: Start the Server
```bash
python app.py
```

You'll see:
```
[*] Plum EMS >> http://localhost:5000
Running on http://127.0.0.1:5000
```

### Step 3: Open in Browser
Visit: **http://localhost:5000**

---

## Testing the Daily Brief

1. Click **"Daily Brief"** in sidebar (it's the default)
2. Wait for page to load
3. You should see:
   - ✓ 5 narrative bullets (e.g., "[CRITICAL] 29 Critical escalations remain...")
   - ✓ 4 stat cards (Critical Unresolved, SLA Breaches, Blocked, Unassigned)
   - ✓ Top 10 critical open escalations in a table
   - ✓ Highest risk accounts
   - ✓ Unassigned items table
   - ✓ Blocked escalations table
   - ✓ Department SLA heatmap

---

## Testing the Upload Data Feature

### Option A: Use Sample File
1. Click **"Upload Data"** in sidebar
2. Click the upload area or drag file
3. Select: `sample_data.csv` (in the plum-ems folder)
4. See instant analysis with:
   - Priority distribution chart
   - Avg delay stats
   - Top issues
   - Sample rows preview
   - Narrative bullets

### Option B: Use Your Own File

**CSV Format (required columns):**
```
priority,status,department,issue_type,delay_days,account_name
Critical,Open,Claims,Claims Delay,5,My Company
High,In Progress,Engineering,Portal Issue,3,Another Corp
```

**Excel Format:**
- Same columns as CSV
- Supports .xlsx files
- Auto-detects column headers

---

## What's Behind the Scenes

### Daily Brief Fixed:
- **Problem:** SQLite SUM() returns NULL (not 0) causing Python errors
- **Solution:** Used COALESCE(SUM(...), 0) in SQL queries
- **Result:** API now returns clean JSON with valid data

### Upload Feature Added:
- **Backend:** 3 new endpoints (/api/upload, /api/analysis/:file_id, /api/brief/:file_id)
- **Frontend:** New upload.js view with drag-and-drop support
- **Storage:** Files kept in memory (lost on server restart — OK for testing)

---

## API Endpoints (New)

### POST /api/upload
Upload a CSV or Excel file

**Request:**
```javascript
const formData = new FormData();
formData.append("file", file); // File object from <input type="file">
await fetch("/api/upload", {method: "POST", body: formData});
```

**Response:**
```json
{
  "file_id": "a1b2c3d4",
  "rows": 150,
  "columns": ["priority", "status", "department", ...],
  "message": "Uploaded 150 rows successfully"
}
```

### GET /api/analysis/:file_id
Analyze uploaded data

**Response:**
```json
{
  "file_id": "a1b2c3d4",
  "total_rows": 150,
  "priority_distribution": {"Critical": 20, "High": 85, "Medium": 45},
  "status_distribution": {"Open": 75, "Closed": 65, ...},
  "avg_delay_days": 12.5,
  "top_issues": {"Claims Delay": 40, "Billing": 30, ...},
  "sample_rows": [...]
}
```

### GET /api/brief/:file_id
Generate summary bullets for uploaded data

**Response:**
```json
{
  "file_id": "a1b2c3d4",
  "summary_bullets": [
    "[CUSTOM DATA] 20 records marked Critical priority...",
    "[CUSTOM DATA] Most records have status 'Open'...",
    ...
  ],
  "data_summary": {
    "total_rows": 150,
    "columns": 7,
    "column_names": [...]
  }
}
```

---

## File Structure
```
plum-ems/
├── README.md                   ← Full documentation
├── UPDATES.md                  ← What was changed
├── STARTUP_GUIDE.md            ← This file
├── sample_data.csv             ← Test file for upload
├── backend/
│   ├── app.py                  ← Flask API (+ 3 new endpoints)
│   ├── generate_data.py        ← Data generator (1152 records)
│   ├── requirements.txt        ← flask, pandas, openpyxl
│   └── plum_ems.db             ← SQLite database
└── frontend/
    ├── index.html
    ├── css/styles.css
    └── js/
        ├── utils.js
        ├── api.js              ← + uploadFile(), customAnalysis(), customBrief()
        ├── components.js       ← + Upload Data nav item
        ├── app.js              ← + upload router
        └── views/
            ├── brief.js        ← ✓ Fixed (error handling + data)
            ├── dashboard.js
            ├── escalations.js
            ├── analytics.js
            ├── intake.js
            └── upload.js       ← ✨ NEW
```

---

## Troubleshooting

### "Daily Brief still shows 'Generating brief...'"
- **Check:** Browser console (F12 → Console tab)
- **Look for:** Network error or API response
- **Fix:** Refresh page (Ctrl+R) and wait 3 seconds

### "Upload button doesn't work"
- **Check:** File is .csv or .xlsx (not .xls)
- **Check:** File size < 10MB
- **Check:** Browser console for errors
- **Try:** Drag and drop instead of click

### "Can't find pandas/openpyxl error"
- **Fix:** Install dependencies:
  ```bash
  pip install flask pandas openpyxl
  ```

### "Address already in use (port 5000)"
- **Fix:** Change port in app.py line: `app.run(debug=True, port=5001)`
- Or: Find and close process using port 5000

---

## Next Steps

1. ✅ Start server: `python app.py`
2. ✅ Open http://localhost:5000
3. ✅ Test Daily Brief (default view)
4. ✅ Test Upload Data with sample_data.csv
5. ✅ Explore other views: Dashboard, Escalations, Analytics
6. 🎉 Done!

---

## Questions?

Check the README.md for:
- Full API documentation
- Architecture overview
- Feature descriptions
- Deployment guide
