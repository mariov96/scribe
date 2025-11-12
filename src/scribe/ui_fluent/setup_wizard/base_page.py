"""
Base page class for Setup Wizard pages.

All wizard pages must inherit from BasePage and implement required methods.
"""

from abc import ABCMeta, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal as Signal, QTimer


# Custom metaclass to resolve QWidget and ABC metaclass conflict
class QABCMeta(type(QWidget), ABCMeta):
    pass


class ValidationState(Enum):
    """Validation states for wizard pages."""
    INVALID = "invalid"
    VALID = "valid"
    PENDING = "pending"
    ERROR = "error"


class BasePage(QWidget, metaclass=QABCMeta):
    """
    Abstract base class for wizard pages.
    
    All wizard pages must implement:
    - get_title(): Return page title
    - get_description(): Return page description
    - validate(): Check if page can proceed
    - get_data(): Return page configuration data
    """
    
    # Signals
    page_complete = Signal(bool)  # Emitted when page validation state changes
    next_requested = Signal()  # Emitted when user wants to go to next page
    back_requested = Signal()  # Emitted when user wants to go back
    cancel_requested = Signal()  # Emitted when user cancels wizard
    validation_changed = Signal(ValidationState, str)  # Emitted when validation state changes with message
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._validation_state = ValidationState.INVALID
        self._validation_message = ""
        self._is_valid = False
        self._async_validation_timer = None
        self.setup_ui()
        
    def setup_ui(self):
        """
        Set up page UI. Called automatically during initialization.
        Override this method to create your page layout.
        """
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 20, 40, 40)
        self.layout.setSpacing(24)
        
    @abstractmethod
    def get_title(self) -> str:
        """
        Get the page title.
        
        Returns:
            str: Page title displayed at top of wizard
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get the page description.
        
        Returns:
            str: Page description text explaining what user should do
        """
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """
        Validate the page data.
        
        Returns:
            bool: True if page data is valid and user can proceed
        """
        pass
    
    @abstractmethod
    def get_data(self) -> dict:
        """
        Get the configuration data from this page.
        
        Returns:
            dict: Configuration data to save
        """
        pass
    
    def validate_async(self) -> bool:
        """
        Perform asynchronous validation if needed.
        
        Returns:
            bool: True if async validation was started, False if not applicable
        """
        # Default implementation - override in subclasses for async validation
        return self.validate()
    
    def on_page_enter(self):
        """
        Called when page becomes visible.
        Override to perform initialization when page is shown.
        """
        # Trigger validation when page enters
        self._trigger_validation()
        
    def on_page_leave(self):
        """
        Called when leaving the page.
        Override to perform cleanup or save state.
        """
        # Cancel any pending async validation
        self._cancel_async_validation()
        
    def cleanup(self):
        """
        Clean up page resources.
        Called when wizard is closing or page is being destroyed.
        """
        self._cancel_async_validation()
        
    def set_validation_state(self, state: ValidationState, message: str = ""):
        """
        Update the validation state with optional message.
        
        Args:
            state: New validation state
            message: Optional validation message
        """
        old_state = self._validation_state
        self._validation_state = state
        self._validation_message = message
        
        # Update internal validity
        self._is_valid = (state == ValidationState.VALID)
        
        # Emit signals if state changed
        if old_state != state:
            self.validation_changed.emit(state, message)
            self.page_complete.emit(self._is_valid)
    
    def get_validation_state(self) -> ValidationState:
        """
        Get the current validation state.
        
        Returns:
            ValidationState: Current validation state
        """
        return self._validation_state
    
    def get_validation_message(self) -> str:
        """
        Get the current validation message.
        
        Returns:
            str: Validation message
        """
        return self._validation_message
    
    def set_valid(self, valid: bool, message: str = ""):
        """
        Update page validation state (legacy method for compatibility).
        
        Args:
            valid: Whether page is currently valid
            message: Optional validation message
        """
        if valid:
            self.set_validation_state(ValidationState.VALID, message)
        else:
            self.set_validation_state(ValidationState.INVALID, message)
    
    def is_valid(self) -> bool:
        """
        Check if page is currently valid.
        
        Returns:
            bool: Current validation state
        """
        return self._is_valid
    
    def can_skip(self) -> bool:
        """
        Check if this page can be skipped.
        
        Returns:
            bool: True if page is optional and can be skipped
        """
        return False
    
    def can_proceed(self) -> bool:
        """
        Check if user can proceed from this page.
        
        Returns:
            bool: True if page is valid and user can proceed
        """
        return self.is_valid()
    
    def _trigger_validation(self, delay_ms: int = 100):
        """
        Trigger validation with optional delay for UI responsiveness.
        
        Args:
            delay_ms: Delay in milliseconds before validation
        """
        if delay_ms > 0:
            if self._async_validation_timer is None:
                self._async_validation_timer = QTimer(self)
                self._async_validation_timer.setSingleShot(True)
                self._async_validation_timer.timeout.connect(self._perform_validation)
            
            self._async_validation_timer.start(delay_ms)
        else:
            self._perform_validation()
    
    def _perform_validation(self):
        """
        Perform validation and update state.
        """
        try:
            # Start with pending state for async operations
            if self.validate_async():
                # Async validation started - wait for completion
                self.set_validation_state(ValidationState.PENDING, "Validating...")
            else:
                # Synchronous validation
                if self.validate():
                    self.set_validation_state(ValidationState.VALID, "Validation successful")
                else:
                    self.set_validation_state(ValidationState.INVALID, "Validation failed")
        except Exception as e:
            self.set_validation_state(ValidationState.ERROR, f"Validation error: {str(e)}")
    
    def _cancel_async_validation(self):
        """
        Cancel any pending async validation.
        """
        if self._async_validation_timer is not None:
            self._async_validation_timer.stop()
            self._async_validation_timer = None
    
    def _on_validation_complete(self, is_valid: bool, message: str = ""):
        """
        Called when async validation completes.
        Subclasses should call this method when async validation finishes.
        
        Args:
            is_valid: Whether validation passed
            message: Validation message
        """
        if is_valid:
            self.set_validation_state(ValidationState.VALID, message)
        else:
            self.set_validation_state(ValidationState.INVALID, message)
