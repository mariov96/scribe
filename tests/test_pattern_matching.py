"""
Unit tests for pattern matching with variable extraction
"""
import pytest
import re
from typing import Dict, Tuple


def pattern_matches(text: str, pattern: str) -> Tuple[bool, Dict[str, str]]:
    """Pattern matching function (copied from app.py for testing)"""
    pattern = pattern.strip().lower()
    text = text.strip().lower()
    
    if not pattern:
        return False, {}

    # Build regex with named capture groups for placeholders
    tokens = []
    placeholder_names = []
    
    for i, part in enumerate(pattern.split()):
        if part.startswith("{") and part.endswith("}"):
            # Extract placeholder name
            name = part[1:-1]
            placeholder_names.append(name)
            
            # Check if this is the last token - if so, match everything remaining
            is_last = (i == len(pattern.split()) - 1)
            
            if is_last:
                # Last placeholder: greedy match to end of string
                tokens.append(rf"(?P<{name}>.+)")
            else:
                # Middle placeholder: non-greedy match for one or more words
                tokens.append(rf"(?P<{name}>\S+)")
        else:
            # Literal text - escape special regex characters
            tokens.append(re.escape(part))
    
    # Join with flexible whitespace matching
    regex = r"\b" + r"\s+".join(tokens) + r"\b"
    
    # Try to match
    match = re.search(regex, text)
    
    if match:
        # Extract all named groups (parameters)
        params = match.groupdict()
        # Clean up parameters - strip whitespace
        params = {k: v.strip() for k, v in params.items()}
        return True, params
    else:
        return False, {}


class TestPatternMatching:
    """Test suite for pattern matching and variable extraction"""
    
    def test_simple_match_no_params(self):
        """Test simple pattern with no parameters"""
        matched, params = pattern_matches("minimize", "minimize")
        assert matched is True
        assert params == {}
    
    def test_simple_match_two_words(self):
        """Test pattern with multiple words, no parameters"""
        matched, params = pattern_matches("list windows", "list windows")
        assert matched is True
        assert params == {}
    
    def test_no_match_different_command(self):
        """Test that different commands don't match"""
        matched, params = pattern_matches("open spotify", "close {app}")
        assert matched is False
        assert params == {}
    
    def test_single_param_extraction(self):
        """Test extraction of single parameter"""
        matched, params = pattern_matches("switch to chrome", "switch to {app}")
        assert matched is True
        assert params == {"app": "chrome"}
    
    def test_multi_word_param_at_end(self):
        """Test extraction of multi-word parameter at end of pattern"""
        matched, params = pattern_matches("switch to visual studio code", "switch to {app}")
        assert matched is True
        assert params == {"app": "visual studio code"}
    
    def test_param_in_middle(self):
        """Test parameter in middle of pattern"""
        matched, params = pattern_matches("open file.txt in notepad", "open {file} in {app}")
        assert matched is True
        assert params == {"file": "file.txt", "app": "notepad"}
    
    def test_multiple_params(self):
        """Test pattern with multiple parameters"""
        matched, params = pattern_matches("send hello to john", "send {message} to {recipient}")
        assert matched is True
        assert params == {"message": "hello", "recipient": "john"}
    
    def test_case_insensitive(self):
        """Test that matching is case-insensitive"""
        matched, params = pattern_matches("SWITCH TO CHROME", "switch to {app}")
        assert matched is True
        assert params == {"app": "chrome"}
    
    def test_extra_words_at_end(self):
        """Test that extra words at end are captured in last parameter"""
        matched, params = pattern_matches("close firefox now", "close {app}")
        assert matched is True
        assert params == {"app": "firefox now"}
    
    def test_whitespace_handling(self):
        """Test that extra whitespace is handled correctly"""
        matched, params = pattern_matches("  switch  to   chrome  ", "switch to {app}")
        assert matched is True
        assert params == {"app": "chrome"}
    
    def test_empty_pattern(self):
        """Test that empty pattern returns no match"""
        matched, params = pattern_matches("anything", "")
        assert matched is False
        assert params == {}
    
    def test_empty_text(self):
        """Test that empty text doesn't match pattern"""
        matched, params = pattern_matches("", "switch to {app}")
        assert matched is False
        assert params == {}
    
    def test_partial_match_fails(self):
        """Test that partial matches don't succeed"""
        matched, params = pattern_matches("switch", "switch to {app}")
        assert matched is False
        assert params == {}
    
    def test_similar_but_different_command(self):
        """Test that similar commands are distinguished"""
        matched, params = pattern_matches("minimize chrome", "maximize {app}")
        assert matched is False
        assert params == {}
    
    def test_special_characters_in_param(self):
        """Test parameter with special characters"""
        matched, params = pattern_matches("open file-name_2.txt", "open {file}")
        assert matched is True
        assert params == {"file": "file-name_2.txt"}
    
    def test_numbers_in_param(self):
        """Test parameter with numbers"""
        matched, params = pattern_matches("switch to chrome123", "switch to {app}")
        assert matched is True
        assert params == {"app": "chrome123"}
    
    @pytest.mark.parametrize("text,pattern,expected_match,expected_params", [
        # Window management commands
        ("switch to chrome", "switch to {app}", True, {"app": "chrome"}),
        ("open spotify", "open {app}", True, {"app": "spotify"}),
        ("minimize", "minimize", True, {}),
        ("maximize window", "maximize window", True, {}),
        ("close firefox", "close {app}", True, {"app": "firefox"}),
        
        # Complex multi-word parameters
        ("switch to visual studio code", "switch to {app}", True, {"app": "visual studio code"}),
        ("open microsoft edge", "open {app}", True, {"app": "microsoft edge"}),
        
        # Multiple parameters
        ("move window to left", "move {target} to {position}", True, {"target": "window", "position": "left"}),
        
        # No matches
        ("hello world", "switch to {app}", False, {}),
        ("maximize", "minimize", False, {}),
    ])
    def test_parametrized_patterns(self, text, pattern, expected_match, expected_params):
        """Parametrized test for various pattern combinations"""
        matched, params = pattern_matches(text, pattern)
        assert matched == expected_match
        assert params == expected_params


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
