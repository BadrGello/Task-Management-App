from PyQt5.QtWidgets import QApplication, QSystemTrayIcon
from PyQt5.QtGui import QIcon
import sys

def send_notification():
    print("start")
    # Create a QApplication instance
    app = QApplication(sys.argv)
    app.setApplicationName("MyApp")
    app.setApplicationDisplayName("My Custom App")
    # Check if the system tray is available
    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("System tray is not available.")
        sys.exit(1)

    # Create a QSystemTrayIcon instance
    tray_icon = QSystemTrayIcon()
    tray_icon.setIcon(QIcon('App/Icons/appIcon (1).svg'))  # Set an icon file

    # Show the tray icon
    tray_icon.setVisible(True)

    # Send a notification
    tray_icon.showMessage(
        "todays Tasks",
        "This is the notification message.",
        QSystemTrayIcon.Information,  # Message type
        5000  # Duration in milliseconds
    )

    # Exit the application after a short delay
    print("end")
    sys.exit(app.exec_())

# Call the function to send a notification
send_notification()
