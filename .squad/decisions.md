# Squad Decisions

## Active Decisions

### Application Insights Telemetry Not Working — Root Cause & Fix
**Author:** Tony Stark (Engineer)  
**Date:** 2026-04-10 | **Status:** Diagnosed, awaiting fix

Container App `gl4lk3hwa6s26-app` not sending live metrics to Application Insights. Root cause: telemetry instrumentation code exists in source (3 unpushed commits) but container was built before those commits. Running container contains old code. Fix: `git push origin main` to trigger CI/CD rebuild. Decision: Always verify commits are pushed and CI/CD deployment completes before expecting runtime behavior changes in deployed environment.

### Workshop SWA — Single-File Architecture
**Author:** Tony Stark  
**Date:** 2026-04-09 | **Status:** Implemented

Dashboard for manual workshop tasks across Exercises 4, 5, and 6. Built as single `index.html` file at `src/swa/` with no build step, no framework, no external JS dependencies. All CSS and JS inline. Zero build complexity, no dependency drift, portable (works offline), and uses localStorage for checkpoint persistence. 42KB single file with ~80 lines of inline JS. No changes to existing code or workflows.

### Exercise 6: Red Teaming Agent & Custom Attack Prompts
**Author:** Natasha Romanoff (Security & Testing)  
**Date:** 2026-04-09 | **Status:** Complete

Created the red teaming agent initializer and extended custom attack seed prompts to cover all four risk categories (violence, sexual, hate_unfairness, self_harm) required for comprehensive AI safety testing.

### Exercise 5: CI/CD Workflows for Container and Agent Deployment
**Author:** Tony Stark (Engineer) | **Date:** 2026-04-09 | **Status:** Complete

Created 8 GitHub Actions workflow files: 1 for container deployment + 6 for agent deployment. Also deleted jekyll-gh-pages.yml and updated CustomerLoyaltyAgentPrompt.txt.

### Exercise 4: Enable OpenTelemetry + Azure Monitor Instrumentation
**Author:** Tony Stark (Engineer) | **Date:** 2026-04-09 | **Status:** Complete

Uncommented OpenTelemetry + Azure Monitor instrumentation in `chat_app.py`, `agent_processor.py`, and `discountLogic.py`. Auto-instruments OpenAI SDK calls and exports to Application Insights.

### Exercise 3: A2A Protocol Architecture
**Author:** Tony Stark | **Date:** 2026-04-09 | **Status:** Implemented

Created final A2A server with ProductManagerAgent orchestrator, MarketingAgent, RankerAgent, ProductAgent (with get_products tool), and A2A executor. Multi-agent delegation pattern with streaming support.

### Container App Deployment Strategy
**Author:** Tony Stark (Engineer) | **Date:** 2026-04-09 | **Status:** Implemented

Use system-managed identity for ACR authentication. Deploy image and env vars via separate `az containerapp update` calls. Env vars for AI endpoints are non-sensitive.

### Docker Build Configuration for Zava Chat App
**Author:** Tony Stark (Engineer) | **Date:** 2026-04-09 | **Status:** Implemented

ACR: `gl4lk3hwa6s26cosureg.azurecr.io`, Image: `chat-app:latest`, Platform: `linux/amd64`. Use ACR Tasks for remote builds.

### RBAC Permissions for Container App Managed Identity
**Author:** Tony Stark (Engineer) | **Date:** 2026-04-09 | **Status:** Implemented

Assigned three roles to Container App's managed identity: Azure AI User (AI Services), Storage Blob Data Contributor (Storage), Cosmos DB Built-in Data Contributor (Cosmos DB).

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
