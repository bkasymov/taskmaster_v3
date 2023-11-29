import unittest
from process_manager import ProcessManager

class TestProcessManager(unittest.TestCase):
    def setUp(self):
        self.pm = ProcessManager()

    def test_start_process(self):
        result = self.pm.start_process()
        self.assertTrue(result, "Process should be started")

    def test_stop_process(self):
        self.pm.start_process()
        result = self.pm.stop_process()
        self.assertTrue(result, "Process should be stopped")

    def test_restart_process(self):
        self.pm.start_process()
        result = self.pm.restart_process()
        self.assertTrue(result, "Process should be restarted")

if __name__ == '__main__':
    unittest.main()