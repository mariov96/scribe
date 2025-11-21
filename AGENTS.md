# AI Assistant Integration Guide

This project uses the **Session Continuity Framework (SCF) v2.0** for context preservation and AI cost optimization.

## For AI Assistants

**Read these files first when starting work**:

1. **`.scf/BUILDSTATE.md`** - Strategic context, vision, architecture, key decisions
2. **`.scf/BUILDSTATE.json`** - Technical specifications, metadata, current phase

These files contain everything you need to understand:
- Project goals and constraints
- Current development phase and focus areas
- Architecture patterns and technology stack
- Key decisions with rationale
- Active work areas and blockers

## Context Caching (Cost Optimization)

This project supports **automatic context caching**:

- BUILDSTATE files cached when >4096 tokens
- Cache invalidated automatically on content changes
- **Savings**: 75-90% cost reduction on repeated context loads
- Cost tracking in `.scf/cache_metadata.json`

## Voice Profiles

Tracks which AI assistant is active:
- **Current**: GitHub Copilot (pragmatic, moderate verbosity)
- **Session History**: `.scf/sessions/`
- **Preferences**: Defined in `voice_context` of BUILDSTATE.json

## Project Hub

This is a **spoke project** connected to the SCF hub:
```
/home/mario/projects/session-continuity-framework
```

**Hub provides**:
- AI service registry (model pricing, capabilities)
- Recommendation engine (cost optimization suggestions)
- Learning moments (high-impact insights shared across projects)
- Service discovery (new models, pricing changes)

## Quick Context Load

```python
from pathlib import Path
import json

buildstate = Path(".scf/BUILDSTATE.json")
context = json.loads(buildstate.read_text())

print(f"Project: {context['project']['name']}")
print(f"Phase: {context['current_phase']['name']}")
print(f"Focus: {context['voice_context']['focus_areas']}")
```

## Updating Context

When making significant changes:

1. Update `.scf/BUILDSTATE.md` (strategic context)
2. Update `.scf/BUILDSTATE.json` (technical specs)
3. Add entry to `change_log` array
4. Tag high-impact decisions (impact >= 8) for moment tracking

## Cost Optimization

Check AI service recommendations:
```bash
python3 ~/projects/session-continuity-framework/scf_recommendation_engine.py "C:\code\scribe" --recommend
```

Get service alternatives:
```bash
python3 ~/projects/session-continuity-framework/scf_service_registry.py --check-alternatives gpt-4o
```

## Project Structure

```
scribe/
├── .scf/                  # SCF v2.0 continuity framework
│   ├── BUILDSTATE.json    # Technical specs
│   ├── BUILDSTATE.md      # Strategic context
│   ├── archives/          # Historical snapshots
│   ├── sessions/          # AI conversation logs
│   └── voices/            # AI personality profiles
├── src/scribe/            # Core application
├── tests/                 # Test suite
├── docs/                  # Documentation
└── AGENTS.md              # This file (symlink to BUILDSTATE.md)
```

---

**Note**: AGENTS.md is linked to `.scf/BUILDSTATE.md` for compatibility with AI tools that look for this filename.
