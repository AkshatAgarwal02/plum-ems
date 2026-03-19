# Recent Updates

## 1. Fixed Daily Brief View ✓
**Issue:** Daily Brief was stuck on "Generating brief..." and not displaying content

**Root Cause:** SQLite SUM() queries return NULL for empty sets, causing comparison errors in Python

**Solution:** 
- Wrapped all SUM() queries with COALESCE(SUM(...), 0)
- Used .get() with default values when accessing totals dictionary
- Added error handling in frontend to display API errors

**Testing:** Verified `/api/brief` endpoint returns valid JSON with analysis bullets

---

## 2. Added CSV/Excel File Upload Feature ✓

### New Features:
- **Upload View:** New "Upload Data" navigation item in sidebar
- **File Support:** CSV and Excel (.xlsx) file support
- **Flexible Column Mapping:** Auto-detects priority, status, department, issue_type, delay_days columns (case-insensitive)
- **Custom Analysis:** Generates distribution charts, top issues, avg delay metrics
- **Custom Brief:** Creates narrative bullets summarizing uploaded data
- **Sample Data Display:** Shows first 5 rows of uploaded file

### New API Endpoints:
1. **POST /api/upload** — Upload CSV/Excel file
   - Returns: file_id, row count, columns detected
   
2. **GET /api/analysis/:file_id** — Analyze uploaded data
   - Returns: priority/status/dept/issue distribution, avg_delay, sample rows
   
3. **GET /api/brief/:file_id** — Generate brief for uploaded data
   - Returns: 5 narrative bullets, data summary

### Frontend Files:
- `frontend/js/views/upload.js` — New upload view with drag-and-drop
- `frontend/js/api.js` — Added uploadFile(), customAnalysis(), customBrief()
- `frontend/js/app.js` — Added upload router and topbar entry
- `frontend/js/components.js` — Added Upload Data nav item
- `frontend/index.html` — Added upload.js script tag
- `frontend/css/styles.css` — Added upload view styles

### Backend Changes:
- `backend/app.py` — Added 3 new endpoints for file handling
- `backend/requirements.txt` — Added pandas, openpyxl dependencies

### Workflow:
1. Click "Upload Data" in sidebar
2. Drag and drop (or click to select) CSV/Excel file
3. System auto-detects columns and generates analysis
4. View distribution charts, avg metrics, summary bullets
5. See API endpoints for programmatic access

---

## 3. Dependencies
```
flask>=3.0.0
pandas>=1.3.0
openpyxl>=3.6.0
```

Install with:
```bash
pip install flask pandas openpyxl
```

---

## Testing Instructions

```bash
cd backend
python app.py
```

Then visit http://localhost:5000 and:
1. ✓ Open Daily Brief (should show narrative bullets and data)
2. ✓ Click "Upload Data" in sidebar
3. ✓ Upload a CSV file with columns: priority, status, department, issue_type, delay_days
4. ✓ See analysis with charts, metrics, and narrative summary

---

## Sample CSV Format
```
priority,status,department,issue_type,delay_days,account_name
Critical,Open,Claims,Claims Delay,5,ABC Corp
High,In Progress,Engineering,Portal Issue,3,XYZ Ltd
Medium,Blocked,Finance,Billing Dispute,12,123 Industries
```

---

## Known Limitations
- File uploads stored in memory (lost on server restart)
- No file persistence to database
- Max file size: whatever Flask allows (default ~16MB)
- Column names must contain priority/status/dept/issue/delay keywords to be detected

## Future Enhancements
- Persist uploaded files to disk
- Database import for uploaded CSVs
- Custom column mapping UI
- File history / previous uploads
- Export analysis as PDF/Excel
- Comparison between default and custom datasets
