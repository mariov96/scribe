"""
Status Popup Window - Minimal, discreet recording indicator
Similar to WhisperFlow's compact design
"""
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPainter, QColor, QPen
from PyQt5.QtWidgets import QApplication, QLabel, QHBoxLayout, QWidget, QGraphicsOpacityEffect
from qfluentwidgets import FluentWindow

class StatusPopup(QWidget):
    """
    Minimal frameless popup that shows in top-right corner
    Just a small pulsing dot with minimal text
    """

    def __init__(self):
        super().__init__()
        self.pulse_opacity = 1.0
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self._pulse_animation)
        self.pulse_direction = -1  # -1 for fade out, 1 for fade in
        
        # Fade animation setup
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(300)  # 300ms fade
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        self.initUI()

    def initUI(self):
        """Initialize the minimal status popup UI"""
        # Frameless, always on top, does not accept focus
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus |  # Prevents stealing focus
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)  # Show without activating

        # Wider to accommodate full error messages like "No speech detected"
        self.setFixedSize(280, 50)

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        # Icon label (emoji for visual clarity)
        self.icon_label = QLabel()
        self.icon_label.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        self.icon_label.setAlignment(Qt.AlignCenter)

        # Small pulsing dot indicator
        self.dot_label = QLabel()
        self.dot_label.setFixedSize(10, 10)
        self.dot_label.setStyleSheet("""
            QLabel {
                background-color: #F44336;
                border-radius: 5px;
                border: none;
            }
        """)

        # Descriptive status text
        self.status_label = QLabel()
        self.status_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #FFFFFF;
            background: transparent;
            border: none;
        """)

        # Container with softer grey background for better visibility
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(60, 60, 60, 0.95);
                border-radius: 12px;
                border: 1px solid rgba(100, 100, 100, 0.3);
                padding: 4px;
            }
        """)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.dot_label)
        layout.addWidget(self.status_label)
        layout.addStretch()

    def _pulse_animation(self):
        """Animate the pulsing dot"""
        self.pulse_opacity += self.pulse_direction * 0.05
        if self.pulse_opacity <= 0.4:
            self.pulse_direction = 1
        elif self.pulse_opacity >= 1.0:
            self.pulse_direction = -1

        # Update dot opacity
        self.dot_label.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(244, 67, 54, {self.pulse_opacity});
                border-radius: 6px;
                border: none;
            }}
        """)

    def show_recording(self):
        """Show descriptive recording status"""
        self.icon_label.setText("🎤")
        self.status_label.setText("Scribe is listening...")
        self.dot_label.setStyleSheet("""
            QLabel {
                background-color: #F44336;
                border-radius: 5px;
                border: none;
            }
        """)
        self.pulse_timer.start(50)  # Pulse every 50ms
        self._fade_in()

    def show_transcribing(self):
        """Show transcribing status"""
        self.pulse_timer.stop()
        self.icon_label.setText("✍️")
        self.status_label.setText("Scribe is transcribing...")
        self.dot_label.setStyleSheet("""
            QLabel {
                background-color: #2196F3;
                border-radius: 5px;
                border: none;
            }
        """)
        # Make sure we're visible and force repaint
        if not self.isVisible():
            self._fade_in()
        else:
            self.update()
            self.repaint()

    def show_complete(self):
        """Show completion status briefly"""
        self.pulse_timer.stop()
        self.icon_label.setText("✅")
        self.status_label.setText("Complete!")
        self.dot_label.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                border-radius: 5px;
                border: none;
            }
        """)
        # Make sure we're visible and force repaint
        if not self.isVisible():
            self._fade_in()
        else:
            self.update()
            self.repaint()

    def show_error(self, message="Error"):
        """Show error status"""
        self.pulse_timer.stop()
        self.icon_label.setText("❌")
        self.status_label.setText(message)
        self.dot_label.setStyleSheet("""
            QLabel {
                background-color: #F44336;
                border-radius: 5px;
                border: none;
            }
        """)
        # Make sure we're visible
        if not self.isVisible():
            self._fade_in()
    
    def _fade_in(self):
        """Fade in animation"""
        self.position_and_show()
        self.fade_animation.stop()
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
    
    def _fade_out(self):
        """Fade out animation"""
        self.fade_animation.stop()
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self._on_fade_out_finished)
        self.fade_animation.start()
    
    def _on_fade_out_finished(self):
        """Called when fade out animation completes"""
        self.fade_animation.finished.disconnect()
        super().close()

    def position_and_show(self):
        """Position at bottom-center of screen"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        window_width = self.width()
        window_height = self.height()

        # Bottom-center with comfortable margin from bottom
        x = (screen_width - window_width) // 2
        y = screen_height - window_height - 80

        self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()

    def close(self):
        """Stop animations when closing with fade out"""
        self.pulse_timer.stop()
        if self.isVisible():
            self._fade_out()
        else:
            super().close()

    def hide_indicator(self):
        """Convenience method to hide the indicator with fade"""
        self.close()


if __name__ == '__main__':
    """Test the status popup"""
    import sys
    from PyQt5.QtCore import QTimer

    app = QApplication(sys.argv)

    popup = StatusPopup()

    # Test sequence
    popup.show_recording()
    QTimer.singleShot(2000, popup.show_transcribing)
    QTimer.singleShot(4000, popup.show_complete)
    QTimer.singleShot(5500, popup.close)

    sys.exit(app.exec_())
