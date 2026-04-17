# 🌌 Cloud Sovereignty: 'One-Click' Deployment Guide

This guide describes how to deploy the **Universal Talent Singularity (v8.1)** to the cloud using **Render** or **Railway**. By following these steps, you will transition the ecosystem from a local environment to a managed, high-availability institutional cloud.

---

## 🚀 One-Click Deploy (Render.com)

Render uses the `render.yaml` "Blueprint" included in this project to orchestrate your entire stack.

### 1. Connect your Repository
1. Log in to your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** -> **Blueprint**.
3. Connect your GitHub repository.

### 2. Configure Institutional Secrets
During the Blueprint setup, you will be prompted for environment variables. Ensure the following are set:
- **`GROQ_API_KEY`**: Your live Groq API key (Required for AI Analysis).
- **`SECRET_KEY`**: A long, random string for JWT security (If not generated automatically).
- **`DATABASE_URL`**: This will be automatically linked via the included PostgreSQL service.

### 3. Deploy
1. Click **Apply**.
2. Render will automatically spin up:
   - **`singularity-api`**: The FastAPI Backend.
   - **`singularity-dashboard`**: The Streamlit Frontend.
   - **`singularity-db`**: The Managed PostgreSQL database.

---

## ⚡ Deployment via Railway.app

Railway utilizes the `Procfile` and Dockerfiles for deployment.

1.  Connect your GitHub repository to a new Railway project.
2.  Railway will detect the Dockerfiles.
3.  Add two services:
    -   **Backend**: Set the build command to use `Dockerfile.backend`.
    -   **Frontend**: Set the build command to use `Dockerfile.frontend`.
4.  Add a **Postgres** plugin to your project.
5.  Set the `API_URL` environment variable for the Frontend to point to your Railway Backend URL.

---

## 🛡️ Post-Deployment Health Check

Once live, verify your deployment:
- **API Health**: Visit `https://your-api-name.onrender.com/health` (Should return `{"status": "healthy"}`).
- **Neural Docs**: Visit `https://your-api-name.onrender.com/docs` to verify all recruitment modules are active.
- **Strategic Dashboard**: Visit the Frontend URL to begin global talent mapping.

---
*End of Institutional Cloud Roadmap*
