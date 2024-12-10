    
    # Progress Tab #

    def update_progress(self):
        self.progressMonthly()
        self.progressWeekly()

    def progressMonthly(self):

        """
        Updates the progress bar for tasks completed in the current month.
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

        #Calculate number of current month tasks as well as completed tasks
        total_tasks_this_month = len(current_month_tasks)
        completed_tasks_this_month = sum(1 for task in current_month_tasks if task["complete"])

        if total_tasks_this_month > 0:
            completion_percentage = completed_tasks_this_month / total_tasks_this_month * 100
        else:
            completion_percentage = 0
            
        self.completion_bar_month.setValue(int(completion_percentage))
        self.doneNum_month.display(completed_tasks_this_month)
        self.leftNum_month.display(total_tasks_this_month - completed_tasks_this_month)

    def progressWeekly(self):
        """
        Updates the progress bar for tasks completed in the current week.
        """
        self.completion_bar_week.setValue(0)

        current_date = datetime.now()
        start_of_week = current_date - timedelta(days=(current_date.weekday() + 2) % 7)  # Start on Monday

        current_week_tasks = [
            task for task in self.tasksList
            if start_of_week <= datetime.strptime(task["date"], "%Y-%m-%d %H:%M:%S") <= current_date
        ]

        total_tasks_this_week = len(current_week_tasks)
        completed_tasks_this_week = sum(1 for task in current_week_tasks if task["complete"])

        if total_tasks_this_week > 0:
            completion_percentage = completed_tasks_this_week / total_tasks_this_week * 100
        else:
            completion_percentage = 0

        self.completion_bar_week.setValue(int(completion_percentage))
        self.doneNum_week.display(completed_tasks_this_week)
        self.leftNum_week.display(total_tasks_this_week - completed_tasks_this_week)


    ##################
