import pytest
def test_func1():
    assert 1 == 1

def test_func2():
    assert 2 == 2

# pytest fixture (픽스처)
# 테스트 함수의 앞뒤에 처리하는 기능
# 예를 들어 데이터베이스를 사용하는 테스트하는 경우 테스트 함수 실행전에 데이터베이스 셋팅을 실시
# 테스트 종료 후에는 클린업(데이터베이스 close : 정제)를 실시할 수 있다

# @pytest.fixture
# def app_data():
#     return 3

def test_func3(app_data):
    assert app_data == 3