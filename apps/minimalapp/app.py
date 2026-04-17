from email_validator import validate_email, EmailNotValidError
from flask_debugtoolbar import DebugToolbarExtension
import logging
import os
from flask_mail import Mail, Message
from dotenv import load_dotenv


# import문이 길어지므로 줄 바꿈
from flask import (
    Flask,
    render_template,
    current_app,
    g,
    url_for,
    request,
    redirect,
    flash,
    make_response,
    session,
)

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = "2AZSMss3p5QPbcY2hBsJ"
# 로그 레벨을 설정한다
app.logger.setLevel(logging.DEBUG)
app.logger.critical("fetal error")
app.logger.error("error")
app.logger.warning("warning")
app.logger.info("info")
app.logger.debug("debug")

# 리다이렉트를 중단하지 않도록 한다
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
# DebugToolbarExtension에 애플리케이션을 설정한다
toolbar = DebugToolbarExtension(app)


# Mail 클래스의 config를 추가한다
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "True") == "True"
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")


@app.route("/")
def index():
    return "Hello, Flaskbook!"


@app.route("/hello/<name>", methods=["GET", "POST"], endpoint="hello-endpoint")
def hello(name):
    return f"Hello, {name}!"


@app.route("/name/<name>")
def show_name(name):
    return render_template("index.html", name=name)


with app.test_request_context():
    print(url_for("index"))
    print(url_for("hello-endpoint", name="world"))
    print(url_for("show_name", name="AK", page="1"))

ctx = app.app_context()
ctx.push()

print(current_app.name)

g.connection = "connection"
print(g.connection)

with app.test_request_context("/users?updated=true"):
    print(request.args.get("updated"))


@app.route("/contact")
def contact():
    # 응답 객체를 취득한다
    response = make_response(make_response(render_template("contact.html")))

    # 쿠키를 설정한다
    response.set_cookie("flaskbook key", "flaskbook value")

    # 세션을 설정한다
    session["username"] = "AK"

    return response


@app.route("/contact/complete", methods=["GET", "POST"])
def contact_complete():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        description = request.form["description"]

        # 입력체크
        is_valid = True
        if not username:
            flash("사용자명은 필수입니다")
            is_valid = False
        if not email:
            flash("메일 주소는 필수입니다 ")
            is_valid = False
        try:
            validate_email(email)
        except EmailNotValidError:
            flash("메일 주소의 형식으로 입력해 주세요")
            is_valid = False

        if not description:
            flash("문의 내용은 필수입니다")
            is_valid = False

        if not is_valid:
            return redirect(url_for("contact"))
            # .env에 내용 확인용 코드
        print("MAIL_USERNAME:", app.config["MAIL_USERNAME"])
        print("MAIL_PASSWORD:", app.config["MAIL_PASSWORD"])
        print("MAIL_SERVER:", app.config["MAIL_SERVER"])
        print("MAIL_PORT:", app.config["MAIL_PORT"])
        print("MAIL_USE_TLS:", app.config["MAIL_USE_TLS"])

        # 문의 완료 엔드 포인트로 리다이렉트한다
        flash("문의해주셔서 감사합니다.")

        # 이메일을 보낸다
        send_email(
            email,
            "문의 감사합니다.",
            "contact_mail",
            username=username,
            description=description,
        )
        flash("문의해 주셔서 감사합니다.")
        return redirect(url_for("contact_complete"))
        # 메서드가 POST로 요청이 들어오면 앤드포인트로 리다이렉트 한다.

    return render_template("contact_complete.html")


# flask-maiil 확장을 등록한다
mail = Mail(app)


def send_email(to, subject, template, **kwargs):
    """메일을 송신하는 함수"""
    msg = Message(subject, recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    mail.send(msg)
