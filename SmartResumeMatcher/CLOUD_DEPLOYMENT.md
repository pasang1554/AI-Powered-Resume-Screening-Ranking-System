# Deployment Guide

## Cloud Deployment Options

### 1. Railway (Easiest)

1. Push to GitHub
2. Connect to Railway.app
3. Auto-deploys with Dockerfile

### 2. Render

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: resume-api
    dockerfilePath: ./Dockerfile
    envVars:
      - key: DATABASE_URL
        value: sqlite:///data.db
```

### 3. Fly.io

```bash
fly launch
fly deploy
```

### 4. AWS ECS / Google Cloud Run

Use the Dockerfile for container deployment.

## Frontend (Streamlit)

### Streamlit Cloud (Free)

1. Push to GitHub
2. Connect at streamlit.io/cloud
3. Deploy directly

### HuggingFace Spaces (Free GPU)

1. Create new Space
2. Upload code
3. Auto-builds container

## Environment Variables

```env
DATABASE_URL=sqlite:///./smartresume.db
SECRET_KEY=your-secure-secret-key
GROQ_API_KEY=your-groq-api-key
```

## Production Checklist

- [ ] Change SECRET_KEY
- [ ] Enable HTTPS
- [ ] Set up monitoring (Sentry)
- [ ] Configure rate limiting
- [ ] Add proper CORS origins
- [ ] Set up CI/CD pipeline
- [ ] Add database backups
