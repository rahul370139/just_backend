# AgentOps RCA Backend

A FastAPI backend for performing Root Cause Analysis (RCA) on incidents using LLM (Llama-3.3-70B-Versatile via Groq API) and Supabase data.

## Features

- **Incident Management**: Create, list, and manage incidents from Supabase
- **Artifact Storage**: Store and retrieve artifacts with SHA256 digest
- **Span Tracking**: Track execution spans for incident analysis
- **LLM-Powered RCA**: Deep Root Cause Analysis using Groq's Llama-3.3-70B-Versatile model
- **KPI Calculation**: Compute evidence time, time to RCA, and token costs
- **Bundle Export**: Export signed bundles with incident data and artifacts

## Prerequisites

- Python 3.8+
- Supabase account with `incidents`, `spans`, and `artifacts` tables
- Groq API key for LLM access

## Environment Variables

Copy `env.example` to `.env` and fill in your values:

```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Application Configuration
ARTIFACT_DIR=./artifacts
PORT=8000
ENVIRONMENT=development
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your actual values
```

3. Run the application:
```bash
uvicorn backend_fastapi:app --reload
```

## Railway Deployment

1. **Connect to Railway**: Link your GitHub repository to Railway
2. **Set Environment Variables**: Add all required environment variables in Railway dashboard
3. **Deploy**: Railway will automatically detect the Procfile and deploy your app

### Railway Environment Variables

Set these in your Railway project dashboard:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/service key
- `GROQ_API_KEY`: Your Groq API key
- `ARTIFACT_DIR`: `/tmp/artifacts` (for Railway's ephemeral filesystem)
- `PORT`: Railway will set this automatically

## API Endpoints

### Incidents
- `POST /incidents` - Create a new incident
- `GET /incidents` - List all incidents
- `GET /incidents/{id}` - Get incident details
- `POST /incidents/{id}/approve` - Approve an incident
- `GET /incidents/{id}/kpis` - Get incident KPIs

### Artifacts
- `POST /artifacts` - Upload an artifact
- `GET /artifacts/{digest}` - Get artifact details

### Spans
- `POST /traces/spans` - Upload execution spans

### RCA & Analysis
- `POST /rca/analyze` - Perform Root Cause Analysis
- `POST /replay/strict` - Strict replay of incident data
- `POST /bundles` - Export incident bundle

## Database Schema

The application expects these Supabase tables:

### incidents
- `id` (UUID, primary key)
- `order_id` (text)
- `eta_delta_hours` (float)
- `problem_type` (text)
- `status` (text)
- `created_ts` (timestamp)
- `details` (jsonb)

### spans
- `span_id` (text, primary key)
- `parent_id` (text, nullable)
- `tool` (text)
- `start_ts` (bigint)
- `end_ts` (bigint)
- `args_digest` (text)
- `result_digest` (text)
- `attributes` (jsonb)
- `incident_id` (text, nullable)

### artifacts
- `digest` (text, primary key)
- `mime` (text)
- `length` (bigint)
- `pii_masked` (boolean)
- `created_ts` (timestamp)

## LLM Integration

The application uses Groq's API to access Llama-3.3-70B-Versatile for:

- **Root Cause Analysis**: Deep analysis of incident data
- **Pattern Recognition**: Identifying common failure patterns
- **Recommendations**: Suggesting preventive measures

## License

MIT License
