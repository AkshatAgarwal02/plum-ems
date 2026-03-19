# Deploy Plum EMS to Render.com

## ✅ Quick Deploy (5 minutes)

### Step 1: Create Render Account
1. Go to **https://render.com**
2. Click **"Sign Up"**
3. Create free account (email or GitHub)

### Step 2: Push Code to GitHub
If your code isn't on GitHub yet:
```bash
cd plum-ems
git init
git add .
git commit -m "Initial commit: Plum EMS"
git remote add origin https://github.com/YOUR_USERNAME/plum-ems.git
git push -u origin main
```

### Step 3: Create New Web Service on Render

1. Log in to **Render.com**
2. Click **"New"** → **"Web Service"**
3. Select **"Connect a repository"** → Choose your `plum-ems` repo
4. Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `plum-ems` |
| **Environment** | `Python 3` |
| **Region** | `Oregon` (or closest to you) |
| **Branch** | `main` |
| **Build Command** | `pip install -r backend/requirements.txt` |
| **Start Command** | `python backend/app.py` |

5. Click **"Create Web Service"**

### Step 4: Wait for Deployment
- Render will automatically build and deploy
- Takes ~2-3 minutes
- You'll see logs in real-time
- When complete, you'll get a URL like: `https://plum-ems-abc123.onrender.com`

### Step 5: Test Your App
Visit: `https://YOUR_RENDER_URL`

You should see:
- ✅ Daily Brief loading
- ✅ All sidebar items (including Upload Data)
- ✅ All features working

---

## 🔧 Environment Variables (if needed)

If you want to add environment variables:
1. In Render dashboard, go to **Settings**
2. Scroll to **Environment**
3. Add any variables (we don't need any for now)

---

## 📊 Database Notes

- SQLite database (`plum_ems.db`) is stored on the container
- **It resets when Render redeploys**
- For production: Use PostgreSQL (add-on in Render)

To add PostgreSQL:
1. Create PostgreSQL database in Render
2. Update `app.py` to use PostgreSQL connection string
3. Redeploy

---

## 🚀 Your Live URL

Once deployed, share this link:
```
https://plum-ems-abc123.onrender.com
```

---

## ❓ Troubleshooting

**App won't start?**
- Check logs in Render dashboard
- Verify `python backend/app.py` runs locally first

**Database empty?**
- Run `python backend/generate_data.py` locally first, then redeploy

**Upload feature not working?**
- Check browser cache (Ctrl+Shift+Delete)
- Hard refresh page (Ctrl+F5)

---

## 📌 Keep Your App Awake

Free Render apps spin down after 15 min of inactivity.
To keep it running:
- Upgrade to paid plan ($7/month), or
- Use a uptime monitor service (e.g., Uptime Robot - free)

---

**Your Plum EMS is now LIVE! 🎉**
