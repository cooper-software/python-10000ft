from mock import Mock


class MockHTTPResponse(object):
    def __init__(self, data=None):
        self.status_code = 200
        self.text = 'foo'
        self._data = data if data else {}
        
    def json(self):
        return self._data
        

def make_mock_response_obj(data=None):
    return Mock(return_value=MockHTTPResponse(data=data))