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

# Import UI files
FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), mainWindowFileName))
TASK_WIDGET_CLASS, _ = loadUiType(path.join(path.dirname(__file__), taskWidgetFileName))
ADD_TASK_CLASS, _ = loadUiType(path.join(path.dirname(__file__), addTaskWindowFileName))

#When you start a new design on Qt designer, you are promted many chocies, the important 2 are "Main Window" 
#and "Widget", and based on that is the first argument, the second argument is this "FROM_CLASS" that loads file path

class mainApp(QMainWindow, FORM_CLASS):
    #Constructor
    def __init__(self, parent=None):
        super(mainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        # self.setWindowIcon(QIcon('Task-Management-App\App\App_icon.png'))
        self.setupUi(self)
        

        # Set up the scroll area
        self.scrollAreaContent = QWidget()  # Create a new QWidget to hold the layout
        self.scrollAreaLayout = QVBoxLayout()  # Create a vertical layout
        self.scrollAreaContent.setLayout(self.scrollAreaLayout)  # Set the layout to the content widget
        self.scrollArea_tasks.setWidget(self.scrollAreaContent)  # Set the content widget to the scroll area

        #Function calls
        self.Handle_UI()
        self.Handle_searchBar()
        
        #Connecting signals (buttons, etc) to slots (functions)
            #Handles adding new tasks
        self.pushButton_addTask.clicked.connect(self.Handle_add_window) # Upon clicking the button "Add" which its object name is pushButton_addTask, it excutes the function "add_task_widget"
            #When the search bar button is clicked, it goes to the function "Handle_searchBar"
        self.pushButton_searchTask.clicked.connect(self.Handle_searchBar) 

        #Variables
        self.searchBarText = ""
        
        #ScrollArea Task Widgets
        self.addTaskList = []
        self.addTask = None
        self.tasksGroupBox = None
        self.tasksForm  = None
        # self.taskList = dict()

        #Add Window
        self.addWin = None


    def Handle_UI(self):
        self.setWindowTitle("Taskyyy")

    #Prints what's in the search bar, the function is called when the button is pressed
    def Handle_searchBar(self):
        self.searchBarText = self.plainTextEdit_searchTask.toPlainText()
        print(self.searchBarText)

    def Handle_add_window(self):
        if self.addWin is None:
            self.addWin = addWindow(self)

        self.addWin.show()


    def add_task_widget(self):

        self.addTask = addTask(self)
        if (self.tasksGroupBox == None):
            self.tasksGroupBox = QGroupBox('Tasks and Events')
        if(self.tasksForm == None):
            self.tasksForm= QFormLayout()
        self.tasksGroupBox.setLayout(self.tasksForm)
        
        
        self.addTaskList.append(addTask(self))

        for task in self.addTaskList:
            self.tasksForm.addRow(task)

       
        self.scrollArea_tasks.setWidget(self.tasksGroupBox)
        self.scrollArea_tasks.setWidgetResizable(True)

class addWindow(QDialog, ADD_TASK_CLASS):
    #Constructor
    def __init__(self, parent=None):
        super(addWindow, self).__init__(parent)
        QDialog.__init__(self)
        self.setupUi(self)

        #The parent is the main window, SO IT'S IMPORTANT TO: pass self when initiating addWindow -> addWindow(self)
        self.mainWindow = parent

        #Connecting signals
        self.EventDialogButtonBox.accepted.connect(self.Handle_ok_clicked)
        self.EventDialogButtonBox.rejected.connect(self.Handle_cancel_clicked)

        self.TaskDialogButtonBox.accepted.connect(self.Handle_ok_clicked)
        self.TaskDialogButtonBox.rejected.connect(self.Handle_cancel_clicked)

    def Handle_ok_clicked(self):
        self.mainWindow.add_task_widget()
        self.close()
    
    def Handle_cancel_clicked(self):
        self.close()

        
     
        

class addTask(QWidget, TASK_WIDGET_CLASS):
    #Constructor
    def __init__(self, parent=None):
        super(addTask, self).__init__(parent)
        QWidget.__init__(self)
        self.setupUi(self)

       

def main():
    app = QApplication(sys.argv)
    window = mainApp() #An instance of the class mainApp
    window.show()
    app.exec_() #Infinite loop

#Where the program starts
if __name__ == '__main__':
    main()
