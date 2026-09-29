import unittest
from unittest.mock import patch
from ala.ai_runtime import AIRuntime

class AIRuntimeTests(unittest.TestCase):
    settings={'model':'test-model','ollamaUrl':'http://127.0.0.1:11434'}
    def test_reachable_unloaded_model_and_ready_are_distinct(self):
        runtime=AIRuntime()
        with patch('ala.ai_runtime.request_json',side_effect=[{'models':[{'name':'test-model'}]},{'models':[]} ]):
            self.assertEqual('available',runtime.status(self.settings)['state'])
        with patch('ala.ai_runtime.request_json',return_value={'models':[{'name':'test-model'}]}):
            self.assertEqual('ready',runtime.status(self.settings)['state'])
    def test_unavailable_service_does_not_download_or_install(self):
        runtime=AIRuntime()
        with patch('ala.ai_runtime.request_json',side_effect=OSError),patch('ala.ai_runtime.shutil.which',return_value=None),patch('ala.ai_runtime.Path.is_file',return_value=False),patch('ala.ai_runtime.subprocess.Popen') as launch:
            runtime._start(self.settings)
            self.assertEqual('not_installed',runtime.failure);launch.assert_not_called()
    def test_missing_model_requires_selection(self):
        with patch('ala.ai_runtime.request_json',return_value={'models':[]}):
            self.assertEqual('choose_model',AIRuntime().status(self.settings)['state'])
