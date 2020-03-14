from flask import make_response, jsonify


class InvalidUsage(Exception):
    def __init__(self, message='InvalidUsage', status_code=400, header=None):
        self.message = message
        self.status_code = status_code
        self.header = header

    def make_response(self):
        content = {
            'error': {
                'message': self.message,
                'type': self.__class__.__name__,
                'code': self.status_code
            }
        }
        res = make_response(jsonify(content), self.status_code)
        if self.header:
            res.headers.extend(self.header)
        return res
