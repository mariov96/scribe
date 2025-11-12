# 🚀 Quick Start Guide

Get Scribe running in 5 minutes!

## Prerequisites

- **Windows 10/11** (Linux/Mac coming soon)
- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **4GB RAM minimum** (8GB recommended)
- **(Optional)** NVIDIA GPU with CUDA for 10x faster transcription

## Installation Steps

### 1. Download Scribe

```bash
# Clone the repository
git clone https://github.com/yourusername/scribe.git
cd scribe
```

Or [download ZIP](https://github.com/yourusername/scribe/archive/refs/heads/main.zip) and extract.

### 2. Run Setup Script

**Windows:**
```cmd
setup_dev.bat
```

**Linux/Mac:**
```bash
chmod +x setup_dev.sh
./setup_dev.sh
```

This will:
- Create virtual environment
- Install dependencies
- Create data directories

### 3. Activate Virtual Environment

**Windows:**
```cmd
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Run Scribe

```bash
python run_scribe.py
```

## First-Time Setup

On first run, Scribe will:

1. **Select Audio Device**
   - Choose your microphone from the list
   - Test recording to verify it works

2. **Configure Hotkey**
   - Default: `Ctrl+Alt`
   - Press keys when prompted to set custom hotkey

3. **Download Model**
   - Recommends `base` model (140MB, fast)
   - Downloads from HuggingFace automatically
   - Takes 1-2 minutes depending on connection

## Basic Usage

### Recording

1. **Press and hold** `Ctrl+Alt` (or your custom hotkey)
2. **Speak** while holding the keys
3. **Release** to transcribe
4. **Text appears** in the app you were using!

### Features

**System Tray:**
- Minimize to tray for background operation
- Right-click icon for quick access

**History:**
- All transcriptions saved automatically
- Search by text or application
- Export to text files

**Insights:**
- See productivity gains
- Track words saved
- View usage patterns

## Configuration

Edit `config/default.yaml`:

```yaml
# Whisper model: tiny, base, small, medium, large
whisper:
  model: base
  device: auto  # auto, cuda, cpu

# Hotkey configuration
hotkeys:
  toggle_recording: "ctrl+alt"

# Audio settings
audio:
  sample_rate: 16000
```

## Troubleshooting

### Model Download Fails
**Solution:** Check internet connection and HuggingFace status

### Hotkey Doesn't Work
**Solution:** 
- Try running as administrator
- Check if another app uses the same hotkey
- Change hotkey in settings

### Poor Transcription Quality
**Solution:**
- Check microphone levels
- Reduce background noise
- Try a better model (small or medium)
- Enable GPU if available

### App Crashes
**Solution:**
- Check `data/logs/scribe.log`
- Report issue with logs attached
- Clear cache: Delete `models/` folder

## GPU Acceleration (Optional)

**10x faster transcription!**

### Windows (NVIDIA)

1. Install CUDA Toolkit 11.8+
2. Install cuDNN
3. Install PyTorch with CUDA:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

4. Restart Scribe - GPU will be detected automatically

### Verify GPU

Check logs for:
```
🚀 Using device: cuda with compute type: float16
```

## Next Steps

- **Explore Plugins:** Check Settings → Plugins
- **Customize Hotkeys:** Settings → Hotkeys
- **Review Insights:** See your productivity gains
- **Create Plugin:** See [Plugin Development](plugin-development.md)

## Getting Help

- 📖 [Full Documentation](../README.md)
- 💬 [Discussions](https://github.com/yourusername/scribe/discussions)
- 🐛 [Report Issues](https://github.com/yourusername/scribe/issues)

## Tips

💡 **Pro Tip 1:** Use shorter holds for better accuracy (5-10 seconds)

💡 **Pro Tip 2:** Speak naturally - the model handles pauses and corrections

💡 **Pro Tip 3:** Check History tab for recent transcriptions if text doesn't paste

💡 **Pro Tip 4:** Enable GPU for real-time transcription (<1 second)

---

**Ready to go! Press `Ctrl+Alt` and start dictating!** 🎤
