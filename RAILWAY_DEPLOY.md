# 🚀 Railway Deployment Guide for Planfinity Backend

Follow these steps **in order**. Each step must complete before moving to the next.

---

## ✅ STEP 1: Create GitHub Repository

**What**: Create a new empty repo on GitHub (backend only).

**How**:
1. Go to: https://github.com/new
2. Repository name: `planfinity-backend`
3. Description: `Planfinity FastAPI Backend`
4. Choose: **Public** (for easier Railway linking)
5. Do NOT initialize with README, .gitignore, or license
6. Click: **Create repository**

**After**: You'll see a page with commands. Copy your repo URL (looks like `https://github.com/yourusername/planfinity-backend.git`)

---

## ✅ STEP 2: Push Backend Code to GitHub

**What**: Upload the local backend code to your new GitHub repo.

**How**: Open PowerShell in `e:\planfinity\planfinity-backend` and run:

```powershell
cd e:\planfinity\planfinity-backend

git remote add origin https://github.com/yourusername/planfinity-backend.git

git push -u origin main
```

**Note**: Replace `yourusername` with your actual GitHub username.

**After**: Refresh GitHub in browser—you should see all backend files there.

---

## ✅ STEP 3: Create Railway Account & Project

**What**: Set up Railway to deploy your backend.

**How**:
1. Go to: https://railway.app
2. Click: **Login with GitHub** (easier if you already have GH account)
3. After login, click: **New Project**
4. Select: **Deploy from GitHub Repo**

**After**: Railway will show you permissions request—approve it.

---

## ✅ STEP 4: Select Your Backend Repository

**What**: Tell Railway which GitHub repo to deploy.

**How**:
1. In Railway's "Deploy from GitHub" dialog:
2. Search for: `planfinity-backend`
3. Click to select it
4. Click: **Create Project**

**After**: Railway will start a build (may take 1-2 minutes). You'll see logs on screen.

---

## ✅ STEP 5: Wait for Build to Complete

**What**: Railway detects Python, installs dependencies, attempts to run.

**Expected logs**:
```
Building...
Installing dependencies...
Starting application...
```

⚠️ **It's OK if it fails at this step** — we'll fix it in the next step.

**After**: Build completes (you'll see either ✅ success or ❌ failed).

---

## ✅ STEP 6: Set Start Command (CRITICAL STEP)

**What**: Tell Railway how to start your FastAPI app.

**How**:
1. In Railway dashboard, click: **Settings** (gear icon, top right)
2. Go to: **Deploy** tab
3. Find: **Start Command** field
4. Clear any existing command
5. Paste:
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```
6. Click: **Save**

**After**: Railway should auto-trigger a redeploy.

---

## ✅ STEP 7: Add Environment Variables

**What**: Set secrets that your backend needs (Mongo, JWT, OpenAI).

**How**:
1. In Railway dashboard, click: **Variables** tab
2. Click: **+ New Variable**
3. Add each one (click **+ New Variable** between each):

| Key | Value |
|-----|-------|
| `MONGO_URL` | Copy from your local `.env` file (full MongoDB Atlas URL) |
| `JWT_SECRET` | Copy from your local `.env` file |
| `OPENAI_API_KEY` | Real OpenAI key OR keep placeholder |
| `CORS_ORIGINS` | `*` |

**After**: All 4 variables appear in the Variables tab.

---

## ✅ STEP 8: Redeploy with New Settings

**What**: Restart app with the new start command and variables.

**How**:
1. In Railway dashboard, click: **Deploy** button (top right)
2. Select: **Redeploy** latest commit
3. Watch the logs—app should now start correctly ✅

**Expected logs**:
```
uvicorn main:app --host 0.0.0.0 --port $PORT
Uvicorn running on http://0.0.0.0:PORT
```

**After**: You see "running" in logs = success ✅

---

## ✅ STEP 9: Get Your Public API URL

**What**: Find the live URL where your backend is running.

**How**:
1. In Railway dashboard, click: **Settings**
2. Go to: **Domains** tab
3. You'll see a URL like: `https://planfinity-backend-xxx.up.railway.app`
4. Copy this URL

**After**: You have a live API URL.

---

## ✅ STEP 10: Test Your Backend

**What**: Verify the API is working.

**How**:
1. Open browser: `https://your-railway-url/docs`
   - (Replace with your actual Railway URL from step 9)
2. You should see **Swagger UI** (interactive API tester)
3. Find: **POST /auth/signup**
4. Click it, then click **Try it out**
5. Fill in:
```json
{
  "name": "Test User",
  "email": "test@example.com",
  "password": "password123"
}
```
6. Click: **Execute**

**Success response** (should see):
```json
{
  "message": "User created successfully",
  "user_id": "..."
}
```

**After**: If you see this ✅, your backend is deployed!

---

## ❌ If Something Fails

**Error**: Build fails with "Python not detected"
- **Fix**: Make sure `requirements.txt` exists at repo root (not in subfolder)

**Error**: App crashes with "MONGO_URL is not configured"
- **Fix**: Add `MONGO_URL` variable in Railway Variables tab (step 7)

**Error**: 502 Bad Gateway
- **Fix**: Check Railway logs—usually means start command is wrong. Verify step 6.

**Error**: Can't find /docs endpoint
- **Fix**: Try `/docs` (with slash). If still fails, app isn't running—check logs.

---

## 🎉 Next Steps After Deployment

Once backend is live:
1. **Update frontend** to use new Railway URL instead of `localhost:8000`
2. **Connect Flutter app** to the live API
3. **Test end-to-end**: Sign up in app → verify user in MongoDB

---

