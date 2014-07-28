import unittest
from httmock import urlmatch, HTTMock
from mock import Mock
from tenthousandfeet import HTTPClient, CollectionClient


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
        client.http.get = Mock()
        client.list()
        client.http.get.assert_called_with(path='foo/', data={})
        client.list(bar=123)
        client.http.get.assert_called_with(path='foo/', data={'bar':123})
        client.list(bar=123,baz='skidoo')
        client.http.get.assert_called_with(path='foo/', data={'bar':123})
        
        
    def test_show(self):
        client = CollectionClient(self.http, 'foo', {'show': {'optional': ['bar']} }, {})
        client.http.get = Mock()
        client.show('foo#1')
        client.http.get.assert_called_with(path='foo/foo#1', data={})
        client.show('foo#1', bar=123)
        client.http.get.assert_called_with(path='foo/foo#1', data={'bar':123})
        
        
    def test_create(self):
        client = CollectionClient(self.http, 'foo', {'create': {'required': ['bar','baz']} }, {})
        client.http.post = Mock()
        client.create(bar=123,baz='hello')
        client.http.post.assert_called_with(path='foo/', data={'bar':123,'baz':'hello'})
        
        
    def test_update(self):
        client = CollectionClient(self.http, 'foo', {'update': {'optional': ['bar','baz']} }, {})
        client.http.put = Mock()
        client.update('foo#1', baz='hello')
        client.http.put.assert_called_with(path='foo/foo#1', data={'baz':'hello'})
        
        
    def test_delete(self):
        client = CollectionClient(self.http, 'foo', {'delete': {} }, {})
        client.http.delete = Mock()
        client.delete('foo#1')
        client.http.delete.assert_called_with(path='foo/foo#1', data={})
        