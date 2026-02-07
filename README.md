# IdeaForge

A starter web app that turns a product idea into an implementation plan, optimized tech stack, prompt pack, and draft docs.

## Structure
- `frontend/`: Next.js web UI
- `backend/`: FastAPI service

## Run locally

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# set your key
cat <<'ENV' > .env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1
ENV

uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend expects the API at `http://localhost:8000` by default. Override with:
```bash
export NEXT_PUBLIC_API_URL="http://localhost:8000"
```

## Next steps
- Add persistence for project history.
- Add auth and billing.
