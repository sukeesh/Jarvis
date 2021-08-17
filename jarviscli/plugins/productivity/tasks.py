from colorama import Fore

from packages.memory.memory import Memory
from plugin import plugin


@plugin("tasks")
class TaskManager():
    """
    Jarvis plugin For Managing User Tasks

    """

    def __call__(self, jarvis, s):
        self.load_tasks()
        jarvis.say("Welcome To Your Tasks Manager\n")
        while True:
            option = self.get_option(jarvis)
            if option is None:
                return
            self.procces_chosen_option(option, jarvis)

    def list_all(self, jarvis):
        jarvis.say("")
        task_count = len(self.tasks)
        if task_count == 0:
            jarvis.say("Your Task List Is Empty, Good Job")
            return
        jarvis.say("You Have {} {}".format(task_count, "Task" if task_count == 1 else "Tasks"))
        for i in range(task_count):
            try:
                priority = self.tasks[i]["priority"]
                jarvis.say("{}. {} PR: {}".format(
                    i + 1, self.tasks[i]["name"], priority), self.get_color_with_priority(priority))
            except BaseException:
                jarvis.say("{}. {}".format(i + 1, self.tasks[i]["name"]))

    def get_color_with_priority(self, priority):
        if priority == "High":
            return Fore.RED
        elif priority == "Medium":
            return Fore.YELLOW
        else:
            return Fore.GREEN

    def add_task(self, jarvis):
        new_task = jarvis.input("Enter New Task: ", Fore.GREEN)
        self.tasks.append({"name": new_task})
        self.update_tasks(self.tasks)
        jarvis.say("Task Was Successfully Added")
        self.list_all(jarvis)

    def choose_task(self, exit_text, input_text, jarvis):
        tasks_count = len(self.tasks)
        self.list_all(jarvis)
        jarvis.say("{}. {}".format(tasks_count + 1, exit_text))
        return self.get_choice(input_text, tasks_count, tasks_count + 1, jarvis)

    def update_task(self, jarvis):
        task_index = self.choose_task("EXIT Editing", "Exit Editing or Choose Which Task To Edit: ", jarvis)
        if task_index == -1:
            return
        chosen_task_name = self.tasks[task_index - 1]["name"]
        jarvis.say("Chosen Task: {}".format(chosen_task_name))
        updated_task = jarvis.input("Enter Updated Task: ", Fore.GREEN)
        new_tasks = map(lambda task: {"name": updated_task} if task["name"] == chosen_task_name else task, self.tasks)
        self.update_tasks(list(new_tasks))
        jarvis.say("Task Was Successfully Updated")

    def get_priority(self, jarvis):
        jarvis.say("")
        jarvis.say("Choose Priority For Task", Fore.BLUE)
        jarvis.say("")
        jarvis.say("1: High")
        jarvis.say("2: Medium")
        jarvis.say("3: Low")
        jarvis.say("4: Exit Priority Mode ")
        jarvis.say("")
        return self.get_choice("Enter your choice: ", 3, 4, jarvis)

    def add_priority_to_task(self, jarvis):
        options = {1: "High", 2: "Medium", 3: "Low"}
        task_index = self.choose_task("EXIT Add Priority Mode",
                                      "Exit Priority Mode or Choose Taks To Add Priority: ", jarvis)
        if task_index == -1:
            return
        priority = self.get_priority(jarvis)
        if priority == -1:
            return
        task_name = self.tasks[task_index - 1]["name"]
        new_tasks = map(lambda t: {"name": task_name,
                                   "priority": options[priority]} if t["name"] == task_name else t, self.tasks)
        self.update_tasks(list(new_tasks))

    def delete_task(self, jarvis):
        task_index = self.choose_task("EXIT Delete Mode", "Exit Delte Mode or Choose Taks To Delete: ", jarvis)
        if task_index == -1:
            return
        chosen_task_name = self.tasks[task_index - 1]["name"]
        new_tasks = filter(lambda x: x["name"] != chosen_task_name, self.tasks)
        self.update_tasks(list(new_tasks))
        jarvis.say("Task Was Successfully Deleted")

    def get_sorting_startegy(self, jarvis):
        jarvis.say("")
        jarvis.say("Choose Sorting Strategy", Fore.BLUE)
        jarvis.say("")
        jarvis.say("1: By Name")
        jarvis.say("2: By Priority")
        jarvis.say("3: Exit Sorting Mode ")
        jarvis.say("")
        return self.get_choice("Enter your choice: ", 2, 3, jarvis)

    def display_sorted(self, jarvis):
        options = {1: "name", 2: "pr"}
        tasks_count = len(self.tasks)
        if tasks_count == 0 | tasks_count == 1:
            jarvis.say("There is Not Enough Tasks To sort")
            return
        strategy = self.get_sorting_startegy(jarvis)
        if strategy == -1:
            return

        def sort_by_priority(task):
            try:
                priority = task["priority"]
                if priority == "High":
                    return 3
                elif priority == "Medium":
                    return 2
                else:
                    return 1
            except BaseException:
                return 0

        def sort_by_name(task):
            return task["name"]

        sorted_tasks = self.tasks.copy()
        if options[strategy] == "name":
            sorted_tasks.sort(key=sort_by_name)
        else:
            sorted_tasks.sort(key=sort_by_priority, reverse=True)
        jarvis.say("")
        for i in range(len(sorted_tasks)):
            try:
                priority = sorted_tasks[i]["priority"]
                color = self.get_color_with_priority(priority)
                jarvis.say("{}. {} PR: {}".format(i + 1, sorted_tasks[i]["name"], priority), color)
            except BaseException:
                jarvis.say("{}. {}".format(i + 1, sorted_tasks[i]["name"]))

    def procces_chosen_option(self, option, jarvis):
        if option == "ann_new":
            self.add_task(jarvis)
        elif option == "edit_cur":
            self.update_task(jarvis)
        elif option == "list_all":
            self.list_all(jarvis)
        elif option == "add_priority":
            self.add_priority_to_task(jarvis)
        elif option == "delete_task":
            self.delete_task(jarvis)
        elif option == "sort":
            self.display_sorted(jarvis)
        else:
            return

    def get_option(self, jarvis):
        options = {1: "list_all", 2: "ann_new", 3: "edit_cur", 4: "delete_task", 5: "add_priority", 6: "sort"}
        jarvis.say("")
        jarvis.say("How Can I Help You?", Fore.BLUE)
        jarvis.say("")
        jarvis.say("1: List All My Tasks")
        jarvis.say("2: Add New Task")
        jarvis.say("3: Edit Existing Task")
        jarvis.say("4: Delete  Task")
        jarvis.say("5: Add Priority To Task")
        jarvis.say("6: Sort")
        jarvis.say("7: Exit ")
        jarvis.say("")
        choice = self.get_choice("Enter your choice: ", 6, 7, jarvis)
        if choice == -1:
            return
        else:
            return options[choice]

    def get_choice(self, input_text, max_valid_value, terminator, jarvis):
        while True:
            try:
                inserted_value = int(jarvis.input(input_text, Fore.GREEN))
                if inserted_value == terminator:
                    return -1
                elif inserted_value <= max_valid_value:
                    return inserted_value
                else:
                    jarvis.say(
                        "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
            except ValueError:
                jarvis.say(
                    "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
            jarvis.say("")

    def load_tasks(self):
        m = Memory("tasks.json")
        if m.get_data("tasks_list") is None:
            self.tasks = []
        else:
            self.tasks = m.get_data("tasks_list")

    def update_tasks(self, new_tasks):
        m = Memory("tasks.json")
        if m.get_data("tasks_list") is None:
            m.add_data("tasks_list", new_tasks)
        else:
            m.update_data("tasks_list", new_tasks)
        m.save()
        self.tasks = new_tasks
