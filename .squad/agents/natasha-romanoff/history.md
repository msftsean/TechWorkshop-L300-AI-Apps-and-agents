# Project Context

- **Project:** TechWorkshop-L300-AI-Apps-and-agents
- **Created:** 2026-04-09

## Core Context

Agent Natasha Romanoff initialized and ready for work.

## Recent Updates

📌 Team initialized on 2026-04-09

## Learnings

Initial setup complete.

### Exercise 6 — Red Teaming Agent & Custom Attack Prompts
- Created `src/app/agents/redTeamingAgent_initializer.py` with full red team agent: Azure AI Project config, OpenAI chat target, Cora agent HTTP target, and async scan with 5 attack strategies (Flip, ROT13, Base64, AnsiAttack, Tense).
- Extended `src/data/custom_attack_prompts.json` from 1 category (violence) to 4 categories: violence, sexual, hate_unfairness, self_harm.
- Both files pass Python AST and JSON syntax validation.
- Red team custom attack prompts follow a strict schema: metadata with target_harms, messages array, modality, source, and id fields.
