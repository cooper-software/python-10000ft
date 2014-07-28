import requests
import json
from datetime import date, datetime

TEST_URL = 'http://tenthousandfeettest/'
VNEXT_URL = 'https://vnext-api.10000ft.com/api/v1/'
PREPROD_URL = 'https://pre-prod-api.10000ft.com/'
PROD_URL = 'https://api.10000ft.com/api/v1/'

collections = [
    {
        'name': 'users',
        'methods': {
            'list': { 'optional': ['fields'] },
            'show': { 'optional': ['fields'] },
            'create': { 'required': ['email', 'first_name', 'last_name'] }, 
            'update': { 'optional': ['email', 'first_name', 'last_name'] }
        },
        'collections': [
            {
                'name': 'statuses',
                'methods': {
                    
                }
            }
        ]
    }
]


class HTTPClient(object):
    
    def __init__(self, token, endpoint):
        self.token = token
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.headers['auth'] = token
        
    def request(self, method, path, data):
        return method(self.endpoint + path, data=data)
        
    def get(self, path='', data=None):
        return self.request(self.session.get, path, data)
        
    def post(self, path='', data=None):
        return self.request(self.session.post, path, data)
        
    def put(self, path='', data=None):
        return self.request(self.session.put, path, data)
        
    def delete(self, path='', data=None):
        return self.request(self.session.delete, path, data)


class CollectionClient(object):
    
    def __init__(self, http, name, methods, collections):
        self.name = name
        self.http = http
        self.methods = methods
        self.collections = collections
        
        
    def list(self, **kwargs):
        return self.request(self.http.get, 'list', '', kwargs)
        
        
    def show(self, object_id, **kwargs):
        return self.request(self.http.get, 'show', object_id, kwargs)
        
        
    def create(self, **kwargs):
        return self.request(self.http.post, 'create', '', kwargs)
        
        
    def update(self, object_id, **kwargs):
        return self.request(self.http.put, 'update', object_id, kwargs)
        
        
    def delete(self, object_id, **kwargs):
        return self.request(self.http.delete, 'delete', object_id, kwargs)
        
        
    def request(self, http_fn, method, path, kwargs):
        self.require_method(method)
        data = self.check_kwargs(method, kwargs)
        return http_fn(path=self.name + '/' + path, data=data)
        
        
    def require_method(self, name):
        if name not in self.methods:
            raise Exception, "%s does not implement %s" % (self.name, name)
        
        
    def check_kwargs(self, method, kwargs):
        method_desc = self.methods[method]
        optional = method_desc.get('optional', [])
        required = method_desc.get('required', [])
        new_kwargs = {}
        
        for r in required:
            v = kwargs.get(r)
            if v is None:
                raise Exception, "%s is a required argument of %s.%s" % (r, self.name, method)
            new_kwargs[r] = v
        
        for o in optional:
            v = kwargs.get(o)
            if v:
                new_kwargs[o] = v
        
        return new_kwargs
                


class TenThousandFeet(object):
    
    def __init__(self, token, endpoint=PROD_URL):
        http = HTTPClient(token, endpoint)
        for desc in collections:
            setattr(self, desc['name'], 
                CollectionClient(
                    http,
                    desc['name'], 
                    desc.get('methods', []), 
                    desc.get('collections', [])
                ))
            