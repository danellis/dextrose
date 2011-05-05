import json
from werkzeug import BaseRequest, BaseResponse

class Request(BaseRequest):
    """Derived from Werkzeug's `BaseRequest`."""
    
class Response(BaseResponse):
    """Derived from Werkzeug's `BaseResponse`."""

class JsonResponse(Response):
    def __init__(self, data={}):
        response = json.dumps(data)
        super(JsonResponse, self).__init__(
            response=response,
            status=200,
            mimetype='text/json'
        )

def returns_json(fn):
    def decorator(*args, **kwargs):
        data = fn(*args, **kwargs) or {}
        return JsonResponse(data)
    return decorator
