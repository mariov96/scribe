# Plugin Architecture Analysis - Three Approaches

## Context
We need a plugin system that supports:
- Voice command registration
- Dynamic loading/unloading
- OS automation (windows, media, apps)
- Easy contribution path
- Type safety and validation
- Performance (command execution <100ms)

---

## 🏗️ Approach 1: Class-Based Inheritance (Chosen)

### Design
```python
class BasePlugin(ABC):
    """Abstract base class for all plugins"""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def commands(self) -> List[CommandDefinition]:
        pass

    @abstractmethod
    def initialize(self, config: Dict) -> bool:
        pass

    def shutdown(self):
        pass
```

### Implementation
- Plugins inherit from `BasePlugin`
- Command registry pattern
- Dependency injection via `initialize(config)`
- Lifecycle management (init/shutdown)

### Pros ✅
- **Type safety**: ABC enforces contract at import time
- **IDE support**: Autocomplete, type hints work perfectly
- **Clear structure**: Inheritance makes relationship obvious
- **Easy validation**: Can check `isinstance(plugin, BasePlugin)`
- **Familiar pattern**: Most Python devs know OOP
- **Performance**: Direct method calls, no reflection overhead

### Cons ❌
- **Rigid**: Hard to compose multiple behaviors
- **Inheritance coupling**: Plugins coupled to base class
- **Testing**: Must mock entire class hierarchy

### Performance Estimate
- Command lookup: O(1) dictionary access
- Execution: Direct method call
- **Expected: 1-5ms overhead** ✅ Under 100ms target

### Use Cases Best For
- Clean, structured plugins
- Type-safe development
- IDE-driven development
- New contributors (familiar pattern)

---

## 🔌 Approach 2: Decorator-Based Registration

### Design
```python
plugin_registry = PluginRegistry()

@plugin_registry.register("window_manager", version="1.0.0")
class WindowManager:
    @command(patterns=["switch to {app}"])
    def switch_app(self, app: str):
        pass
```

### Implementation
- Decorators register plugins and commands
- No inheritance required
- Registry manages discovery
- Reflection for command extraction

### Pros ✅
- **Flexible**: No inheritance constraints
- **Composable**: Mix multiple decorators
- **Lightweight**: Less boilerplate code
- **Python-native**: Decorator pattern is pythonic
- **Easy testing**: Test plain methods

### Cons ❌
- **Magic behavior**: Decorators hide registration
- **Runtime errors**: Issues only caught at runtime
- **IDE confusion**: Autocomplete doesn't understand decorators
- **Debugging harder**: Stack traces through decorator layers
- **Performance**: Reflection has overhead

### Performance Estimate
- Command lookup: O(n) scan or dict caching needed
- Execution: Decorator unwrapping overhead
- **Expected: 5-15ms overhead** ⚠️ Approaching limit

### Use Cases Best For
- Rapid prototyping
- Functional programming style
- Dynamic plugin loading
- Experienced Python developers

---

## 🧩 Approach 3: Protocol-Based (Structural Subtyping)

### Design
```python
class PluginProtocol(Protocol):
    """Structural type for plugins"""
    name: str
    version: str

    def commands(self) -> List[CommandDef]:
        ...

    def initialize(self, config: Dict) -> bool:
        ...
```

### Implementation
- Duck typing with type hints
- No inheritance required
- `mypy` validates structure
- Runtime validation via `@runtime_checkable`

### Pros ✅
- **Flexible**: No inheritance needed
- **Type-safe**: `mypy` catches issues
- **Decoupled**: Plugins don't import base
- **Modern**: Python 3.8+ typing best practice
- **Testing**: Can use any conforming object

### Cons ❌
- **Less discoverable**: No explicit inheritance
- **Runtime validation needed**: Structure not enforced at import
- **Newer concept**: Less familiar to many devs
- **Tooling**: Some IDEs don't fully support Protocols

### Performance Estimate
- Command lookup: Same as Approach 1 (dict)
- Execution: No overhead vs direct call
- **Expected: 1-5ms overhead** ✅ Under 100ms target

### Use Cases Best For
- Large plugin ecosystem
- Third-party plugin authors
- Type-checked codebases
- Modern Python projects

---

## 📊 Comparison Matrix

| Criterion | Approach 1 (Inheritance) | Approach 2 (Decorator) | Approach 3 (Protocol) |
|-----------|-------------------------|------------------------|----------------------|
| **Type Safety** | ✅ Strong (ABC) | ❌ Weak (runtime) | ✅ Strong (mypy) |
| **Performance** | ✅ Excellent (1-5ms) | ⚠️ Good (5-15ms) | ✅ Excellent (1-5ms) |
| **IDE Support** | ✅ Excellent | ❌ Poor | ✅ Good |
| **Learning Curve** | ✅ Easy (OOP) | ⚠️ Medium | ❌ Hard (new concept) |
| **Flexibility** | ❌ Rigid | ✅ Very flexible | ✅ Flexible |
| **Debugging** | ✅ Clear stack traces | ❌ Decorator noise | ✅ Clear |
| **Testing** | ⚠️ Mock hierarchy | ✅ Test functions | ✅ Mock interface |
| **Community Familiarity** | ✅ Very familiar | ✅ Familiar | ❌ Less familiar |

---

## 🎯 Recommendation: Approach 1 (Class-Based)

### Why Class-Based Wins for Scribe

**1. Performance Critical**
- Voice commands must execute in <100ms
- Direct method calls are fastest
- No reflection or decorator unwrapping

**2. New Contributor Friendly**
- OOP is familiar to 90%+ of Python devs
- Clear structure: "inherit BasePlugin, implement methods"
- IDE autocomplete works perfectly
- Type hints guide development

**3. Type Safety Matters**
- ABC catches missing methods at import time
- Prevents runtime errors in production
- Users rely on voice commands working instantly

**4. Clear Error Messages**
```python
# Approach 1: Clear error at import
TypeError: Can't instantiate abstract class BadPlugin
with abstract methods commands

# Approach 2: Runtime error when command used
AttributeError: 'BadPlugin' has no attribute 'switch_app'
```

**5. Maintainability**
- Explicit is better than implicit (Zen of Python)
- Easy to understand codebase structure
- Future maintainers understand immediately

### Implementation Strategy

**Phase 1: Core (Now)**
```python
src/scribe/plugins/
├── __init__.py
├── base.py              # BasePlugin ABC
└── registry.py          # PluginRegistry
```

**Phase 2: Day 1 Plugins (This session)**
```python
src/scribe/plugins/
├── window_manager/
│   ├── __init__.py
│   └── plugin.py        # Inherits BasePlugin
└── media_control/
    ├── __init__.py
    └── plugin.py        # Inherits BasePlugin
```

**Phase 3: Future Enhancement**
- Could add decorator sugar LATER: `@register_plugin`
- Could support Protocol for third-party authors
- Start simple, evolve based on real usage

---

## 🔮 Future Considerations

### Hybrid Approach Possibility
```python
# Power users can use inheritance (type-safe)
class WindowManager(BasePlugin):
    pass

# Quick scripts can use decorator (rapid)
@plugin()
def quick_command():
    pass

# Both registered in same registry
```

### Versioning Strategy
```python
class BasePlugin(ABC):
    VERSION_REQUIRED = "2.0"  # Plugin API version

    @property
    def api_version(self) -> str:
        return "2.0"  # Plugin declares compatibility
```

### Performance Monitoring
```python
class BasePlugin(ABC):
    def execute_command(self, cmd):
        start = time.perf_counter()
        result = cmd.handler(*args)
        elapsed = time.perf_counter() - start

        if elapsed > 0.1:  # Warn if >100ms
            logger.warning(f"{cmd.name} took {elapsed:.2f}s")

        return result
```

---

## 📝 Decision Log

**Date:** 2024-11-07
**Decision:** Approach 1 (Class-Based Inheritance)
**Rationale:**
- Performance critical (voice UX)
- New contributor friendly (community growth)
- Type safety (production reliability)
- IDE support (developer experience)
- Clear error messages (debugging)

**Trade-offs Accepted:**
- Less flexible than decorators (worth it for safety)
- Inheritance coupling (mitigated by clear interface)
- Not the "newest" pattern (but most battle-tested)

**Review Trigger:**
- When plugin count > 50 (complexity may favor Protocol)
- When performance <100ms becomes issue (would need profiling)
- When contributor feedback suggests different approach

---

*This analysis informs the plugin architecture for Scribe v2.0 and beyond. Start simple, measure real usage, evolve based on data.*
