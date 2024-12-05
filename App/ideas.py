# 1
from win11toast import toast
# Don't forget to enable Notifications on your system
toast('Hello Python', 'Click to open url', on_click='https://www.python.org')

# 2
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtMultimedia import QSound

def show_reminder():
    QSound.play("App/Audio/notif_1.wav")
    msg = QMessageBox()
    msg.setWindowTitle("Reminder")
    msg.setText("This is your reminder notification!")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

app = QApplication([])

# Timer for the reminder
timer = QTimer()
timer.timeout.connect(show_reminder)
timer.start(2000)  # Reminder after 2 seconds

app.exec_()
