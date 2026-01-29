<!--
SYNC IMPACT REPORT
==================
Version Change: [Baseline] → 3.0.0
Rationale: MAJOR bump - Phase III introduces fundamentally new architectural principles (stateless backend, tool-only mutations, agentic dev stack) that supersede prior development models.

Modified Principles:
- NEW: I. Agentic Dev Stack (Strict)
- NEW: II. Spec-Driven Authority
- NEW: III. Stateless Architecture
- NEW: IV. Tool-Only Mutation Rule
- NEW: V. Clear Responsibility Separation
- NEW: VI. Phase-II Protection
- NEW: VII. Spec Decomposition Rule
- NEW: VIII. Agent Behavior Standards
- NEW: IX. Test-First Discipline

Added Sections:
- Technology Stack
- Development Workflow
- Spec Structure Requirements
- Agent Behavior Rules
- Governance

Templates Requiring Updates:
✅ constitution.md - Updated
⚠ .specify/templates/plan-template.md - Requires Phase III alignment check
⚠ .specify/templates/spec-template.md - Requires stateless architecture validation section
⚠ .specify/templates/tasks-template.md - Requires MCP tool task categorization

Follow-up TODOs:
- Validate all Phase II APIs remain unchanged
- Create Phase III feature specs (Chat Interface, Agent Behavior, MCP Server, Persistence & Memory)
-->

# Phase III: AI-Powered Todo App Constitution

**Hackathon II – The Evolution of Todo**

This constitution governs Phase III development, which extends the completed Phase II full-stack Todo application with AI-powered conversational task management capabilities.

## Context

- **Phase II Status**: Complete (Next.js frontend + FastAPI backend + SQLModel + Neon DB + Better Auth)
- **Phase III Objective**: Add conversational AI interface while preserving all Phase II functionality
- **Development Model**: Spec-Driven Development + Agentic Dev Stack
- **Architecture Shift**: Stateless backend with database-persisted conversation memory

## Core Principles

### I. Agentic Dev Stack (Strict)

**Rule**: All development MUST follow: Spec → Plan → Tasks → Claude Code → Review

**Non-Negotiables**:
- Manual coding is **PROHIBITED**
- Specs must be refined iteratively until Claude Code generates correct output
- No implementation begins without approved spec + plan + tasks
- All code changes originate from Claude Code execution of validated tasks

**Rationale**: Ensures reproducibility, consistency, and prevents scope creep. Forces precision in requirements before implementation begins.

### II. Spec-Driven Authority

**Rule**: Specifications are the single source of truth for all behavior and architecture decisions.

**Non-Negotiables**:
- Any behavior not defined in specs is invalid and must not be implemented
- Phase III specs may **extend** but MUST NOT **contradict** Phase II behavior
- Conflicts between specs and code are always resolved by updating code to match specs
- Ambiguities in specs must be clarified through spec amendments before coding

**Rationale**: Prevents drift, ensures judge-readable documentation, and maintains hackathon presentation clarity.

### III. Stateless Architecture

**Rule**: The FastAPI backend MUST hold NO in-memory state between requests.

**Non-Negotiables**:
- Conversation context reconstructed from database on every request
- No session stores, memory caches, or global variables for conversational state
- System must survive server restarts without losing functionality
- All agent state persisted in Neon database

**Rationale**: Ensures scalability, simplifies deployment, and prevents data loss. Critical for production-ready hackathon demo.

### IV. Tool-Only Mutation Rule

**Rule**: AI agents CANNOT write to the database directly. All task mutations MUST occur via MCP tools.

**Non-Negotiables**:
- Agent → MCP tool → Database is the only valid mutation path
- MCP tools are stateless and database-backed
- Agents may read from database for context but never write
- All CRUD operations on todos abstracted into MCP tool functions

**Rationale**: Enforces separation of concerns, makes agent logic testable in isolation, and ensures data integrity through controlled interfaces.

### V. Clear Responsibility Separation

**Rule**: Each component has exactly one responsibility.

**Responsibilities**:
- **Chat API (FastAPI)**: HTTP request handling + response delivery + auth validation
- **Agent (OpenAI Agents SDK)**: Natural language understanding + intent detection + reasoning
- **MCP Tools (Official MCP SDK)**: Todo data mutations + database interactions
- **Database (Neon)**: Persistent memory for todos + conversations

**Non-Negotiables**:
- No business logic in API routes (delegate to agent)
- No database access in agent code (use MCP tools)
- No AI reasoning in MCP tools (pure data operations)

**Rationale**: Simplifies testing, debugging, and future maintenance. Each layer can be modified independently.

### VI. Phase-II Protection

**Rule**: Phase III MUST NOT break any Phase II functionality.

**Non-Negotiables**:
- All Phase II REST APIs remain unchanged and functional
- No modifications to existing auth flows
- Database schema may be extended but existing tables/columns unchanged
- Phase II frontend must continue working without modification

**Constraints**:
- Only **additive** changes allowed
- New features isolated in separate routes/modules
- Backward compatibility mandatory

**Rationale**: Preserves hackathon progression narrative. Judges must see evolution, not replacement.

### VII. Spec Decomposition Rule

**Rule**: Phase III MUST NOT be implemented as a single monolithic spec.

**Required Specs** (each as separate file under `specs/phase-iii/`):
1. **Chat Interface Spec** (`chat-interface.spec.md`)
   - OpenAI ChatKit integration
   - UI/UX for conversational todo management
   - Message rendering and interaction patterns

2. **Agent Behavior Spec** (`agent-behavior.spec.md`)
   - Intent detection logic
   - Natural language → MCP tool mapping
   - Confirmation and error handling flows

3. **MCP Server Spec** (`mcp-server.spec.md`)
   - Tool definitions and schemas
   - Database interaction layer
   - Stateless operation guarantees

4. **Persistence & Memory Spec** (`persistence-memory.spec.md`)
   - Conversation history schema
   - Context reconstruction logic
   - Database design for stateless sessions

**Rationale**: Prevents overwhelming complexity, enables parallel development planning, and ensures each concern is thoroughly addressed.

### VIII. Agent Behavior Standards

**Rule**: The AI agent MUST be helpful, transparent, and safe.

**Required Behaviors**:
- Natural language intent → MCP tool mapping with reasoning
- Confirmation after every successful action (e.g., "✅ Created task: 'Buy groceries'")
- Graceful error handling with user-friendly messages
- Clarification requests when intent is ambiguous
- No exposure of internal prompts, system messages, or reasoning traces

**Prohibited Behaviors**:
- Hallucinating task data not in database
- Executing destructive operations without confirmation
- Exposing implementation details to end users
- Assuming user intent without clarification

**Rationale**: Builds trust, prevents data corruption, and ensures professional demo quality.

### IX. Test-First Discipline

**Rule**: Tests written → User approved → Tests fail → Then implement.

**Non-Negotiables**:
- Red-Green-Refactor cycle strictly enforced
- Unit tests for MCP tools (isolated from database)
- Integration tests for agent + MCP tool flows
- End-to-end tests for chat API → agent → tools → database

**Coverage Requirements**:
- MCP tools: 100% (all CRUD operations)
- Agent logic: Core intent detection paths
- API routes: Auth + happy path + error cases

**Rationale**: Prevents regressions, ensures Phase II compatibility, and validates stateless architecture.

## Technology Stack

**Mandated Technologies**:
- **Frontend**: Next.js + OpenAI ChatKit
- **Backend**: Python FastAPI
- **AI**: OpenAI Agents SDK
- **Tools**: Official MCP SDK (Python)
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Auth**: Better Auth (existing Phase II)

**Prohibited Substitutions**:
- No alternative AI frameworks (must use OpenAI Agents SDK)
- No alternative MCP implementations (must use official SDK)
- No alternative databases (must use existing Neon instance)

**Rationale**: Ensures compatibility with Phase II and leverages officially supported libraries for hackathon credibility.

## Development Workflow

**Mandatory Sequence**:
1. **Spec Creation**: Use `/sp.specify` for each of the four required specs
2. **Architecture Planning**: Use `/sp.plan` for each spec (capture ADRs)
3. **Task Generation**: Use `/sp.tasks` for each spec
4. **Implementation**: Use Claude Code to execute tasks from `tasks.md`
5. **Review**: Validate Phase II compatibility + test coverage

**Checkpoints**:
- Spec approval before planning
- Plan approval before task generation
- Task approval before implementation
- Test pass before marking task complete

**Prohibited Shortcuts**:
- Skipping spec/plan/task phases
- Manual coding outside Claude Code
- Merging failing tests
- Implementing features not in specs

## Spec Structure Requirements

Each of the four Phase III specs MUST include:

**Required Sections**:
1. **Scope Boundaries**: In-scope vs out-of-scope (explicit)
2. **Phase II Dependencies**: Which Phase II components are consumed
3. **Interface Contracts**: API schemas, tool signatures, data models
4. **Stateless Guarantees**: How statelessness is maintained
5. **Error Handling**: Failure modes and recovery strategies
6. **Testing Strategy**: Unit, integration, and E2E test scenarios
7. **Acceptance Criteria**: Testable conditions for completion

**Validation Rules**:
- No ambiguous requirements ("should", "might", "could")
- All external dependencies explicitly named
- All data flows diagrammed or described
- All error paths documented

## Agent Behavior Rules

**Intent Detection**:
- Parse natural language to identify: CREATE, READ, UPDATE, DELETE, LIST
- Map intents to specific MCP tools
- Request clarification for ambiguous commands (e.g., "delete task" without ID)

**Execution Flow**:
1. Receive user message
2. Reconstruct conversation context from database
3. Detect intent + extract parameters
4. Call appropriate MCP tool(s)
5. Confirm result to user in natural language

**Error Handling**:
- Database errors → "⚠️ Unable to save changes. Please try again."
- Invalid parameters → "❓ Which task did you mean? Here are your open tasks: ..."
- Tool failures → "⚠️ That didn't work. [brief explanation]"

**Transparency**:
- Always confirm destructive actions before execution
- Show task details after creation/update
- Explain why clarification is needed

## Governance

**Authority**:
- This constitution supersedes all other development practices
- Amendments require documented justification + version bump
- All PRs must include constitution compliance checklist

**Versioning**:
- **MAJOR**: Backward-incompatible principle changes
- **MINOR**: New principles or sections added
- **PATCH**: Clarifications, wording fixes

**Compliance Review**:
- Every spec must reference applicable constitutional principles
- Every plan must validate against stateless architecture rule
- Every task must map to test-first discipline

**Amendment Process**:
1. Propose change with rationale in constitution issue
2. Validate impact on existing specs/plans/tasks
3. Update constitution with version bump
4. Propagate changes to all dependent templates
5. Create ADR if architecturally significant

**Enforcement**:
- Claude Code validates tasks against constitution before execution
- Spec reviews must verify constitutional alignment
- Non-compliant code rejected in review phase

---

**Version**: 3.0.0 | **Ratified**: 2026-01-25 | **Last Amended**: 2026-01-25
