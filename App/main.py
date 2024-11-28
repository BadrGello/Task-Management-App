from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
import sys
from os import path

stream = QFile('App\LightMode.qss')
app = QApplication(sys.argv)

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

#When you start a new design on Qt designer, you are promted many chocies, the important 2 are "Main Window"

#and "Widget", and based on that is the first argument, the second argument is this "FROM_CLASS" that loads file path


class mainApp(QMainWindow, FORM_CLASS):
    # Constructor
    def __init__(self, parent=None):
        super(mainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        global stream
        global app
        stream.open(QIODevice.ReadOnly)
        app.setStyleSheet(QTextStream(stream).readAll())
        
        self.Settings = settingWindow(self)
        # Icons
        self.pushButton_sort1.setIcon(QIcon('App/sort.png'))
        self.pushButton_sort1.setIconSize(QSize(24, 24))
        self.setWindowIcon(QIcon('App/App_icon.png'))

        # Function calls
        self.Handle_UI()
        self.Handle_searchBar()
        
        #Connecting signals (buttons, etc) to slots (functions)

        #Handles adding new tasks
        self.pushButton_addTask.clicked.connect(self.Handle_add_window) # Upon clicking the button "Add" which its object name is pushButton_addTask, it excutes the function "add_task_widget"

        #When the search bar button is clicked, it goes to the function "Handle_searchBar"

        # Connecting signals
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
        # self.taskList = dict()

        # Add Window
        self.addWin = None

        self.iterate_buttons(self)
        
        self.iterate_combobox(self)

    def iterate_buttons(self, parent_widget):
        for child in parent_widget.findChildren(QWidget):
            if isinstance(child, QAbstractButton):
                # SIZE
                child.setFixedSize(150, 30)
                
            self.iterate_buttons(child)

    

    def iterate_combobox(self, parent_widget):
        for child in parent_widget.findChildren(QWidget):
            if isinstance(child, QComboBox):
                # SIZE
                child.setFixedSize(150, 30)
                
            self.iterate_combobox(child)
            

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
            instruction_label.setStyleSheet("font-family: Arial; font-size: 20px; margin-left: 20px; color:rgb(252,189,16);")
            layout.addWidget(instruction_label)

            study_time_label = QLabel("Study Time (minutes):")
            study_time_input = QSpinBox()
            study_time_input.setRange(1, 1440)
            study_time_input.setStyleSheet("font-size: 13px; font-family: Arial; height:35px; border-radius:5px;border:1px solid rgb(248,218,111);")
            layout.addWidget(study_time_label)
            layout.addWidget(study_time_input)

            break_time_label = QLabel("Break Time (minutes):")
            break_time_input = QSpinBox()
            break_time_input.setRange(1, 1440)
            break_time_input.setStyleSheet("font-size: 13px; font-family: Arial; height:35px; border-radius:5px;border:1px solid rgb(248,218,111);")
            layout.addWidget(break_time_label)
            layout.addWidget(break_time_input)

            # Create countdown label
            self.countdown_label = QLabel("")
            self.countdown_label.setStyleSheet("font-size: 20px; font-family: Arial; color: rgb(209,56,62); font-weight:bold; text-align: center;")
            layout.addWidget(self.countdown_label)

            self.study_time_input = study_time_input  # Store reference
            self.break_time_input = break_time_input    # Store reference

            # Connect button to start_countdown function
            self.pushButton_study.clicked.connect(lambda: self.start_countdown(study_time_input.value(), break_time_input.value()))

            # Set layout to TextBrowser
            self.TextBrowser_display.setLayout(layout)
        else:
            
            # Default descriptions for other techniques
            descriptions = {
                "Pomodoro Technique": """
                <br>
                    <h1 style="font-family: Arial; text-align: left; font-size: 22px; margin-left: 20px; color:rgb(252,189,16); ">
                        Pomodoro Technique
                    </h1>
                    <p style="font-family: Arial; font-size: 20px; margin-left: 20px; color:rgb(248,218,111);">
                        <br><br><b>-</b>This technique involves working in focused 25-minute intervals, followed by a 5-minute break.<br><br>
                        <b>-</b>After four Pomodoros, take a longer 15-20 minute break.
                    </p>
                """,
                "52-17 Technique": """
                <br>
                    <h1 style="font-family: Arial; text-align: left; font-size: 22px; margin-left: 20px; color:rgb(252,189,16);">
                        52-17 Technique
                    </h1>
                    <p style="font-family: Arial; font-size: 20px; margin-left: 20px; color:rgb(248,218,111);">
                        <br><br><b>-</b>Study for 52 minutes, then take a 17-minute break.<br><br>
                        <b>-</b>This cycle can be repeated multiple times throughout the day.
                    </p>
                """,
                "The 45-15 Method": """
                <br>
                    <h1 style="font-family: Arial; text-align: left; font-size: 22px; margin-left: 20px; color:rgb(252,189,16);">
                        The 45-15 Method
                    </h1>
                    <p style="font-family: Arial; font-size: 20px; margin-left: 20px; color:rgb(248,218,111);">
                        <br><br><b>-</b>Study for 45 minutes, then take a 15-minute break.<br><br>
                        <b>-</b>This cycle can be repeated throughout the day.
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
                self.doneNum_3.display(total_seconds)
                self.countdown_label.setText(f"{minutes:02}:{seconds:02}")
                total_seconds -= 1
            else:
                self.timer.stop()
                self.doneNum_3.display(0)
                self.countdown_label.setText("Break Time! Take a rest.")

        # Create a QTimer to update the countdown every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(update_timer)
        self.timer.start(1000)

    def Handle_searchBar(self):
        self.searchBarText = self.plainTextEdit_searchTask.toPlainText()
        print(self.searchBarText)

    def Handle_add_window(self):
        # if self.addWin is None:
        #     self.addWin = addWindow(self)
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

        self.iterate_buttons(self)

    def Handle_settings(self):
        self.Settings.show()

        self.iterate_combobox(self)

class addWindow(QDialog, ADD_TASK_CLASS):
    #Constructor
    def __init__(self, parent=None):
        super(addWindow, self).__init__(parent)
        QDialog.__init__(self)
        self.setupUi(self)
        #The parent is the main window, SO IT'S IMPORTANT TO: pass self when initiating addWindow -> addWindow(self)
        self.mainWindow = parent
        #Connecting signals
        # self.EventDialogButtonBox.accepted.connect(self.Handle_ok_clicked)
        # self.EventDialogButtonBox.rejected.connect(self.Handle_cancel_clicked)
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
        self.ThemeComboBox.currentTextChanged.connect(self.change_theme)
        global stream,app
        
    
    def change_theme(self, text):
        """
        Change the theme based on the selected text from ThemeComboBox.
        """
        global stream
        global app

        # Close the current theme file if open
        if stream.isOpen():
            stream.close()

        # Select the appropriate theme file
        if text == "Light theme":
            stream = QFile('App\LightMode.qss')
            stream.open(QIODevice.ReadOnly)
            app.setStyleSheet(QTextStream(stream).readAll())
        elif text == "Dark theme":
            stream = QFile('App\DarkMode.qss')
            stream.open(QIODevice.ReadOnly)
            app.setStyleSheet(QTextStream(stream).readAll())
        else:
            print(f"Unknown theme selected: {text}")
            return

        # Reopen the selected theme file
        
        
        

# This is the task widget
class addTask(QWidget, TASK_WIDGET_CLASS):
    #Constructor
    def __init__(self, parent=None):
        super(addTask, self).__init__(parent)
        QWidget.__init__(self)
        self.setupUi(self)

        ##Steps List##
        self.stepInput.returnPressed.connect(self.add_step)  # When pressing Enter after writing a step, it will add it to the list
        self.stepsListWidget.itemDoubleClicked.connect(self.toggle_step_completion) #We can double click to mark as completed
        self.stepsListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.stepsListWidget.customContextMenuRequested.connect(self.show_context_menu) # Right click a step and click delete to delete
        ##          ##

        ##Complete Button##
        self.completeStatus = False
        self.taskCompletetoolButton.setAccessibleDescription("Incompleted")
        self.taskCompletetoolButton.setCheckable(True)  # Button stays pressed when clicked
        self.taskCompletetoolButton.toggled.connect(self.toggle_task_completion)
        ##               ##

    #Following functions for steps list
    def add_step(self):
        
        step_desc = self.stepInput.text()
        if (step_desc):
            item = QListWidgetItem(step_desc)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable) #Creates a checkbox related to the item (step)
            item.setCheckState(Qt.Unchecked)  #Default is unchecked
            self.stepsListWidget.addItem(item) #Add step
            self.stepInput.clear()

    def toggle_step_completion(self, item):

        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)

    def show_context_menu(self, position):

        menu = QMenu()
        delete_step = menu.addAction("Delete Step")
        action = menu.exec_(self.stepsListWidget.mapToGlobal(position))
        if (action == delete_step):
            selected_items = self.stepsListWidget.selectedItems() #Displays the context menu and returns the action selected by the user or none
            for item in selected_items:
                deleted_step = self.stepsListWidget.takeItem(self.stepsListWidget.row(item))

    # When clicking on Incompleted/Completed button
    def toggle_task_completion(self):
        
        if(self.completeStatus):
            # self.taskCompletetoolButton.setIcon(QIcon("path_to_icon.png")) # Can set an icon instead of text
            self.taskCompletetoolButton.setText("Incompleted")
            self.completeStatus = False
        else:
            self.taskCompletetoolButton.setText("Completed")
            self.completeStatus = True


def main():
    
    
    #Applying Style Sheet
    
    window = mainApp() #An instance of the class mainApp

    window.show()
    app.exec_()#Infinite loop

if __name__ == '__main__':
    main()