from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
import sys
from os import path

# Constants
mainWindowFileName = "mainWindow.ui"
taskWidgetFileName = "taskWidget.ui"
addTaskWindowFileName = "AddWindow.ui"
settingsWindowFilName = "SettingWindow.ui"

# Import UI files
FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), mainWindowFileName))
TASK_WIDGET_CLASS, _ = loadUiType(path.join(path.dirname(__file__), taskWidgetFileName))
ADD_TASK_CLASS, _ = loadUiType(path.join(path.dirname(__file__), addTaskWindowFileName))
SETTING_CLASS, _ = loadUiType(path.join(path.dirname(__file__), settingsWindowFilName))

class mainApp(QMainWindow, FORM_CLASS):
    # Constructor
    def __init__(self, parent=None):
        super(mainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        
        # Icons
        self.pushButton_sort1.setIcon(QIcon('App/sort.png'))
        self.pushButton_sort1.setIconSize(QSize(24, 24))
        self.setWindowIcon(QIcon('App/App_icon.png'))

        # Function calls
        self.Handle_UI()
        self.Handle_searchBar()
        
        # Connecting signals
        self.pushButton_addTask.clicked.connect(self.Handle_add_window)
        self.pushButton_searchTask.clicked.connect(self.Handle_searchBar)
        self.actionPreferences.triggered.connect(self.Handle_settings)

        # Handle ComboBox changes
        self.comboBox_techniques.currentTextChanged.connect(self.update_textbox)

        # Variables
        self.searchBarText = ""
        self.timer = None

        # ScrollArea Task Widgets
        self.addTaskList = []
        self.addTask = None
        self.tasksGroupBox = None
        self.tasksForm = None

        # Add Window
        self.addWin = None

    def Handle_UI(self):
        self.setWindowTitle("Taskyyy")

    def update_textbox(self, text):
        layout = self.TextBrowser_display.layout()
        self.TextBrowser_display.clear()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                del item
            layout.deleteLater()

        if text == "Your Own Time Blocking":
            # Create layout directly in TextBrowser
            layout = QVBoxLayout()

            # Create labels and inputs
            instruction_label = QLabel("Enter your study and break times (in minutes): ")
            instruction_label.setStyleSheet("font-size: 14px; font-family: Arial;")
            layout.addWidget(instruction_label)

            study_time_label = QLabel("Study Time (minutes):")
            study_time_input = QSpinBox()
            study_time_input.setRange(1, 1440)
            study_time_input.setStyleSheet("font-size: 14px; font-family: Arial;")
            layout.addWidget(study_time_label)
            layout.addWidget(study_time_input)

            break_time_label = QLabel("Break Time (minutes):")
            break_time_input = QSpinBox()
            break_time_input.setRange(1, 1440)
            break_time_input.setStyleSheet("font-size: 14px; font-family: Arial;")
            layout.addWidget(break_time_label)
            layout.addWidget(break_time_input)

            # Create start button
            start_button = QPushButton("Start Countdown")
            start_button.setStyleSheet("font-size: 14px; font-family: Arial;")
            layout.addWidget(start_button)

            # Create countdown label
            self.countdown_label = QLabel("")
            self.countdown_label.setStyleSheet("font-size: 18px; font-family: Arial; color: red; text-align: center;")
            layout.addWidget(self.countdown_label)

            # Connect button to start_countdown function
            start_button.clicked.connect(lambda: self.start_countdown(study_time_input.value(), break_time_input.value()))

            # Set layout to TextBrowser
            self.TextBrowser_display.setLayout(layout)
        else:
            
            # Default descriptions for other techniques
            descriptions = {
                "Pomodoro Technique": """
                    <h1 style="font-family: Arial; font-weight: bold; text-align: center;font-size: 32px;">
                        <u>Pomodoro Technique</u>
                    </h1>
                    <p style="font-family: Arial; font-size: 32px;">
                        <b>How it works:</b> This technique involves working in focused 25-minute intervals, followed by a 5-minute break.
                        After four Pomodoros, take a longer 15-20 minute break.
                    </p>
                """,
                "52-17 Technique": """
                    <h1 style="font-family: Arial; font-weight: bold; text-align: center;">
                        <u>52-17 Technique</u>
                    </h1>
                    <p style="font-family: Arial; font-size: 32px;">
                        <b>How it works:</b> Study for 52 minutes, then take a 17-minute break.
                        This cycle can be repeated multiple times throughout the day.
                    </p>
                """,
                "The 45-15 Method": """
                    <h1 style="font-family: Arial; font-weight: bold; text-align: center;">
                        <u>The 45-15 Method</u>
                    </h1>
                    <p style="font-family: Arial; font-size: 32px;">
                        <b>How it works:</b> Study for 45 minutes, then take a 15-minute break.
                        This cycle can be repeated throughout the day.
                    </p>
                """
            }

            formatted_text = descriptions.get(text, "<p>No description available for this technique.</p>")
            self.TextBrowser_display.setText(formatted_text)

    def start_countdown(self, study_time, break_time):
        total_seconds = study_time * 60  # Convert minutes to seconds for the timer

        def update_timer():
            nonlocal total_seconds
            if total_seconds > 0:
                minutes, seconds = divmod(total_seconds, 60)
                self.countdown_label.setText(f"Time Remaining: {minutes:02}:{seconds:02}")
                total_seconds -= 1
            else:
                self.timer.stop()
                self.countdown_label.setText("Break Time! Take a rest.")

        # Create a QTimer to update the countdown every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(update_timer)
        self.timer.start(1000)

    def Handle_searchBar(self):
        self.searchBarText = self.plainTextEdit_searchTask.toPlainText()
        print(self.searchBarText)

    def Handle_add_window(self):
        self.addWin = addWindow(self)
        self.addWin.show()

    def add_task_widget(self):
        self.addTask = addTask(self)
        if self.tasksGroupBox is None:
            self.tasksGroupBox = QGroupBox('Tasks')
        if self.tasksForm is None:
            self.tasksForm = QFormLayout()
        self.tasksGroupBox.setLayout(self.tasksForm)

        self.addTaskList.append(addTask(self))

        for task in self.addTaskList:
            self.tasksForm.addRow(task)

        self.scrollArea_tasks.setWidget(self.tasksGroupBox)
        self.scrollArea_tasks.setWidgetResizable(True)

    def Handle_settings(self):
        self.Settings = settingWindow(self)
        self.Settings.show()

class addWindow(QDialog, ADD_TASK_CLASS):
    def __init__(self, parent=None):
        super(addWindow, self).__init__(parent)
        QDialog.__init__(self)
        self.setupUi(self)
        self.mainWindow = parent
        self.TaskDialogButtonBox.accepted.connect(self.Handle_ok_clicked)
        self.TaskDialogButtonBox.rejected.connect(self.Handle_cancel_clicked)

    def Handle_ok_clicked(self):
        self.mainWindow.add_task_widget()
        self.close()

    def Handle_cancel_clicked(self):
        self.close()

class settingWindow(QMainWindow, SETTING_CLASS):
    def __init__(self, parent=None):
        super(settingWindow, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.mainWindow = parent

class addTask(QWidget, TASK_WIDGET_CLASS):
    def __init__(self, parent=None):
        super(addTask, self).__init__(parent)
        QWidget.__init__(self)
        self.setupUi(self)

def main():
    app = QApplication(sys.argv)
    window = mainApp()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()