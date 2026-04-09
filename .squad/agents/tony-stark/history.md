# Project Context

- **Project:** TechWorkshop-L300-AI-Apps-and-agents
- **Created:** 2026-04-09

## Core Context

Agent Tony Stark initialized and ready for work.

## Recent Updates

📌 Team initialized on 2026-04-09

## Learnings

Initial setup complete.

### Exercise 3 — A2A Protocol Integration (2026-04-09)
- **Task:** Implemented Exercise 3 (Task 1 + Task 2) — A2A Protocol integration for the Zava Product Helper.
- **Files created:**
  1. `src/a2a/agent/product_management_agent.py` — Main agent with ProductAgent (get_products tool), MarketingAgent, RankerAgent, and ProductManagerAgent orchestrator. Uses Agent Framework with Azure OpenAI via managed identity.
  2. `src/a2a/agent/agent_executor.py` — A2A protocol executor bridging the agent to A2A event queues (streaming, task lifecycle).
  3. `src/a2a/agent/a2a_server.py` — A2A server wrapper with AgentCard, skills, and Starlette app for mounting.
  4. `src/a2a/api/chat.py` — FastAPI chat router with `/chat/message` (sync), `/chat/stream` (SSE), and session management endpoints.
- **Architecture:** Multi-agent delegation pattern — ProductManagerAgent delegates to ProductAgent, MarketingAgent, or RankerAgent based on query type. ResponseFormat (Pydantic) enforces structured output with status tracking.
- **Verification:** All 4 files pass `ast.parse` syntax check and the product_management_agent imports successfully.

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

### Exercise 4 — Telemetry Instrumentation (2026-04-09)
- **What:** Uncommented OpenTelemetry + Azure Monitor instrumentation in 3 files: `chat_app.py`, `agent_processor.py`, `discountLogic.py`.
- **Pattern:** Each file imports `OpenAIInstrumentor` from `opentelemetry.instrumentation.openai_v2`, then calls `configure_azure_monitor()` with the `APPLICATIONINSIGHTS_CONNECTION_STRING` env var, then calls `OpenAIInstrumentor().instrument()` to auto-instrument all OpenAI SDK calls.
- **Files changed:**
  1. `src/chat_app.py` — lines 14, 20-21, 67-69
  2. `src/app/agents/agent_processor.py` — lines 31, 35-36
  3. `src/app/tools/discountLogic.py` — lines 12, 16-17
- **Gotchas:**
  - `APPLICATIONINSIGHTS_CONNECTION_STRING` must be set as an env var on the Container App, otherwise the app will crash on startup with a `KeyError`.
  - The `opentelemetry-instrumentation-openai-v2` package must be installed (it's already in `pyproject.toml`).
  - `configure_azure_monitor()` is called at module import time (top-level), so telemetry is active from the very start of the process.

### Exercise 5 — CI/CD Workflows (2026-04-09)
- **Task:** Created GitHub Actions workflows for container deployment and all 6 Foundry agent deployments, plus prompt update.
- **Files created:**
  1. `.github/workflows/deploy-container.yml` — Container Apps build+deploy on push to `src/**` on main.
  2. `.github/workflows/customer-loyalty_agent_update.yml` — Deploys customer-loyalty agent on prompt/JSON change.
  3. `.github/workflows/cart-manager_agent_update.yml` — Deploys cart-manager agent.
  4. `.github/workflows/cora_agent_update.yml` — Deploys cora agent (ShopperAgentPrompt.txt).
  5. `.github/workflows/handoff-service_agent_update.yml` — Deploys handoff-service agent.
  6. `.github/workflows/interior-designer_agent_update.yml` — Deploys interior-designer agent.
  7. `.github/workflows/inventory-agent_agent_update.yml` — Deploys inventory-agent agent.
- **Files deleted:** `.github/workflows/jekyll-gh-pages.yml` (unused in fork).
- **Files modified:** `src/prompts/CustomerLoyaltyAgentPrompt.txt` — added content handling guideline for answer and discount_percentage columns.
- **Pattern:** Each agent workflow triggers on push to its prompt file, JSON definition, or own workflow file. Uses az rest POST to Foundry REST API with jq-built payload.
- **Validation:** All 11 workflow YAML files pass yaml.safe_load validation.

### Workshop Manual Tasks SWA (2026-04-09)
- **Task:** Built a standalone Azure Static Web App for tracking manual workshop tasks.
- **Files created:**
  1. `src/swa/index.html` — Single-file SWA with 7 tabbed task panels (Exercises 4/5/6), 45 checkable steps, copy-to-clipboard buttons, localStorage progress persistence, progress bar, and celebration state.
  2. `src/swa/staticwebapp.config.json` — Azure SWA config with navigation fallback and security headers.
- **Design:** Mission-control dashboard aesthetic — dark theme (#06090f base), Chakra Petch + JetBrains Mono fonts, cyan/amber/green accent palette, scanline overlay, grid texture background, CSS-only checkboxes with glow effects.
- **Features:** 7 tabs (Connect App Insights, Set Env Vars, Deploy to Production, Create Service Principal, Set GitHub Secrets, Run Red Team Eval, Create Agent Evals), per-step checkboxes with localStorage, overall progress bar, tab completion badges, copy-to-clipboard for commands/values, particle celebration overlay on 100% completion.
- **No build step:** Pure HTML + CSS + JS, no framework, no dependencies.
