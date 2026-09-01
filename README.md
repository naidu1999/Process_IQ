# ProcessIQ - Enterprise AI Process Intelligence Engine

## Final submission project

ProcessIQ prioritises enterprise processes for AI and automation using transparent, explainable scoring.

### Included capabilities
- Dashboard with portfolio metrics
- Search button and keyboard search
- Department and industry filters
- Process ranking and detail view
- Explainable score breakdown
- Suggested AI implementation approach
- Runtime onboarding of new processes
- Data appears without code changes or redeployment
- Current-data Q&A endpoint
- Separated frontend files: `index.html`, `style.css`, `app.js`
- Well-commented FastAPI backend

## Run on Windows

Open PowerShell in the `backend` folder:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open: `http://127.0.0.1:8000`

## Quick test
1. Search `Exit Clearance` and click **Search**.
2. Change department or industry filters.
3. Click **View**.
4. Click **Add new process** and save a process.
5. Ask: `Which processes should we automate first?`

## Architecture

Browser → FastAPI API → Explainable Scoring Engine → Runtime CSV Data Source

The CSV data source is deliberately used for a zero-cost local demo. The API contract allows a production database or AI/RAG provider to be introduced later without redesigning the frontend.
