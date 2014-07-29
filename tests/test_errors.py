import unittest
from mock import Mock
from tenthousandfeet import HTTPClient, CollectionClient, Error
from . import MockHTTPResponse


class TestErrors(unittest.TestCase):
    
    def setUp(self):
        self.http = HTTPClient('abc123', 'http://endpoint')
        
        
    def test_error(self):
        error_response = MockHTTPResponse(status_code=401, data={'message': "You aren't allowed to do that!"})
        client = CollectionClient(self.http, 'foo', {'show':{}}, {})
        client.http.session.get = Mock(return_value=error_response)
        
        with self.assertRaises(Error) as context:
            client.show(123)
            
        exc = context.exception
        self.assertEqual(exc.status_code, 401)
        self.assertEqual(exc.message, "You aren't allowed to do that!")