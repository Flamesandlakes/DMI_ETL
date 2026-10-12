from dmi_etl.interface import UserInterface, validate_input
from unittest.mock import Mock
from unittest.mock import patch
import tkinter
import datetime
import os
import unittest

class Test_valid_input(unittest.TestCase):
    def test_correct_time_format(self):
        test_input = "11:44:10"
        self.assertEqual(validate_input(test_input, "time"), True)

    def test_incorrect_time_format(self):
        test_input = "twelve o'clock"
        self.assertEqual(validate_input(test_input, "time"), False)

    def test_correct_time_format_but_impossible_time_A(self):
        test_input = "10:77:88"
        self.assertEqual(validate_input(test_input, "time"), False)

    def test_correct_time_format_but_impossible_time_B(self):
        test_input = "30:17:18"
        self.assertEqual(validate_input(test_input, "time"), False)

    def test_correct_coordinates_format(self):
        test_input = "4,10,8,12"
        self.assertEqual(validate_input(test_input, "coordinates"), True)

    def test_correct_coordinates_format_with_minus_values(self):
            test_input = "-4,10,-8,12"
            self.assertEqual(validate_input(test_input, "coordinates"), True)

    def test_wrong_coordinates_format_A(self):
        test_input = "500 steps above the equator and 500 to the east of London"
        self.assertEqual(validate_input(test_input, "coordinates"), False)

    def test_wrong_coordinates_format_B(self):
        test_input = "500 steps above the equator, then 500 to the east of London"
        self.assertEqual(validate_input(test_input, "coordinates"), False)

    def test_wrong_coordinates_format_C(self):
        test_input = "500 steps, 500 more, 500 extra, 500 back"
        self.assertEqual(validate_input(test_input, "coordinates"), False)

    def test_wrong_coordinates_format_D(self):
        test_input = "-500 steps, 500 more, 500 extra, -500 back"
        self.assertEqual(validate_input(test_input, "coordinates"), False)

    def test_impossible_latitude_coordinates(self):
        test_input = "91,10,92,14"
        self.assertEqual(validate_input(test_input, "coordinates"))

    def test_impossible_longitude_coordiantes(self):
        test_input = "50,125,80,140"
        self.assertEqual(validate_input(test_input, "coordinates"))
class Test_UserInterface_Methods(unittest.TestCase):
    def test_exit_response(self):
        ui = UserInterface()
        ui.exit()
        self.assertEqual(ui.halt, 1)
        del ui

    def test_continue_response(self):
        ui = UserInterface()
        ui.continue_pipeline()
        self.assertEqual(ui.halt, 0)


# class TkinterTestCase(unittest.TestCase):
#     def setUp(self):
#         self.root = tkinter.Tk()
#         self.pump_events()

#     def tearDown(self):
#         if self.root:
#             self.root.destroy()
#             self.pump_events()

#     def pump_events(self):
#         while self.root.dooneevent(tkinter.ALL_EVENTS or tkinter.DONT_WAIT):
#             pass


# class 
# if __name__ == '__main__':
