# ============================================
# 라이브러리 import
# ===========================================
import numpy as np
from pathlib import Path
from flask import current_app
from PIL import Image

# ============================================
# 이미지 → 그레이스케일 변환
# ============================================

def get_grayscale(filenames: list[str]):
    """
    손글씨 문자 이미지 파일을 하나씩 읽어서
    그레이스케일(L 모드) 이미지로 변환하여 반환하는 제너레이터 함수
    """
    # Flask 설정에서 이미지가 저장된 디렉터리 이름 가져오기
    dir_name = current_app.config["DIR_NAME"]
    dir_path = Path(__file__).resolve().parent.parent / dir_name
    for filename in filenames:
        img = Image.open(f'{dir_path}/{filename}').convert('L')
        yield img
# ============================================
# 이미지 축소 및 명암 정규화 (8x8, 16계조)
# ============================================
def shrink_image(img, offset = 5, crop_size: int = 8, pixel_size: int = 255, max_size : int = 16):
    """이미지 크기를 8×8 픽셀의 크기로 통일하고, 밝기도 16계조의 그레이스케일로 흑백으로 변환하는 함수"""
    img_array = np.asarray(img)
    h_indxis = np.where(img_array.min(axis=0) < 255)
    v_indxis = np.where(img_array.min(axis=1) < 255)
    h_min, h_max = h_indxis[0].min(), h_indxis[0].max()
    v_min, v_max = v_indxis[0].min(), v_indxis[0].max()
    width, hight = h_max-h_min, v_max-v_min

    # ============================================
    # 가로/세로 비율에 따라 crop 영역 계산
    # ============================================
    if width > hight:
        center = (v_max + v_min) // 2
        left = h_min - offset
        upper = (center -width // 2) -1 -offset
        right = h_max + offset
        lower = (center + width // 2) + offset
    else:
        center = (h_max + h_min +1)//2
        left = (center - hight // 2) -1 - offset
        upper = v_min - offset
        right = (center + hight // 2) + offset
        lower = v_max + offset
    # ============================================
    # 이미지 crop 및 8x8 리사이즈
    # ============================================
    img_croped = img.crop((left, upper, right, lower)).resize((crop_size, crop_size))
    img_data256 = pixel_size - np.asarray(img_croped)
    # ============================================
    # 명암값 정규화 (0~16)
    # ============================================
    min_bright, max_bright = img_data256.min(), img_data256.max()
    img_data16 = (img_data256 - min_bright) / (max_bright - min_bright) * max_size
    return img_data16

# ============================================
# 모델 입력용 데이터 생성
# ============================================
def get_shrinked_img(filenames: list[str]):
    """
    여러 개의 손글씨 이미지를
    모델 입력용 (N, 64) numpy 배열로 변환하는 함수
    """
    # 빈 테스트 데이터 배열 생성
    img_test=np.empty((0, 64))
    for img in get_grayscale(filenames):
        img_data16 = shrink_image(img)
        img_test = np.r_[img_test, img_data16.astype(np.uint8).reshape(1, -1)]
    return img_test