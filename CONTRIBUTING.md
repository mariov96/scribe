# Contributing to Scribe

First off, thank you for considering contributing to Scribe! It's people like you that make Scribe such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

**Before Submitting A Bug Report:**
- Check the [existing issues](https://github.com/yourusername/scribe/issues)
- Check if the bug has already been reported
- Collect information:
  - Scribe version (check bottom of settings page or logs)
  - Operating system and version
  - Python version (`python --version`)
  - Steps to reproduce
  - Expected vs actual behavior
  - Screenshots if applicable
  - Log files from `data/logs/scribe.log`

**How to Submit:**
1. Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
2. Provide all requested information
3. Use a clear, descriptive title
4. Include code samples or test cases if possible

### Suggesting Features

**Before Submitting:**
- Check if the feature already exists
- Check the [roadmap](ROADMAP.md) to see if it's planned
- Consider if it should be a **plugin** instead of core functionality

**How to Submit:**
1. Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
2. Explain the use case (why is this needed?)
3. Describe your proposed solution
4. Provide examples or mockups if applicable

### Pull Requests

**Development Process:**

1. **Fork & Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/scribe.git
   cd scribe
   ```

2. **Set Up Development Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. **Create a Branch**
   ```bash
   git checkout -b feature/my-amazing-feature
   # or
   git checkout -b fix/issue-123
   ```

4. **Make Changes**
   - Follow our [coding standards](#coding-standards)
   - Write tests for new functionality
   - Update documentation as needed
   - Keep commits atomic and well-described

5. **Test Your Changes**
   ```bash
   # Run tests
   pytest

   # Run the app
   python run_scribe.py
   ```

6. **Commit**
   ```bash
   git add .
   git commit -m "feat: Add amazing feature

   - Implement feature X
   - Add tests for feature X
   - Update documentation

   Closes #123"
   ```

   **Commit Message Format:**
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes (formatting, etc.)
   - `refactor:` Code refactoring
   - `test:` Adding or updating tests
   - `chore:` Maintenance tasks

7. **Push & Create PR**
   ```bash
   git push origin feature/my-amazing-feature
   ```
   Then open a PR on GitHub using our [template](.github/pull_request_template.md)

**PR Guidelines:**
- Reference related issues
- Provide clear description of changes
- Include screenshots/GIFs for UI changes
- Ensure all tests pass
- Keep PRs focused (one feature/fix per PR)
- Be responsive to feedback

## Coding Standards

### Python Style

We follow [PEP 8](https://pep8.org/):

```python
# Good
def transcribe_audio(self, audio_data: bytes) -> str:
    """
    Transcribe audio data to text.
    
    Args:
        audio_data: Raw audio bytes
        
    Returns:
        Transcribed text
    """
    result = self.engine.transcribe(audio_data)
    return result.text

# Bad
def transcribe(d):
    return self.e.transcribe(d).text
```

**Key Points:**
- Use type hints for function signatures
- Write docstrings for all public methods/classes
- Descriptive variable names (no single letters except loop counters)
- Max line length: 100 characters
- Use logging instead of print statements

### Architecture Principles

1. **Plugin-First**: New features should be plugins when possible
2. **Separation of Concerns**: Keep core, plugins, UI, and analytics separate
3. **Testability**: Write code that can be easily tested
4. **Configuration**: Make behavior configurable via YAML
5. **Logging**: Use `logger` instead of `print()` statements

### Testing

- Write tests for new functionality
- Use `pytest` fixtures for setup/teardown
- Mock external dependencies (audio devices, models, etc.)

```python
# Good test example
def test_pattern_matching():
    """Test pattern matching with parameters"""
    app = ScribeApp()
    matched, params = app._pattern_matches(
        "switch to chrome",
        "switch to {app}"
    )
    assert matched is True
    assert params == {"app": "chrome"}
```

### Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Create guides in `docs/` for complex features

## Session Continuity Framework (SCF)

Scribe uses SCF for development continuity. When contributing:

1. **Before Starting**: Review `BUILDSTATE.md` for current context
2. **During Development**: Document significant decisions
3. **After Completion**: Update changelog in `BUILDSTATE.md`

**Example Entry:**
```markdown
### 2025-11-12 - Pattern Matching Enhancement
**Status:** Complete
**Changes:**
- Implemented regex-based parameter extraction
- Added support for multi-word placeholders
**Files Modified:**
- src/scribe/app.py (_pattern_matches method)
- tests/test_pattern_matching.py (new file)
```

See [`docs/scf-guide.md`](docs/scf-guide.md) for full details.

## Community

### Getting Help

- 💬 [GitHub Discussions](https://github.com/yourusername/scribe/discussions) - Q&A, ideas, show & tell
- 🐛 [Issue Tracker](https://github.com/yourusername/scribe/issues) - Bug reports
- 📖 [Documentation](docs/) - Guides and API reference

### Recognition

Contributors who make significant improvements will be:
- Listed in [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Mentioned in release notes
- Given credit in the README

## Development Tips

### Recommended IDE Setup

**VS Code Extensions:**
- Python (Microsoft)
- Pylance
- GitLens

### Common Issues

**Issue:** Tests fail with "No module named 'scribe'"  
**Solution:** Install package in editable mode:
```bash
pip install -e .
```

**Issue:** Hotkey not working  
**Solution:** Run as administrator (Windows) or check permissions (Linux)

**Issue:** Model download fails  
**Solution:** Check internet connection and HuggingFace availability

## Questions?

Don't hesitate to ask! Open a [discussion](https://github.com/yourusername/scribe/discussions) or check existing docs.

---

**Thank you for contributing to Scribe! 🎉**
