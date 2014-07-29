import unittest
from mock import Mock
from tenthousandfeet import HTTPClient, CollectionClient, date_parse
from datetime import date, datetime
from dateutil.tz import tzutc
from . import make_mock_response_obj


class TestDates(unittest.TestCase):
    
    def setUp(self):
        self.http = HTTPClient('abc123', 'http://endpoint')
        
        
    def test_parsing(self):
        client = CollectionClient(
            self.http,
            'foo',
            {
                'show': {
                    'process': {
                        'foo': date_parse,
                        'bar': date_parse
                    }
                }
            },
            {}
        )
        
        client.http.get = make_mock_response_obj({
            'data': {
                'foo': '1982-09-06',
                'bar': '1982-09-06T08:34:00Z'
            }
        })
        
        res = client.show(123)
        self.assertEqual(res['foo'], datetime(1982, 9, 6, 0, 0, 0, 0))
        self.assertEqual(res['bar'], datetime(1982, 9, 6, 8, 34, 0, 0, tzinfo=tzutc()))
        
        
    def test_serialization(self):
        client = CollectionClient(
            self.http,
            'foo',
            {
                'show': {
                    'optional': ['date']
                }
            },
            {}
        )
        client.http.get = make_mock_response_obj()
        res = client.show(123, date=datetime(1982, 9, 6, 8, 34, 0, 0, tzinfo=tzutc()))
        client.http.get.assert_called_with(path='foo/123', data={'date':'1982-09-06T08:34:00+0000'})