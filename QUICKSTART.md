

## Step 4: Run the Server

```bash
# Create and activate virtual environment (recommended on macOS/Homebrew Python)
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python3 run.py
```

API will be at: `http://localhost:8000`

## Step 4b: Run the Frontend (Optional)

```bash
# From project root
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local` if the API runs elsewhere.

## Step 5: Run with Docker (Option B)

```bash
# Build and run
docker-compose up --build

# Or run in background
docker-compose up -d
```

## Step 6: Test the API

### Test Health Check
```bash
curl http://localhost:8000/health
```

### Test Email Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/emails/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Urgent: Project deadline tomorrow",
    "sender": "boss@company.com",
    "recipient": "you@company.com",
    "body": "Hi, we need to finish the project by tomorrow. This is urgent!",
    "received_at": "2024-01-15T10:00:00"
  }'
```

### Test Response Generation
```bash
curl -X POST "http://localhost:8000/api/v1/responses/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "email_subject": "Meeting tomorrow",
    "email_body": "Can we schedule a meeting for tomorrow?",
    "tone": "professional"
  }'
```

### Check Metrics
```bash
curl http://localhost:8000/metrics
```

## Step 7: View API Documentation

Open in browser: `http://localhost:8000/docs`

You'll see interactive Swagger UI with all endpoints!

## Next Steps

1. **Use the frontend**: Run `frontend` (see Step 4b) to analyze emails, connect your inbox (IMAP), and generate responses.
2. **Connect real email**: In the frontend, use **Connect inbox** with Gmail (app password) or other IMAP.
3. **Deploy**: Backend on **Railway**, frontend on **Vercel** — see `DEPLOY_RAILWAY_VERCEL.md`.
4. **Monitor**: Check `/metrics` and Railway/Vercel logs.

## Troubleshooting

**Issue**: `ModuleNotFoundError` (e.g. `fastapi`, `bs4`, `uvicorn`)
- Solution: Use a virtual environment, then `pip install -r requirements.txt`. See Step 4.

**Issue**: `Address already in use` when running the server
- Solution: Stop any process on port 8000 (e.g. another `run.py`), or change the port in `run.py`.

**Issue**: `Pinecone index not found`
- Solution: Create index in Pinecone dashboard first

**Issue**: `Supabase connection failed`
- Solution: Check URL and key in `.env`

**Issue**: Models loading slowly
- Solution: First run downloads models (~500MB). Be patient!

## Need Help?

- Check `README.md` for detailed docs
- Check `DEPLOYMENT.md` for deployment help
- Check `PROJECT_PLAN.md` for architecture details

Happy coding! 🎉
