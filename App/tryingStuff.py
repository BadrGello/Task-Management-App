from PyQt5.QtWidgets import QApplication, QCalendarWidget, QMenu, QAction
from PyQt5.QtCore import QDate

class CustomCalendar(QCalendarWidget):
    def contextMenuEvent(self, event):
        # Create context menu
        menu = QMenu(self)

        # Add actions
        edit_action = QAction("Edit", self)
        delete_action = QAction("Delete", self)

        # Connect actions
        edit_action.triggered.connect(self.edit_date)
        delete_action.triggered.connect(self.delete_date)

        menu.addAction(edit_action)
        menu.addAction(delete_action)

        # Show menu
        menu.exec_(event.globalPos())

    def edit_date(self):
        date = self.selectedDate()
        print(f"Editing date: {date.toString()}")

    def delete_date(self):
        date = self.selectedDate()
        print(f"Deleting date: {date.toString()}")

app = QApplication([])

calendar = CustomCalendar()
calendar.show()

app.exec_()
