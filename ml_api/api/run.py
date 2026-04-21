import json
import os
from pathlib import Path

from flask import Flask
from flask_migrate import Migrate

from . import api
from .config import config
from .models import db


def create_app():
    config_name = os.environ.get("CONFIG", "local")

    app = Flask(__name__)
    app.config.from_object(config.config[config_name])

    # JSON schema 로딩
    config_json_path = Path(__file__).parent / "config" / "json-schemas"
    for p in config_json_path.glob("*.json"):
        with open(p) as f:
            json_name = p.stem
            schema = json.load(f)
        app.config[json_name] = schema

    db.init_app(app)
    return app


app = create_app()

# DB 마이그레이션
Migrate(app, db)

# blueprint 등록
app.register_blueprint(api)


# 실행 테스트 파워셀
# Invoke-RestMethod `
#   -Uri http://127.0.0.1:5000/v1/check-schema `
#   -Method POST `
#   -ContentType "application/json" `
#   -Body '{"file_id": 1, "file_name": "handwriting"}'

# cmd
# curl http://127.0.0.1:5000/v1/check-schema ^
# -X POST ^
# -H "Content-Type: application/json" ^
# -d "{\"file_id\": 1, \"file_name\": \"handwriting\"}"

# 이미지를 데이터베이스에 저장하고 응답으로 서 파일 id를 받는 테스트
# Invoke-RestMethod `
#   -Uri http://127.0.0.1:5000/v1/file-id `
#   -Method POST `
#   -ContentType "application/json" `
#   -Body '{"dir_name":"handwriting_pics"}'