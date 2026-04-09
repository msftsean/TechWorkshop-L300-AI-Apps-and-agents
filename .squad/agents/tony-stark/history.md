# Project Context

- **Project:** TechWorkshop-L300-AI-Apps-and-agents
- **Created:** 2026-04-09

## Core Context

Agent Tony Stark initialized and ready for work.

## Recent Updates

📌 Team initialized on 2026-04-09

## Learnings

Initial setup complete.

### Docker Build to ACR (2026-04-09)
- **ACR name:** `gl4lk3hwa6s26cosureg` (full: `gl4lk3hwa6s26cosureg.azurecr.io`)
- **Image:** `chat-app:latest`
- **Build command (from repo root):**
  ```
  az acr build --registry gl4lk3hwa6s26cosureg --image chat-app:latest --platform linux/amd64 --file src/Dockerfile src/
  ```
- **Build context must be `src/`** — the Dockerfile COPYs `pyproject.toml`, `uv.lock`, and `.` relative to its own directory, so the context needs to be the `src/` folder.
- **Platform:** `linux/amd64` is required for consistency.
- **Build time:** ~2m20s via ACR Tasks (Run ID: ch1).
- **Digest:** `sha256:faf85978437295e4e735eb5beea93ce8fb0e70f33a68527cc788dffba85e523e`
- **Gotchas:** The `.venv` directory is auto-excluded; `.dockerignore` in `src/` controls what gets uploaded. No auth issues when running from a Codespace with an active `az` session.

### Container App Deployment (2026-04-09)
- **Container App:** `gl4lk3hwa6s26-app`
- **Resource Group:** `rg-TechWorkshop-L300-AI-Apps-and-agents`
- **FQDN:** `gl4lk3hwa6s26-app.orangepebble-0db1aa7f.eastus2.azurecontainerapps.io`
- **Image deployed:** `gl4lk3hwa6s26cosureg.azurecr.io/chat-app:latest`
- **Target port:** 8000
- **ACR auth:** System-managed identity (`--identity system`). No passwords/secrets needed.
- **Deployment commands (in order):**
  1. `az containerapp registry set` — configure ACR auth with system identity
  2. `az containerapp update --image ...` — set the container image
  3. `az containerapp update --set-env-vars ...` — inject env vars (FOUNDRY_ENDPOINT, gpt_endpoint, embedding_endpoint, phi_4_endpoint)
- **Env vars set:** FOUNDRY_ENDPOINT, gpt_endpoint, embedding_endpoint, phi_4_endpoint
- **Gotchas:**
  - `minReplicas: 0` means the app scales to zero; first request after idle triggers a cold start (~2 min).
  - Curl needs `--max-time 120` or similar to survive the cold-start delay.
  - The system identity was already assigned; no AcrPull role grant was needed.
  - Provisioning state: Succeeded, running status: Running, HTTP 200 confirmed.

### Permission Fixes for Container App Managed Identity (2026-04-09)
- **Problem:** Container App `gl4lk3hwa6s26-app` system identity (principal `64597083-cad9-41b2-96fc-d05536a5302e`) got `PermissionDenied` calling Foundry agents — missing `Microsoft.CognitiveServices/accounts/AIServices/agents/write` data action.
- **Root cause:** The identity had `Cognitive Services OpenAI User` (sufficient for model calls) but **not** `Azure AI User` (required for Foundry agent operations like POST `/api/projects/{projectName}/openai/*`).
- **Roles assigned:**
  1. **Azure AI User** → on `aif-gl4lk3hwa6s26` (AI Services resource) — fixes the Foundry agent PermissionDenied error.
  2. **Storage Blob Data Contributor** → on `gl4lk3hwa6s26sa` (Storage account) — enables blob upload/download/delete for image storage and file tools.
  3. **Cosmos DB Built-in Data Contributor** → on `gl4lk3hwa6s26-cosmosdb` (Cosmos DB account, via SQL RBAC) — enables read/write to product catalog.
- **Commands used:**
  ```bash
  # Azure AI User on AI Services
  az role assignment create --assignee-object-id 64597083-cad9-41b2-96fc-d05536a5302e \
    --assignee-principal-type ServicePrincipal --role "Azure AI User" \
    --scope /subscriptions/.../Microsoft.CognitiveServices/accounts/aif-gl4lk3hwa6s26

  # Storage Blob Data Contributor
  az role assignment create --assignee-object-id 64597083-cad9-41b2-96fc-d05536a5302e \
    --assignee-principal-type ServicePrincipal --role "Storage Blob Data Contributor" \
    --scope /subscriptions/.../Microsoft.Storage/storageAccounts/gl4lk3hwa6s26sa

  # Cosmos DB Built-in Data Contributor (SQL RBAC, not Azure RBAC)
  az cosmosdb sql role assignment create --account-name gl4lk3hwa6s26-cosmosdb \
    --resource-group rg-TechWorkshop-L300-AI-Apps-and-agents \
    --role-definition-id "00000000-0000-0000-0000-000000000002" \
    --principal-id 64597083-cad9-41b2-96fc-d05536a5302e --scope "/"
  ```
- **Gotchas:**
  - `Cognitive Services OpenAI User` ≠ `Azure AI User`. The former covers model inference; the latter covers Foundry agent operations. You often need both.
  - Cosmos DB uses its own SQL RBAC system (`az cosmosdb sql role assignment create`), not standard Azure RBAC (`az role assignment create`). The built-in Data Contributor role ID is `00000000-0000-0000-0000-000000000002`.
  - Role propagation can take 5-10 minutes. If the app still errors after assignment, wait or restart the Container App revision.
