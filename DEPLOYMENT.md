# 🚀 Deployment Guide

## Deployment Options

### Option 1: Railway (Recommended for Portfolio)

**Why Railway?**
- Easy setup, perfect for portfolio projects
- Free tier available
- Automatic HTTPS
- Simple environment variable management

**Steps:**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables in Railway dashboard → Variables (see DEPLOY_NOW.md for the list)
6. Railway will automatically detect Docker and deploy
7. Your API will be available at `https://your-project.railway.app`

**Cost**: Free tier includes 500 hours/month, $5/month for more

---

### Option 2: Render

**Why Render?**
- Similar to Railway
- Good free tier
- Easy PostgreSQL integration

**Steps:**
1. Go to [render.com](https://render.com)
2. Sign up
3. Click "New" → "Web Service"
4. Connect your GitHub repo
5. Configure:
   - **Build Command**: `docker build -t email-prioritizer .`
   - **Start Command**: `docker run -p 8000:8000 email-prioritizer`
   - Or use Docker Compose
6. Add environment variables
7. Deploy!

**Cost**: Free tier available, $7/month for better performance

---

### Option 3: AWS (More Professional)

**Services Needed:**
- **ECS (Elastic Container Service)**: Run Docker containers
- **RDS**: PostgreSQL database (or use Supabase)
- **EC2**: Alternative to ECS
- **Elastic Beanstalk**: Easier option

**Steps (Elastic Beanstalk):**
1. Install AWS CLI and EB CLI
2. Initialize: `eb init`
3. Create environment: `eb create email-prioritizer-env`
4. Set environment variables: `eb setenv KEY=value`
5. Deploy: `eb deploy`

**Cost**: ~$20-50/month depending on usage

---

### Option 4: Google Cloud Platform

**Services:**
- **Cloud Run**: Serverless containers (best option)
- **Cloud SQL**: PostgreSQL (or use Supabase)

**Steps (Cloud Run):**
1. Install Google Cloud SDK
2. Build image: `gcloud builds submit --tag gcr.io/PROJECT-ID/email-prioritizer`
3. Deploy: `gcloud run deploy email-prioritizer --image gcr.io/PROJECT-ID/email-prioritizer`
4. Set environment variables in Cloud Run console

**Cost**: Free tier available, pay-as-you-go

---

## Pre-Deployment Checklist

- [ ] All environment variables set
- [ ] Supabase database tables created
- [ ] Pinecone index created
- [ ] Hugging Face API key configured
- [ ] Docker image builds successfully
- [ ] Health check endpoint works (`/health`)
- [ ] API tested locally
- [ ] CORS configured for frontend (if applicable)

## Database Setup (Supabase)

1. Go to Supabase dashboard
2. SQL Editor → Run this:

```sql
-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create emails table
CREATE TABLE emails (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    subject TEXT NOT NULL,
    sender TEXT NOT NULL,
    recipient TEXT NOT NULL,
    body TEXT NOT NULL,
    html_body TEXT,
    priority_score FLOAT DEFAULT 0,
    priority_level TEXT DEFAULT 'normal',
    intent TEXT,
    sentiment TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    received_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_emails_user_id ON emails(user_id);
CREATE INDEX idx_emails_priority_score ON emails(priority_score DESC);
CREATE INDEX idx_emails_received_at ON emails(received_at DESC);
```

## Pinecone Setup

1. Go to [pinecone.io](https://pinecone.io)
2. Create account
3. Create index:
   - Name: `email-prioritizer`
   - Dimension: `384` (for all-MiniLM-L6-v2)
   - Metric: `cosine`
4. Copy API key and environment

## Monitoring After Deployment

1. Check health: `https://your-url.com/health`
2. Check metrics: `https://your-url.com/metrics`
3. Monitor logs in deployment platform
4. Set up alerts for errors

## Custom Domain (Optional)

1. Buy domain (Namecheap, Google Domains)
2. In Railway/Render: Add custom domain
3. Update DNS records
4. SSL certificate auto-generated

## CI/CD (Optional but Impressive)

**GitHub Actions Example:**

```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        run: railway up
```

## Troubleshooting

**Issue**: Container won't start
- Check environment variables
- Check logs: `docker logs <container-id>`
- Verify all services are accessible

**Issue**: Database connection fails
- Verify Supabase URL and key
- Check network connectivity
- Verify database tables exist

**Issue**: High latency
- Enable caching (Redis)
- Optimize model loading
- Use smaller models for faster inference

## Performance Optimization

1. **Caching**: Add Redis for frequently accessed data
2. **Batch Processing**: Process emails in batches
3. **Model Optimization**: Use quantized models
4. **CDN**: Serve static assets via CDN
5. **Load Balancing**: For high traffic

## Cost Estimation

**Free Tier (Railway/Render):**
- $0/month (limited hours)

**Production (Small Scale):**
- Railway: $5-20/month
- Render: $7-25/month
- AWS: $20-50/month
- GCP: $10-30/month

**Plus:**
- Supabase: Free tier available
- Pinecone: Free tier available (100K vectors)
- Hugging Face: Free API tier available

**Total**: ~$0-50/month depending on scale
