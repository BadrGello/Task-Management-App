import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel
)

class DynamicRow(QWidget):
    def __init__(self, delete_callback):
        super().__init__()
        self.layout = QHBoxLayout()
        
        self.line_edit = QLineEdit(self)
        self.layout.addWidget(self.line_edit)
        
        self.delete_button = QPushButton("Delete", self)
        self.delete_button.clicked.connect(delete_callback)
        self.layout.addWidget(self.delete_button)
        
        self.setLayout(self.layout)

    def get_text(self):
        return self.line_edit.text()

    def set_text(self, text):
        self.line_edit.setText(text)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Row Example")
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.add_button = QPushButton("Add Row", self)
        self.add_button.clicked.connect(self.add_row)
        self.layout.addWidget(self.add_button)
        
        self.rows = []  # List to keep track of rows

    def add_row(self):
        # Create a new row and add it to the layout
        row = DynamicRow(lambda: self.delete_row(row))
        self.rows.append(row)
        self.layout.addWidget(row)

    def delete_row(self, row):
        # Remove the row from the layout and the list
        self.layout.removeWidget(row)
        row.deleteLater()  # Properly delete the widget
        self.rows.remove(row)  # Remove from the list

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())