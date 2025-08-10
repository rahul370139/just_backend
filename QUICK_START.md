# 🚀 Quick Start Guide - AgentOps RCA Backend

## What This Backend Does

This is a **simple, focused backend** that:
1. **Reads data directly from Supabase tables** (incidents, spans, artifacts)
2. **Passes that data to Groq LLM** (Llama-3.3-70B-Versatile)
3. **Creates detailed Root Cause Analysis (RCA)**
4. **Provides clean FastAPI endpoints** for your frontend

## 🗄️ Database Setup

### 1. Create Supabase Tables
Run this SQL in your Supabase SQL editor:

```sql
-- Copy the contents of supabase_schema.sql
-- This creates the 3 tables you need: incidents, spans, artifacts
```

### 2. Get Your Supabase Credentials
- Go to your Supabase project dashboard
- Copy the **Project URL** and **anon/public key**
- These go in your `.env` file

## 🔑 API Keys

### 1. Get Groq API Key
- Go to [groq.com](https://groq.com)
- Sign up and get your API key
- This lets you use the powerful Llama-3.3-70B model

### 2. Create `.env` File
```bash
# Copy from env.example and fill in your real values
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
GROQ_API_KEY=your_groq_api_key_here
PORT=8000
```

## 🚀 Deploy to Railway

### Option 1: GitHub Integration (Recommended)
1. Push your code to GitHub
2. Connect Railway to your GitHub repo
3. Railway will auto-deploy when you push changes

### Option 2: Manual Deploy
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

## 🧪 Test Your Deployment

### 1. Test Locally First
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python backend_fastapi.py

# Test with the simple test script
python test_simple.py
```

### 2. Test on Railway
```bash
# Update BASE_URL in test_simple.py to your Railway URL
# Then run the test
python test_simple.py
```

## 📡 API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /incidents` - List all incidents
- `GET /incidents/{id}` - Get specific incident
- `GET /incidents/{id}/full` - Get incident + spans + artifacts
- `POST /rca/analyze` - **Main RCA analysis endpoint**

### RCA Analysis
```bash
# This is the main endpoint you'll use
POST /rca/analyze
{
  "incident_id": "your-incident-uuid"
}
```

**Response:**
```json
{
  "incident_id": "uuid",
  "summary": "Brief incident summary",
  "root_cause": "Main cause of the problem",
  "contributing_factors": ["factor1", "factor2"],
  "recommendations": ["action1", "action2"],
  "confidence": 0.85,
  "analysis_timestamp": "2024-01-01T12:00:00Z"
}
```

## 🔗 Frontend Integration

### Simple Frontend Call
```javascript
// Get RCA analysis for an incident
const analyzeIncident = async (incidentId) => {
  const response = await fetch('/rca/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ incident_id: incidentId })
  });
  
  const rca = await response.json();
  console.log('Root Cause:', rca.root_cause);
  console.log('Recommendations:', rca.recommendations);
};
```

## 🐛 Troubleshooting

### Common Issues
1. **"Supabase not configured"** - Check your `.env` file
2. **"Groq API error"** - Verify your Groq API key
3. **"Incident not found"** - Make sure you have data in your tables

### Check Health
```bash
curl https://your-railway-app.railway.app/health
```

## 📊 What Happens When You Call RCA

1. **Backend reads** incident data from Supabase
2. **Combines** incident + spans + artifacts
3. **Sends to Groq LLM** with a clear prompt
4. **LLM analyzes** the data and returns structured RCA
5. **Backend formats** the response for your frontend

## 🎯 Next Steps

1. **Deploy to Railway** ✅
2. **Test the endpoints** ✅
3. **Connect your frontend** ✅
4. **Customize the LLM prompt** (if needed)
5. **Add more data sources** (if needed)

## 💡 Tips

- The LLM prompt is simple and focused - it works well with the data structure
- All data is read directly from Supabase - no local file storage
- CORS is enabled for frontend integration
- Error handling is robust with clear error messages

---

**Need help?** Check the error messages - they're designed to be clear and helpful!
