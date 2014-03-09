import json
import numpy
from django.http import HttpResponse


def distance(a, b):
    """Euclidean distance.

    a = (xa, ya, za)
    b = (xb, yb, zb)
    """
    if len(a) > len(b):
        a = a[:len(b)]
    elif len(b) > len(a):
        b = b[:len(a)]

    ar = numpy.array(a)
    br = numpy.array(b)
    dist = numpy.linalg.norm(ar-br)

    return dist


class JSONResponse(HttpResponse):
    """JSON Response class."""
    def __init__(self, obj='', json_opts={}, mimetype="application/json", *args, **kwargs):
        content = json.dumps(obj, **json_opts)
        super(JSONResponse, self).__init__(content, mimetype, *args, **kwargs)


def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"

