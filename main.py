import sys
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.resize(1000, 400)
    window.show()
    
    sys.exit(app.exec())