# GPU Acceleration - Quick Reference

## ✅ Installation Complete

**GPU**: NVIDIA Quadro T1000 (4GB)  
**PyTorch**: 2.5.1 with CUDA 12.1  
**Expected**: **5-10x faster transcription**

---

## Quick Checks

### Is GPU Working?

**Method 1: Python**
```cmd
python -c "import torch; print(torch.cuda.is_available())"
```
Expected: `True`

**Method 2: Verification Script**
```cmd
verify_gpu.bat
```
Expected: `SUCCESS: GPU acceleration is ready!`

**Method 3: Scribe Logs**
```
%USERPROFILE%\.scribe\logs\scribe_YYYYMMDD.log
```
Look for: `🎮 CUDA GPU detected: Quadro T1000`

**Method 4: Settings UI**
```
Settings → Transcription → Status Chip
```
Shows: `● Active: model · cuda · float16`

---

## Performance

| Audio | CPU Time | GPU Time | Speedup |
|-------|----------|----------|---------|
| 10s   | ~6s      | ~1s      | **6x** ⚡ |
| 30s   | ~20s     | ~4s      | **5x** ⚡ |
| 60s   | ~40s     | ~8s      | **5x** ⚡ |

---

## Troubleshooting

### GPU Not Used?
1. Restart Scribe
2. Check: `python -c "import torch; print(torch.cuda.is_available())"`
3. If False, reinstall: `pip install torch --index-url https://download.pytorch.org/whl/cu121 --force-reinstall`

### Out of Memory?
1. Switch to smaller model (`distil-medium.en`)
2. Close other GPU apps
3. Keep recordings <2 minutes

### Still Slow?
1. First run includes model loading (~5s)
2. Check model not downloading (⬇ in Settings)
3. Update GPU driver: nvidia.com/drivers

---

## Documentation

📄 **Quick Start**: `GPU_QUICKSTART.md`  
📄 **Full Guide**: `GPU_SETUP.md`  
📄 **Install Summary**: `INSTALL_SUMMARY.md`  
🧪 **Verification**: `verify_gpu.bat`

---

## Support

**Verify Installation**:
```cmd
cd C:\code\scribe
verify_gpu.bat
```

**Check Logs**:
```cmd
%USERPROFILE%\.scribe\logs\
```

**Reinstall if Needed**:
```cmd
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --force-reinstall
```

---

**🚀 Launch Scribe and enjoy 5-10x faster transcription!**
