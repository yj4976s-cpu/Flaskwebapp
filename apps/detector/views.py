from flask_login import current_user, login_required
from flask import ( Blueprint, render_template, current_app, send_from_directory,
redirect, url_for, flash, request)
from apps.app import db
from apps.crud.models import User
from apps.detector.models import UserImage, UserImageTag
from pathlib import Path
from PIL import Image  
from sqlalchemy.exc import SQLAlchemyError  
import cv2  
import numpy as np  
import torch  
import torchvision 
import random
import uuid
from apps.detector.forms import UploadImageForm, DetectorForm, DeleteForm
# template_folder를 지정한다(static은 지정하지 않는다)
dt = Blueprint("detector", __name__, template_folder="templates")

@dt.route("/")

def index():
    user_images = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .all()
    )

    user_image_tag_dict = {}
    for user_image in user_images:
        user_image_tags = (
            db.session.query(UserImageTag)
            .filter(UserImageTag.user_image_id ==
                    user_image.UserImage.id)
            .all()
        )
        user_image_tag_dict[user_image.UserImage.id] =  user_image_tags

    detector_form = DetectorForm()
    delete_form = DeleteForm()
    return render_template(
        "detector/index.html",
        user_images=user_images,
        user_image_tag_dict=user_image_tag_dict,
        detector_form=detector_form,
        delete_form=delete_form
        )

@dt.route("/images/<path:filename>")
def image_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)

@dt.route("/upload", methods=["GET", "POST"])

@login_required
def upload_image():
    form = UploadImageForm()
    if form.validate_on_submit():
        file = form.image.data
        ext = Path(file.filename).suffix
        image_uuid_file_name = str(uuid.uuid4()) + ext
        image_path = Path(
            current_app.config["UPLOAD_FOLDER"], image_uuid_file_name

        )
        file.save(image_path)
        user_image = UserImage(
            user_id=current_user.id, image_path=image_uuid_file_name
        )
        db.session.add(user_image)
        db.session.commit()

        return redirect(url_for("detector.index"))
    return render_template("detector/upload.html", form=form)
def make_color(labels):
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in labels]
    color = random.choice(colors)
    return color
def make_line(result_image):
    line =  round(0.0002* max(result_image.shape[0:2]))+1
    return line

def draw_lines(c1, c2, result_image, line, color):
    # 사각형의 테두리 선을 이미지에 덧붙여씀
    cv2.rectangle(result_image, c1, c2, color, thickness=line)
    return cv2
def draw_texts(result_image, line, c1, c2, color, labels, label):
    display_txt = f"{labels[label]}"
    font = max(line - 1, 1)
    t_size = cv2.getTextSize(display_txt, 0, fontScale=line / 3, thickness=font)[0]
    c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
    cv2.rectangle(result_image,c1,c2,color, -1)
    cv2.putText(
        result_image,
        display_txt,
        (c1[0], c1[1] - 2),
        0,
        line / 3,
        [255, 255, 255],
        thickness=font,
        lineType=cv2.LINE_AA,
    )
    return cv2

def exec_detect(target_image_path):
    labels = current_app.config["LABELS"]
    image =  Image.open(target_image_path)
    image_tensor = torchvision.transforms.functional.to_tensor(image)
    model = torch.load(Path(current_app.root_path, "detector", "model.pt"), weights_only=False)
    # 모델의 추론 모드로 전환
    model = model.eval()

    # 추론 실행
    output = model([image_tensor])[0]

    tags = []
    result_image = np.array(image.copy())

    # 학습 완료 모델이 감지한 각 물체만큼 이미지에 덧붙여씀
    for box, label, score in zip(
        output["boxes"], output["labels"], output["scores"]

    ):
        if score > 0.5 and labels[label] not in tags:
            color = make_color(labels)
            line = make_line(result_image)
            # 감지 이미지의 테두리 선과 텍스트 라벨의 테두리 선의 위치 정보
            c1 = (int(box[0]), int(box[1]))
            c2 = (int(box[2]), int(box[3]))
            # 이미지에 테두리 선을 덧붙여 씀
            cv2 = draw_lines(c1, c2, result_image, line, color)
            # 이미지에 텍스트 라벨을 덧붙여 씀
            cv2 = draw_texts(result_image, line, c1, cv2, color, labels, label)
            tags.append(labels[label])

    detected_image_file_name =  str(uuid.uuid4()) + ".jpg"

        # 이미지 복사처 패스를 취득한다
    detected_image_file_path = str(
    Path(current_app.config["UPLOAD_FOLDER"], detected_image_file_name)
    )

    # 변환 후의 이미지 파일을 보존처로 복사한다
    cv2.imwrite(detected_image_file_path, cv2.cvtColor(
        result_image, cv2.COLOR_RGB2BGR)
    )

    return tags, detected_image_file_name

def save_detected_image_tags(user_image,tags, detected_image_file_name):
        # 감지 후 이미지의 보존처 패스를 DB에 보존한다
    user_image.image_path = detected_image_file_name
    # 감지 플래그를 True로 한다
    user_image.is_detected = True
    db.session.add(user_image)

    for tag in tags:
        user_image_tag = UserImageTag(user_image_id=user_image.id, tag_name=tag)
        db.session.add(user_image_tag)
    db.session.commit()

@dt.route("/detect/<string:image_id>", methods = ["POST"])
@login_required

def detect(image_id):
    user_image = db.session.query(UserImage).filter(
            UserImage.id == image_id).first()
    if user_image is None:
        flash("물체 대상의 이미지가 존재하지 않습니다.")
        return redirect(url_for("detector.index"))
    
  # 물체 감지 대상의 이미지 경로를 가져온다
    target_image_path = Path(
        current_app.config["UPLOAD_FOLDER"], user_image.image_path
    )

    # 물체 감지를 실행하여 태그와 변환 후의 이미지 경로를 가져온다
    tags, detected_image_file_name = exec_detect(target_image_path)

    try:
        # 데이터베이스에 태그와 변환 후의 이미지 패스 정보를 저장한다
        save_detected_image_tags(user_image, tags, detected_image_file_name)
    except SQLAlchemyError as e:
        flash("물체 감지 처리에서 오류가 발생했습니다. ")
        # 롤백한다
        db.session.rollback()
        # 오류 로그 출력
        current_app.logger.error(e)
        return redirect(url_for("detector.index"))
    return redirect(url_for("detector.index"))
    
@dt.route("/images/delelte/<string:image_id>", methods=["POST"])

@login_required
def delete_image(image_id):
    try:
        # user_image_tags 테이블로부터 레코드를 삭제한다
        db.session.query(UserImageTag).filter(
            UserImageTag.user_image_id == image_id
        ).delete()
        # user_images 테이블로부터 레코드를 삭제한다
        db.session.query(UserImage).filter(UserImage.id == image_id).delete()

        db.session.commit()
    except SQLAlchemyError as e:
        flash("이미지 삭제 처리에서 오류가 발생했습니다. ")
        current_app.logger.error(e)
        db.session.rollback()
    return redirect(url_for("detector.index"))

@dt.route("/images/search", methods=["GET"])
def search():
    user_images = db.session.query(User,UserImage).join(
        UserImage, User.id == UserImage.user_id)
    
    search_text = request.args.get("search")
    user_image_tag_dict = {}
    filtered_user_images = []
    # user_images를 반복하여 user_images에 연결된 정보를 검색한다
    for user_image in user_images:
        if not search_text:
            user_image_tags = (
                db.session.query(UserImageTag)
                .filter(UserImageTag.user_image_id == user_image.UserImage.id)
                .all()

            )
        else:
            user_image_tags = (
                db.session.query(UserImageTag)
                .filter(UserImageTag.user_image_id == user_image.UserImage.id)
                .filter(UserImageTag.tag_name.like( "%" + search_text + "%"))
                .all()

            )

            if not user_image_tags:
                continue
            
            user_image_tags = (
                db.session.query(UserImageTag)
                .filter(UserImageTag.user_image_id == user_image.UserImage.id)
                .all()
            )
        
        # user_image_id를 키로 하는 사전에 태그 정보를 설정한다
        user_image_tag_dict[user_image.UserImage.id] = user_image_tags

        filtered_user_images.append(user_image)
        delete_form = DeleteForm()
        detector_form = DetectorForm()

    return render_template(
        "detector/index.html",
        user_images=filtered_user_images,
        user_image_tag_dict=user_image_tag_dict,
        delete_form=delete_form,
        detector_form=detector_form,
    )
