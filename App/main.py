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
    def __init__(self):
        super(mainApp, self).__init__()
        QMainWindow.__init__(self)
        # self.setWindowIcon(QIcon('Task-Management-App\App\App_icon.png'))
        self.setupUi(self)
        

        # Set up the scroll area
        self.scrollAreaContent = QWidget()  # Create a new QWidget to hold the layout
        self.scrollAreaLayout = QVBoxLayout()  # Create a vertical layout
        self.scrollAreaContent.setLayout(self.scrollAreaLayout)  # Set the layout to the content widget
        self.scrollArea_tasks.setWidget(self.scrollAreaContent)  # Set the content widget to the scroll area

        #Function calls
        self.Handle_pushButton_addTask()
        self.Handle_UI()
        self.Handle_searchBar()
        self.Handle_pushButton_searchTask()

        #Variables
        self.searchBarText = ""
        self.addWin = None #For the add task window
        self.taskList = dict()

    #Handles adding new tasks
    def Handle_pushButton_addTask(self):
        self.pushButton_addTask.clicked.connect(self.add_task_widget) # Upon clicking the button "Add" which its object name is pushButton_addTask, it excutes the function "add_task_widget"

    #When the search bar button is clicked, it goes to the function "Handle_searchBar"
    def Handle_pushButton_searchTask(self):
        self.pushButton_searchTask.clicked.connect(self.Handle_searchBar) 



    def Handle_UI(self):
        self.setWindowTitle("Taskyyy")

    #Prints what's in the search bar, the function is called when the button is pressed
    def Handle_searchBar(self):
        self.searchBarText = self.plainTextEdit_searchTask.toPlainText()
        print(self.searchBarText)


    def add_task_widget(self):

        if self.addWin is None:
            self.addWin = addWindow()
     
        self.addWin.show()









        # Create a new card (QGroupBox)
        # card = self.taskGroupBox
        # card = QGroupBox()
        # card.setTitle("Task Title")
        # # card.setStyleSheet("QGroupBox { background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 5px; padding: 10px; }")
        # card.setMinimumSize(250, 100)

        # task_widget = TASK_WIDGET_CLASS()

        # # Add content to the card
        # layout = QVBoxLayout()
        # label = QLabel("Task Description")
        # label.setFont(QFont("Arial", 10))
        # layout.addWidget(label)
        # card.setLayout(layout)

        # # Add the card to the scroll area's layout
        # self.scrollArea_tasks.widget().layout().addWidget(task_widget)


class addWindow(QDialog, ADD_TASK_CLASS):
    #Constructor
    def __init__(self):
        super(addWindow, self).__init__()
        QDialog.__init__(self)
        self.setupUi(self)
        
    

def main():
    app = QApplication(sys.argv)
    window = mainApp() #An instance of the class mainApp
    window.show()
    app.exec_() #Infinite loop

#Where the program starts
if __name__ == '__main__':
    main()
