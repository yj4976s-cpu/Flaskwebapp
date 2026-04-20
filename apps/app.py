from pathlib import Path
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

from apps.config import config

# SQLALchemy를 인스턴스화 한다
db = SQLAlchemy()

csrf = CSRFProtect()
# LoginManager를 인스턴스화한다
login_manager = LoginManager() 
# login_view 속성에 미로그인 시에 리다이렉트하는 엔드포인트를 지정한다
login_manager.login_view = "auth.signup"
# login_message 속성에 로그인 후에 표시하는 메시지를 지정한다
# 여기에서는 아무것도 표시하지 않도록 공백을 지정한다
# 미로그인시 회원가입페이지로 이동
login_manager.login_message = ""

# create_app 함수를 작성한다
def create_app(config_key="local"):
    # 플라스크 인스턴스 생성
    app = Flask(__name__)
    app.config.from_object(config[config_key])

    # # app의 config 설정을 한다
    # app.config.from_mapping(
    #     SECRET_KEY="2AZSMss3p5QPbcY2hBsJ",
    #     SQLALCHEMY_DATABASE_URI=f"sqlite:///{Path(__file__).parent.parent / 'local.sqlite'}",
    #     SQLALCHEMY_TRACK_MEDIFICATIONS=False,
    #     # SQL을 콘솔 로그에 출력하는 설정
    #     SQLALCHEMY_ECHO=True,
    #     WTF_CSRF_SECRET_KEY="AuwzyszU5sugKN7KZs6f",
    # )

    # config를 읽어 들이는 방법 example
    # from_mapping 이용하는 방법
    # app.config.from_mapping(
    # SECRET_KEY="2AZSMss3p5QPbcY2hBsJ",
    #     SQLALCHEMY_DATABASE_URI=f"sqlite:///{Path(__file__).parent.parent / 'local.sqlite'}",
    #     SQLALCHEMY_TRACK_MEDIFICATIONS=False,
    #     # SQL을 콘솔 로그에 출력하는 설정
    #     SQLALCHEMY_ECHO=True,
    #     WTF_CSRF_SECRET_KEY="12345678901234567890",
    # )

    # from_envvar 이용하는 방법
    # 환경 변수에 config 파일의 경로 정보를 기술해 두고, 앱을 실행할 때 환경변수를 지정한 경로를
    # config값 에서 읽어 들이는 방법
    # .env 에 추가
    # APPLICATION_SETTINGS = /path/to/apps/config.py
    # def create_app() 하단에 추가
    # app.config.from_envvar("APPLICATION_SETTINGS")

    # from_pyfile를 사용하는 방법
    # 직업 파이썬 config 파일을 지정해서 읽어 들이는 방버
    # 이방법은 환경별로 py 파일을 만들어 준비하고, 이용하고 싶은 환경에 맞춰 파일을 복사
    # app.config.from_pyfile("config.py") 로 설정한다.

    csrf.init_app(app)
    # SQLALchemy와 앱을 연계한다
    db.init_app(app)
    # Migrate와 앱을 연계한다
    Migrate(app, db)

    login_manager.init_app(app)
    # crud 패키지로부터 views를 import한다
    from apps.crud import views as crud_views

    # register_blueprint를 사용해 views의 crud를 앱에 등록한다
    app.register_blueprint(crud_views.crud, url_prefix="/crud")
    
    from apps.auth import views as auth_views

    # register_blueprint를 이용하여 views와 auth를 앱에 등록한다.
    app.register_blueprint(auth_views.auth, url_prefix="/auth") 

    from apps.detector import views as dt_views
    app.register_blueprint(dt_views.dt)

    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error) 

    return app

def page_not_found(e):
    """404 Not Found"""
    return render_template("404.html"),404

def internal_server_error(e):
    """500 Internal Server Error"""
    return render_template("500.html"),500





