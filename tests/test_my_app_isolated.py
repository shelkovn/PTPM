import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from user_inputs_getter import TkinterInterface
from repository import TriangleRepository, Triangle
from external_service import ExternalService


class TestTriangleUnitComponents(unittest.TestCase):
#1. repository
    def test_repository_delete_by_sides_success(self):
        repo = TriangleRepository(db_path=":memory:") #clean

        triangle = Triangle(
            side_a="5", side_b="5", side_c="5",
            coord_a=(0,0), coord_b=(10,0), coord_c=(5,5),
            triangle_type="равносторонний"
        )
        repo.add_triangle(triangle)
        
        self.assertIsNotNone(repo.fetch_by_sides("5", "5", "5"))
        delete_result = repo.delete_by_sides("5", "5", "5")
        self.assertTrue(delete_result) #returns true if deleted successfully
        self.assertIsNone(repo.fetch_by_sides("5", "5", "5"))

#2. inferface
    def test_repository_delete_by_sides_non_existent(self):
        repo = TriangleRepository(db_path=":memory:")
        delete_result = repo.delete_by_sides("99", "99", "99")
        self.assertFalse(delete_result)

    def test_interface_initial_state_is_disabled(self):
        ui = TkinterInterface()

        for entry in ui.entries: #buttons disabled until scenario runs
            self.assertEqual(entry.cget("state"), "disabled")
            
        self.assertEqual(ui.submit_btn.cget("state"), "disabled")
        
        ui.root.destroy()

    def test_interface_get_user_data_activation_and_flow(self):
        ui = TkinterInterface()

        #simulate input
        def inputs():
            test_values = ["10", "20", "30.5"]
            for entry, value in zip(ui.entries, test_values):
                entry.insert(0, value)
            ui.submit_btn.invoke()

        
        #simulate scenario ran
        ui.root.after(50, inputs)

        result = ui.get_user_data()
        self.assertEqual(result, ["10", "20", "30.5"])
        
        #assert disabled again
        for entry in ui.entries:
            self.assertEqual(entry.cget("state"), "disabled")
            
        ui.root.destroy()

    def test_interface_draw_triangle_updates_canvas_and_label(self):
        ui = TkinterInterface()
        
        #assert empty
        self.assertEqual(len(ui.canvas.find_all()), 0)
        
        ui.draw_triangle([(0, 0), (10, 0), (0, 10)], info_text="тест_тип")
        
        # assert drawn and displaying type
        self.assertEqual(len(ui.canvas.find_all()), 1)
        self.assertEqual(ui.info_label.cget("text"), "тест_тип")
        
        ui.root.destroy()

#3. external service
    def test_external_service_send_result_prints(self):
        service = ExternalService()
        
        with patch('sys.stdout') as mock_stdout:
            service.send_result("test_message")
            # sent to console
            mock_stdout.write.assert_called()


if __name__ == "__main__":
    unittest.main()
