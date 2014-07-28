import unittest
from httmock import urlmatch, HTTMock
import tenthousandfeet


class TestUsers(unittest.TestCase):
    
    def setUp(self):
        self.client = tenthousandfeet.TenThousandFeet('abc123', 
                        endpoint=tenthousandfeet.TEST_URL)
        