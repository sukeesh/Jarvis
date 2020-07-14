import unittest
from tests import PluginTest
from plugins.tasks import TaskManager
from packages.memory.memory import Memory


class TaskManagerTest(PluginTest):
    """
    Tests For TaskManger Plugin

    """

    def setUp(self):
        self.test = self.load_plugin(TaskManager)
        self.test.load_tasks()

    def test_add_task(self):
        self.queue_input("test_task")
        self.test.add_task(self.jarvis_api)
        self.assertTrue(self.lookup_taks_in_memory("test_task"))

    def test_edit_task(self):
        self.queue_input("test_task")
        self.test.add_task(self.jarvis_api)
        self.queue_input(self.get_task_count())
        self.queue_input("test_task_updated")
        self.test.update_task(self.jarvis_api)
        self.assertTrue(self.lookup_taks_in_memory("test_task_updated"))
        self.assertFalse(self.lookup_taks_in_memory("test_task"))

    def test_add_priority(self):
        self.queue_input("test_task")
        self.test.add_task(self.jarvis_api)
        self.queue_input(self.get_task_count())
        self.queue_input(1)
        self.test.add_priority_to_task(self.jarvis_api)
        self.assertTrue(self.lookup_taks_priority_in_memory("test_task", "High"))

    def test_delete_task(self):
        self.queue_input("test_task")
        self.test.add_task(self.jarvis_api)
        self.queue_input(self.get_task_count())
        self.test.delete_task(self.jarvis_api)
        self.assertFalse(self.lookup_taks_in_memory("test_task"))

    def get_task_count(self):
        m = Memory("tasks.json")
        task_list = m.get_data("tasks_list")
        if task_list is None:
            return 0
        return len(task_list)

    def lookup_taks_priority_in_memory(self, task_name, desired_priority):
        m = Memory("tasks.json")
        task_list = m.get_data("tasks_list")
        if task_list is None:
            return False
        result = False
        for i in range(len(task_list)):
            if task_list[i]["name"] == task_name:
                try:
                    result = task_list[i]["priority"] == desired_priority
                except BaseException:
                    pass
        self.remove_task_from_memory(task_name)
        return result

    def lookup_taks_in_memory(self, task_name):
        m = Memory("tasks.json")
        task_list = m.get_data("tasks_list")
        if task_list is None:
            return False
        result = False
        for i in range(len(task_list)):
            if task_list[i]["name"] == task_name:
                result = True
        self.remove_task_from_memory(task_name)
        return result

    # delete task which was added while testing
    def remove_task_from_memory(self, task_name):
        m = Memory("tasks.json")
        task_list = m.get_data("tasks_list")
        if task_list is None:
            return
        old_task = filter(lambda x: x["name"] != task_name, task_list)
        m.update_data("tasks_list", list(old_task))
        m.save()


if __name__ == '__main__':
    unittest.main()
