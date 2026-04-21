# ============================================
# 표준 라이브러리 import
# ============================================
import uuid 
from pathlib import Path  # 파일/디렉터리 경로 처리
from flask import abort, current_app, jsonify
from sqlalchemy.exc import SQLAlchemyError # DB 예외처리

from .models import ImageInfo, db  # SQLAlchemy 모델 및 db세션
# ============================================
# 디렉터리에서 이미지 파일명 읽기
# ============================================

def load_filenames(dir_name:str) -> list[str]:
    """손글씨 문자 이미지가 놓여 있는 패스로부터 파일명을 취득하고, 리스트를 작성"""

    # Flask 설정 파일에서 허용 확장자 목록 읽기
    included_ext = current_app.config["INCLUDED_EXTENSION"]

    # 현재 파일 기준으로 상위 디렉터리로 이동 후 dir_name 경로 생성
    dir_path = Path(__file__).resolve().parent.parent / dir_name
    # 디렉터리 내부 파일/폴더 목록 iterator
    files = Path(dir_path).iterdir()
    # 확장자가 허용된 파일만 골라서 파일명 리스트 생성
    filenames = sorted(
        [
            Path(str(file)).name # 파일 이름만 추출
            for file in files
            if Path(str(file)).suffix in included_ext # 확장자 필터
        ]
    )
    return filenames

# ============================================
# 이미지 파일명을 DB에 저장
# ============================================

def insert_filenames(request) -> tuple:
    """
    요청으로 받은 디렉터리 이름을 기준으로
    이미지 파일명을 데이터베이스에 저장
    """

    # 요청 JSON에서 디렉터리 이름 추출
    dir_name = request.json["dir_name"]

    # 디렉터리 내 이미지 파일명 로드
    filenames = load_filenames(dir_name)

    # 파일 묶음을 구분하기 위한 고유 ID 생성
    file_id = str(uuid.uuid4())

    # 각 파일명을 DB 세션에 추가
    for filename in filenames:
        db.session.add(ImageInfo(file_id=file_id, filename=filename))

    # DB 커밋 시도
    try:
        db.session.commit()
    except SQLAlchemyError as error:
        # 오류 발생 시 롤백
        db.session.rollback()

        # 500 에러와 함께 메시지 반환
        abort(500, {"error_message": str(error)})

    # 성공 시 file_id 반환 (HTTP 201 Created)
    return jsonify({"file_id": file_id}), 201

# ============================================
# file_id로부터 이미지 파일명 조회
# ============================================
def extract_filenames(file_id: str) -> list[str]:
    """
    file_id를 기준으로
    데이터베이스에 저장된 이미지 파일명을 조회
    """

    # file_id에 해당하는 ImageInfo 객체 조회
    img_obj = db.session.query(ImageInfo).filter(ImageInfo.file_id == file_id)

    # 조회 결과에서 filename만 추출
    filenames = [img.filename for img in img_obj if img.filename]

    # 파일명이 하나도 없을 경우
    if not filenames:
        #  abort로는 처리가 멈추기 때문에 변경
        # abort(404, {"error_message": "filenames are not found in database"})

       return jsonify({"error_message": "filenames are not found in database", "result": 404}), 404
    # 정상 조회 시 파일명 리스트 반환
    return filenames