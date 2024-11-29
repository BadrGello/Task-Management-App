from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
import sys
from os import path

stream = QFile('App/LightMode.qss')
app = QApplication(sys.argv)

appIcon = 'App/Icons/appIcon (1).svg'
appName = 'Tasky' #Temp
settingsIcon = 'App/Icons/settings.svg'
addIcon = 'App/Icons/add.svg'

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

def refresh():
    # A trick to refresh the app in order to apply the font and fix display issue in QCheckBox in Settings 
    if stream.isOpen():
        stream.close()
    stream.open(QIODevice.ReadOnly)
    app.setStyleSheet(QTextStream(stream).readAll())

#When you start a new design on Qt designer, you are promted many chocies, the important 2 are "Main Window"
#and "Widget", and based on that is the first argument, the second argument is this "FROM_CLASS" that loads file path

class mainApp(QMainWindow, FORM_CLASS):
    # Constructor
    def __init__(self, parent=None):
        super(mainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        # Setting a default theme (light) (TEMPORARY)
        global stream, app
        stream.open(QIODevice.ReadOnly)
        app.setStyleSheet(QTextStream(stream).readAll())
        
        # Create a settings window instance on startup
        self.Settings = settingWindow(self)
        self.settingsOpenedBefore = False

        """""
        Calender
        """""
        # self.calendarWidget.setLocale(QLocale(QLocale.Arabic, QLocale.Egypt))
        self.calendarWidget.setFirstDayOfWeek(Qt.Saturday)

        """""
        Icons
        """""
        self.pushButton_sort1.setIcon(QIcon('App/sort.png'))
        self.pushButton_sort1.setIconSize(QSize(24, 24))
        self.setWindowIcon(QIcon(appIcon))
        # app.setWindowIcon(QIcon(appIcon))
        

        """""
        Initial Function Calls
        """""
        self.setWindowTitle(appName)
        self.Handle_searchBar()

        # Set fixed size for buttons and comboboxes
        self.iterate_buttons(self)
        self.iterate_combobox(self)
        
        # Comment this for original Tabs Layout
        self.setTabsLabelsHorizontal()

        """""
        Connecting signals (buttons, etc) to slots (functions)
        """""
        #Handles adding new tasks
        self.pushButton_addTask.clicked.connect(self.Handle_add_window) # Upon clicking the button "Add" which its object name is pushButton_addTask, it excutes the function "add_task_widget"
        #When the search bar button is clicked, it goes to the function "Handle_searchBar"
        self.pushButton_searchTask.clicked.connect(self.Handle_searchBar)
        self.actionPreferences.triggered.connect(self.Handle_settings)
        # Handle ComboBox changes
        self.comboBox_techniques.currentTextChanged.connect(self.update_study_textbox)

        """""
        Initialize Variables
        """""

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

        """""
        Initialize App System Tray
        """""
        # We create a new TrayIcon (which is more than an icon), create a new context menu and add it to it
        self.trayIcon = QSystemTrayIcon(QIcon(appIcon), self)
        self.trayIcon.setToolTip(appName)
        self.trayMenu = QMenu()
        self.trayRestoreApp = QAction("Restore", self)
        self.trayQuitApp = QAction("Quit", self)
        self.trayRestoreApp.triggered.connect(self.restoreApp)
        self.trayQuitApp.triggered.connect(self.quitApp)

        self.trayMenu.addAction(self.trayRestoreApp)
        self.trayMenu.addAction(self.trayQuitApp)

        self.trayIcon.setContextMenu(self.trayMenu)
        self.trayIcon.activated.connect(self.trayIconClicked)

        self.trayIcon.show()
        
    # App Tray #
    def restoreApp(self):
        self.show()
        self.activateWindow()

    def quitApp(self):
        self.trayIcon.hide()
        QApplication.quit()

    def trayIconClicked(self, event):
        if (event == QSystemTrayIcon.DoubleClick):
            self.restoreApp()

    # Override the closeEvent so when the user closes the app it gets minimized instead
    def closeEvent(self, event):
        event.ignore()
        self.hide()
    ############
        
    # General Functions #
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
    def setTabsLabelsHorizontal(self):
        self.tabWidget_mainTabs.setTabPosition(QTabWidget.West)  # Set tabs to West first (text will be rotated so the following fixes)
        for i in range(self.tabWidget_mainTabs.count()):
            label = QLabel(self.tabWidget_mainTabs.tabText(i)) 
            label.setAlignment(Qt.AlignCenter)
            
            self.tabWidget_mainTabs.tabBar().setTabText(i, "")  # Remove the default tab text
            self.tabWidget_mainTabs.tabBar().setTabButton(i, QTabBar.LeftSide, label)  # Add custom text with correct orientation

    
    ##################### 
            
    # Study Tech Tab #      
    def update_study_textbox(self, text):
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

            # Connect button to start_study_countdown function
            self.pushButton_study.clicked.connect(lambda: self.start_study_countdown(study_time_input.value(), break_time_input.value()))

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

    def start_study_countdown(self, study_time, break_time):
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
    ##################
        
    # Tasks Tab #
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
    ##############
        
    # Settings Window #
    def Handle_settings(self):
        self.Settings.show()
        if (not self.settingsOpenedBefore):
            refresh()
            self.settingsOpenedBefore = True
        self.iterate_combobox(self)
    ###################
        
class addWindow(QDialog, ADD_TASK_CLASS):
    #Constructor
    def __init__(self, parent=None):
        super(addWindow, self).__init__(parent)
        QDialog.__init__(self)
        self.setupUi(self)
        #The parent is the main window, SO IT'S IMPORTANT TO: pass self when initiating addWindow -> addWindow(self)
        self.mainWindow = parent

        """""
        Icons
        """""
        self.setWindowIcon(QIcon(addIcon))

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

        """""
        Icons
        """""
        self.setWindowIcon(QIcon(settingsIcon))

        # Connecting signals to slots
        self.ThemeComboBox.currentTextChanged.connect(self.change_theme)
        self.FontComboBox.currentFontChanged.connect(self.change_font)

        global stream,app
        
    
    def change_theme(self, text):
        """
        Change the theme based on the selected text from ThemeComboBox.
        """
        global stream, app

        # Close the current theme file if open
        if stream.isOpen():
            stream.close()

        # Select the appropriate theme file
        if text == "Light theme":
            stream = QFile('App/LightMode.qss')
            stream.open(QIODevice.ReadOnly)
            app.setStyleSheet(QTextStream(stream).readAll())
        elif text == "Dark theme":
            stream = QFile('App/DarkMode.qss')
            stream.open(QIODevice.ReadOnly)
            app.setStyleSheet(QTextStream(stream).readAll())
        else:
            print(f"Unknown theme selected: {text}")
            return

    def change_font(self, font):
        global app, stream
        QApplication.setFont(font)
        refresh()
        
        
        
        

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