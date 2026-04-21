
import pickle  # 학습된 모델(pickle 파일) 로드

import numpy as np  # 수치 계산 및 배열 처리
from flask import jsonify  # JSON 응답 생성

# 내부 모듈 import
from .preparation import extract_filenames  # file_id → 이미지 파일명 조회
from .preprocess import get_shrinked_img  # 이미지 전처리 (8x8, 64차원)

# ============================================
# 손글씨 예측 및 결과 평가 함수
# ============================================


def evaluate_probs(request) -> tuple:
    """
    file_id에 해당하는 손글씨 이미지들을 불러와
    학습된 로지스틱 회귀 모델로 예측하고
    결과와 정확도를 JSON 형태로 반환하는 함수
    """

    # ============================================
    # 1. 요청 데이터에서 file_id 추출
    # ============================================

    file_id = request.json["file_id"]

    # ============================================
    # 2. DB에서 file_id에 해당하는 이미지 파일명 조회
    # ============================================

    filenames = extract_filenames(file_id)

    # ============================================
    # 3. 이미지 전처리 → 모델 입력 데이터 생성
    #    (N, 64) 형태의 numpy 배열
    # ============================================

    img_test = get_shrinked_img(filenames)

    # ============================================
    # 4. 저장된 학습 모델 로드
    # ============================================

    # pickle 파일을 바이너리 읽기 모드로 열기
    with open("model.pickle", mode="rb") as fp:
        model = pickle.load(fp)

    # ============================================
    # 5. 정답(label) 생성 (파일명 기반)
    #    예: "3_test.png" → 3
    # ============================================

    X_true = [int(filename[:1]) for filename in filenames]
    X_true = np.array(X_true)

    # ============================================
    # 6. 모델 예측 및 정확도 계산
    # ============================================

    # 예측 결과 (numpy → list 변환, JSON 응답용)
    predicted_result = model.predict(img_test).tolist()

    # 정확도 계산 (float → JSON 직렬화 가능 형태)
    accuracy = model.score(img_test, X_true)

    # 관측 결과(정답)
    observed_result = X_true.tolist()

    # ============================================
    # 7. 결과 JSON 응답 반환
    # ============================================

    return jsonify(
        {
            "results": {
                "file_id": file_id,  # 요청에 사용된 file_id
                "observed_result": observed_result,  # 실제 값
                "predicted_result": predicted_result,  # 예측 값
                "accuracy": accuracy,  # 예측 정확도
            }
        }
       
    ), 201  # HTTP 상태 코드 (Created)