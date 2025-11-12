"""
Setup Wizard Manager - orchestrates the first-run setup flow.
"""

from typing import List, Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QStackedWidget, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal as Signal
from PyQt5.QtGui import QFont
from qfluentwidgets import (
    PushButton, PrimaryPushButton, 
    ProgressBar, BodyLabel, TitleLabel, IconWidget, FluentIcon,
    InfoBar, InfoBarPosition
)

from .base_page import BasePage, ValidationState


class SetupWizardManager(QDialog):
    """
    Manages the setup wizard flow.
    
    Handles:
    - Page navigation (next/back)
    - Progress tracking
    - Data collection from all pages
    - Final configuration saving
    - Validation and navigation guards
    """
    
    # Signals
    wizard_completed = Signal(dict)  # Emitted when wizard completes with collected data
    wizard_cancelled = Signal()  # Emitted when wizard is cancelled
    
    def __init__(self, parent: Optional[QDialog] = None):
        super().__init__(parent)
        self.pages: List[BasePage] = []
        self.current_page_index = 0
        self.collected_data = {}
        self._navigation_blocked = False
        
        self.setWindowTitle("Scribe Setup Wizard")
        self.setMinimumSize(900, 875)
        self.resize(900, 875)
        self.setModal(True)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the wizard UI structure."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header area
        header = self._create_header()
        layout.addWidget(header)
        
        # Progress bar
        self.progress_bar = ProgressBar(self)
        self.progress_bar.setFixedHeight(4)
        layout.addWidget(self.progress_bar)
        
        # Page title and description
        title_frame = QFrame(self)
        title_frame.setObjectName("titleFrame")
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(40, 30, 40, 20)
        title_layout.setSpacing(10)
        
        self.page_title = TitleLabel("", self)
        self.page_description = BodyLabel("", self)
        self.page_description.setWordWrap(True)
        
        title_layout.addWidget(self.page_title)
        title_layout.addWidget(self.page_description)
        layout.addWidget(title_frame)
        
        # Validation status (hidden initially)
        self.validation_status = BodyLabel("", self)
        self.validation_status.setStyleSheet("color: #666; font-style: italic; padding: 0 40px;")
        self.validation_status.hide()
        layout.addWidget(self.validation_status)
        
        # Page content area (stacked widget)
        self.stack = QStackedWidget(self)
        layout.addWidget(self.stack, 1)
        
        # Button bar
        button_bar = self._create_button_bar()
        layout.addWidget(button_bar)
        
    def _create_header(self) -> QFrame:
        """Create the wizard header with logo/branding."""
        header = QFrame(self)
        header.setObjectName("wizardHeader")
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame#wizardHeader {
                background-color: #6750A4;
                border: none;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(40, 0, 40, 0)
        layout.setSpacing(12)
        
        # Icon
        icon_widget = IconWidget(FluentIcon.MICROPHONE, header)
        icon_widget.setFixedSize(32, 32)
        layout.addWidget(icon_widget)
        
        # Title
        title = QLabel("Scribe Setup", header)
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        return header
        
    def _create_button_bar(self) -> QFrame:
        """Create the bottom button bar with navigation buttons."""
        button_bar = QFrame(self)
        button_bar.setObjectName("buttonBar")
        button_bar.setFixedHeight(80)
        button_bar.setStyleSheet("""
            QFrame#buttonBar {
                background-color: #F5F5F5;
                border-top: 1px solid #E0E0E0;
            }
        """)
        
        layout = QHBoxLayout(button_bar)
        layout.setContentsMargins(40, 20, 40, 20)
        
        # Cancel button
        self.cancel_btn = PushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self._on_cancel)
        layout.addWidget(self.cancel_btn)
        
        layout.addStretch()
        
        # Back button
        self.back_btn = PushButton("Back", self)
        self.back_btn.clicked.connect(self._on_back)
        layout.addWidget(self.back_btn)
        
        # Next/Finish button
        self.next_btn = PrimaryPushButton("Next", self)
        self.next_btn.clicked.connect(self._on_next)
        layout.addWidget(self.next_btn)
        
        return button_bar
    
    def add_page(self, page: BasePage):
        """
        Add a page to the wizard.
        
        Args:
            page: The wizard page to add
        """
        self.pages.append(page)
        self.stack.addWidget(page)
        
        # Connect page signals
        page.page_complete.connect(self._on_page_validation_changed)
        page.next_requested.connect(self._on_next)
        page.back_requested.connect(self._on_back)
        page.cancel_requested.connect(self._on_cancel)
        page.validation_changed.connect(self._on_validation_state_changed)
        
    def start(self):
        """Start the wizard by showing the first page."""
        if not self.pages:
            raise ValueError("No pages added to wizard")
            
        self.current_page_index = 0
        self._show_page(0)
        self.show()
        
    def _show_page(self, index: int):
        """
        Show a specific page.
        
        Args:
            index: Page index to show
        """
        if index < 0 or index >= len(self.pages):
            return
            
        # Leave current page
        if self.current_page_index < len(self.pages):
            current_page = self.pages[self.current_page_index]
            current_page.on_page_leave()
        
        # Update index and UI
        self.current_page_index = index
        page = self.pages[index]
        
        # Update page content
        self.stack.setCurrentWidget(page)
        self.page_title.setText(page.get_title())
        self.page_description.setText(page.get_description())
        
        # Update progress bar
        progress = int((index / (len(self.pages) - 1)) * 100) if len(self.pages) > 1 else 100
        self.progress_bar.setValue(progress)
        
        # Update buttons
        self.back_btn.setEnabled(index > 0)
        
        is_last_page = (index == len(self.pages) - 1)
        self.next_btn.setText("Finish" if is_last_page else "Next")
        
        # Update validation status
        self._update_validation_status(page)
        
        # Enter new page
        page.on_page_enter()
        
    def _update_validation_status(self, page: BasePage):
        """Update validation status display for current page."""
        validation_state = page.get_validation_state()
        validation_message = page.get_validation_message()
        
        if validation_state == ValidationState.PENDING:
            self.validation_status.setText(f"⏳ {validation_message}")
            self.validation_status.setStyleSheet("color: #1976D2; font-style: italic; padding: 0 40px;")
            self.validation_status.show()
        elif validation_state == ValidationState.ERROR:
            self.validation_status.setText(f"❌ {validation_message}")
            self.validation_status.setStyleSheet("color: #D32F2F; font-style: italic; padding: 0 40px;")
            self.validation_status.show()
        elif validation_state == ValidationState.INVALID:
            self.validation_status.setText(f"⚠️ {validation_message}")
            self.validation_status.setStyleSheet("color: #F57C00; font-style: italic; padding: 0 40px;")
            self.validation_status.show()
        else:
            # Valid or no message - hide status
            self.validation_status.hide()
    
    def _can_navigate_next(self) -> bool:
        """
        Check if navigation to next page is allowed.
        
        Returns:
            bool: True if navigation is allowed
        """
        if self._navigation_blocked:
            return False
            
        current_page = self.pages[self.current_page_index]
        
        # Check if current page is valid
        if not current_page.can_proceed():
            return False
        
        # Check if current page has async validation in progress
        if current_page.get_validation_state() == ValidationState.PENDING:
            return False
        
        return True
    
    def _can_navigate_back(self) -> bool:
        """
        Check if navigation to previous page is allowed.
        
        Returns:
            bool: True if navigation is allowed
        """
        if self._navigation_blocked:
            return False
            
        return self.current_page_index > 0
    
    def _on_next(self):
        """Handle next button click."""
        if not self._can_navigate_next():
            self._show_validation_error()
            return
            
        current_page = self.pages[self.current_page_index]
        
        # Validate current page one more time
        if not current_page.validate():
            InfoBar.warning(
                title="Validation Required",
                content="Please complete required fields before proceeding.",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
            
        # Collect data from current page
        try:
            page_data = current_page.get_data()
            if page_data:
                self.collected_data.update(page_data)
        except Exception as e:
            InfoBar.error(
                title="Data Collection Error",
                content=f"Failed to save page data: {str(e)}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self
            )
            return
        
        # Check if this is the last page
        if self.current_page_index == len(self.pages) - 1:
            self._complete_wizard()
        else:
            self._show_page(self.current_page_index + 1)
            
    def _on_back(self):
        """Handle back button click."""
        if not self._can_navigate_back():
            return
            
        self._show_page(self.current_page_index - 1)
            
    def _on_cancel(self):
        """Handle cancel button click."""
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Cancel Setup",
            "Are you sure you want to cancel the setup wizard? Any configuration progress will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.wizard_cancelled.emit()
            self.reject()
        
    def _on_page_validation_changed(self, is_valid: bool):
        """Handle page validation state changes."""
        current_page = self.pages[self.current_page_index]
        self.next_btn.setEnabled(is_valid and current_page.can_proceed())
        
    def _on_validation_state_changed(self, state: ValidationState, message: str):
        """Handle validation state changes with detailed information."""
        current_page = self.pages[self.current_page_index]
        self._update_validation_status(current_page)
        
        # Update next button based on validation state
        can_proceed = (state == ValidationState.VALID) and current_page.can_proceed()
        self.next_btn.setEnabled(can_proceed)
    
    def _show_validation_error(self):
        """Show validation error message to user."""
        current_page = self.pages[self.current_page_index]
        validation_state = current_page.get_validation_state()
        validation_message = current_page.get_validation_message()
        
        if validation_state == ValidationState.PENDING:
            InfoBar.info(
                title="Validation in Progress",
                content="Please wait for validation to complete.",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
        elif validation_message:
            InfoBar.warning(
                title="Validation Required",
                content=validation_message or "Please complete required fields before proceeding.",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        else:
            InfoBar.warning(
                title="Validation Required",
                content="Please complete required fields before proceeding.",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        
    def _complete_wizard(self):
        """Complete the wizard and emit collected data."""
        try:
            # Final validation of all collected data
            if not self._validate_collected_data():
                return
                
            self.wizard_completed.emit(self.collected_data)
            self.accept()
            
        except Exception as e:
            InfoBar.error(
                title="Setup Error",
                content=f"Failed to complete setup: {str(e)}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self
            )
    
    def _validate_collected_data(self) -> bool:
        """
        Validate all collected data before completing wizard.
        
        Returns:
            bool: True if data is valid
        """
        # Check for required fields
        required_fields = ['audio_device', 'hotkey']
        missing_fields = [field for field in required_fields if field not in self.collected_data]
        
        if missing_fields:
            InfoBar.error(
                title="Missing Required Information",
                content=f"Please complete: {', '.join(missing_fields)}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self
            )
            return False
        
        return True
        
    def get_collected_data(self) -> dict:
        """
        Get all collected configuration data.
        
        Returns:
            dict: All data collected from wizard pages
        """
        return self.collected_data.copy()
    
    def closeEvent(self, event):
        """Handle wizard close event."""
        # Clean up all pages
        for page in self.pages:
            page.cleanup()
        
        super().closeEvent(event)
