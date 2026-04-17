from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required 
from apps.crud.forms import UserForm

# Blueprint로 crud 앱을 생성한다
crud = Blueprint(
    "crud",
    __name__,
    template_folder="templates",
    static_folder="static",
)

# index 엔드포인트를 작성하고 index.html을 반환한다
@crud.route("/")
@login_required
def index():
    return render_template("crud/index.html")
# db를 import한다
from apps.app import db
# User클래스를 import 한다
from apps.crud.models import User

@crud.route("/sql")
@login_required
def sql():
   
    # db.session.query(User).all()

    # print(
    #     "=============User테이블에 모든 정보 (모델 객체로 처리하는 문)=================="
    # )
    # User.query.all()

    # print("=============User테이블에 처음 1건 가져오기==================")
    # db.session.query(User).first()

    # print("=============User테이블에 처음 1건 가져오기 없으면 404==================")
    # db.session.query(User).first_or_404()

    # print("=============User테이블에 처음 기본키 2번행 ==================")
    # db.session.query(User).get(2)

    # print("=============User테이블에 레코드 개수 출력 ==================")
    # db.session.query(User).count()

    # print("=============User테이블 페이징 처리용 ==================")
    # db.session.query(User).paginate(page=2, per_page=10, error_out=False)

    # print("=============User테이블 where조건 처리용(filter_by) ==================")
    # db.session.query(User).filter_by(id=2, username="admin").all()

    # print("=============User테이블 where조건 처리용(filter) ==================")
    # db.session.query(User).filter(User.id==2, User.username=="admin").all() 

    # print("=============User테이블 where조건 처리용(LIMIT) ==================")
    # db.session.query(User).limit(1).all()

    # print("=============User테이블 where조건 처리용(OFFSET) ==================")
    # db.session.query(User).limit(1).offset(2).all()

    # print("=============User테이블 where조건 처리용(ORDER BY) ==================")
    # db.session.query(User).order_by("username").all()
    # username 오름차순 정렬 order_by(User.username)
    # username 내림차순 정렬 order_by(User.username.desc())
    # 여러 기준 정렬 order_by(User.age, User.username)

    # print("=============User테이블 where조건 처리용(GROUP BY) ==================")
    # db.session.query(User).group_by("username").all()

    print("=======================사용자 추가 테스트=============================")
    # user = User(
    #     username="사용자명",
    #     email="flaskbook@example.com",
    #     password="비밀번호"
    # )
    # db.session.add(user)

    # db.session.commit()

    user = db.session.query(User).filter_by(id=1).first()
    user.username = "사용자명2"
    user.email = "flaskbook2@example.com"
    user.password = "비밀번호2"
    db.session.add(user)
    db.session.commit()

    user = db.session.query(User).filter_by(id=1).delete()
    db.session.commit()
    return "콘솔 로그를 확인해 주세요"

@crud.route("/users/new", methods=["GET", "POST"])
@login_required
def create_user():
    form =  UserForm()
    if form.validate_on_submit():
        # 사용자를 작성한다
        user = User(
            username=form.username.data,
            email=form.email.data,
            password = form.password.data,
        )

        db.session.add(user)
        db.session.commit()
        return redirect(url_for("crud.users"))
    return render_template("crud/create.html", form=form)

@crud.route("/users")
@login_required
def users():
    """사용자의 일람을 취득한다"""
    users = User.query.all()
    return render_template("crud/index.html", users=users)

@crud.route("/users/<user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    form = UserForm()

    user = User.query.filter_by(id=user_id).first()
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("crud.users"))
    return render_template("crud/edit.html",user=user, form=form)

@crud.route("/users/<user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()

    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("crud.users"))
