from plugin import plugin, require
from colorama import Fore
from packages.memory.memory import Memory


@plugin("tasks")
class TaskManager():
    """
    Jarvis plugin For Managing User Tasks

    """

    def __call__(self, jarvis, s):
        self.load_tasks()
        self.jarvis = jarvis
        print("Welcome To Your Tasks Manager\n")
        while True:
            option = self.get_option()
            if option is None:
                return
            self.procces_chosen_option(option)

    def list_all(self,):
        print("")
        task_count = len(self.tasks)
        if task_count == 0:
            print("Your Task List Is Empty, Good Job")
            return
        print("You Have {} {}".format(task_count, "Task" if task_count == 1 else "Tasks"))
        for i in range(task_count):
            try:
                priority = self.tasks[i]["priority"]
                self.jarvis.say("{}. {} PR: {}".format(i + 1, self.tasks[i]["name"], priority), self.get_color_with_priority(priority))
            except:
                print("{}. {}".format(i + 1, self.tasks[i]["name"]))

    def get_color_with_priority(self, priority):
        if priority == "High":
            return Fore.RED
        elif priority == "Medium":
            return Fore.YELLOW
        else:
            return Fore.GREEN

    def add_task(self):
        new_task = self.jarvis.input("Enter New Task: ", Fore.GREEN)
        self.tasks.append({"name": new_task})
        self.update_tasks(self.tasks)
        print("Task Was SuccesFully Added")
        self.list_all()

    def choose_task(self, exit_text, input_text):
        tasks_count = len(self.tasks)
        self.list_all()
        print("{}. {}".format(tasks_count + 1, exit_text))
        return self.get_choice(input_text, tasks_count, tasks_count + 1)

    def update_task(self):
        task_index = self.choose_task("EXIT Editing", "Exit Editing or Choose Which Task To Edit: ")
        if task_index == -1:
            return
        chosen_task = self.tasks[task_index - 1]["name"]
        print("Chosen Task: {}".format(chosen_task))
        updated_task = self.jarvis.input("Enter Updated Task: ", Fore.GREEN)
        new_tasks = map(lambda task: {"name": updated_task} if task["name"] == chosen_task else task, self.tasks)
        self.update_tasks(list(new_tasks))
        print("Task Was SuccesFully Updated")

    def get_priority(self,):
        print()
        self.jarvis.say("Choose Priority For Task", Fore.BLUE)
        print()
        print("1: High")
        print("2: Medium")
        print("3: Low")
        print("4: Exit Priority Mode ")
        print()
        return self.get_choice("Enter your choice: ", 3, 4)

    def add_priority_to_task(self):
        options = {1: "High", 2: "Medium", 3: "Low"}
        task_index = self.choose_task("EXIT Add Priority Mode", "Exit Priority Mode or Choose Taks To Add Priority: ")
        if task_index == -1:
            return
        priority = self.get_priority()
        if priority == -1:
            return
        chosen_task = self.tasks[task_index - 1]["name"]
        new_tasks = map(lambda t: {"name": chosen_task, "priority": options[priority]} if t["name"] == chosen_task else t, self.tasks)
        self.update_tasks(list(new_tasks))

    def procces_chosen_option(self, option):
        if option == "ann_new":
            self.add_task()
        elif option == "edit_cur":
            self.update_task()
        elif option == "list_all":
            self.list_all()
        elif option == "add_priority":
            self.add_priority_to_task()
        else:
            return

    def get_option(self):
        options = {1: "list_all", 2: "ann_new", 3: "edit_cur", 4: "add_priority"}
        print()
        self.jarvis.say("How Can I Help You?", Fore.BLUE)
        print()
        print("1: List All My Tasks")
        print("2: Add New Task")
        print("3: Edit Existing Task")
        print("4: Add Priority To Task")
        print("5: Exit ")
        print()
        choice = self.get_choice("Enter your choice: ", 4, 5)
        if choice == -1:
            return
        else:
            return options[choice]

    def get_choice(self, input_text, max_valid_value, terminator):
        while True:
            try:
                inserted_value = int(self.jarvis.input(input_text, Fore.GREEN))
                if inserted_value == terminator:
                    return -1
                elif inserted_value <= max_valid_value:
                    return inserted_value
                else:
                    self.jarvis.say(
                        "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
            except ValueError:
                self.jarvis.say(
                    "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
            print()

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
