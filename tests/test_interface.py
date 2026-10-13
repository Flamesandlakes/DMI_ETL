from dmi_etl.interface import UserInterface, validate_input, ErrorLogger
from unittest.mock import Mock, MagicMock
from unittest.mock import patch
import tkinter
import datetime
import os
import unittest
from subprocess import Popen, PIPE

class Test_valid_input(unittest.TestCase):
    
    ## testing time inputs
    def test_correct_time_format(self):
        test_input = "11:44:10"
        self.assertEqual(validate_input(test_input, "time"), True)

    def test_incorrect_time_format_A(self):
        test_input = "twelve o'clock"
        self.assertEqual(validate_input(test_input, "time"), False)
        
    def test_incorrect_time_format_B(self):
        test_input = "Let us say: twelve o'clock"
        self.assertEqual(validate_input(test_input, "time"), False)
    
    def test_incorrect_time_format_C(self):
        test_input = "AM:23:23"
        self.assertEqual(validate_input(test_input, "time"), False)
        
    def test_incorrect_time_format_D(self):
        test_input = "302:23:23"
        self.assertEqual(validate_input(test_input, "time"), False)

    def test_correct_time_format_but_impossible_time_A(self):
        test_input = "10:77:88"
        self.assertEqual(validate_input(test_input, "time"), False)

    def test_correct_time_format_but_impossible_time_B(self):
        test_input = "30:17:18"
        self.assertEqual(validate_input(test_input, "time"), False)

    ## testing coordinate inputs
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
        self.assertEqual(validate_input(test_input, "coordinates"), False)

    def test_impossible_longitude_coordiantes(self):
        test_input = "50,212,80,190"
        self.assertEqual(validate_input(test_input, "coordinates"), False)
        
    ## testing integer inputs
    def test_correct_integer(self):
        test_input = "57"
        self.assertEqual(validate_input(test_input, "integer"), True)
    
    def test_float_instead_of_integer(self):
        test_input = "57.5"
        self.assertEqual(validate_input(test_input, "integer"), False)
class Test_UserInterface_Methods(unittest.TestCase):
    def test_halt_pipeline_response(self):
        ui = UserInterface()
        ui.halt_pipeline()
        self.assertEqual(ui.halt, 1)

    def test_continue_response(self):
        ui = UserInterface()
        ui.continue_pipeline()
        self.assertEqual(ui.halt, 0)
        
    def test_get_url_and_params(self):
        ui = UserInterface()
        test_call = {"api_url":"correct.com/api", "api_parameters": {"param_x":1,"param_y":1}, "api_fluff": "to be excluded"}
        result = ui.get_url_and_params(test_call)
        self.assertEqual(len(result), 2)
        self.assertEqual("param_x" in result[1].keys(), True)
        
class Test_ErrorLogger(unittest.TestCase):
    # def setUp(self):
    #     self.root = tkinter.Tk()
    #     self.root.bind('<Key>', lambda e: print(self.root, e.keysym))
        
    def test_log_error(self):
        logger = ErrorLogger()
        n = 5
        for i in range(n):
            logger.log_error(f"SOME ERROR {i}")
        _time = datetime.datetime.now()
            
        self.assertEqual(len(logger.session_errors), n)
        self.assertAlmostEqual(logger.session_errors[n-1][1], _time, delta=datetime.timedelta(seconds=1)) # allowing for 1 sec lag between logging and post loop time

    def test_log_and_check(self):
        with patch("tkinter.messagebox.askretrycancel", return_value=True):
            logger = ErrorLogger()
            self.assertEqual(logger.error_check(), 0)   # no errors yet
            logger.log_error("simulated error")
            self.assertEqual(logger.error_check(), 1)
        
        
        
    def test_display_errors_formats_message(self):
        logger = ErrorLogger()
        logger.log_error("another simulated error")
        with patch("dmi_etl.interface.messagebox.askretrycancel") as mock_mb:
            logger.display_errors()
        mock_mb.assert_called_once()
        self.assertIn("another simulated error", mock_mb.call_args[0][1])
        self.assertIn("1) error(s)", mock_mb.call_args[0][1])
        
class TestUserInterface(unittest.TestCase):
    def setUp(self):
        self.ui = UserInterface()
        # Inject mocks for every widget get_user_input() touches
        self.ui.api_source_choice = MagicMock()
        self.ui.parameter_choice = MagicMock()
        self.ui.start_date = MagicMock()
        self.ui.start_time = MagicMock()
        self.ui.end_date = MagicMock()
        self.ui.end_time = MagicMock()
        self.ui.bbox_entry = MagicMock()
        self.ui.limit_entry = MagicMock()

    def test_get_user_input_builds_packages(self):
        self.ui.api_source_choice.get.return_value = "DMI readings"
        self.ui.parameter_choice.curselection.return_value = [0, 1] # simulate n of chosen parameters
        self.ui.parameter_choice.get.side_effect = ["temp_mean_past1h", "wind_speed_past1h"] # the name of the chosen parameters
        self.ui.start_date.get_date.return_value = "2026-10-01"
        self.ui.start_time.get.return_value = "00:00:00"
        self.ui.end_date.get_date.return_value = "2026-10-02"
        self.ui.end_time.get.return_value = "00:00:00"
        self.ui.bbox_entry.get.return_value = "7,54,16,58"
        self.ui.limit_entry.get.return_value = "100"

        self.ui.get_user_input()

        self.assertEqual(len(self.ui.request_packages), 2)
        pkg = self.ui.request_packages[0]
        self.assertEqual(pkg["api"], "DMI readings")
        self.assertEqual(pkg["api_url"],
                        "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items")
        self.assertEqual(pkg["api_parameters"]["parameterId"], "temp_mean_past1h")
        self.assertEqual(pkg["api_parameters"]["limit"], "100")

    def test_invalid_time_logs_error(self):
        with patch("dmi_etl.interface"):#.messagebox.askretrycancel"):
            self.assertEqual(self.ui.get_selected_timeperiod(), "")

    def test_no_parameters_selected_yields_empty_packages(self):
        self.ui.parameter_choice.curselection.return_value = []
        with patch("dmi_etl.interface.messagebox.askretrycancel", return_value = True):
            self.ui.get_user_input()
            self.assertEqual(self.ui.request_packages, [])


### Partially generated tests for widget methods 
@unittest.skipUnless(hasattr(tkinter, "Tk"), "Tk available")
class TestWidgets(unittest.TestCase):
    def setUp(self):
        try:
            self.ui = UserInterface()
            self.ui.start()
            self.addCleanup(self.ui.cleanup)
        except tkinter.TclError:   # no $DISPLAY
            raise unittest.SkipTest("No display available")

    def test_update_parameters_populates_listbox(self):
        self.ui.api_source_choice.set("DMI readings")
        self.ui.update_parameters(None)
        params = list(self.ui.parameter_choice.get(0, tkinter.END))
        self.assertIn("temp_mean_past1h", params)


# class Test_MockUserInterface(unittest.TestCase):
#     def setUp(self):
#         print("test, setup a")
#         self.tk_patcher = patch("dmi_etl.interface.tk.Tk")
#         self.mock_tk_class = self.tk_patcher.start()
#         self.addCleanup(self.tk_patcher.stop)
#         self.mock_root = self.mock_tk_class.return_value
        
#         self.ui = UserInterface()
#         self.ui.start()
#         print("test, setup b")
        
#     def test_cleanup_does_not_enter_mainloop(self):
#         print("test, cleanup a")
#         self.ui.cleanup()
#         self.mock_root.mainloop.assert_not_called()
#         print("test, clean up b")
    
#     def test_root_from_start(self):
#         self.mock_tk_class.assert_called_once()
#         self.mock_root.title.assert_called_once_with("Define API call")
#         self.assertTrue(self.ui.has_root())

# # class TkinterTestCase(unittest.TestCase):
# #     def setUp(self):
# #         self.root = tkinter.Tk()
# #         self.pump_events()

# #     def tearDown(self):
# #         if self.root:
# #             self.root.destroy()
# #             self.pump_events()

# #     def pump_events(self):
# #         while self.root.dooneevent(tkinter.ALL_EVENTS or tkinter.DONT_WAIT):
# #             pass


# class 
# if __name__ == '__main__':
