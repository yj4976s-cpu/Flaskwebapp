from functools import wraps
from flask import (
    current_app,
    jsonify,
    request,
)

from jsonschema import ValidationError, validate
from werkzeug.exceptions import BadRequest

def validate_json(f):
    @wraps(f)
    def wrapper(*args, **kw):
        ctype = request.headers.get("Content-Type", "")
        method_ = request.headers.get("X-HTTP-Method-Overide", request.method)

        if method_.lower() == request.method.lower() and "json" in ctype:
            try:
                # body 메시지가 애당초 있는지 여부를 확인한다
                request.json
            except BadRequest as e:
                msg ="This is invalid json"
                return jsonify({"error": msg}),400
            return f(*args, **kw)
    return wrapper
def validate_schema(schema_name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kw):
            try:
                # 조금 전 정의한 json파일 대로 json의 body 메세지가 보내졌는지 확인한다
                validate(request.json, current_app.config[schema_name])
            except ValidationError as e:
                return jsonify({"error": e.message}), 400
            
            return f(*args, **kw)
        return wrapper
    return decorator
