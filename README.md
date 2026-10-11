# Phase 3 — AI Career Assistant (Git-ready)

This package preserves the existing portfolio and adds a real Python FastAPI retrieval backend. **Local mode uses TF-IDF retrieval with extractive answers, not an LLM or embedding vectors.** Optional Bedrock mode adds grounded LLM generation; it requires AWS permissions and incurs usage charges. The resume and project knowledge files are curated public-facing summaries; inspect them before publishing.

## Step 1 — Extract and open PowerShell
Extract ZIP to `C:\AI_Projects\career-portfolio-phase3`. Run:
```powershell
cd C:\AI_Projects\career-portfolio-phase3\backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```
If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass` then activate again.

## Step 2 — Configure and test backend
```powershell
Copy-Item .env.example .env
python -m pytest -q
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```
Open http://127.0.0.1:8001/health and http://127.0.0.1:8001/sources.
In a **second** PowerShell window test:
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8001/chat -Method Post -ContentType 'application/json' -Body '{"question":"What AWS and AI projects have you built?"}'
```

## Step 3 — Run website
In another PowerShell window:
```powershell
cd C:\AI_Projects\career-portfolio-phase3
python -m http.server 8000
```
Open http://localhost:8000 and ask a question. Frontend `config.js` points to local API by default.

## Step 4 — Enable Bedrock locally (optional)
Edit `backend/.env`: `AI_MODE=bedrock`, `AWS_REGION=ap-south-1`, and `BEDROCK_MODEL_ID` to an inference profile available in your account. Authenticate AWS locally using a profile or AWS SSO (do not commit credentials). Ensure permission `bedrock:InvokeModel` for the selected model/profile. Restart FastAPI. Test `/chat`. This may incur AWS charges.

## Step 5 — Deploy safely
1. Commit to GitHub Desktop after reviewing the public knowledge files and resume. Never commit `.env`.
2. Deploy the backend **separately** to a HTTPS container host, with AWS identity/role or protected secrets, HTTPS, logging, spending controls and `ALLOWED_ORIGINS=https://career-portfolio-starter.vercel.app`.
3. Set `config.js` to the HTTPS backend URL and push through GitHub Desktop. Vercel will redeploy the frontend.
4. Do **not** point a public Vercel page to localhost. Do **not** expose the backend publicly until you add persistent distributed rate limiting, abuse controls, monitoring and spending limits. The current in-memory limiter is suitable only for local testing/single-process demos.

## Architecture and limits
- `backend/knowledge/*.md`: approved source material (edit to update content; restart backend to reindex)
- `backend/rag.py`: chunking and local TF-IDF retrieval
- `backend/main.py`: `/health`, `/sources`, `/chat`; optional Bedrock Converse API
- `config.js`: frontend API URL
- Local mode is deterministic retrieval/extractive text, not a full embedding-based production RAG system. Phase 3b can add neural embeddings, Qdrant, ingestion automation, evaluations, secure cloud deployment and a persistent rate limiter.
- Source links point to website sections, not document-level citations. No confidential internal runbooks or incident data should be added.
