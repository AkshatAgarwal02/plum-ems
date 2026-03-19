# Upload Feature Testing Guide

## Quick Debug Check

Follow these exact steps:

### 1. Stop Everything
```bash
# In terminal, press Ctrl+C to stop server
```

### 2. Open Browser DevTools
- Open browser
- Press **F12** to open Developer Tools
- Click **Console** tab
- Keep it open!

### 3. Clear Cache (Important!)
- Press **Ctrl+Shift+Delete** (Windows) or **Cmd+Shift+Delete** (Mac)
- Select **All time**
- Click **Clear data**
- Close the clear cache dialog

### 4. Start Fresh Server
```bash
cd plum-ems/backend
python app.py
```

### 5. Load Page and Watch Console
- Go to: **http://localhost:5000**
- Press **Ctrl+F5** (hard refresh)
- Look at Console (F12)

### What You Should See in Console
You should see this message:
```
UploadView loaded successfully
```

If you **DON'T** see this message:
- There's a JavaScript syntax error
- Share the error message with me

---

## Check Navigation Items

After page loads, look at the sidebar:

**Count the items in NAVIGATION section:**
1. ⚡ Daily Brief
2. 🔲 Dashboard
3. ⚠️ Escalations
4. 📈 Analytics
5. ➕ New Intake
6. 📤 Upload Data ← Should be here!

**If you only see 5 items**, scroll down in sidebar to see if "Upload Data" is below.

---

## Test the Feature

1. Click **"Upload Data"** in sidebar
2. You should see:
   - Upload icon 📤
   - "Upload Custom Data" title
   - Upload area with instructions
   - Drag-and-drop zone

3. Drag `sample_data.csv` into the upload area
4. Should show:
   - "Uploading and analyzing..."
   - Then results with charts

---

## If Still Not Working

Take a screenshot of:
1. The sidebar (show all nav items)
2. The browser console (F12) - any error messages?

Share the screenshot and console output, and I'll fix it!

