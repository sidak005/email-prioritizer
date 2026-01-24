# 🚀 Setup and Run Guide

Complete guide to set up and run the backend and frontend for the first time.

## Prerequisites

- ✅ Python 3.11+ (you have Python 3.13.4)
- ✅ Node.js 18+ (you have Node.js v20.17.0)
- ✅ Homebrew (for installing libpq)

## 📦 Backend Setup (FastAPI)

### Step 1: Install PostgreSQL Development Libraries

```bash
brew install libpq
```

### Step 2: Create and Activate Virtual Environment

```bash
cd "/Users/sidaksingh/Desktop/COMP9417/Main files/Machine Learning/project/new"
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Set Environment Variables for PostgreSQL

```bash
export PATH="/opt/homebrew/opt/libpq/bin:$PATH"
export LDFLAGS="-L/opt/homebrew/opt/libpq/lib"
export CPPFLAGS="-I/opt/homebrew/opt/libpq/include"
```

### Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note:** This may take 5-10 minutes as it installs PyTorch, transformers, and other large packages.

### Step 5: Verify .env File

Make sure your `.env` file exists in the project root with all required variables:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `PINECONE_API_KEY`
- `PINECONE_ENVIRONMENT`
- `PINECONE_INDEX_NAME`
- `HUGGINGFACE_API_KEY`
- `ENVIRONMENT=development`

### Step 6: Run the Backend

```bash
# Make sure you're in the project root and venv is activated
python3 run.py
```

The backend will start on **http://localhost:8000**

You can verify it's running by visiting:
- http://localhost:8000 (root endpoint)
- http://localhost:8000/health (health check)
- http://localhost:8000/docs (API documentation - Swagger UI)

---

## 🎨 Frontend Setup (Next.js)

### Step 1: Navigate to Frontend Directory

```bash
cd "/Users/sidaksingh/Desktop/COMP9417/Main files/Machine Learning/project/new/frontend"
```

### Step 2: Install Node Dependencies

```bash
npm install
```

### Step 3: Run the Frontend

```bash
npm run dev
```

The frontend will start on **http://localhost:3000**

---

## 🎯 Running Both Services

You'll need **two terminal windows**:

### Terminal 1 - Backend:
```bash
cd "/Users/sidaksingh/Desktop/COMP9417/Main files/Machine Learning/project/new"
source venv/bin/activate
export PATH="/opt/homebrew/opt/libpq/bin:$PATH"
export LDFLAGS="-L/opt/homebrew/opt/libpq/lib"
export CPPFLAGS="-I/opt/homebrew/opt/libpq/include"
python3 run.py
```

### Terminal 2 - Frontend:
```bash
cd "/Users/sidaksingh/Desktop/COMP9417/Main files/Machine Learning/project/new/frontend"
npm run dev
```

---

## 🔧 Troubleshooting

### Backend Issues:

1. **psycopg2-binary installation fails:**
   - Make sure `libpq` is installed: `brew install libpq`
   - Set the environment variables before installing

2. **Module not found errors:**
   - Make sure virtual environment is activated: `source venv/bin/activate`
   - Reinstall dependencies: `pip install -r requirements.txt`

3. **Port 8000 already in use:**
   - Change port in `run.py` or kill the process using port 8000

### Frontend Issues:

1. **npm install fails:**
   - Try deleting `node_modules` and `package-lock.json`, then run `npm install` again

2. **Port 3000 already in use:**
   - Next.js will automatically use the next available port (3001, 3002, etc.)

---

## 📝 Quick Reference

| Service | Port | URL | Command |
|---------|------|-----|---------|
| Backend API | 8000 | http://localhost:8000 | `python3 run.py` |
| Frontend | 3000 | http://localhost:3000 | `npm run dev` |
| API Docs | 8000 | http://localhost:8000/docs | Auto-available |

---

## ✅ Verification Checklist

- [ ] Backend dependencies installed (`pip list` shows packages)
- [ ] Frontend dependencies installed (`ls frontend/node_modules`)
- [ ] `.env` file exists with all required variables
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can access http://localhost:8000/health
- [ ] Can access http://localhost:3000
