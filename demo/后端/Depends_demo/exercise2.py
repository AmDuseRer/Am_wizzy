"""
练习 2：第一次使用 FastAPI 的 Depends

要练会什么：
  掌握最基础格式：参数名: 类型 = Depends(函数名)

运行方式：
  pip install -r requirements.txt
  python exercise2.py

  （可选）启动服务手动访问：
  uvicorn exercise2:app --reload
  浏览器打开 http://127.0.0.1:8000/welcome

预期输出：
  [PASS] GET /welcome -> 200 {'message': '欢迎光临'}
  ---
  status=200 body={'message': '欢迎光临'}
"""

from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI(title="Exercise 2 - Basic Depends")


def get_greeting() -> str:
    """依赖函数：负责准备 greeting"""
    return "欢迎光临"


@app.get("/welcome")
def welcome(msg: str = Depends(get_greeting)):
    """接口函数体内没有调用 get_greeting()，但 FastAPI 会自动注入 msg"""
    return {"message": msg}


def run_tests() -> None:
    client = TestClient(app)

    response = client.get("/welcome")
    assert response.status_code == 200, response.text
    assert response.json() == {"message": "欢迎光临"}, response.json()

    print("[PASS] GET /welcome -> 200 {'message': '欢迎光临'}")
    print("---")
    print(f"status={response.status_code} body={response.json()}")


if __name__ == "__main__":
    run_tests()
