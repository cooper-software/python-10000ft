from mock import Mock


class MockHTTPResponse(object):
    def __init__(self, status_code=200, text='', data=None):
        self.status_code = status_code
        self.text = text
        self._data = data if data else {}
        
    def json(self):
        return self._data
        

def make_mock_response_obj(data=None):
    return Mock(return_value=MockHTTPResponse(data=data))