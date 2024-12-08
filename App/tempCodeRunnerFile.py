
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

        """""
        Initialize Variables
        """""

        self.searchBarText = ""
        self.timer = None

        # Add Window
        self.addWin = None

        # ScrollArea Task Widgets
        self.taskWidgetsList = [] # Widgets themselves are stored here, we iterate over them to display them
        self.tempTaskWidgetsList =[]
        self.newTaskWidget = None
        self.tasksGroupBox = None
        self.tasksForm = None
        self.tasksList = [] # Tasks dict() are stroed here [task1, task2] where task1 is same form as taskTemplate
        self.tempTaskList = []

        super(mainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        # Setting a default theme (light) (TEMPORARY)
        # global stream, app
        # stream.open(QIODevice.ReadOnly)
        # app.setStyleSheet(QTextStream(stream).readAll())
        refresh()
        
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
        self.Handle_searchBar()

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
        self.pushButton_searchTask.clicked.connect(self.Handle_searchBar)
        self.actionPreferences.triggered.connect(self.Handle_settings)
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
    
    def delete_task(self, task):

        # Delete it from tasksList
        for i in range(len(self.tasksList)):
            if (self.tasksList[i]["id"] == task["id"]):
                del self.tasksList[i]
                break
        
        # Delete it from taskWidgetsList
        for widget in self.taskWidgetsList:
            if (widget.task["id"] == task["id"]): 
                self.tasksForm.removeRow(widget)
                self.taskWidgetsList.remove(widget)
                break

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

        print(data)
        print("Data saved to data.json")

    def loadApp(self):
        # Path to the JSON file
        file_path = path.join(self.db_folder, "data.json")
        
        # Load the data from the JSON file if it exists
        if path.exists(file_path):
            with open(file_path, "r") as json_file:
                data = json.load(json_file)

                self.tasksList = data.get("tasks", [])
                self.settingsOptions = data.get("settings", None)
            
            print(data)
            print("Data loaded from tasks_data.json")
        
        else:
            print("No data found to load.")

        # Add task widgets with the data loaded from JSON file
        for task in self.tasksList:
            self.add_task_widget(task)

    #################
