# Scribe Development Tools

Utility scripts for Scribe development and release management.

## update_build_timestamp.py

Updates the `BUILD_TIMESTAMP` in `src/scribe/__version__.py` to the current time.

### Usage

```bash
python tools/update_build_timestamp.py
```

### When to Use

Run this script:
- **Before creating a release** - Ensures the build timestamp reflects the release time
- **After significant changes** - Marks when major features were added
- **In CI/CD pipeline** - Automatically timestamp builds
- **Before testing upgrades** - Create distinguishable builds for testing auto-upgrade

### Example Output

```
✅ Build timestamp updated!
   Version: 2.0.1
   Build time: 2025-11-13 12:51:40
   Timestamp: 1763067100
   
   File: /path/to/src/scribe/__version__.py
```

### How Build Timestamps Work

1. **Version + Build Time**: Scribe uses both semantic versioning AND build timestamps
2. **Auto-Upgrade**: When starting a newer build, Scribe automatically closes older instances
3. **Downgrade Protection**: Prevents accidentally starting older builds
4. **Clear Messaging**: Users see exactly which version/build is running and which they're trying to start

### Example Scenarios

#### Scenario 1: Same Version, Newer Build
```
Running: v2.0.1 (built 2025-11-13 10:00:00)
Start:   v2.0.1 (built 2025-11-13 12:51:40)
Result:  ✅ Auto-closes old build, starts new one
```

#### Scenario 2: Same Version, Older Build
```
Running: v2.0.1 (built 2025-11-13 12:51:40)
Start:   v2.0.1 (built 2025-11-13 10:00:00)
Result:  ⚠️ Warns user, requires manual close
```

#### Scenario 3: Newer Version
```
Running: v2.0.0 (any build time)
Start:   v2.0.1 (any build time)
Result:  ✅ Auto-closes old version, starts new one
```

#### Scenario 4: Older Version
```
Running: v2.0.1 (any build time)
Start:   v2.0.0 (any build time)
Result:  ⚠️ Warns user, requires manual close
```

## Integration with Development Workflow

### Manual Testing

```bash
# Make some changes to your code
git add .
git commit -m "feat: Add new feature"

# Update build timestamp
python tools/update_build_timestamp.py

# Test the upgrade
python run_scribe.py
# Should auto-close any older running instance
```

### Pre-Commit Hook (Optional)

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python tools/update_build_timestamp.py
git add src/scribe/__version__.py
```

### CI/CD Integration

In your CI/CD pipeline:

```yaml
- name: Update build timestamp
  run: python tools/update_build_timestamp.py
  
- name: Commit updated timestamp
  run: |
    git add src/scribe/__version__.py
    git commit -m "chore: Update build timestamp"
```
