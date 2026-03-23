# QueryMind Deployment Guide

This guide provides step-by-step instructions on how to deploy your **FastAPI + Vanilla UI** QueryMind application to production environments.

## Option 1: Deploying to Vercel (Serverless)

Vercel is an excellent option for hosting FastAPI Python applications using their Serverless Functions.

### 1. Create a `vercel.json` configuration

In the root of your project `c:\Users\dell\Desktop\coding\QueryMind`, create a file named `vercel.json` and add the following:

```json
{
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

### 2. Prepare dependencies
Ensure your `requirements.txt` includes exactly what the app needs to run:
```txt
fastapi
uvicorn
python-dotenv==1.0.1
mysql-connector-python==9.0.0
langchain==0.3.6
langchain-google-genai>=1.0.1
```

*(Note: Streamlit is no longer required and can be omitted from production dependencies).*

### 3. Push and Deploy
1. Commit your code and push it to a GitHub repository.
2. Go to the [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New > Project**.
3. Import your GitHub repository.
4. Open the **Environment Variables** section and add your production variables:
   - `GOOGLE_API_KEY`
   - `GEMINI_MODEL` (e.g. `gemini-1.5-pro`)
   - `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` *(Note: ensure your production database allows connections from Vercel's IP addresses or is accessible over the internet).*
5. Click **Deploy**. Vercel will automatically detect `vercel.json`, install your Python dependencies, and serve your API endpoints alongside your static frontend!

---

## Option 2: Deploying to Render / Railway (Docker / PaaS)

For long-running servers and persistent connections, a Platform-as-a-Service (PaaS) like Render or Railway is highly recommended.

### 1. Application adjustments
Ensure your app binds to the `0.0.0.0` host and the required `$PORT` environment variable which is typical across PaaS providers. You can adjust the run command instead of changing `main.py`.

### 2. Deploy on Render (Web Service)
1. Push your code to GitHub.
2. Go to the [Render Dashboard](https://dashboard.render.com/) and click **New > Web Service**.
3. Connect your GitHub repository.
4. Use the following configuration:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click **Advanced** and add your Environment Variables (like `GOOGLE_API_KEY`).
6. Click **Create Web Service**.

### 3. Deploy on Railway
1. Push your code to GitHub.
2. Go to the [Railway Dashboard](https://railway.app/) and click **New Project > Deploy from GitHub repo**.
3. Railway will automatically detect the Python environment.
4. Add your Environment variables in the **Variables** tab.
5. In the **Settings** tab under **Deploy**, set your Custom Start Command to:
   `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Click Deploy.

---

> [!CAUTION]
> **Database Security Reminder**: Whenever deploying to production, ensure that your MySQL instance uses strong passwords, encrypts connections (SSL/TLS), and tightly controls user privileges. Since QueryMind is designed to only process `SELECT` queries, ensure the production database user provided in the `.env` configuration *only* has read privileges on the targeted tables to prevent any unauthorized escalation!
