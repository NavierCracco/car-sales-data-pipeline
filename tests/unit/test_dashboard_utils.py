import unittest
from unittest.mock import patch
import os
from dashboard.utils import get_secret

class TestSecretManagement(unittest.TestCase):

    def test_priority_docker_env(self):
        """We are in Docker (Local). There is an Environment Variable."""
        
        with patch.dict(os.environ, {'TEST_KEY': 'DOCKER_VALUE'}):
            # --- We simulate that Streamlit secrets do NOT exist (or they throw an error when accessing them)
            with patch('streamlit.secrets', side_effect=FileNotFoundError):
                
                result = get_secret('TEST_KEY')
                
                self.assertEqual(result, 'DOCKER_VALUE')

    def test_fallback_streamlit_cloud(self):
        """We are in the Cloud. There is NO Env Var, but there st.secrets."""
        
        # --- We ensure there are NO environment variables (we clean them up)
        with patch.dict(os.environ, {}, clear=True):
            
            # --- We simulate the st.secrets object as a dictionary
            mock_secrets = {'TEST_KEY': 'CLOUD_VALUE'}
            
            with patch('streamlit.secrets', mock_secrets):
                result = get_secret('TEST_KEY')
                
                self.assertEqual(result, 'CLOUD_VALUE')

    def test_missing_secret(self):
        """It's nowhere to be found."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('streamlit.secrets', side_effect=FileNotFoundError):
                
                result = get_secret('NON_EXISTENT_KEY')
                
                self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()