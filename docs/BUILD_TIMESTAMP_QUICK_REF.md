# Build Timestamp Quick Reference

## For Users

### What You'll See

**✅ Starting a Newer Version/Build**
```
🔄 Upgrading from v2.0.0 → v2.0.1
   Closing older instance (PID=12345)...
✅ Upgrade successful! Starting new version...
```
*The old version closes automatically. No action needed!*

**⚠️ Starting an Older Version/Build**
```
⚠️  Cannot start older version!
   Currently running: v2.0.1 (built 2025-11-13 12:51:40)
   Attempting to start: v2.0.0

   Please close the running instance first if you need to downgrade.
```
*You must manually close the newer version to use an older one.*

**⚠️ Same Version Already Running**
```
⚠️  Scribe v2.0.1 is already running
   PID: 12345
   Build: 2025-11-13 12:51:40
```
*Close the existing instance first, or use it!*

---

## For Developers

### Update Build Timestamp Before Release

```bash
python tools/update_build_timestamp.py
```

Output:
```
✅ Build timestamp updated!
   Version: 2.0.1
   Build time: 2025-11-13 12:51:40
   Timestamp: 1763067100
```

### Test Version Checking

```bash
python tools/test_version_checking.py
```

Output:
```
✅ PASS - Newer version (any build)
✅ PASS - Older version (any build)
✅ PASS - Same version, newer build
✅ PASS - Same version, older build
✅ PASS - Same version and build

5/5 tests passed
🎉 All tests passed!
```

### Test Real Upgrade Flow

```bash
# Terminal 1: Start current version
python run_scribe.py

# Terminal 2: Update timestamp and start new version
python tools/update_build_timestamp.py
python run_scribe.py

# Terminal 1 should auto-close, Terminal 2 should start
```

---

## Key Files

| File | Purpose |
|------|---------|
| `src/scribe/__version__.py` | Version and build timestamp |
| `src/scribe/core/single_instance.py` | Single instance manager |
| `tools/update_build_timestamp.py` | Update timestamp tool |
| `tools/test_version_checking.py` | Test suite |
| `docs/BUILD_TIMESTAMP.md` | Full documentation |

---

## Decision Logic

```
Is another instance running?
  ├─ No → Start normally ✅
  └─ Yes → Compare versions
        ├─ New version > Old version → Auto-close old, start new ✅
        ├─ New version < Old version → Show warning, exit ⚠️
        └─ Same version → Compare build timestamps
              ├─ New build > Old build → Auto-close old, start new ✅
              ├─ New build < Old build → Show warning, exit ⚠️
              └─ Same build → Show "already running", exit ⚠️
```

---

## Troubleshooting

### Lock File Stuck?

```bash
# Windows
del %TEMP%\.scribe.lock

# Linux/Mac
rm /tmp/.scribe.lock
```

### Check for Running Instances

```bash
# Windows
tasklist | findstr python

# Linux/Mac
ps aux | grep scribe
```

---

## More Info

- Full documentation: `docs/BUILD_TIMESTAMP.md`
- Tool documentation: `tools/README.md`
- Changelog: `CHANGELOG.md`
