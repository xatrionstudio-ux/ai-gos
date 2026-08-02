# ADR-001: Selection of LangGraph as Workflow Runtime Engine

- **Status**: Approved
- **Deciders**: Platform Architecture Team
- **Date**: 2026-08-02

## Context & Problem Statement
AGOS requires an agent orchestration runtime capable of executing multi-node directed graphs with state persistence, automated checkpoints after every node, conditional routing based on confidence scores, and native Human-in-the-Loop (HITL) pause/resume semantics.

## Decision Drivers
- State persistence and state serialization
- Checkpointing after every node execution
- Parallel node execution (concurrency)
- Dynamic graph compilation
- Human-in-the-Loop approval pausing

## Considered Options
1. Custom asyncio graph runner
2. CrewAI
3. AutoGen
4. LangGraph

## Decision Outcome
Chosen Option: **LangGraph**, because it natively models agent workflows as directed state graphs (`StateGraph`), provides automated checkpoints, and natively supports conditional edge routing and HITL pauses.
