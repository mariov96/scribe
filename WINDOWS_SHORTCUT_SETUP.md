# Windows Shortcut Setup Instructions

## Quick Start

**Option 1: Using the VBS Launcher (Recommended)**
1. Double-click `Start Scribe.vbs` to test it works
2. Right-click `Start Scribe.vbs` → **Create shortcut**
3. Right-click the shortcut → **Properties**
4. Click **Change Icon** → **Browse** → Select `assets\scribe-icon.ico`
5. Click **OK** to save
6. Move the shortcut to your Desktop or Pin to Taskbar

**Option 2: Using the Batch File**
1. Double-click `Start Scribe.bat` to test it works
2. Right-click `Start Scribe.bat` → **Create shortcut**
3. Right-click the shortcut → **Properties**
4. Click **Change Icon** → **Browse** → Select `assets\scribe-icon.ico`
5. Click **OK** to save
6. Move the shortcut to your Desktop or Pin to Taskbar

## Creating Desktop Shortcut Manually

If you want to create a shortcut from scratch:

1. **Right-click** on your Desktop → **New** → **Shortcut**

2. **Target (VBS method):**
   ```
   "C:\Windows\System32\wscript.exe" "C:\code\scribe\Start Scribe.vbs"
   ```

3. **Target (Direct Python method):**
   ```
   "C:\Python313\python.exe" "C:\code\scribe\run_scribe.py"
   ```

4. **Name it:** `Scribe`

5. **Change Icon:**
   - Right-click shortcut → Properties
   - Click "Change Icon"
   - Browse to: `C:\code\scribe\assets\scribe-icon.ico`
   - Click OK

6. **Pin to Taskbar (Optional):**
   - Right-click the shortcut → "Pin to Taskbar"

## Features

✅ **Icon**: Uses the official Scribe microphone icon  
✅ **Focus**: Window automatically comes to front on launch  
✅ **No Console**: VBS launcher hides the console window  
✅ **Python Detection**: Automatically finds your Python installation  

## Troubleshooting

**"Python not found" error:**
- Open `Start Scribe.vbs` in a text editor
- Update the `PythonPath` line to your Python installation path
- Common paths: `C:\Python311\python.exe`, `C:\Python312\python.exe`, etc.

**Icon doesn't show:**
- Make sure you're pointing to the `.ico` file, not `.png` or `.svg`
- Full path should be: `C:\code\scribe\assets\scribe-icon.ico`

**Window doesn't take focus:**
- This is normal Windows behavior sometimes
- Click the taskbar button to bring it to front
- The VBS launcher tries to maximize focus

## Advanced: Pin to Start Menu

1. Press `Win` key
2. Type "Scribe" to find your shortcut
3. Right-click → **Pin to Start**

Enjoy! 🎤
