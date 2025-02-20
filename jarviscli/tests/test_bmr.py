import unittest
import plugins.bmr as b
from tests import PluginTest  


class BMRTest(PluginTest): 
    def setUp(self):
        super().setUp()
        self.bmr_plugin = self.load_plugin(b.bmr)  

    def test_bmr_amr_for_male(self):
        """Test BMR and AMR calculation for male (M)."""
        inputs = ["1", "M", "180", "75", "30", "Y", "3"]
        for input in inputs:
            self.queue_input(input)  

        self.bmr_plugin.run("")
        
        expected_bmr = (int(inputs[2]) * 6.25) + (int(inputs[3]) * 9.99) - (int(inputs[4]) * 4.92) - 5
        expected_amr = expected_bmr * 1.55

        self.assertTrue(self.history_say().contains('text', f"BMR: {expected_bmr}"))
        self.assertTrue(self.history_say().contains('text', f"AMR: {expected_amr}"))

    def test_bmr_amr_for_female(self):
        """Test BMR and AMR calculation for female (F)."""
        inputs = ["1", "F", "165", "60", "28", "Y", "2"]
        for input in inputs:
            self.queue_input(input)

        self.bmr_plugin.run("")

        expected_bmr = (int(inputs[2]) * 6.25) + (int(inputs[3]) * 9.99) - (int(inputs[4]) * 4.92) - 116
        expected_amr = expected_bmr * 1.375

        self.assertTrue(self.history_say().contains('text', f"BMR: {expected_bmr}"))
        self.assertTrue(self.history_say().contains('text', f"AMR: {expected_amr}"))


if __name__ == "__main__":
    unittest.main()