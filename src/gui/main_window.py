from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QComboBox, QLabel)
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt6.QtCore import Qt, QRectF

from src.core.music_theory import Fretboard, CHROMATIC_SCALE, SCALE_FORMULAS

class FretboardWidget(QWidget):
    def __init__(self, fretboard_model: Fretboard):
        super().__init__()
        self.model = fretboard_model
        
        self.active_positions = [] 
        self.current_root = ""
        self.current_scale = ""
        self.blue_note = None
        
        self.setMinimumHeight(250)

    def set_active_notes(self, positions: list, root_note: str, scale_type: str):
        """Updates the notes and calculates their musical roles (Root, Blue Note) before redrawing."""
        self.active_positions = positions
        self.current_root = root_note.upper()
        self.current_scale = scale_type
        
        # Calculate the Blue Note (b5) which is exactly 6 semitones from the root
        if scale_type == 'blues':
            root_idx = CHROMATIC_SCALE.index(self.current_root)
            blue_note_idx = (root_idx + 6) % 12
            self.blue_note = CHROMATIC_SCALE[blue_note_idx]
        else:
            self.blue_note = None
            
        self.update()

    def paintEvent(self, event):
        """Native PyQt6 method called whenever the widget needs to be drawn."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        
        margin_x = 30
        margin_y = 40
        
        draw_width = width - (margin_x * 2)
        draw_height = height - (margin_y * 2)
        
        num_strings = len(self.model.tuning)
        num_frets = self.model.frets
        
        fret_spacing = draw_width / num_frets
        string_spacing = draw_height / (num_strings - 1)

        # 1. Draw the "Wood" of the fretboard
        painter.setBrush(QColor("#2c1b12"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(margin_x, margin_y, int(draw_width), int(draw_height))

        # 2. Draw the Frets (Vertical lines)
        painter.setPen(QPen(QColor("#c0c0c0"), 2))
        for f in range(num_frets + 1):
            x = margin_x + (f * fret_spacing)
            painter.drawLine(int(x), margin_y, int(x), margin_y + int(draw_height))

        # 3. Draw the Strings (Horizontal lines)
        for s in range(num_strings):
            y = margin_y + ((num_strings - 1 - s) * string_spacing)
            thickness = 1 + (s * 0.5) 
            painter.setPen(QPen(QColor("#e0e0e0"), thickness))
            painter.drawLine(margin_x, int(y), margin_x + int(draw_width), int(y))
            
            painter.setPen(QPen(QColor("#ffffff")))
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(5, int(y + 5), self.model.tuning[s])

        # 4. Draw the Active Notes with Visual Hierarchy
        painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        for string_idx, fret_idx, note in self.active_positions:
            
            if fret_idx == 0:
                x = margin_x - 15 
            else:
                x = margin_x + (fret_idx * fret_spacing) - (fret_spacing / 2)
                
            y = margin_y + ((num_strings - 1 - string_idx) * string_spacing)
            
            # Determine color based on musical role
            if note == self.current_root:
                bg_color = QColor("#d32f2f") # Red for Root Note
                text_color = QColor("#ffffff")
            elif self.blue_note and note == self.blue_note:
                bg_color = QColor("#1976d2") # Blue for Blue Note
                text_color = QColor("#ffffff")
            else:
                bg_color = QColor("#ffb74d") # Light Orange for standard notes
                text_color = QColor("#000000")
            
            # Draw the note circle
            radius = 12
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(QColor("#ffffff"), 1))
            painter.drawEllipse(QRectF(x - radius, y - radius, radius * 2, radius * 2))
            
            # Draw the note text inside the circle
            painter.setPen(QPen(text_color))
            painter.drawText(QRectF(x - radius, y - radius, radius * 2, radius * 2), 
                             Qt.AlignmentFlag.AlignCenter, note)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scale Visualizer")
        
        self.guitar_model = Fretboard()
        self.init_ui()
        self.update_fretboard()

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        control_layout = QHBoxLayout()
        
        self.root_combo = QComboBox()
        self.root_combo.addItems(CHROMATIC_SCALE)
        self.root_combo.setCurrentText("A")
        
        self.scale_combo = QComboBox()
        scales = [s.replace('_', ' ').title() for s in SCALE_FORMULAS.keys()]
        self.scale_combo.addItems(scales)
        self.scale_combo.setCurrentText("Blues")
        
        self.root_combo.currentTextChanged.connect(self.update_fretboard)
        self.scale_combo.currentTextChanged.connect(self.update_fretboard)
        
        control_layout.addWidget(QLabel("Root:"))
        control_layout.addWidget(self.root_combo)
        control_layout.addWidget(QLabel("Scale:"))
        control_layout.addWidget(self.scale_combo)
        control_layout.addStretch()
        
        self.fretboard_widget = FretboardWidget(self.guitar_model)
        
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.fretboard_widget)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def update_fretboard(self):
        root_note = self.root_combo.currentText()
        scale_display = self.scale_combo.currentText()
        scale_key = scale_display.lower().replace(' ', '_')
        
        try:
            scale_notes = self.guitar_model.get_scale_notes(root_note, scale_key)
            positions = self.guitar_model.find_notes_on_fretboard(scale_notes)
            
            self.fretboard_widget.set_active_notes(positions, root_note, scale_key)
        except Exception as e:
            print(f"Error updating fretboard: {e}")