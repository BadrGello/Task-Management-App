from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
import sys
from os import path

# Constants
mainWindowFileName = "mainWindow.ui"

# Import UI files
FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), mainWindowFileName))

#When you start a new design on Qt designer, you are promted many chocies, the important 2 are "Main Window" 
#and "Widget", and based on that is the first argument, the second argument is this "FROM_CLASS" that loads file path

class mainApp(QMainWindow, FORM_CLASS):
    #Constructor
    def __init__(self, parent=None):
        super(mainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        
    

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("Task-Management-App\App\creative app icon for a task manager app.png"))
    window = mainApp() #An instance of the class mainApp
    window.show()
    app.exec_() #Infinite loop

#Where the program starts
if __name__ == '__main__':
    main()
