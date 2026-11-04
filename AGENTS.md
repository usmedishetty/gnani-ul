# Global Agent Constitution & Navigation Map

> **Harness Platform:** Google Antigravity (AGY)  
> **Architecture:** Antigravity-ECC (Version 1.0.0)  
> **Status:** Canonical Navigation Map & Cognitive Router  

---

## 1. The Invariant Lifecycle Loop

Every Antigravity session operates strictly under the 8-stage engineering loop:

```
[research] ➔ [plan] ➔ [test] ➔ [implement] ➔ [review] ➔ [verify] ➔ [remember] ➔ [improve]
```

No implementation code may be authored before research and test contracts are established.

---

## 2. Global Agent Taxonomy & Cognitive Routing

Antigravity-ECC routes incoming developer goals to 78 specialized agents:

```
                               ┌─────────────────────────────────┐
                               │   orchestrator (Lifecycle Hub)  │
                               └────────────────┬────────────────┘
          ┌───────────────────────┬─────────────┴─────────────┬───────────────────────┐
          ▼                       ▼                           ▼                       ▼
┌──────────────────┐    ┌──────────────────┐        ┌──────────────────┐    ┌──────────────────┐
│ Planning & Spec  │    │  Build & Repair  │        │ Review & Verify  │    │Domain Specialists│
│ • research-first │    │ • tdd-driver     │        │ • code-reviewer  │    │ • react-spec     │
│ • spec-writer    │    │ • build-fixer    │        │ • security-audit │    │ • node-backend   │
│ • arch-planner   │    │ • refactor-surg  │        │ • test-coverage  │    │ • go-microserv   │
│ • risk-assessor  │    │ • migration-eng  │        │ • regression-grd │    │ • python-fastapi │
└──────────────────┘    └──────────────────┘        └──────────────────┘    └──────────────────┘
```

See [docs/AGENT-CATALOG.md](file:///./docs/AGENT-CATALOG.md) for full descriptions, trigger conditions, and tool whitelists.

---

## 3. Context Window Optimization & Compaction Policy

1. **Context Scratchpad:** Keep the active context window lean. Offload logs, raw tool outputs, and documentation into SQLite `memory.db` or persistent Antigravity Artifacts.
2. **Threshold Gating:** When token usage approaches **135,000 tokens**, the `auto-compact-trigger` hook fires automatically:
   - Writes a persistent Compaction Artifact.
   - Purges transient tool stdout.
   - Flushes state to SQLite.
3. **Progressive Skill Disclosure:** Only frontmatter triggers are registered in system awareness. Detailed `SKILL.md` instructions are loaded just-in-time when trigger conditions match.

---

## 4. Tool Sandboxing & Privilege Tiers

Agents operate under least-privilege boundaries:
- **Read-Only Specialists (`research-first`, `code-reviewer`, `security-auditor`):** Restricted to `view_file`, `search`, and `browser`. Denied write or shell tools.
- **Implementation Drivers (`tdd-driver`, `refactor-surgeon`):** Permitted `view_file`, `replace_file_content`, and sandboxed `run_command`.
- **System Commands:** Intercepted by `command-sandbox-guard` to prevent destructive shell operations.

---

## 5. Hook Execution Graph

The hook runtime enforces 15 lifecycle events:
- **Startup:** `SessionStart` ➔ Loads memory facts and ADRs.
- **Invocation:** `BeforeAgentInvoke` ➔ Validates lifecycle loop order.
- **Tooling:** `BeforeToolCall` ➔ Checks agent whitelist. `AfterToolCall` ➔ Telemetry & instinct tracking.
- **Filesystem:** `BeforeFileEdit` ➔ AgentShield secret leak blocker. `AfterFileEdit` ➔ Test re-verification.
- **Compaction:** `OnTokenThreshold` (135k tokens) ➔ Triggers auto-compaction artifact.
- **Teardown:** `SessionEnd` ➔ Rotates JSONL logs and updates skill success rates.

---

## 6. Selective Rule Pack Inclusion

Rule packs located in `rules/` are loaded selectively:
- `rules/common/`: Universal standards (security baseline, code quality, commit conventions, token discipline, lifecycle loop).
- `rules/<language>/`: Per-language standards (TypeScript, Python, Go, Rust, Java, C#, Ruby, PHP, Swift, Kotlin).
- `rules/<framework>/`: Per-framework standards (React, Next.js, Django, FastAPI, Spring, Rails).

