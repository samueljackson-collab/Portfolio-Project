# Infrastructure Stack

This directory contains a reproducible Docker Compose stack for the analytics and automation platform that powers Matomo, n8n, the hosted LLM, Stable Diffusion, Whisper ASR, and a Scrapyd-backed Scrapy service. The configuration is designed for operators who need clear runbooks, secrets management, and post-launch validation steps.

> **Prerequisites**
>
> - Docker Engine 20.10 or newer with the Docker Compose plugin
> - 16+ CPU cores and 32 GB RAM recommended (see per-service limits in `docker-compose.yml`)
> - Access to any model registries that require authentication (Hugging Face tokens, etc.)
> - Ports 5678, 6800, 8080, 8081, 9000, and 9090 available on the host

## 1. Bootstrap

1. Copy the environment template and edit secrets:

   ```bash
   cp infrastructure/.env.example infrastructure/.env
   $EDITOR infrastructure/.env
   ```

   Replace every `CHANGE_ME` value with production credentials. Populate `HUGGINGFACEHUB_API_TOKEN` if you need gated models for the LLM or Stable Diffusion services.

2. Pull images and launch the stack (choose the workflow that fits your team):

   - **Via scripts**

     ```bash
     scripts/bootstrap_stack.sh
     ```

   - **Via Makefile**

     ```bash
     make bootstrap
     ```

   Both options will pull images, build the custom Scrapyd container, and start all services in the background.

## 2. Day-to-Day Lifecycle

| Action             | Preferred command                         | Alternate command                         |
| ------------------ | ----------------------------------------- | ----------------------------------------- |
| Start (no pull)    | `make start`                              | `docker compose up -d` (with env flags)   |
| Stop & remove      | `make stop`                               | `scripts/shutdown_stack.sh`               |
| Restart            | `make restart`                            | `make stop && make start`                 |
| Show status        | `make status`                             | `docker compose ps`                       |
| Tail logs          | `make logs`                               | `docker compose logs -f`                  |
| Health validation  | `make validate`                           | `scripts/validate_stack.sh`               |

> All `docker compose` commands assume `--env-file infrastructure/.env -f infrastructure/docker-compose.yml`. The helper scripts wrap these flags so operators never have to remember them.

## 3. Health Checks & Post-Launch Validation

After the stack reports healthy containers (`make status`), run the scripted validation:

```bash
make validate
```

The script performs the following checks:

| Service             | Health URL (curl)                                         | Admin / UI URL                                   | Expected response                                          |
| ------------------- | -------------------------------------------------------- | ------------------------------------------------ | --------------------------------------------------------- |
| Matomo              | `curl -f http://localhost:${MATOMO_HTTP_PORT}/`           | `http://localhost:${MATOMO_HTTP_PORT}/`          | Returns HTML login/setup page                             |
| n8n                 | `curl -f http://localhost:${N8N_HTTP_PORT}/rest/healthz`  | `http://localhost:${N8N_HTTP_PORT}/`             | JSON body `{"status":"ok"}`                             |
| LLM (TGI)           | `curl -f http://localhost:${LLM_HTTP_PORT}/health`        | `http://localhost:${LLM_HTTP_PORT}/docs`         | JSON with model readiness & queue depth                   |
| Stable Diffusion    | `curl -f http://localhost:${STABLE_DIFFUSION_HTTP_PORT}/health` | `http://localhost:${STABLE_DIFFUSION_HTTP_PORT}/` | JSON containing `"status": "ok"`                        |
| Whisper (ASR Webservice) | `curl -f http://localhost:${WHISPER_HTTP_PORT}/health`    | `http://localhost:${WHISPER_HTTP_PORT}/docs`     | JSON containing `"status": "ok"` or model metadata      |
| Scrapyd (Scrapy)    | `curl -f http://localhost:${SCRAPYD_HTTP_PORT}/`          | `http://localhost:${SCRAPYD_HTTP_PORT}/`         | HTML landing page listing deployed Scrapy projects        |

If any check fails, inspect logs with `make logs` and review the troubleshooting section below.

## 4. Troubleshooting Guide

| Symptom | Likely Cause | Resolution |
| ------- | ------------ | ---------- |
| `scripts/bootstrap_stack.sh` exits complaining about Docker | Docker Engine or Compose plugin missing | Install Docker Engine 20.10+ and ensure `docker compose version` returns successfully. |
| Compose refuses to start because of missing `.env` | The secrets file has not been created | Copy `.env.example` to `.env` and populate credentials. |
| LLM container loops on download errors | Missing or invalid Hugging Face token | Export `HUGGINGFACEHUB_API_TOKEN` in `.env` with access to the requested model. |
| Stable Diffusion web UI prompts for password repeatedly | `INVOKEAI_WEB_UI_PASSWORD` not set or mismatched | Update the password in `.env` and restart the service: `docker compose ... up -d stable-diffusion`. |
| Matomo installer cannot reach the database | Database container still starting or credentials mismatch | Wait for health checks to pass, then confirm `MATOMO_DB_*` values in `.env` match the database container. |
| Whisper health check returns HTTP 404 | Model download still in progress or incorrect port | Wait for the container to finish downloading models and confirm `${WHISPER_HTTP_PORT}` is free; inspect `docker compose logs whisper` for progress. |

## 5. Teardown & Data Persistence

- Use `make stop` (or `scripts/shutdown_stack.sh`) to stop containers while retaining persistent volumes.
- Add `--volumes` to the shutdown script if you want to wipe state: `scripts/shutdown_stack.sh --volumes`.
- Persistent data paths are defined as Docker volumes in `docker-compose.yml`:
  - `matomo_db`, `matomo_html`
  - `n8n_data`
  - `llm_models`
  - `stable_diffusion_data`
  - `whisper_models`
  - `scrapy_projects`

## 6. Manual Validation (Advanced)

After `make validate`, you can conduct deeper checks:

1. **Matomo** – Visit the admin UI and finish the web installer. Verify the system report at `http://localhost:${MATOMO_HTTP_PORT}/index.php?module=CoreAdminHome&action=systemCheck`. Export the tracker code to confirm DB connectivity.
2. **n8n** – Log in with basic auth and run the demo workflow in `/workflows`. Ensure the webhook URL matches `N8N_WEBHOOK_URL`.
3. **LLM API** – Call the inference endpoint:

   ```bash
   curl -X POST http://localhost:${LLM_HTTP_PORT}/generate \
     -H 'Content-Type: application/json' \
     -d '{"inputs": "Hello"}'
   ```

4. **Stable Diffusion** – Authenticate with the web UI password, queue an image generation job, and confirm output in `/opt/invokeai/outputs`.
5. **Whisper** – Submit an audio transcription request to `http://localhost:${WHISPER_HTTP_PORT}/asr` or use the built-in Swagger UI to confirm the pipeline works.
6. **Scrapyd** – Deploy a sample project with `scrapyd-deploy` and verify it appears in the Scrapyd dashboard.

Keeping these runbooks version-controlled ensures the environment remains reproducible across operators and hardware.
