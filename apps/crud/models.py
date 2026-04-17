from datetime import datetime

from apps.app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    # 테이블명을 지정한다
    __tablename__="users"
    id =db.Column(db.Integer, primary_key=True)
    username =db.Column(db.String, index=True)
    email = db.Column(db.String, unique=True, index=True)
    password_hash = db.Column(db.String)
    created_at =db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now
    )

    user_images = db.relationship("UserImage", backref="user")
    
    # 비밀번호를 설정하기 위한 프로퍼티
    @property
    def password(self):
        raise AttributeError("읽어 들일수 없음")
    
    # 비밀번호를 설정하기 위해 setter 함수로 해시화한 비밀번호를 설정한다
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # 이메일 주소 중복체크
    def is_duplicate_email(self):
        return User.query.filter_by(email=self.email).first() is not None
    
    # 사용자의 유니크 ID를 인수로 넘겨서 데이터베이스로부터 특정 사용자를 취득해서 반환해야 한다.
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

      