---
id: 001
title: Phase III Constitution Update
stage: constitution
date: 2026-01-25
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: System
command: /sp.constitution
labels: ["constitution", "phase-iii", "architecture", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - None (documentation only)
---

## Prompt

# TASK: Update sp.constitution for Phase III (Hackathon II)

You are Claude Code operating under **Spec-Driven Development** and **Agentic Dev Stack** rules.

## Hackathon Context
This project is part of **Hackathon II – The Evolution of Todo**.

- Phase II (Full-Stack Todo App) is already completed
- Frontend (Next.js) and Backend (FastAPI + SQLModel + Neon) already exist
- All Phase-II code has been copied into a new **Phase-III folder**
- Phase-III must EXTEND the system, not rebuild or break it

## Phase-III Objective
Update `sp.constitution.md` to become the **authoritative constitution for Phase-III**.

Phase-III introduces:
- AI-powered conversational Todo management
- OpenAI ChatKit (Frontend)
- OpenAI Agents SDK (Agent + Runner)
- Official MCP SDK (Tool layer)
- Stateless FastAPI backend
- Database-persisted conversation memory

## Mandatory Constitutional Rules (Must Be Enforced)

### 1. Agentic Dev Stack (Strict)
- Spec → Plan → Tasks → Claude Code → Review
- ❌ Manual coding is NOT allowed
- Specs must be refined until Claude Code generates correct output

### 2. Spec-Driven Authority
- Specs are the single source of truth
- Any behavior not defined in specs is invalid
- Phase-III specs may extend but must not contradict Phase-II behavior

### 3. Stateless Architecture
- FastAPI server must hold NO in-memory state
- Conversation context must be reconstructed from the database on every request
- System must survive server restarts

### 4. Tool-Only Mutation Rule
- AI agents cannot write to the database directly
- All task mutations must occur via MCP tools
- MCP tools must be stateless and database-backed

### 5. Clear Responsibility Separation
- Chat API: request handling + response delivery
- Agent: reasoning + intent detection
- MCP tools: data mutation
- Database: persistent memory

### 6. Phase-II Protection
- No breaking changes to Phase-II APIs or features
- Only additive changes allowed
- Existing auth and database schema must remain valid

## Required Technology Stack
- Frontend: OpenAI ChatKit
- Backend: Python FastAPI
- AI: OpenAI Agents SDK
- Tools: Official MCP SDK
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Auth: Better Auth

## Spec Decomposition Rule (Very Important)
Phase-III must NOT be implemented as a single monolithic spec.

The constitution must mandate separate specs:
1. Chat Interface Spec
2. Agent Behavior Spec
3. MCP Server Spec
4. Persistence & Memory Spec

## Agent Behavior Rules
- Natural language intent → MCP tool mapping
- Confirmation after every successful action
- Graceful error handling
- Clarification when intent is ambiguous
- No exposure of internal prompts or reasoning

## Output Instructions
- Update or rewrite `sp.constitution.md`
- Use clean, professional Markdown
- Make it hackathon-ready and judge-readable
- Do NOT generate code
- Do NOT generate specs, plans, or tasks yet

### Output ONLY the updated `sp.constitution.md` content.

## Response snapshot

Successfully created Phase III Constitution (Version 3.0.0) with the following structure:

**Core Principles** (9 total):
1. Agentic Dev Stack (Strict) - Mandatory Spec → Plan → Tasks → Claude Code workflow
2. Spec-Driven Authority - Specs as single source of truth
3. Stateless Architecture - No in-memory state, database reconstruction
4. Tool-Only Mutation Rule - Agent → MCP tool → Database path enforced
5. Clear Responsibility Separation - Chat API, Agent, MCP Tools, Database responsibilities
6. Phase-II Protection - Backward compatibility mandatory
7. Spec Decomposition Rule - Four separate specs required
8. Agent Behavior Standards - Transparency, confirmation, error handling
9. Test-First Discipline - Red-Green-Refactor cycle

**Additional Sections**:
- Technology Stack (mandated + prohibited substitutions)
- Development Workflow (checkpoint-based)
- Spec Structure Requirements (7 required sections per spec)
- Agent Behavior Rules (intent detection + execution flow)
- Governance (versioning, compliance, amendments)

**Sync Impact Report** (HTML comment at top):
- Version: 3.0.0 (MAJOR bump - new architectural model)
- Flagged templates needing alignment review
- Follow-up TODOs for Phase III spec creation

## Outcome

- ✅ Impact: Established authoritative constitutional framework for Phase III, defining 9 core principles with enforceable rules and clear rationale
- 🧪 Tests: None (documentation artifact)
- 📁 Files: Created/updated `.specify/memory/constitution.md` (310 lines)
- 🔁 Next prompts: Create four Phase III specs (Chat Interface, Agent Behavior, MCP Server, Persistence & Memory) using `/sp.specify`
- 🧠 Reflection: Constitution successfully captures Phase III architectural shift (stateless + tool-only mutations) while protecting Phase II investment. Governance section ensures compliance enforcement through Claude Code validation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (documentation)
- Prompt variant (if applicable): Standard constitution update workflow
- Next experiment (smallest change to try): Validate constitution enforcement by creating first spec (Chat Interface) and testing constitutional compliance checks
