import unittest
from unittest.mock import MagicMock
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from user_inputs_getter import TkinterInterface
from repository import TriangleRepository, Triangle
from triangle_placer import triangle_placer
from external_service import ExternalService
from controller_class import GeometryController


class TestTriangleIntegration(unittest.TestCase):

    def setUp(self):
        self.repository = TriangleRepository(db_path=":memory:") #clean db for every run
        
        #mock classes
        self.view = MagicMock(spec=TkinterInterface)
        self.external_service = MagicMock(spec=ExternalService)     
        self.calc_service = triangle_placer()

        #initialize
        self.controller = GeometryController(
            view=self.view,
            repository=self.repository,
            calculation_service=self.calc_service,
            external_service=self.external_service
        )

    def test_1_successful_triangle_calculation_and_saving(self):
        #imitate user input
        self.view.get_user_data.return_value = ["3", "4", "5"]

        result = self.controller.start_new_scenario()
        self.assertEqual(result, "разносторонний") 
        self.view.draw_triangle.assert_called_once() #drawn  
        self.external_service.send_result.assert_called_with("success. type: разносторонний") #data sent

        db_record = self.repository.fetch_by_sides("3", "4", "5") #db result
        self.assertIsNotNone(db_record)
        self.assertEqual(db_record.triangle_type, "разносторонний")
        self.assertIsNone(db_record.error_message)

    def test_2_cache_hit(self):
        existing_triangle = Triangle(
            side_a="7", side_b="7", side_c="7",
            coord_a=(0,0), coord_b=(10,0), coord_c=(5,5),
            triangle_type="равносторонний",
            error_message=None
        )
        self.repository.add_triangle(existing_triangle) #setup db
        self.calc_service.calculate_triangle = MagicMock() # prevent from calculating new triangles
        self.view.get_user_data.return_value = ["7", "7", "7"]

        result = self.controller.start_new_scenario()

        self.assertEqual(result, "равносторонний")
        self.calc_service.calculate_triangle.assert_not_called()
        self.view.draw_triangle.assert_called_once() #drawn from cache

    def test_3_invalid_geometry_error_saved_and_cached(self):
        self.view.get_user_data.return_value = ["1", "2", "10"]
        result = self.controller.start_new_scenario()

        self.assertEqual(result, "не треугольник")
        self.view.show_error.assert_called_with("not a triangle!") 
        self.external_service.send_result.assert_called_with("Error: invalid triangle")

        db_record = self.repository.fetch_by_sides("1", "2", "10")
        self.assertIsNotNone(db_record)
        self.assertEqual(db_record.triangle_type, "не треугольник")
        self.assertEqual(db_record.error_message, "Not a triangle (Geometry Error)")

    def test_4_validation_type_error_saved_and_cached(self): #value error
        self.view.get_user_data.return_value = ["abc", "4", "5"]

        result = self.controller.start_new_scenario()

        self.assertEqual(result, "Validation failed")
        self.view.show_error.assert_called_with("Incorrect inputs!")
        self.external_service.send_result.assert_called_with("Error: invalid values")

        db_record = self.repository.fetch_by_sides("abc", "4", "5")
        self.assertIsNotNone(db_record)
        self.assertEqual(db_record.error_message, "Invalid values (Type Error)")

    def test_5_missing_inputs_handled(self):
        self.view.get_user_data.return_value = [] #imitating uninitialized view

        result = self.controller.start_new_scenario()

        self.assertEqual(result, "view error, inputs missing!")
        self.view.show_error.assert_called_with("view error, inputs missing!")
        self.external_service.send_result.assert_not_called() #nothing sent


if __name__ == "__main__":
    unittest.main()
