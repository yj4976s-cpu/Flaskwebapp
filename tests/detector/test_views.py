def test_index(client):
    rv = client.get("/")
    assert "로그인" in rv.data.decode()
    assert "이미지 신규 등록" in rv.data.decode()

def signup(client, username, email, password):
    data = dict(username=username, email=email, password=password)
    return client.post("/auth/signup", data=data, follow_redirects=True)

def test_index_signup(client):
    rv = signup(client, "admin", "flaskbook@example.com", "password")
    assert "admin" in rv.data.decode()
    assert "이미지 신규 등록" in rv.data.decode()

def test_upload_no_auth(client):
    rv =client.get("/upload", follow_redirects=True)
    # 이미지 업로드 화면에는 접근할 수 없다
    assert "업로드" not in rv.data.decode()
    assert "메일 주소" in rv.data.decode()
    assert "비밀번호" in rv.data.decode()

def test_upload_signup_get(client):
    signup(client, "admin", "flaskbook@example.com", "password")
    rv = client.get("/upload")
    assert "업로드" in rv.data.decode()

from pathlib import Path
from flask.helpers import get_root_path
from werkzeug.datastructures import FileStorage
def upload_image(client,image_path):
    image = Path(get_root_path("tests"), image_path)

    test_file = (
        FileStorage(
            stream=open(image,"rb"),
            filename=Path(image_path).name,
            content_type="multipart/form-data",

        ),
    )
    data = dict(
        image=test_file,
    )
    return client.post("/upload", data=data, follow_redirects=True)
def test_upload_signup_post_validate(client):
    signup(client, "admin", "flaskbook@example.com", "password")
    rv= upload_image(client, 
                     "detector/testdata/test_invalid_file.txt")
    assert "지원되지 않는 이미지 형식입니다." in rv.data.decode()


from apps.detector.models import UserImage

def test_upload_signup_post(client):
    signup(client, "admin", "flaskbook@example.com", "password")
    rv = upload_image(client, "detector/testdata/test_valid_image.jpg")
    user_image = UserImage.query.first()
    assert user_image.image_path in rv.data.decode()

def test_detect_no_user_image(client):
    signup(client, "admin", "flaskbook@example.com", "password")
    upload_image(client, "detector/testdata/test_valid_image.jpg")
    rv = client.post("/detect/notexistid",follow_redirects=True)
    assert "물체 대상의 이미지가 존재하지 않습니다." in rv.data.decode()

def test_detect(client):
    signup(client, "admin", "flaskbook@example.com", "password")
    upload_image(client, "detector/testdata/test_valid_image.jpg")
    user_image = UserImage.query.first()

    # 물체 감지를 실행한다
    rv = client.post(f"/detect/{user_image.id}", follow_redirects=True)
    user_image = UserImage.query.first()
    assert user_image.image_path in rv.data.decode()
    assert "dog" in rv.data.decode()

def test_detect_search(client):
    signup(client, "admin", "flaskbook@example.com", "password")
    upload_image(client, "detector/testdata/test_valid_image.jpg")
    user_image = UserImage.query.first()
    client.post(f"/detect/{user_image.id}", follow_redirects=True)
    # dog 단어로 검색한다
    rv = client.get("/images/search?search=dog")
    # dog 태그의 이미지가 있는 것을 확인한다
    assert user_image.image_path in rv.data.decode()
    # dog 태그가 있는 것을 확인한다
    assert "dog" in rv.data.decode()

    # test 단어로 검색한다
    rv = client.get("/images/search?search=test")
    # dog 태그의 이미지가 없는 것을 확인한다
    assert user_image.image_path not in rv.data.decode()
    # dog 태그가 없는 것을 확인한다
    assert "dog" not in rv.data.decode()

def test_delete(client):
    signup(client, "admin", "flaskbook@example.com", "password")
    upload_image(client, "detector/testdata/test_valid_image.jpg")
    user_image = UserImage.query.first()
    image_path = user_image.image_path
    rv= client.post(f"/images/delete/{user_image.id}", follow_redirects =True)
    assert image_path not in rv.data.decode()

def test_custom_error(client):
    rv =  client.get("/notfound")
    assert "404 Not Found" in rv.data.decode()
