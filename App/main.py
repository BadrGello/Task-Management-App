from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
import sys
from os import path

# Constants
mainWindowFileName = "mainWindow.ui"
taskWidgetFileName = "taskWidget.ui"

# Import UI files
FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), mainWindowFileName))
TASK_WIDGET_CLASS, _ = loadUiType(path.join(path.dirname(__file__), taskWidgetFileName))

#When you start a new design on Qt designer, you are promted many chocies, the important 2 are "Main Window" 
#and "Widget", and based on that is the first argument, the second argument is this "FROM_CLASS" that loads file path

class mainApp(QMainWindow, FORM_CLASS):
    #Constructor
    def __init__(self, parent=None):
        super(mainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setWindowIcon(QIcon("Task-Management-App\App\creative app icon for a task manager app.png"))
        self.setupUi(self)
        
        #Function calls
        self.Handle_pushButton_addTask()
        self.Handle_UI()
        self.Handle_searchBar()
        self.Handle_pushButton_searchTask()

        #Variables
        self.searchBarText = ""

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

        
        #### TO DO ###
        # Be able to add the custom widget "taskWidget" -which can be seen in Qt Designer-, to the scrollable area which represents the tasks
        # Create an instance of the custom widget "taskWidget", not sure if this is right
        addTaskWidget = TASK_WIDGET_CLASS()


        ###############THE FOLLOWING IS AN EXAMPLE ONLY NOT A PROGRAM FEATURE#####################
        self.widget = QWidget()        # Widget that contains the collection of Vertical Box
        self.vbox = QVBoxLayout()      # The Vertical Box that contains the Horizontal Boxes of  labels and buttons

        for i in range(1,3):
            object = QLabel("TextLabel")
            self.vbox.addWidget(object)

        self.widget.setLayout(self.vbox)

        #Scroll Area Properties
        self.scrollArea_tasks.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea_tasks.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea_tasks.setWidgetResizable(True)
        self.scrollArea_tasks.setWidget(self.widget)
        #########################################################################################

        return


        
    

def main():
    app = QApplication(sys.argv)
    window = mainApp() #An instance of the class mainApp
    window.show()
    app.exec_() #Infinite loop

#Where the program starts
if __name__ == '__main__':
    main()
