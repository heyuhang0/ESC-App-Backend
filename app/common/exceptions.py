from flask import make_response, jsonify


class InvalidUsage(Exception):
    def __init__(self, message='InvalidUsage', status_code=400, header=None):
        self.message = message
        self.status_code = status_code
        self.header = header

    def make_response(self):
        res = make_response(jsonify({'message': self.message}), self.status_code)
        if self.header:
            res.headers.extend(self.header)
        return res


class NotFoundException(InvalidUsage):
    def __init__(self, obj):
        if isinstance(obj, str):
            message = obj
        else:
            message = obj.__name__ + ' not found'
        super().__init__(message, 404)
