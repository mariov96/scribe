# Build Timestamp & Auto-Upgrade System

Scribe includes an intelligent version checking system that prevents conflicts between multiple instances and enables seamless auto-upgrades.

## How It Works

### Single Instance Lock

Scribe uses a lock file (`.scribe.lock`) that stores:
- **PID** - Process ID of the running instance
- **Version** - Semantic version (e.g., 2.0.1)
- **Build Timestamp** - Unix timestamp of when the build was created

When you start Scribe, it checks this lock file and makes smart decisions about what to do.

## Upgrade Scenarios

### ✅ Auto-Upgrade: Newer Version

When you start a **newer version**, Scribe automatically closes the older instance:

```
Currently Running: v2.0.0 (any build time)
You Start:         v2.0.1 (any build time)

Result:
  🔄 Upgrading from v2.0.0 → v2.0.1
     Closing older instance (PID=12345)...
  ✅ Upgrade successful! Starting new version...
```

The old instance is terminated gracefully (3-second timeout, then force kill if needed).

### ✅ Auto-Upgrade: Newer Build

When you start a **newer build** of the same version, Scribe auto-upgrades:

```
Currently Running: v2.0.1 (built 2025-11-13 10:00:00)
You Start:         v2.0.1 (built 2025-11-13 12:51:40)

Result:
  🔄 Upgrading to newer build of v2.0.1
     Old build: 2025-11-13 10:00:00
     New build: 2025-11-13 12:51:40
     Closing older instance (PID=12345)...
  ✅ Upgrade successful! Starting new build...
```

### ⚠️ Downgrade Protection: Older Version

When you try to start an **older version**, Scribe prevents it:

```
Currently Running: v2.0.1 (built 2025-11-13 12:51:40)
You Start:         v2.0.0 (any build time)

Result:
  ⚠️  Cannot start older version!
     Currently running: v2.0.1 (built 2025-11-13 12:51:40)
     Attempting to start: v2.0.0
     
     Please close the running instance first if you need to downgrade.
  
  ❌ Another instance of Scribe is already running.
     Only one instance can run at a time.
  
  Press Enter to exit...
```

You must **manually close** the newer version before starting an older one.

### ⚠️ Downgrade Protection: Older Build

When you try to start an **older build** of the same version:

```
Currently Running: v2.0.1 (built 2025-11-13 12:51:40)
You Start:         v2.0.1 (built 2025-11-13 10:00:00)

Result:
  ⚠️  Cannot start older build!
     Currently running: v2.0.1 (built 2025-11-13 12:51:40)
     Attempting to start: v2.0.1 (built 2025-11-13 10:00:00)
     
     Please close the running instance first if you need to run this older build.
  
  ❌ Another instance of Scribe is already running.
     Only one instance can run at a time.
  
  Press Enter to exit...
```

### ⚠️ Same Version/Build Already Running

When you try to start the **exact same build** that's already running:

```
⚠️  Scribe v2.0.1 is already running
   PID: 12345
   Build: 2025-11-13 12:51:40

❌ Another instance of Scribe is already running.
   Only one instance can run at a time.

Press Enter to exit...
```

## For Developers

### Updating Build Timestamp

Before creating a release or after significant changes, update the build timestamp:

```bash
python tools/update_build_timestamp.py
```

This updates `src/scribe/__version__.py` with the current timestamp.

### Testing Upgrades

1. **Start first instance:**
   ```bash
   python run_scribe.py
   ```

2. **Update build timestamp:**
   ```bash
   python tools/update_build_timestamp.py
   ```

3. **Start second instance:**
   ```bash
   python run_scribe.py
   ```
   
   The first instance should auto-close and the new one should start.

### Version Comparison Logic

The system uses a hierarchical comparison:

1. **Version Number** (highest priority)
   - 2.0.1 > 2.0.0 > 1.9.9
   - Uses semantic versioning comparison

2. **Build Timestamp** (if versions are equal)
   - Compares Unix timestamps
   - Newer timestamp wins

3. **Exact Match** (if both are equal)
   - Shows "already running" message
   - No action taken

## Benefits

- **Seamless Updates**: No need to manually close old instances when upgrading
- **Safety**: Prevents accidental downgrades that could cause data issues
- **Transparency**: Clear messages about what's happening and why
- **Developer-Friendly**: Easy to test upgrades during development
- **CI/CD Ready**: Build timestamps can be automated in deployment pipelines

## Technical Details

### Lock File Location

- **Windows**: `%TEMP%\.scribe.lock`
- **Linux/Mac**: `/tmp/.scribe.lock`

### Lock File Format

```
PID|VERSION|BUILD_TIMESTAMP
```

Example:
```
12345|2.0.1|1763067100
```

### Process Detection

The system verifies that the PID in the lock file is:
1. Actually running
2. A Python process
3. Running Scribe (checks command line and working directory)

This prevents false positives from reused PIDs or other applications.

### Graceful Termination

When auto-upgrading:
1. Sends `SIGTERM` to old process
2. Waits 3 seconds for graceful shutdown
3. If still running, sends `SIGKILL`
4. Waits 2 seconds for forced termination
5. Acquires lock and starts new instance

## Troubleshooting

### Lock File Issues

If Scribe won't start and you believe no instance is running:

1. Check for running processes:
   ```bash
   # Windows
   tasklist | findstr python
   
   # Linux/Mac
   ps aux | grep scribe
   ```

2. Manually remove stale lock file:
   ```bash
   # Windows
   del %TEMP%\.scribe.lock
   
   # Linux/Mac
   rm /tmp/.scribe.lock
   ```

### Development Testing

To test different scenarios without waiting:

```bash
python tools/test_version_checking.py
```

This runs automated tests of all upgrade/downgrade scenarios.
