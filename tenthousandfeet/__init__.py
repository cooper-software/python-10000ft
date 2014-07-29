import requests
import json
from datetime import date, datetime
from dateutil.parser import parse as date_parse
from functools import partial
import re


TEST_URL = 'http://tenthousandfeettest/'
VNEXT_URL = 'https://vnext-api.10000ft.com/api/v1/'
PREPROD_URL = 'https://pre-prod-api.10000ft.com/api/v1/'
PROD_URL = 'https://api.10000ft.com/api/v1/'

project_process_fields = {
    'created_at': date_parse,
    'deleted_at': date_parse,
    'ends_at': date_parse,
    'secureurl_expiration': date_parse,
    'starts_at': date_parse,
    'updated_at': date_parse
}

project_methods = {
    'list': {
        'optional': ['from', 'to', 'fields', 'project_code', 'phase_name', 'with_archived', 'with_phases'],
        'process': project_process_fields
    },
    'show': {
        'optional': ['fields']
    },
    'create': {
        'required': ['name'],
        'optional': ['client', 'description', 'phase_name', 'project_code', 'settings', 'thumbnail'],
        'process': project_process_fields
    },
    'update': {
        'optional': ['name', 'client', 'description', 'phase_name', 'project_code', 'settings', 'thumbnail'],
        'process': project_process_fields
    },
    'delete': {}
}

user_process_fields = {
    'deleted_at': date_parse,
    'hire_date': date_parse,
    'termination_date': date_parse
}

time_entries = {
    'methods': {
        'list': {
            'optional': ['from', 'to', 'with_suggestions'],
            'process': {
                'date': date_parse
            }
        },
        'show': {
            'process': {
                'date': date_parse
            }
        },
        'create': {
            'required': ['date', 'hours'],
            'optional': ['leave_id', 'project_id', 'assignable_id'],
            'process': {
                'date': date_parse
            }
        },
        'update': {
            'optional': ['date', 'hours', 'leave_id', 'project_id', 'assignable_id'],
            'process': {
                'date': date_parse
            }
        },
        'delete': {}
    }
}

assignment_process_fields = {
    'ends_at': date_parse,
    'starts_at': date_parse
}

budget_item_process_fields = {
    'created_at': date_parse,
    'updated_at': date_parse
}

leave_type_process_fields = {
    'deleted_at': date_parse,
    'created_at': date_parse,
    'updated_at': date_parse
}

tags = {
    'methods': {
        'list': {},
        'create': { 'optional': ['value'] },
        'delete': {}
    }
}

collections = {
    'projects': {
        'methods': project_methods,
        'collections': {
            'phases': {
                'methods': project_methods
            },
            'time_entries': time_entries,
            'budget_items': {
                'methods': {
                    'list': {
                        'required': ['item_type'],
                        'process': budget_item_process_fields
                    },
                    'show': {
                        'process': budget_item_process_fields
                    },
                    'create': {
                        'required': ['item_type', 'amount'],
                        'optional': ['project_id', 'assignable_id', 'leave_id'],
                        'process': budget_item_process_fields
                    },
                    'update': {
                        'optional': ['item_type', 'amount', 'project_id', 'assignable_id', 'leave_id'],
                        'process': budget_item_process_fields
                    },
                    'delete': {}
                }
            },
            'tags': tags,
            'users': {
                'methods': {
                    'list': {
                        'optional': ['fields'],
                        'process': user_process_fields
                    }
                }
            }
        }
    },
    'users': {
        'methods': {
            'list': {
                'optional': ['fields'],
                'process': user_process_fields
            },
            'show': {
                'optional': ['fields'],
                'process': user_process_fields
            },
            'create': {
                'required': ['email', 'first_name', 'last_name'],
                'process': user_process_fields
            }, 
            'update': {
                'optional': ['email', 'first_name', 'last_name'],
                'process': user_process_fields
            }
        },
        'collections': {
            'statuses': {
                'methods': {
                    'list': {
                        'process': {
                            'created_at': date_parse,
                            'updated_at': date_parse
                        }
                    },
                    'create': {
                        'required': ['status'],
                        'process': {
                            'created_at': date_parse,
                            'updated_at': date_parse
                        }
                    }
                }
            },
            'time_entries': time_entries,
            'assignments': {
                'list': {
                    'optional': ['from', 'to'],
                    'process': assignment_process_fields
                },
                'show': {
                    'process': assignment_process_fields
                },
                'create': {
                    'optional': ['starts_at', 'ends_at', 'percent', 'fixed_hours'],
                    'process': assignment_process_fields
                },
                'delete': {}
            },
            'tags': tags
        }
    },
    'budget_item_categories': {
        'methods': {
            'list': {}
        }
    },
    'leave_types': {
        'methods': {
            'list': { 'process': leave_type_process_fields },
            'show': { 'process': leave_type_process_fields }
        }
    }
}


class Error(Exception):
    
    def __init__(self, status_code, message):
        self.status_code = status_code
        super(Exception, self).__init__(message)


class HTTPClient(object):
    
    def __init__(self, token, endpoint):
        self.token = token
        self.endpoint = endpoint
        self.session = requests.Session()
        self.session.headers['auth'] = token
        
    def request(self, method, path, data):
        res = method(self.endpoint + path, data=data)
        if res.status_code not in (200, 201):
            try:
                message = res.json()['message']
            except:
                message = res.reason
            raise Error(res.status_code, message)
        else:
            return res
        
    def get(self, path='', data=None):
        return self.request(self.session.get, path, data)
        
    def post(self, path='', data=None):
        return self.request(self.session.post, path, data)
        
    def put(self, path='', data=None):
        return self.request(self.session.put, path, data)
        
    def delete(self, path='', data=None):
        return self.request(self.session.delete, path, data)


class CollectionClient(object):
    
    underscore_replace_pattern = re.compile('^(_+)')
    
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
        
        
    def request(self, http_fn, method, path, kwargs):
        self.require_method(method)
        data = self.check_kwargs(method, kwargs)
        if not isinstance(path, basestring):
            path = str(path)
        res = http_fn(path=self.name + '/' + path, data=data)
        return self.get_response(method, res)
        
        
    def get_response(self, method, res):
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
            if value is not None:
                set_in_dict(data, parts, fn(value))
        return data
        
        
    def require_method(self, name):
        if name not in self.methods:
            raise Exception, "%s does not implement %s" % (self.name, name)
        
        
    def check_kwargs(self, method, kwargs):
        method_desc = self.methods[method]
        optional = set(method_desc.get('optional', []))
        required = set(method_desc.get('required', []))
        new_kwargs = {}
        
        for k,v in kwargs.items():
            k = self.underscore_replace_pattern.sub('', k)
            new_kwargs[k] = self.serialize_arg(v)
        
        for r in required:
            assert r in kwargs, "%s is a required argument of %s.%s" % (r, self.name, method)
        
        return new_kwargs
        
        
    def serialize_arg(self, value):
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%dT%H:%M:%S%z')
        elif isinstance(value, date):
            return value.strftime('%Y-%m-%d')
        else:
            return value


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
                    desc.get('methods', {}), 
                    desc.get('collections', {})
                ))
            