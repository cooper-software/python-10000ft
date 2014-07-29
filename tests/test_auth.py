import unittest
from httmock import all_requests, HTTMock
import tenthousandfeet


class TestAuth(unittest.TestCase):
        
    def test_auth_token_header(self):
        token = 'abc123'
        request_headers = {}
        client = tenthousandfeet.TenThousandFeet(token, 
                            endpoint=tenthousandfeet.TEST_URL)
        
        @all_requests
        def response(url, request):
            request_headers['auth'] = request.headers['auth']
            return '{"data":{}}'
        
        with HTTMock(response):
            client.users.list()
        
        self.assertEqual(request_headers['auth'], token)