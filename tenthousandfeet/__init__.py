import requests
import json
from datetime import date, datetime
from dateutil.parser import parse as date_parse
from functools import partial


TEST_URL = 'http://tenthousandfeettest/'
VNEXT_URL = 'https://vnext-api.10000ft.com/api/v1/'
PREPROD_URL = 'https://pre-prod-api.10000ft.com/api/v1/'
PROD_URL = 'https://api.10000ft.com/api/v1/'


collections = {
    'users': {
        'methods': {
            'list': { 'optional': ['fields'] },
            'show': { 'optional': ['fields'] },
            'create': { 'required': ['email', 'first_name', 'last_name'] }, 
            'update': { 'optional': ['email', 'first_name', 'last_name'] }
        },
        'collections': {
            'statuses': {
                'methods': {}
            }
        }
    }
}


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
        
        for subname, collection in collections.items():
            setattr(self, subname, self.create_sub_collection_factory(subname, collection))
        
        
    def create_sub_collection_factory(self, name, desc):
        def factory(object_id):
            return CollectionClient(
                        self.http, 
                        '%s/%s/%s' % (self.name, object_id, name),
                        desc.get('methods', {}),
                        desc.get('collections', {})
                    )
        return factory
        
        
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
        
        
    def request(self, http_fn, method, path, kwargs):
        self.require_method(method)
        data = self.check_kwargs(method, kwargs)
        if not isinstance(path, basestring):
            path = str(path)
        res = http_fn(path=self.name + '/' + path, data=data)
        return self.get_response(method, res)
        
        
    def get_response(self, method, res):
        if res.status_code not in (200, 201):
            raise Exception, "Error %d %s: %s" % (res.status_code, res.reason, res.text)
        data = res.json().get('data')
        self.process_response_data(method, data)
        return data
        
        
    def process_response_data(self, method, data):
        process_rules = self.methods[method].get('process', {})
        if isinstance(data, list):
            return map(partial(self.process_response_data_item, process_rules), data)
        else:
            return self.process_response_data_item(process_rules, data)
        
        
    def process_response_data_item(self, process_rules, data):
        for k,fn in process_rules.items():
            parts = k.split('.')
            try:
                value = get_in_dict(data, parts)
            except KeyError:
                continue
            set_in_dict(data, parts, fn(value))
        return data


def get_in_dict(dict, key):
    return reduce(lambda d, k: d[k], key, dict)
    
    
def set_in_dict(dict, key, value):
    get_in_dict(dict, key[:-1])[key[-1]] = value



class TenThousandFeet(object):
    
    def __init__(self, token, endpoint=PROD_URL):
        http = HTTPClient(token, endpoint)
        for name, desc in collections.items():
            setattr(self, name, 
                CollectionClient(
                    http,
                    name, 
                    desc.get('methods', []), 
                    desc.get('collections', [])
                ))
            