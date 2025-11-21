# Scribe - Strategic Context

**SCF v2.0** | **Structure: v2 (.scf/ directory)** | **Hub: /home/mario/projects/session-continuity-framework**

---

## Project Vision

**Scribe** is the **open-source voice-first automation platform** that actually remembers what you said and learns from you. It's the successor to WhisperWriter, evolved into a complete voice ecosystem.

### The Problem We're Solving

Voice assistants today have three fatal flaws:
1. **Corporate Lock-in**: Siri, Alexa, Cortana - all require subscriptions and cloud dependencies
2. **Memory Amnesia**: They forget everything you've told them
3. **Closed Gardens**: No way to extend or customize without vendor approval

### Our Solution

An **open-source, local-first voice platform** that:
- **Remembers Everything**: Conversation memory with instant recall
- **Learns From You**: Voice profiles adapt to your speech patterns and vocabulary
- **Infinitely Extensible**: Community plugins for any use case
- **Proves Its Value**: Quantifiable time savings metrics

---

## Core Capabilities

### 1. Voice-First Everything
```
"Hey Scribe, switch to Chrome"       → App switching
"Scribe, pause Spotify"              → Media control
"Write this down: Meeting notes..."  → Transcription
"Where did we talk about X?"         → Memory search
```

### 2. Persistent Memory System
- **Conversation Storage**: SQLite database with full-text search
- **Context Awareness**: Knows which app, URL, file you were using
- **Cross-Reference**: Links related conversations automatically
- **Privacy-First**: All data stays local unless you opt into sync

### 3. Learning Engine
- **Voice Profile Building**: Adapts to your speech patterns over time
- **Custom Vocabulary**: Learns jargon, names, domain-specific terms
- **Command Patterns**: Discovers your common workflows
- **Performance Metrics**: Tracks accuracy improvements

### 4. Value Proof
```
Your Scribe Value Report - This Month

Time Saved: 26.4 hours
├─ Typing: 13.9h (45,382 words at speaking speed)
├─ Context Switching: 10.4h (1,247 commands)
└─ Memory Recall: 2.1h (23 instant searches)

ROI: $1,320 (at $50/hour knowledge work rate)
```

---

## Technical Architecture

### Core Components

**Voice Pipeline:**
1. **Audio Capture**: System audio input (microphone)
2. **Transcription**: Whisper (local or API)
3. **Command Router**: Parse intent, route to handlers
4. **Action Executor**: Execute command or transcribe

**Memory System:**
1. **Conversation DB**: SQLite with FTS5 full-text search
2. **Context Capture**: App, URL, file, timestamp
3. **Search Engine**: Fast semantic + keyword search
4. **Sync Engine**: Optional cross-device sync

**Plugin Architecture:**
1. **Plugin Loader**: Dynamic plugin discovery
2. **Event System**: Pub/sub for plugin communication
3. **Sandboxing**: Isolated plugin execution
4. **Marketplace**: Community plugin distribution

### Technology Stack

- **Python 3.11+**: Core runtime
- **FastAPI**: REST API and WebSocket support
- **Whisper**: Speech-to-text (OpenAI)
- **SQLite + FTS5**: Memory storage
- **Pydantic**: Data validation
- **pytest**: Testing framework

### Performance Targets

- **Latency**: <200ms voice command execution
- **Accuracy**: >95% transcription accuracy
- **Memory**: <500MB RAM baseline
- **Search**: <50ms memory query response

---

## Development Phases

### Phase 1: Core Platform (Current - v2.0.0-alpha)
- [x] Voice transcription pipeline
- [x] Basic command routing
- [x] Conversation memory database
- [x] Plugin system foundation
- [ ] Value metrics dashboard

### Phase 2: Intelligence (Next)
- [ ] Voice profile learning
- [ ] Context-aware suggestions
- [ ] Command prediction
- [ ] Advanced memory search

### Phase 3: Ecosystem (Future)
- [ ] Plugin marketplace
- [ ] Mobile companion app
- [ ] Enterprise deployment
- [ ] Multi-language support

---

## Key Decisions

### Decision: Local-First Architecture (Impact: 10/10)
**Date**: 2025-11-20

**Rationale**: User privacy and data sovereignty are non-negotiable core values. Cloud sync is optional, not required.

**Alternatives Considered**:
- Cloud-only: Rejected due to privacy concerns and vendor lock-in
- Hybrid-default: Rejected because it normalizes cloud dependency

**Implications**:
- Requires robust local storage and sync conflict resolution
- Limits certain AI features that require cloud processing
- Attracts privacy-conscious users as primary audience

### Decision: Plugin Architecture (Impact: 9/10)
**Date**: 2025-11-20

**Rationale**: Community innovation drives long-term platform success. Plugin system enables rapid feature addition without core complexity.

**Alternatives Considered**:
- Monolithic: Rejected due to maintenance burden
- Microservices-only: Over-engineered for current scale

**Implications**:
- Need solid plugin API and sandboxing
- Community management becomes critical
- Potential security surface area increases

---

## Open Questions

1. **AI Integration**: Which LLMs should we integrate? (Claude, GPT-4, Gemini, local models?)
2. **Monetization**: How do we sustain development? (Enterprise features, hosted option, donations?)
3. **Mobile Strategy**: Native apps vs PWA for mobile companion?
4. **Enterprise Features**: What do corporate users need? (SSO, audit logs, compliance?)

---

## Context for AI Assistants

**Current Focus**: Stabilizing core transcription pipeline and implementing conversation memory database.

**Development Style**:
- Pragmatic, maintainable code
- Comprehensive tests for critical paths
- Clear documentation for community contributors
- Performance-first for user-facing features

**Key Files**:
- `src/scribe/`: Core application code
- `tests/`: Test suite
- `README.md`: User-facing documentation
- `.scf/`: SCF context management

---

## SCF Integration

This project uses **SCF v2.0** for context preservation across development sessions:

- **Context Caching**: Automatic when BUILDSTATE >4096 tokens
- **Cost Tracking**: AI usage monitored for optimization
- **Voice Profiles**: Tracks which AI assistant is active
- **Learning Moments**: High-impact decisions shared with ecosystem

**Hub Connection**: `/home/mario/projects/session-continuity-framework`

This enables:
- Cost-optimized AI interactions
- Service recommendations (best model for each task)
- Cross-project learning moment aggregation
- Persistent conversation context across sessions
