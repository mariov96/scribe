#!/bin/bash
# Cleanup script for Scribe v2.0.0 release

echo "🧹 Cleaning up for release..."

# Remove all Python cache files
echo "Removing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null

# Remove backup files
echo "Removing backup files..."
rm -f buildstate.json.backup.* 2>/dev/null

# Remove development session files
echo "Removing session documentation..."
rm -f SESSION*.md 2>/dev/null
rm -f UAT_*.md 2>/dev/null
rm -f PHASE*.md 2>/dev/null
rm -f *_COMPLETE.md 2>/dev/null
rm -f BUILDSTATE.md 2>/dev/null
rm -f buildstate.json 2>/dev/null

# Remove POC and migration scripts
echo "Removing POC scripts..."
rm -f poc_*.py 2>/dev/null
rm -f POC_*.md 2>/dev/null
rm -f migrate_*.py 2>/dev/null
rm -f MIGRATION*.md 2>/dev/null

# Remove test scripts from root (keep tests/ directory)
echo "Removing root test scripts..."
rm -f test_*.py 2>/dev/null
rm -f test_*.bat 2>/dev/null
rm -f test_*.ps1 2>/dev/null

# Remove development utilities
echo "Removing development utilities..."
rm -f complete_*.py 2>/dev/null
rm -f complete_*.json 2>/dev/null
rm -f complete_*.log 2>/dev/null
rm -f diagnose.py 2>/dev/null
rm -f ai_editor.py 2>/dev/null
rm -f auto_log_analyzer.py 2>/dev/null
rm -f whisper_flow*.py 2>/dev/null

# Remove alternative entry points (keep run_scribe.py)
echo "Removing alternative entry points..."
rm -f start_scribe.py 2>/dev/null
rm -f scribe_simple.py 2>/dev/null
rm -f show_wizard.py 2>/dev/null

# Remove setup scripts that are superseded by setup_dev.*
echo "Removing old setup scripts..."
rm -f setup_audio_test.bat 2>/dev/null
rm -f setup_windows_venv.bat 2>/dev/null
rm -f setup_windows_venv.ps1 2>/dev/null
rm -f requirements_audio_test.txt 2>/dev/null

# Remove internal documentation
echo "Removing internal documentation..."
rm -f ACTION_PLAN.md 2>/dev/null
rm -f AGENTS.md 2>/dev/null
rm -f CLAUDE.md 2>/dev/null
rm -f QUICK_START.md 2>/dev/null
rm -f RUN_AS_ADMIN.md 2>/dev/null
rm -f EXTENSION_IDEAS.md 2>/dev/null
rm -f ww_todo.md 2>/dev/null
rm -f *_GUIDE.md 2>/dev/null
rm -f *_JOBS.md 2>/dev/null
rm -f *_TEST_GUIDE.md 2>/dev/null
rm -f *_VALIDATION_COMPLETE.md 2>/dev/null
rm -f *_OPTIMIZATIONS.md 2>/dev/null

# Remove old source directories
echo "Removing legacy source code..."
rm -rf src/legacy 2>/dev/null
rm -rf src/whisperwriter 2>/dev/null

# Remove old config files at root
echo "Removing old config files..."
rm -f src/config.yaml 2>/dev/null
rm -f src/config_schema.yaml 2>/dev/null

# Remove old source files that are no longer used
echo "Removing old source files..."
rm -f src/input_simulation.py 2>/dev/null
rm -f src/key_listener.py 2>/dev/null
rm -f src/result_thread.py 2>/dev/null
rm -f src/transcription.py 2>/dev/null
rm -f src/utils.py 2>/dev/null

# Remove development directories
echo "Removing development directories..."
rm -rf .scf 2>/dev/null
rm -rf session-continuity-framework 2>/dev/null
rm -rf venv_fluent 2>/dev/null
rm -rf venv_windows 2>/dev/null

# Remove data/logs/sessions (will be created on first run)
echo "Removing user data (will be recreated on first run)..."
rm -rf data/logs 2>/dev/null
rm -rf data/sessions 2>/dev/null
rm -rf data/metrics 2>/dev/null
rm -rf data/analytics 2>/dev/null
rm -rf data/audio 2>/dev/null

# Keep only essential directories in data/
mkdir -p data 2>/dev/null

# Remove test recordings
echo "Removing test files..."
rm -f test_recording.wav 2>/dev/null

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Files kept:"
echo "  - Source code (src/scribe/)"
echo "  - Tests (tests/)"
echo "  - Documentation (docs/, README.md, etc.)"
echo "  - GitHub infrastructure (.github/)"
echo "  - Config (config/)"
echo "  - Assets (assets/)"
echo "  - Setup scripts (setup_dev.sh, setup_dev.bat)"
echo "  - Entry point (run_scribe.py)"
echo ""
echo "Ready for git add and commit!"
