# 📜 SCRIBE

**The Open Voice Platform**

> Your personal memory keeper. From the community, for the community.

[![Version](https://img.shields.io/badge/version-2.0.0--alpha-blue)](https://github.com/yourusername/scribe)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![Open Source](https://img.shields.io/badge/open%20source-forever-brightgreen)](https://github.com/yourusername/scribe)

---

## 🎯 **What is Scribe?**

Scribe is the **open-source successor to WhisperWriter** - evolved into a complete voice automation platform that learns from you.

Think Siri/Alexa/Cortana, but:
- 🔓 **Open source** - See exactly how it works, modify anything
- 🏠 **Local-first** - Your data stays on your machine
- 🧠 **Actually learns** - Gets smarter with every use
- 🔌 **Infinitely extensible** - Community-driven plugins for everything
- 💰 **Free forever** - No subscriptions, no corporate lock-in

---

## ✨ **What Makes Scribe Different?**

### 🗣️ **Voice-First Everything**
```
"Hey Scribe, switch to Chrome"           → Switches to Chrome
"Scribe, pause Spotify"                  → Pauses music
"Write this down: Meeting notes..."      → Transcribes to active window
"Where did we talk about mortgage rates?" → Finds conversation + context
```

### 🧠 **It Actually Remembers**
- **Conversation Memory**: Recalls what you discussed and where
- **Voice Profile Learning**: Adapts to your speech patterns, vocabulary, jargon
- **Cross-Device Sync**: Learn on desktop, use on laptop - same intelligence
- **Context Awareness**: Knows which app, URL, or file you were using

### 📊 **Proves Its Value to YOU**
```
Your Scribe Value Report - This Month

Time Saved: 26.4 hours
├─ Typing: 13.9 hours (45,382 words at speaking speed)
├─ Context Switching: 10.4 hours (1,247 voice commands)
└─ Searching: 2.1 hours (23 instant recalls)

💰 Value at your rate: $1,980

Your Improvement:
├─ Accuracy: 87% → 94% (+7%)
├─ Speed: 145 WPM → 168 WPM (+16%)
└─ Errors: -34%
```

### 🔌 **Day 1 Extensions**
- **Window Manager**: Control windows by voice
- **Media Control**: Spotify, YouTube, system volume
- **Memory Scribe**: Remember and recall conversations
- **Sync Scribe**: Share learnings across devices
- **+ Community Plugins**: Build your own!

### ⚡ **GPU Acceleration** (New!)
- **5-10x faster transcription** with NVIDIA GPU support
- Automatic GPU detection and fallback to CPU
- Supports all modern NVIDIA GPUs (GTX 10 series+)
- See `GPU_QUICKSTART.md` for setup

---

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.11+
- Windows 10/11 (Mac/Linux support coming)
- Microphone
- (Optional) API key for AI enhancement

### **Installation**
```bash
# Clone the repository
git clone https://github.com/yourusername/scribe.git
cd scribe

# Install in development mode
pip install -e .

# Or use pip when released
pip install scribe-voice
```

### **First Run**
```bash
# Launch Scribe (recommended - if installed)
scribe

# Or run directly from source
python scribe.py
```

### **Setup Wizard**
On first run, Scribe will:
1. ✅ Check your Python environment
2. ✅ Configure your microphone
3. ✅ Set up your voice profile
4. ✅ (Optional) Add your API key for AI features
5. ✅ Choose your privacy/telemetry level
6. ✅ Enable default plugins

---

## 🎮 **How to Use**

### **Basic Transcription** (Classic Mode)
```
Press: Ctrl+Win (or configured hotkey)
Speak: "Send an email to John about the project update..."
Release: [Scribe types into active window]
```

### **Voice Commands** (New!)
```
You: "Hey Scribe"
Scribe: 🎤 Active

You: "Switch to Chrome"
Scribe: ✓ Switched to Chrome

You: "Pause Spotify"
Scribe: ✓ Paused Spotify

You: "Thanks"
Scribe: 💤 Sleeping
```

### **Memory & Context** (Game Changer!)
```
[Monday - Browsing mortgage rates in Chrome]
You: "Scribe, remember this page"
Scribe: ✓ Noted

[Friday - Writing code in VS Code]
You: "Scribe, where did we talk about mortgage rates?"
Scribe: "On a Chrome page: 'Top 10 Mortgage Companies'.
        Would you like me to open it?"

You: "Yes"
Scribe: ✓ [Opens exact page]
```

---

## 🏗️ **Architecture**

```
scribe/
├── src/scribe/
│   ├── core/              # Transcription engine
│   ├── plugins/           # Extension system
│   │   ├── window_manager/    # Control windows
│   │   ├── media_control/     # Control media playback
│   │   ├── memory_scribe/     # Remember conversations
│   │   └── sync_scribe/       # Multi-device sync
│   ├── analytics/         # Value tracking & learning
│   ├── ai/               # AI enhancement
│   └── ui/               # User interface
│
├── data/                 # Your data (gitignored)
│   ├── analytics/        # Voice profile, learnings
│   ├── logs/            # Session logs
│   ├── metrics/         # Performance data
│   └── sessions/        # Conversation history
│
├── profiles/            # Multi-user support
│   └── default/         # Your profile
│
└── plugins/             # Custom/community plugins
```

---

## 🔌 **Plugin System**

### **Day 1 Plugins**

#### **1. Window Manager**
```python
Commands:
- "switch to {app}"      → Activate application
- "minimize"             → Minimize current window
- "maximize"             → Maximize current window
- "close window"         → Close current window
```

#### **2. Media Control**
```python
Commands:
- "pause [app]"          → Pause playback
- "play / resume"        → Resume playback
- "next song / skip"     → Next track
- "volume up / down"     → Adjust volume
- "mute"                 → Mute audio
```

#### **3. Memory Scribe** (Opt-in)
```python
Commands:
- "remember this"                    → Save current context
- "where did we talk about {topic}"  → Search conversations
- "open that page"                   → Restore context
- "forget that"                      → Delete memory
```

#### **4. Sync Scribe**
```python
Commands:
- "sync to {device}"     → Sync voice profile
- "export profile"       → Backup profile
- "import profile"       → Load profile from file
```

### **Build Your Own Plugin**
```python
# plugins/my_plugin/plugin.py
from scribe.plugins.base import BasePlugin

class MyPlugin(BasePlugin):
    name = "my_plugin"
    version = "1.0.0"

    def commands(self):
        return [
            {
                'patterns': ['do something cool'],
                'handler': self.do_something,
                'examples': ['do something cool']
            }
        ]

    def do_something(self):
        return "Something cool done!"
```

See [Plugin Development Guide](docs/PLUGIN_DEVELOPMENT.md) for details.

---

## 📊 **Analytics & Privacy**

### **Your Data, Your Choice**

Scribe tracks analytics to prove its value **to you**:
- ✅ Time saved
- ✅ Accuracy improvements
- ✅ Command usage
- ✅ Feature effectiveness

**All data stays local by default.** Optionally share anonymized usage patterns to help improve Scribe.

### **Privacy Levels**
1. **None** (Default): No data shared, complete privacy
2. **Errors Only**: Share crash reports to fix bugs
3. **Usage Insights**: Share feature usage counts (no content)
4. **Full Collaboration**: Detailed patterns (still no conversation content)

**You can view/export/delete all collected data anytime.**

---

## 🌍 **Multi-Device Sync**

Share your voice learnings across devices:

### **Option 1: Local Network** (Most Private)
```bash
# On Desktop
scribe sync start

# On Laptop (same WiFi)
scribe sync discover
scribe sync connect desktop
```

### **Option 2: Manual Export** (Maximum Privacy)
```bash
# Desktop
scribe profile export --output my-profile.scribe

# Laptop
scribe profile import my-profile.scribe
```

### **Option 3: Cloud Sync** (Convenient, E2E Encrypted)
```bash
# Enable cloud sync (you control the keys)
scribe sync enable-cloud
```

**Your API keys are NEVER synced** - each device keeps its own.

---

## 🎯 **Roadmap**

### **v2.0 - The Foundation** (Current)
- ✅ Voice transcription with AI cleanup
- ✅ Plugin architecture
- ✅ Window Manager plugin
- ✅ Media Control plugin
- ✅ Value analytics
- ⏳ Wake word detection ("Hey Scribe")
- ⏳ Memory Scribe plugin
- ⏳ Multi-device sync

### **v2.5 - Intelligence** (Q1 2025)
- Voice macros (multi-step workflows)
- Context awareness (knows what app you're in)
- Proactive suggestions
- Custom wake words

### **v3.0 - Platform** (Q2 2025)
- Cross-platform (macOS, Linux)
- Plugin marketplace
- Team profiles
- Advanced automation

---

## 🤝 **Contributing**

Scribe is **open source and community-driven**. We welcome:
- 🐛 Bug reports
- 💡 Feature requests
- 🔌 Plugin development
- 📚 Documentation improvements
- 🧪 Testing and feedback

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### **Why Contribute?**
- Build features **you** want to use
- Learn voice AI, plugin architecture, Python packaging
- Join a community building the open alternative to corporate voice assistants
- Your contributions help everyone

---

## 📖 **Documentation**

- [User Guide](docs/USER_GUIDE.md) - Complete usage documentation
- [Plugin Development](docs/PLUGIN_DEVELOPMENT.md) - Build your own plugins
- [Analytics Guide](docs/ANALYTICS.md) - Understanding your metrics
- [Team Deployment](docs/DEPLOYMENT.md) - Set up for your team
- [Development Guide](docs/DEVELOPMENT.md) - Contributing to Scribe

---

## 💬 **Community**

- **GitHub Issues**: [Report bugs, request features](https://github.com/yourusername/scribe/issues)
- **Discussions**: [Ask questions, share plugins](https://github.com/yourusername/scribe/discussions)
- **Discord**: [Join the community](#) (coming soon)

---

## 📜 **License**

Scribe is licensed under the [Apache License 2.0](LICENSE).

**TL;DR**: Free to use, modify, distribute. No warranties. Attribution appreciated.

---

## 🙏 **Acknowledgments**

Scribe builds on the foundation of:
- [WhisperWriter](https://github.com/savbell/whisper-writer) by savbell - The original inspiration
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) - Fast, accurate transcription
- [OpenAI Whisper](https://github.com/openai/whisper) - Revolutionary speech recognition
- The open-source community - For making this possible

---

## 🚀 **Why Scribe Exists**

**Corporate voice assistants:**
- Lock you into their ecosystem
- Send your data to their servers
- Prioritize their business goals
- Cost money or show ads

**Scribe:**
- Works with any tool you use
- Keeps your data local
- Prioritizes YOUR productivity
- Free forever, no strings attached

**People deserve better than corporate software.** Scribe is the community's answer.

---

## 📈 **Project Status**

**Current Version**: v2.0.0-alpha
**Status**: Active development
**Stability**: Alpha (usable, but expect changes)
**Looking for**: Early adopters, contributors, feedback

---

## ❓ **FAQ**

**Q: Is this really free?**
A: Yes. Open source, MIT licensed, no hidden costs.

**Q: Does it work offline?**
A: Yes! Local models work completely offline. AI features require API keys.

**Q: Can I use my own API keys?**
A: Absolutely. Your keys, your control.

**Q: What about my privacy?**
A: All data local by default. You control what (if anything) gets shared.

**Q: Can I build commercial products with this?**
A: Yes! The license allows commercial use.

**Q: Why not just use Whisper directly?**
A: Scribe adds: learning, plugins, analytics, multi-device sync, UI, and community.

---

<div align="center">

**Built with ❤️ by the community, for the community**

[⭐ Star on GitHub](https://github.com/yourusername/scribe) • [📖 Read the Docs](docs/) • [🐛 Report Bug](https://github.com/yourusername/scribe/issues) • [💡 Request Feature](https://github.com/yourusername/scribe/issues)

</div>
