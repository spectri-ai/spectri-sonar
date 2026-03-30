---
Date Created: 2026-03-30T00:26:39+0000
Date Updated: 2026-03-30T00:26:39+0000
---

# Spectri Sonar — Product Overview

## What it is

Spectri Sonar is a dashboard and command centre that gives you visibility across all your AI coding agent sessions. It scans session data from disk and presents a live overview of every active conversation across every project — titles, last messages, activity status, and whether a session is waiting for your response.

Think air traffic control for your coding sessions. You see everything at a glance without opening each VS Code window.

## Why it exists

When you're running multiple Claude Code sessions across multiple VS Code workspaces — sometimes 20 or 30 at once — you lose track. Which conversations are active? Which are waiting for input? What was that agent working on in the other project? Currently the only way to know is to click through every VS Code tab.

Sonar solves this by reading the session data that already exists on disk and presenting it in one place.

## Where it fits in the Spectri ecosystem

| Product | Role |
|---------|------|
| **Spectri** | CLI + specs + governance — how an individual agent works |
| **Spectri Scribe** | Collaborative document editor |
| **Spectri Speak** | Voice dictation |
| **Spectri Switch** (formerly PAL MCP) | Multi-model CLI — routes to Gemini, GPT, etc. |
| **Spectri Sonar** | Session dashboard — visibility across all agent sessions |
| **Spectri Synapse** (formerly intercom-mcp) | Agent-to-agent messaging bus |

Sonar is the observation layer. Spectri governs the work. Spectri Synapse (formerly intercom-mcp) carries messages between sessions. Sonar reads state and optionally sends messages through Synapse.

## What data is available

All session data lives in `~/.claude/` and is readable without any API calls:

| Data | Location | Contents |
|------|----------|----------|
| Active sessions | `~/.claude/sessions/*.json` | PID, sessionId, cwd, startedAt, entrypoint |
| Conversation transcripts | `~/.claude/projects/<key>/<sessionId>.jsonl` | Every message, tool call, hook event |
| Conversation titles | JSONL entries with type `ai-title` or `custom-title` | AI-generated and user-renamed titles |
| Session liveness | PID check via `kill -0 <pid>` | Whether the process is still running |
| Waiting for response | Last JSONL entry per session | If last message is assistant with a question, the session is waiting |

Initial implementation targets Claude Code. As the product matures, it will extend to other agents (Gemini CLI, OpenCode, Codex) — each will have its own session data format to parse.

## Session summaries

Conversation summaries can come from multiple sources:

- **Spectri session summary skill** — a skill being built into Spectri that generates summaries at session end or on demand
- **Spectri Switch** (formerly PAL MCP) — route conversation context to a lightweight model (e.g. Haiku) for on-demand summarisation
- **Spectri Synapse** (formerly intercom-mcp) — an agent could request a summary from another agent via the message bus
- **Local model** — a local LLM generating summaries without any API cost

Sonar should consume summaries from whatever source produces them. The dashboard displays the most recent summary per session. The summary generation itself is not Sonar's responsibility — it reads what others produce.

## Phases

### Phase 0 — Proof of concept

Before any UI work, validate that we can send a message from outside VS Code into an active Claude Code session. Build a small CLI test inside this repo that:

1. Reads `~/.claude/sessions/*.json` to find active sessions
2. Picks a target session
3. Sends a message that arrives in the active VS Code conversation

This tests the feasibility of the interactive path. If it works via Spectri Synapse (formerly intercom-mcp), we know the full architecture is viable. If it needs a different approach, we find out early.

### Phase 1 — Read-only dashboard

A localhost web app that scans `~/.claude/` and displays:

- Cards grouped by project
- Each card shows: conversation title, last agent message (truncated), start time, duration
- "Waiting for response" indicator — card header turns red or shows a notification badge when the session's last message is a question from the agent
- Session summaries where available
- Auto-refresh on a short interval (file watchers or polling)

**Start with HTML mockups** to get the UX right before writing any backend. The mockups should nail:
- Card layout and information density
- How projects group visually
- What "waiting for response" looks like
- What expanding a card to see the full conversation thread looks like (scrollable, not paginated)
- Mobile-friendly layout for phone access

Reference Paperclip's dashboard UI (https://github.com/paperclipai/paperclip) for inspiration on card layouts and information hierarchy, but Sonar is simpler — sessions not companies.

### Phase 2 — Conversation viewer

Click a card to expand and see the full conversation thread in a scrollable panel. Read directly from the JSONL transcript. Render:
- User messages
- Agent responses (markdown rendered)
- Tool calls (collapsed by default)
- Timestamps

### Phase 3 — Interactive dashboard

Connect to Spectri Synapse (formerly intercom-mcp) broker to send messages into active sessions:

- Text input per card — type a response, it arrives in the VS Code session
- The agent picks it up via Synapse's `check_messages` tool
- Response appears in both VS Code and the Sonar dashboard

This turns Sonar from a read-only monitor into a lightweight remote control for quick responses — useful when you're on your phone, on a small keyboard, or managing many sessions and don't want to context-switch into each VS Code window for a quick answer.

### Phase 4 — Web app

Move from localhost to a deployed web app accessible from anywhere. Requires:
- Authentication (the session data is sensitive)
- Either syncing session data to a server or running Sonar locally with remote access (e.g. Tailscale)

## Technical approach

- **Frontend:** React (aligns with Spectri ecosystem)
- **Backend:** Lightweight Node/Bun server reading `~/.claude/` directly
- **No database** — all data comes from the filesystem
- **File watchers** for live updates rather than polling where possible
- **Localhost first** — `localhost:3200` or similar, no deployment needed for MVP

## Multi-agent future

Phase 1 targets Claude Code only because that's what we use and the session data format is known. Future agent support:

- **Gemini CLI** — find where it stores session data, build a parser
- **OpenCode** — same approach
- **Codex CLI** — same approach

The dashboard would show tabs or sections per agent type, or a unified view with agent type indicated per card. The Spectri Synapse message bus is already agent-agnostic (the broker doesn't care what agent connects), so interactive messaging would work across agent types once adapters exist.
