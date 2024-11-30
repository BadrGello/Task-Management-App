 # # def start_study_countdown(self, study_time, break_time):
    #     total_seconds = study_time * 60  # Convert minutes to seconds for the timer

    #     def update_timer():
    #         nonlocal total_seconds
    #         if total_seconds > 0:
    #             minutes, seconds = divmod(total_seconds, 60)
    #             self.doneNum_3.display(total_seconds)
    #             self.countdown_label.setText(f"{minutes:02}:{seconds:02}")
    #             total_seconds -= 1
    #         else:
    #             self.timer.stop()
    #             self.doneNum_3.display(0)
    #             self.countdown_label.setText("Break Time! Take a rest.")

    #     # Create a QTimer to update the countdown every second
    #     self.timer = QTimer(self)
    #     self.timer.timeout.connect(update_timer)
    #     self.timer.start(1000)
    # ##################
        