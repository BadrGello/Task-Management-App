from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import sys
from os import path, makedirs
from datetime import datetime, timedelta
import calendar
import json
import time
from PyQt5.QtChart import *
import traceback, pdb

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

# Templates, if you want to copy do task = taskTemplate.copy()
taskTemplate = {
    "type": "",
    "id": "",
    "title": "",
    "desc": "", # Description
    "date": "",
    "repeat": "",

    "priority": 3, # 3 low, 2 med, 1 high
    "tags": list(),
    "steps": list(),
    "complete": False,
}

eventTemplate = {
    "type": "",
    "id": "",
    "title": "",
    "desc": "", # Description
    "date": "",
    "repeat": "",

}

# Should have 1 instance / copy only
settingsOptionsTemplate = {
    "highPrioritise": True,
    "confirmDelete": True,
    "deleteCompleted": False,

    "theme": "Light theme", #"Dark theme"
    "font": "MS Shell Dlg 2",

    "dueTodayNotif": True,
    "dueTodayNotifTime": "04:00",

    "reminderTime": 2,
    "taskReminder": True,
    "eventReminder": True,
    "studyReminder": True,
}


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
    #taskWidgetsList=[]
    # Constructor
    def __init__(self, parent=None):
        super(mainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        
        """""
        Initialize Variables
        """""
        self.taskTimers = []
        self.reminderTimers = []
        self.player = QMediaPlayer()
        self.appPlayer = QMediaPlayer()
        self.searchBarText = ""
        self.timer = None
        
        # Add Window
        self.addWin = None

        self.events=[]


        #Progress Tab
        self.completion_bar_month = QProgressBar()
        self.completion_bar_week = QProgressBar()
        self.doneNum_month = QLCDNumber()
        self.leftNum_month = QLCDNumber()
        self.doneNum_week = QLCDNumber()
        self.leftNum_week = QLCDNumber()
        self.chart_week = QWidget()
        self.chart_month = QWidget()

        # ScrollArea Task Widgets
        # self.taskWidgetsList = [] # Widgets themselves are stored here, we iterate over them to display them

        self.tasksList = [] # Tasks dict() are stroed here [task1, task2] where task1 is same form as taskTemplate
        self.tasksForSearch = []

        self.tasksLayout = None
        self.tasksGroupBox = None

        self.initialise_tasks_layout()        

        refresh()
        
        #state of the study in techniques
        self.state = self.findChild(QTextBrowser, "state")
        self.state.setText("Studying")
        self.current_mode = "study"
        self.stop_study.setEnabled(False)
        self.reset_study.setEnabled(False)

        """""
        Calender
        """""
        # self.calendarWidget.setLocale(QLocale(QLocale.Arabic, QLocale.Egypt))
        self.calendarWidget.setFirstDayOfWeek(Qt.Saturday)

        """""
        Icons
        """""
        self.pushButton_sortType.setIcon(QIcon('App/sort.png'))
        self.pushButton_sortType.setIconSize(QSize(24, 24))
        self.setWindowIcon(QIcon(appIcon))
        # app.setWindowIcon(QIcon(appIcon))
        

        """""
        Initial Function Calls
        """""
        self.setWindowTitle(appName)
        # self.Handle_searchBar()

        # Set fixed size for buttons and comboboxes
        # self.iterate_buttons(self)
        # self.iterate_combobox(self)
        
        # Comment this for original Tabs Layout
        self.setTabsLabelsHorizontal()

        """""
        Connecting signals (buttons, etc) to slots (functions)
        """""
        #Handles adding new tasks
        self.pushButton_addTask.clicked.connect(self.Handle_add_window) # Upon clicking the button "Add" which its object name is pushButton_addTask, it excutes the function "add_task_widget"
        #When the search bar button is clicked, it goes to the function "Handle_searchBar"
        # self.pushButton_searchTask.clicked.connect(self.Handle_searchBar)
        #When the sort button is clicked
        self.pushButton_sortType.clicked.connect(self.Handle_sort)
        #change the order of sorting
        self.pushButton_sortOrder.clicked.connect(self.Change_Sort_Order)
        
        self.actionPreferences.triggered.connect(self.Handle_settings)
        self.actionQuit.triggered.connect(self.quitApp)
        
        # Handle ComboBox changes
        self.comboBox_techniques.currentTextChanged.connect(self.update_study_textbox)

        self.plainTextEdit_searchTask.textChanged.connect(self.Handle_searchBar)

        
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


        """""
        Save and Load Data
        """""
        self.db_folder = "App/Data"
        if not path.exists(self.db_folder):
            makedirs(self.db_folder)

        self.settingsOptions = None
        self.loadApp()


        # Create a settings window instance on startup and a settingsOptions dict()
        self.Settings = settingWindow(self, self.settingsOptions)

        # This fixes a bug caused by loading tasks upon loading

        self.appTimer=QTimer(self)
        self.appTimer.timeout.connect(self.appTimer_event)
        self.timer_interval = 3600000  # 1 hour in milliseconds
        self.menuBar().raise_()
        self.appTimer_event()
        self.appTimer.start(self.timer_interval)
        

        
    def initialise_tasks_layout(self):
        self.tasksLayout = QVBoxLayout()

        # Option 1: No GroupBox
        # self.scrollArea_tasks_content.setLayout(self.tasksLayout)
        
        # Option 2: GroupBox
        self.tasksGroupBox = QGroupBox('Tasks')
        self.tasksGroupBox.setLayout(self.tasksLayout)
        self.scrollArea_tasks.setWidget(self.tasksGroupBox)
        self.scrollArea_tasks.setWidgetResizable(True)
        
    # App Tray #
    def alarmLoop(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.appPlayer.play()
        
    def reminderTimer_event(self,Task):
        self.appPlayer.setMedia(QMediaContent(QUrl.fromLocalFile("App\Audio\Study alarm.wav")))
        self.appPlayer.setVolume(100)
        self.appPlayer.mediaStatusChanged.connect(self.alarmLoop)
        self.appPlayer.play()
        dialog = QDialog(self)
        dialog.setWindowTitle("Reminder")
        dialog.setWindowFlag(Qt.FramelessWindowHint)  
        dialog.resize(400, 300)

        label = QLabel('This is your reminder for '+Task.task["title"], dialog)
        label.setAlignment(Qt.AlignCenter)
        
        dismiss_button = QPushButton("Dismiss", dialog)
        dismiss_button.clicked.connect(self.stopAlarm)
        dismiss_button.clicked.connect(dialog.accept)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(dismiss_button)

        dialog.setLayout(layout)

        dialog.show()
        dialog.raise_()  
        dialog.activateWindow()

    def stopAlarm(self):
        self.appPlayer.stop()

    def taskTimer_event(self,Task):
        Task.task["priority"] =0
        Task.update_task_info()

    def appTimer_event(self):
        for timer in self.taskTimers :
            timer.stop()
        for timer in self.reminderTimers :
            timer.stop()    
        self.taskTimers = []
        self.reminderTimers = []
        current_time = datetime.now()
        current_minutes = current_time.minute
        current_seconds = current_time.second

        # Calculate the remaining time until the next hour
        self.timer_interval = (60 - current_minutes) * 60 * 1000 - current_seconds * 1000
        # for task_ in self.taskWidgetsList:
        for i in range(self.tasksLayout.count()):
            item = self.tasksLayout.itemAt(i)  # Get the item at index `i`
            task_ = item.widget()  # Get the widget from the item
            if task_:  # Ensure it's a valid widget
                
                if not task_.task["complete"]:
                    target_time = datetime.strptime(task_.task["date"], "%Y-%m-%d %H:%M:%S")
                    remainTime =target_time-current_time
                    if remainTime.days==0 and self.settingsOptions["highPrioritise"]:
                        task_.task["priority"] = 1
                    if remainTime.days==0 and (remainTime.seconds//3600) <= 1 and (remainTime.seconds//3600) >= 0 :
                        realRemainTime = remainTime.seconds -remainTime.seconds %60
                        print(remainTime.days )
                        taskTimer=QTimer(self)
                        taskTimer.setSingleShot(True)
                        taskTimer.timeout.connect(lambda: self.taskTimer_event(task_))
                        taskTimer.start(realRemainTime*1000)
                        self.taskTimers.append(taskTimer)
                    elif remainTime.days<0 or (remainTime.seconds//3600) < 0:
                        print(task_.task["title"],remainTime.seconds//3600)
                        self.taskTimer_event(task_)
                    if self.settingsOptions["taskReminder"] and remainTime.days==0 and (remainTime.seconds//3600 - self.settingsOptions["reminderTime"]) <= 1 and (remainTime.seconds//3600 - self.settingsOptions["reminderTime"])>=0:
                        reminderTimer=QTimer(self)
                        reminderTimer.setSingleShot(True)
                        reminderTimer.timeout.connect(lambda: self.reminderTimer_event(task_))
                        reminderTimer.start(realRemainTime*1000-self.settingsOptions["reminderTime"]*3600*1000)
                        self.reminderTimers.append(reminderTimer)
                
        

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

    # For updating the tasksList (either edit an existing task or add new task)
    def update_tasksList(self, task):

        newTask = True

        # If task is present, just update it
        for i in range(len(self.tasksList)):
            if (self.tasksList[i]["id"] == task["id"]):
                newTask = False
                self.tasksList[i] = task
                break

        # If it's a new task, append it
        if (newTask):
            self.tasksList.append(task)

        # print(self.tasksList)
    

    def update_settings(self, settingsOptions):
        self.settingsOptions = settingsOptions
        self.saveApp()

    #####################

    # Save and Load #

    def saveApp(self):
        # Path to the JSON file
        file_path = path.join(self.db_folder, "data.json")
        
        # Currently saves tasksList only
        data = {
            "tasks": self.tasksList,
            "settings": self.settingsOptions,
        }
        
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        # print(data)
        print("Data saved to data.json")

        #For progress bar
        self.update_progress()

    def loadApp(self):
        # Path to the JSON file
        file_path = path.join(self.db_folder, "data.json")
        
        # Load the data from the JSON file if it exists
        if path.exists(file_path):
            with open(file_path, "r") as json_file:
                data = json.load(json_file)

                self.tasksList = data.get("tasks", [])
                self.settingsOptions = data.get("settings", None)
            
            # print(data)
            print("Data loaded from tasks_data.json")
        
        else:
            print("No data found to load.")

        # Add task widgets with the data loaded from JSON file
        for task in self.tasksList:
            self.add_task_widget(task)

        #For progress bar
        self.update_progress()

    #################

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
            try:
                self.pushButton_study.clicked.disconnect()
            except TypeError:
                pass

            try:
                self.stop_study.clicked.disconnect()
            except TypeError:
                pass

            try:
                self.reset_study.clicked.disconnect()
            except TypeError:
                pass
            self.pushButton_study.clicked.connect(lambda: self.start_study_countdown(study_time_input.value(), break_time_input.value()))
            self.stop_study.clicked.connect(self.toggle_study)
            self.reset_study.clicked.connect(self.clear_study)

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
            match text:
                case "Pomodoro Technique":
                    try:
                        self.pushButton_study.clicked.disconnect()
                    except TypeError:
                        pass

                    try:
                        self.stop_study.clicked.disconnect()
                    except TypeError:
                        pass

                    try:
                        self.reset_study.clicked.disconnect()
                    except TypeError:
                        pass
                    self.pushButton_study.clicked.connect(lambda: self.start_study_countdown(25, 5))
                    self.stop_study.clicked.connect(self.toggle_study)
                    self.reset_study.clicked.connect(self.clear_study)
                case "52-17 Technique":
                    try:
                        self.pushButton_study.clicked.disconnect()
                    except TypeError:
                        pass

                    try:
                        self.stop_study.clicked.disconnect()
                    except TypeError:
                        pass

                    try:
                        self.reset_study.clicked.disconnect()
                    except TypeError:
                        pass
                    self.pushButton_study.clicked.connect(lambda: self.start_study_countdown(52, 17))
                    self.stop_study.clicked.connect(self.toggle_study)
                    self.reset_study.clicked.connect(self.clear_study)
                case "The 45-15 Method":
                    try:
                        self.pushButton_study.clicked.disconnect()
                    except TypeError:
                        pass

                    try:
                        self.stop_study.clicked.disconnect()
                    except TypeError:
                        pass

                    try:
                        self.reset_study.clicked.disconnect()
                    except TypeError:
                        pass
                    self.pushButton_study.clicked.connect(lambda: self.start_study_countdown(45, 15))
                    self.stop_study.clicked.connect(self.toggle_study)
                    self.reset_study.clicked.connect(self.clear_study)
            
            self.TextBrowser_display.setText(formatted_text)

    def start_study_countdown(self, study_time, break_time):
        # Convert minutes to seconds for the timer
        study_total_seconds = study_time * 60
        break_total_seconds = break_time * 60
        study = study_total_seconds
        rest = break_total_seconds

        self.study_bar.setValue(0)

        self.stop_study.setEnabled(True)
        self.reset_study.setEnabled(True)
        self.pushButton_study.setEnabled(False)

        def update_timer():
            nonlocal study, rest
            if self.current_mode == "study" and study > 0:
                minutes, seconds = divmod(study, 60)
                self.time_label.setText(f"{minutes:02}:{seconds:02}")
                self.study_bar.setValue(int((study_total_seconds - study) / study_total_seconds * 100))
                study -= 1
            elif self.current_mode == "break" and rest > 0:
                minutes, seconds = divmod(rest, 60)
                self.time_label.setText(f"{minutes:02}:{seconds:02}")
                self.study_bar.setValue(int((break_total_seconds - rest) / break_total_seconds * 100))
                rest -= 1
            else:
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile("App\Audio\Study alarm.wav")))
                self.player.setVolume(100)
                self.player.play()
                self.time_label.setText(f"{0:02}:{0:02}")
                if self.current_mode == "study":
                    rest = break_total_seconds
                    self.current_mode = "break"
                    self.state.setText("Break")
                else:
                    study = study_total_seconds
                    self.current_mode = "study"
                    self.state.setText("Studying")

        # Create a QTimer to update the countdown every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(update_timer)
        self.timer.start(1000)
        self.is_paused = False
        
    def toggle_study(self):
        if self.is_paused:
            self.timer.start(1000)
            self.stop_study.setText("Pause")
        else:
            self.timer.stop()
            self.stop_study.setText("Resume")
        self.is_paused = not self.is_paused

    def clear_study(self):
        self.timer.stop()
        self.is_paused = False
        self.current_mode = "study"
        self.study_bar.setValue(0)
        self.time_label.setText("00:00")
        self.state.setText("Studying")
        self.pushButton_study.setEnabled(True)
        self.stop_study.setEnabled(False)
        self.reset_study.setEnabled(False)
        self.stop_study.setText("Pause")
        self.study_time_input = None
        self.break_time_input = None
    ##################
        
    # Tasks Tab #

    def Handle_add_window(self):
        # if self.addWin is None:
        #     self.addWin = addWindow(self)
        self.addWin = addWindow(self)
        self.addWin.show()

    def edit_task_widget(self, task):
        # for widget in self.taskWidgetsList:
        for i in range(self.tasksLayout.count()):
            item = self.tasksLayout.itemAt(i)  # Get the item at index `i`
            widget = item.widget()  # Get the widget from the item
            if widget:  # Ensure it's a valid widget

                if (widget.task["id"] == task["id"]):
                    # Update the widget with the new task data
                    print("Edit began", task)
                    widget.task = task
                    widget.update_task_info()
                    break
                else:
                    # If no matching widget found, add a new one (shouldn't happen)
                    print("ERROR, Didn't find the task to be edited")
                    self.add_task_widget(task)

        self.appTimer_event() 

        #For progress bar
        self.update_progress()
   
    def delete_task(self, taskWidget):

        settingChoice = self.settingsOptions["confirmDelete"] # Confirm before deletion

        if (settingChoice):
            reply = QMessageBox.question(self, 'Confirm Deletion', 'Are you sure you want to delete this task?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
            if reply != QMessageBox.Yes:
                return
            else:
                pass
 
        
        # Delete it from tasksList
        for i in range(len(self.tasksList)):
            if (self.tasksList[i]["id"] == taskWidget.task["id"]):
                del self.tasksList[i]
                break

        self.tasksLayout.removeWidget(taskWidget)
        taskWidget.setParent(None)
        self.tasksLayout.update()

        self.saveApp()
        
    def add_task_widget(self, task):

        self.plainTextEdit_searchTask.clear()

        newTaskWidget = addTask(parent=self, delete_callback=lambda: self.delete_task(newTaskWidget))
        newTaskWidget.add_new_task_info(task)
        self.update_tasksList(task)

        self.tasksLayout.addWidget(newTaskWidget)

        self.appTimer_event()

        #For progress bar
        self.update_progress()

    #Search
    def Handle_searchBar(self):

        self.searchBarText = self.plainTextEdit_searchTask.toPlainText().strip()

        # If search field is empty, show all widgets
        if not self.searchBarText:
            for i in range(self.tasksLayout.count()):
                item = self.tasksLayout.itemAt(i)
                widget = item.widget()
                if widget:
                    widget.setVisible(True)  # Show all widgets
            return

        # Filter and display tasks based on the search bar text
        for i in range(self.tasksLayout.count()):
            item = self.tasksLayout.itemAt(i)
            widget = item.widget()
            if widget:
                if (self.searchBarText in widget.task["title"] or 
                    self.isSearchTextInTags(widget.task["tags"], self.searchBarText)):
                    widget.setVisible(True)  # Show matching widgets
                else:
                    widget.setVisible(False)  # Hide non-matching widgets

    def isSearchTextInTags(self,tags,searchText):
        for tag in tags:
            if searchText in tag:
                return True
        return False
        
    # sort #
    def Handle_sort (self):
        #determine the sort type from the combo box
        if self.comboBox_sortType.currentText()=="Sort by Title":
            sortType = "title"
        elif self.comboBox_sortType.currentText()=="Sort by Due Date":
            sortType = "date"
        else:
            sortType = "priority"
        # determine the order #
        if self.pushButton_sortOrder.text() == "Ascendingly": 
            order = False
        else:
            order = True         
        
        tempSortList = []

        for i in range(self.tasksLayout.count()):
            item = self.tasksLayout.itemAt(i)  # Get the item at index `i`
            widget = item.widget()  # Get the widget from the item
            if widget:  # Ensure it's a valid widget
                tempSortList.append(widget)
        
        # Remove all widgets from the layout without deleting them
        while self.tasksLayout.count():
            child = self.tasksLayout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)  # Detach widget from the layout but do not delete it
        #sort 
        tempSortList.sort(key = lambda x: x.task[sortType] , reverse = order)
        #Re add tasks
        for widget in tempSortList:
            self.tasksLayout.addWidget(widget)  # Re-add the widget to the layout
    
    def Change_Sort_Order(self):
        if self.pushButton_sortOrder.text() == "Ascendingly":
            self.pushButton_sortOrder.setText("Descendingly")
        else:
            self.pushButton_sortOrder.setText("Ascendingly")    

    # Settings Window #
    def Handle_settings(self):
        self.Settings.show()
        refresh()
    ###################

    # Progress Tab #

    def update_progress(self):
        self.progressMonthly()
        self.progressWeekly()
        self.chartsWeekly()
        self.chartsMonthly()


    def chartsMonthly(self):

        #Calculate current month and year
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year

        #save current month tasks
        current_month_tasks = [
            task for task in self.tasksList
            if datetime.strptime(task["date"], "%Y-%m-%d %H:%M:%S").month == current_month and
            datetime.strptime(task["date"], "%Y-%m-%d %H:%M:%S").year == current_year
        ]

        #Count completed tasks for each week
        weeks_in_month = [[] for _ in range(5)]
        for task in current_month_tasks:
            task_date = datetime.strptime(task["date"], "%Y-%m-%d %H:%M:%S")
            week_of_month = (task_date.day - 1) // 7 
            if task["complete"]:
                weeks_in_month[week_of_month].append(task)
        
        completed_tasks_per_week = [len(week) for week in weeks_in_month]

        #Chart
        self.weeks_of_month = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]
        self.monthly_x_values = list(range(len(self.weeks_of_month)))  #Days of the month
        self.monthly_y_values = completed_tasks_per_week
        monthly_placeholder = self.findChild(QWidget, "chart_month")
        chart = self.create_chart(self.monthly_x_values, self.monthly_y_values, "Previous Month Tasks Progress", self.weeks_of_month)
        self.add_chart_to_placeholder(monthly_placeholder, chart)

    def progressMonthly(self):

        """
        Updates the progress for tasks completed in the current month.
        """

        self.completion_bar_month.setValue(0)


        #Calculate current month and year
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year

        #save current month tasks
        current_month_tasks = [
            task for task in self.tasksList
            if datetime.strptime(task["date"], "%Y-%m-%d %H:%M:%S").month == current_month and
            datetime.strptime(task["date"], "%Y-%m-%d %H:%M:%S").year == current_year
        ]

       

        #Calculate number of current month tasks
        total_tasks_this_month = len(current_month_tasks)
        completed_tasks_this_month = sum(1 for task in current_month_tasks if task["complete"])

        if total_tasks_this_month > 0:
            completion_percentage = completed_tasks_this_month / total_tasks_this_month * 100
        else:
            completion_percentage = 0

            
        #Progress bar and LCDs    
        self.completion_bar_month.setValue(int(completion_percentage))
        self.doneNum_month.display(completed_tasks_this_month)
        self.leftNum_month.display(total_tasks_this_month - completed_tasks_this_month)
             

    def chartsWeekly(self):

        current_date = datetime.now()
        start_of_week = current_date - timedelta(days=(current_date.weekday() + 2) % 7)  #Start of week: Saterday

        #save current week tasks
        current_week_tasks = [
            task for task in self.tasksList
            if start_of_week <= datetime.strptime(task["date"], "%Y-%m-%d %H:%M:%S") <= current_date
        ]
        #Count completed tasks for each day
        completed_tasks_per_day = [0] * 7  
        for task in current_week_tasks:
            task_date = datetime.strptime(task["date"], "%Y-%m-%d %H:%M:%S")
            day_of_week = task_date.weekday()
            if task["complete"]:
                completed_tasks_per_day[(day_of_week + 2) % 7] += 1

        #Chart
        label = ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"]
        self.weekly_x_values = list(range(7))
        self.weekly_y_values = completed_tasks_per_day
        weekly_placeholder = self.findChild(QWidget, "chart_week")
        chart = self.create_chart(self.weekly_x_values, self.weekly_y_values, "My Week Tasks Progress", label)
        self.add_chart_to_placeholder(weekly_placeholder, chart)


    def progressWeekly(self):
        """
        Updates the progress for tasks completed in the current week.
        """
        self.completion_bar_week.setValue(0)

        current_date = datetime.now()
        start_of_week = current_date - timedelta(days=(current_date.weekday() + 2) % 7)  #Start of week: Saterday

        #save current week tasks
        current_week_tasks = [
            task for task in self.tasksList
            if start_of_week <= datetime.strptime(task["date"], "%Y-%m-%d %H:%M:%S") <= current_date
        ]

        

        #Calculate number of current week tasks
        total_tasks_this_week = len(current_week_tasks)
        completed_tasks_this_week = sum(1 for task in current_week_tasks if task["complete"])

        if total_tasks_this_week > 0:
            completion_percentage = completed_tasks_this_week / total_tasks_this_week * 100
        else:
            completion_percentage = 0

        #Progress bar and LCDs
        self.completion_bar_week.setValue(int(completion_percentage))
        self.doneNum_week.display(completed_tasks_this_week)
        self.leftNum_week.display(total_tasks_this_week - completed_tasks_this_week)

        


    #Generating Charts
    def create_chart(self, x, y, title, labels):
        series = QLineSeries()
        
        #Append data points to the series
        for data_x, data_y in zip(x, y):
            series.append(data_x, data_y)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(title)
        chart.createDefaultAxes()

        
        axis_x = QCategoryAxis()
        axis_x.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)
        
        #Labels
        for idx, label in enumerate(labels):
            axis_x.append(label, float(idx))

        chart.setAxisX(axis_x, series)

        #Set Y-axis range
        max_value = max(y)
        axis_y = chart.axes(Qt.Vertical)[0]
        axis_y.setRange(0, max_value + 1)
        axis_y.applyNiceNumbers()

        axis_x.setGridLineVisible(False)
        axis_y.setGridLineVisible(True) 

        return chart
    
    def add_chart_to_placeholder(self, placeholder, chart):
        """
        Adds the chart to the specified placeholder.
        """
             
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

        #Set chart layout
        layout = QHBoxLayout()
        layout.addWidget(chart_view)
        chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        placeholder.setLayout(layout)
        chart_view.update()

        chart.setTitleFont(QFont("Arial", 8, QFont.Bold))
        chart.setTitleBrush(QBrush(Qt.black))
        chart.legend().setVisible(False)
    
    ##################
    
        
class addWindow(QDialog, ADD_TASK_CLASS):
    #Constructor
    def __init__(self, parent=None, editTask=None):
        super(addWindow, self).__init__(parent)
        QDialog.__init__(self)
        self.setupUi(self)
        #The parent is the main window, SO IT'S IMPORTANT TO: pass self when initiating addWindow -> addWindow(self)
        self.mainWindow = parent
        self.editTask = editTask

        """""
        Icons
        """""
        self.setWindowIcon(QIcon(addIcon))

        """""
        Signals
        """""

        #Connecting signals
        self.EventDialogButtonBox.accepted.connect(self.Handle_event_ok_clicked)
        self.EventDialogButtonBox.rejected.connect(self.Handle_cancel_clicked)
        self.TaskDialogButtonBox.accepted.connect(self.Handle_task_ok_clicked)
        self.TaskDialogButtonBox.rejected.connect(self.Handle_cancel_clicked)

        ##Tags List##
        self.AddTag.clicked.connect(self.add_tag)  # When pressing Enter after writing a step, it will add it to the list
        self.TaskTags.setContextMenuPolicy(Qt.CustomContextMenu)
        self.TaskTags.customContextMenuRequested.connect(self.show_context_menu) # Right click a tag and click delete to delete
        ##          ##


        """""
        Initialisations
        """""
        # Set the date of QDateTimeEdit to current time to be easier for user
        self.TaskDate.setDateTime(QDateTime.currentDateTime())

        """""
        Edit Mode
        """""
        if editTask:
            self.Handle_edit_mode()
            
                

    # Following functions for tags list
    def add_tag(self):
        
        tag = self.TaskTagInput.text()
        tag = tag.replace(" ", "")
        if (tag):
            item = QListWidgetItem(tag)
            self.TaskTags.addItem(item)
            self.TaskTagInput.clear()

    def show_context_menu(self, position):

        menu = QMenu()
        delete_step = menu.addAction("Delete Tag")
        action = menu.exec_(self.TaskTags.mapToGlobal(position))
        if (action == delete_step):
            selected_items = self.TaskTags.selectedItems() #Displays the context menu and returns the action selected by the user or none
            for item in selected_items:
                deleted_step = self.TaskTags.takeItem(self.TaskTags.row(item))

    def Handle_edit_mode(self):
        # Hide Event Tab
        self.AddTabs.removeTab(1)

        # Set window name
        self.setWindowTitle("Edit Task")

        # Set every field
        self.TaskTitleInput.setPlainText(self.editTask.get("title", ""))
        self.TaskDescInput.setPlainText(self.editTask.get("desc", ""))
        self.TaskDate.setDateTime(QDateTime.fromString(self.editTask.get("date", ""), "yyyy-MM-dd HH:mm:ss"))
        self.TaskRepeat.setCurrentText(self.editTask.get("repeat", ""))
        if (self.editTask["priority"] == 1): self.TaskPriorityValue.setCurrentText("High Priority")
        elif (self.editTask["priority"] == 2): self.TaskPriorityValue.setCurrentText("Moderate Priority")
        else: self.TaskPriorityValue.setCurrentText("Low Priority")
        for tag in self.editTask.get("tags", []):
            item = QListWidgetItem(tag)
            self.TaskTags.addItem(item)

    def Handle_task_ok_clicked(self):
        
        task = taskTemplate.copy()

        task_title = self.TaskTitleInput.toPlainText()
        task_description = self.TaskDescInput.toPlainText()
        task_due_date = self.TaskDate.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        task_repeat = self.TaskRepeat.currentText()
        task_priority = self.TaskPriorityValue.currentText()
        task_tags = [self.TaskTags.item(i).text() for i in range(self.TaskTags.count())]

        task["type"] = "task"
        task["id"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Unique id as current time
        task["title"] = task_title
        task["desc"] = task_description
        task["date"] = task_due_date
        task["repeat"] = task_repeat
        
        if (task_priority == "High Priority"):
            task["priority"] = 1
        elif (task_priority == "Moderate Priority"):
            task["priority"] = 2
        elif (task_priority == "Low Priority"):
            task["priority"] = 3

        task["tags"] = task_tags
        
        # Edit existing task
        if self.editTask:
            task["id"] = self.editTask["id"]
            task["steps"] = self.editTask["steps"]
            task["priority"] = self.editTask["priority"]
            task["complete"] = self.editTask["complete"]
            self.mainWindow.edit_task_widget(task)

        # Add new task to list
        else:
            self.mainWindow.add_task_widget(task)
        self.close()

    def Handle_event_ok_clicked(self):
        event = eventTemplate.copy()

        event_title = self.EventTitleInput.toPlainText()
        event_description = self.EventDescInput.toPlainText()
        event_date = self.EventDate.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        event_repeat = self.EventRepeatValue.currentText()
        event["type"] = "event"
        event["id"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Unique id as current time
        event["title"] = event_title
        event["desc"] = event_description
        event["date"] = event_date
        event["repeat"] = event_repeat
        # self.events.append(event)
        

        #####################
        # Handle adding event
        # self.mainWindow.add_event(event)
        self.close()

    def Handle_cancel_clicked(self):
        self.close()


class settingWindow(QMainWindow, SETTING_CLASS):
    def __init__(self, parent=None, settingsOptions=None):
        super(settingWindow, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.mainWindow = parent
        self.settingsOptions = settingsOptions

        """""
        Icons
        """""
        self.setWindowIcon(QIcon(settingsIcon))

        """""
        Signals and Slots
        """""
        # Connecting signals to slots
        self.ThemeComboBox.currentTextChanged.connect(self.Handle_change_theme)
        self.FontComboBox.currentFontChanged.connect(self.Handle_change_font)

        self.HighPrioritise.toggled.connect(self.Handle_change_high_priority_incomplete_tasks)
        self.ConfirmDel.toggled.connect(self.Handle_change_confirm_before_delete)
        self.DelAfterComplete.toggled.connect(self.Handle_change_delete_after_complete)
        self.DueTodayNotif.toggled.connect(self.Handle_change_due_today_notification)
        self.SetDueTodayTime.timeChanged.connect(self.Handle_change_due_today_time)
        self.ReminderTime.valueChanged.connect(self.Handle_change_reminder_time)
        self.EnableTasksRem.toggled.connect(self.Handle_change_enable_task_reminder)
        self.EnableEventRem.toggled.connect(self.Handle_change_enable_event_reminder)
        self.EnableStdTechRem.toggled.connect(self.Handle_change_enable_stdtech_reminder)
        
        self.DefaultFontButton.clicked.connect(self.set_default_font)

        """""
        Set Options Upon Loading
        """""
        self.initialize_settings()
        
    def set_default_font(self):
        self.settingsOptions["font"] = "MS Shell Dlg 2"
        self.change_font()
        self.FontComboBox.setCurrentFont(QFont("MS Shell Dlg 2"))



    def initialize_settings(self):
        # Set initial values if settingsOptions is not None
        if self.settingsOptions:
            # Theme
            print("Initialise Settings ", self.settingsOptions)
            theme = self.settingsOptions.get("theme", "Light theme")
            if theme in ["Light theme", "Dark theme"]:
                self.ThemeComboBox.setCurrentText(theme)

            # Font
            font = self.settingsOptions.get("font", "")
            if font:
                self.FontComboBox.setCurrentFont(QFont(font))

            # Checkbox States
            self.HighPrioritise.setChecked(self.settingsOptions.get("highPrioritise", True))
            self.ConfirmDel.setChecked(self.settingsOptions.get("confirmDelete", True))
            self.DelAfterComplete.setChecked(self.settingsOptions.get("deleteCompleted", False))
            self.DueTodayNotif.setChecked(self.settingsOptions.get("dueTodayNotif", True))
            self.EnableTasksRem.setChecked(self.settingsOptions.get("taskReminder", True))
            self.EnableEventRem.setChecked(self.settingsOptions.get("eventReminder", True))
            self.EnableStdTechRem.setChecked(self.settingsOptions.get("studyReminder", True))

            # Reminder Time and Due Today Time
            self.ReminderTime.setValue(int(self.settingsOptions.get("reminderTime", 0)))
            self.SetDueTodayTime.setTime(QTime.fromString(self.settingsOptions["dueTodayNotifTime"], "HH:mm"))

            refresh()

        else:
            self.settingsOptions = settingsOptionsTemplate.copy()

    def Handle_change_high_priority_incomplete_tasks(self, checked):
        self.settingsOptions["highPrioritise"] = checked
        self.mainWindow.update_settings(self.settingsOptions)

    def Handle_change_confirm_before_delete(self, checked):
        self.settingsOptions["confirmDelete"] = checked
        self.mainWindow.update_settings(self.settingsOptions)

    def Handle_change_delete_after_complete(self, checked):
        self.settingsOptions["deleteCompleted"] = checked
        self.mainWindow.update_settings(self.settingsOptions)

    def Handle_change_due_today_notification(self, checked):
        self.settingsOptions["dueTodayNotif"] = checked
        self.mainWindow.update_settings(self.settingsOptions)

    def Handle_change_due_today_time(self, time):
        self.settingsOptions["dueTodayNotifTime"] = time.toString("HH:mm")
        self.mainWindow.update_settings(self.settingsOptions)

    def Handle_change_reminder_time(self, value):
        self.settingsOptions["reminderTime"] = value
        self.mainWindow.update_settings(self.settingsOptions)

    def Handle_change_enable_task_reminder(self, checked):
        self.settingsOptions["taskReminder"] = checked
        self.mainWindow.update_settings(self.settingsOptions)

    def Handle_change_enable_event_reminder(self, checked):
        self.settingsOptions["eventReminder"] = checked
        self.mainWindow.update_settings(self.settingsOptions)

    def Handle_change_enable_stdtech_reminder(self, checked):
        self.settingsOptions["studyReminder"] = checked
        self.mainWindow.update_settings(self.settingsOptions)
        
        
    def Handle_change_theme(self, text):
        self.settingsOptions["theme"] = text
        self.mainWindow.update_settings(self.settingsOptions)
        self.change_theme()

    def change_theme(self):
        """
        Change the theme based on the selected text from ThemeComboBox.
        """
        global stream, app

        # Close the current theme file if open
        if stream.isOpen():
            stream.close()

        # Select the appropriate theme file
        if self.settingsOptions["theme"] == "Light theme":
            stream = QFile('App/LightMode.qss')
            stream.open(QIODevice.ReadOnly)
            app.setStyleSheet(QTextStream(stream).readAll())
        elif self.settingsOptions["theme"] == "Dark theme":
            stream = QFile('App/DarkMode.qss')
            stream.open(QIODevice.ReadOnly)
            app.setStyleSheet(QTextStream(stream).readAll())
        else:
            #print(f"Unknown theme selected: {self.settingsOptions["theme"]}")
            return
    
    def Handle_change_font(self, font):
        self.settingsOptions["font"] = font.family()
        self.mainWindow.update_settings(self.settingsOptions)
        self.change_font()

    def change_font(self):
        QApplication.setFont(QFont(self.settingsOptions["font"], QApplication.font().pointSize()))
        refresh()
        

# This is the task widget
class addTask(QWidget, TASK_WIDGET_CLASS):
    #Constructor
    def __init__(self, delete_callback, parent=None):
        super(addTask, self).__init__(parent)
        QWidget.__init__(self)
        self.setupUi(self)
        self.mainWindow = parent
        self.edit_window = None
        # This "task" dictionary should hold all info, sould be always updated as this is what will be put in DB (JSON)
        self.task = dict()
        """""
        Signals and Slots
        """""
        # Delete and Edit Buttons
        # self.taskDeletePushButton.clicked.connect(self.Handle_delete_task)
        self.taskDeletePushButton.clicked.connect(delete_callback)
        self.taskEditPushButton.clicked.connect(self.Handle_edit_task)

        ##Steps List##
        self.stepInput.returnPressed.connect(self.add_step)  # When pressing Enter after writing a step, it will add it to the list
        self.stepsListWidget.itemDoubleClicked.connect(self.toggle_step_completion) # We can double click to mark as completed
        self.stepsListWidget.itemChanged.connect(self.on_item_checked)
        self.stepsListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.stepsListWidget.customContextMenuRequested.connect(self.show_context_menu) # Right click a step and click delete to delete
        ##          ##

        ##Complete Button##
        self.taskCompletetoolButton.setAccessibleDescription("Incompleted")
        self.taskCompletetoolButton.setCheckable(True)  # Button stays pressed when clicked
        self.taskCompletetoolButton.toggled.connect(self.toggle_task_completion)
        ##               ##

    #Following functions for steps list
    def add_step(self, step=None):
        
        # Add steps when creating a new step
        if (step is None):
            step_desc = self.stepInput.text()
        
            if (step_desc):
                item = QListWidgetItem(step_desc)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable) #Creates a checkbox related to the item (step)
                item.setCheckState(Qt.Unchecked)  #Default is unchecked
                self.stepsListWidget.addItem(item) #Add step
            
                # Add step info to self.task
                self.task["steps"].append({"desc": step_desc, "complete": False})
                self.mainWindow.saveApp()

                self.stepInput.clear()

        # Add steps in loading app phase
        else:
            item = QListWidgetItem(step["desc"])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable) #Creates a checkbox related to the item (step)
            if (step["complete"]):
                item.setCheckState(Qt.Checked)
            else :
                item.setCheckState(Qt.Unchecked)

            self.stepsListWidget.addItem(item) #Add step
        

    def toggle_step_completion(self, item):
        
        row = self.stepsListWidget.row(item)

        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
            self.task["steps"][row]["complete"] = False

        else:
            item.setCheckState(Qt.Checked)
            self.task["steps"][row]["complete"] = True
        
        self.mainWindow.saveApp()

    def on_item_checked(self, item):
        
        row = self.stepsListWidget.row(item)

        if item.checkState() == Qt.Checked:
            self.task["steps"][row]["complete"] = True

        else:
            self.task["steps"][row]["complete"] = False
 
        self.mainWindow.saveApp() 
        
    def show_context_menu(self, position):

        menu = QMenu()
        delete_step = menu.addAction("Delete Step")
        action = menu.exec_(self.stepsListWidget.mapToGlobal(position))
        if (action == delete_step):
            selected_items = self.stepsListWidget.selectedItems() #Displays the context menu and returns the action selected by the user or none
            for item in selected_items:
                
                row = self.stepsListWidget.row(item)
                self.task["steps"].pop(row)

                deleted_step = self.stepsListWidget.takeItem(self.stepsListWidget.row(item))

        self.mainWindow.saveApp()

    # When clicking on Incompleted/Completed button
    def toggle_task_completion(self):
        
        if(self.task["complete"]):
            # self.taskCompletetoolButton.setIcon(QIcon("path_to_icon.png")) # Can set an icon instead of text
            self.taskCompletetoolButton.setText("Incompleted")
            self.task["complete"] = False
            self.update_task_info() # To update the color
        else:
            self.taskCompletetoolButton.setText("Completed")
            self.task["complete"] = True
            self.update_task_info() # To update the color

        self.mainWindow.saveApp()

    # Should be called only when creating a new task
    def add_new_task_info(self, task):
        self.task = task
        self.update_task_info()

    def Handle_edit_task(self):

        self.edit_window = None
        self.edit_window = addWindow(self.mainWindow, self.task)

        self.edit_window.show()
        # edit_window.exec_()  # Show the dialog

    # Call when you updated self.task and want to update the task widget gui / send updated task to be saved
    def update_task_info(self):

        # Update task in tasksList
        self.mainWindow.update_tasksList(self.task)
        self.mainWindow.saveApp()

        # Update the title and description
        self.taskTitlePlainTextEdit.setPlainText(self.task["title"])
        self.taskDescPlainTextEdit.setPlainText(self.task["desc"])

        # Update the date
        date = QDateTime.fromString(self.task["date"], "yyyy-MM-dd hh:mm:ss")
        self.taskDateTimeEdit.setDateTime(date)
        
        # Update the priority line color
        if self.task["priority"] == 0: #late due date
            self.taskPriorityLine.setStyleSheet(" border: 6px solid black;")
        elif self.task["priority"] == 1: # High
            self.taskPriorityLine.setStyleSheet(" border: 6px solid red;")
        elif self.task["priority"] == 2: # Med
            self.taskPriorityLine.setStyleSheet(" border: 6px solid orange;")
        else: # Low
            self.taskPriorityLine.setStyleSheet(" border: 6px solid yellow;")
        
        # Update the task steps
        self.stepsListWidget.clear()
        for step in self.task["steps"]:
            self.add_step(step)
        
        # Update the "completed" status button text (Incompleted/Completed)
        if self.task["complete"]:
            self.taskCompletetoolButton.setText("Completed")
            self.taskPriorityLine.setStyleSheet(" border: 6px solid lime;")
        else:
            self.taskCompletetoolButton.setText("Incompleted")

def main():
    try:
        # pdb.set_trace()
        window = mainApp() #An instance of the class mainApp

        window.show()
        sys.exit(app.exec_())#Infinite loop
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()