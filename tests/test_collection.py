import unittest
from httmock import all_requests, response, HTTMock
from mock import Mock
from tenthousandfeet import HTTPClient, CollectionClient


class MockHTTPResponse(object):
    def __init__(self):
        self.status_code = 200
        self.text = 'foo'
        self._json = {}
        
    def json(self):
        return self._json
        

def make_mock_response_obj():
    return Mock(return_value=MockHTTPResponse())


class TestCollection(unittest.TestCase):
    
    def setUp(self):
        self.http = HTTPClient('abc123', 'http://endpoint')
        
        
    def test_error_calling_missing_method(self):
        client = CollectionClient(self.http, 'foo', {}, {})
        
        with self.assertRaises(Exception):
            client.list()
            
            
    def test_error_missing_required_arg(self):
        client = CollectionClient(self.http, 'foo', 
            {'list':{ 'required': ['bar'] }}, {})
        
        with self.assertRaises(Exception):
            client.list()
            
    
    def test_list(self):
        client = CollectionClient(self.http, 'foo', {'list': {'optional': ['bar']} }, {})
        client.http.get = make_mock_response_obj()
        client.list()
        client.http.get.assert_called_with(path='foo/', data={})
        client.list(bar=123)
        client.http.get.assert_called_with(path='foo/', data={'bar':123})
        client.list(bar=123,baz='skidoo')
        client.http.get.assert_called_with(path='foo/', data={'bar':123})
        
        
    def test_show(self):
        client = CollectionClient(self.http, 'foo', {'show': {'optional': ['bar']} }, {})
        client.http.get = make_mock_response_obj()
        client.show('foo#1')
        client.http.get.assert_called_with(path='foo/foo#1', data={})
        client.show('foo#1', bar=123)
        client.http.get.assert_called_with(path='foo/foo#1', data={'bar':123})
        
        
    def test_create(self):
        client = CollectionClient(self.http, 'foo', {'create': {'required': ['bar','baz']} }, {})
        client.http.post = make_mock_response_obj()
        client.create(bar=123,baz='hello')
        client.http.post.assert_called_with(path='foo/', data={'bar':123,'baz':'hello'})
        
        
    def test_update(self):
        client = CollectionClient(self.http, 'foo', {'update': {'optional': ['bar','baz']} }, {})
        client.http.put = make_mock_response_obj()
        client.update('foo#1', baz='hello')
        client.http.put.assert_called_with(path='foo/foo#1', data={'baz':'hello'})
        
        
    def test_delete(self):
        client = CollectionClient(self.http, 'foo', {'delete': {} }, {})
        client.http.delete = make_mock_response_obj()
        client.delete('foo#1')
        client.http.delete.assert_called_with(path='foo/foo#1', data={})
        
        
    def test_response_processing(self):
        def add_one(val):
            return val + 1
        
        client = CollectionClient(self.http, 'foo', {'show': {'process': {'foo.bar': add_one } } }, {})
        
        @all_requests
        def mock_response(url, request):
            return response(200, { 'data': {'foo': {'bar': 1} }}, {'content-type':'application/json'})
        
        with HTTMock(mock_response):
            res = client.show(123)
        
        self.assertEqual(res['foo']['bar'], 2)
        
        
    def test_sub_collections(self):
        client = CollectionClient(
            self.http,
            'foo',
            {},
            {
                'bar': 
                {
                    'methods': {
                        'list': {}
                    }
                }
            }
        )
        client.http.get = make_mock_response_obj()
        client.bar('foo#1').list()
        client.http.get.assert_called_with(path='foo/foo#1/bar/', data={})
        
        
    def test_sub_sub_collections(self):
        client = CollectionClient(
            self.http,
            'foo',
            {},
            {
                'bar': 
                {
                    'collections':
                    {
                        'baz': {
                            'methods': {
                                    'list': {}
                                }
                        }
                    },
                }
            }
        )
        client.http.get = make_mock_response_obj()
        client.bar('foo#1').baz('bar#1').list()
        client.http.get.assert_called_with(path='foo/foo#1/bar/bar#1/baz/', data={})
        