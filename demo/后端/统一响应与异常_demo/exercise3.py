"""
练习 3：BusinessException + 统一错误 JSON

要练会什么：
  - 业务失败（如「找不到」）用 BusinessException 主动抛出
  - 捕获后转成 { code, message, data }，而不是程序崩溃成 500

运行方式（Windows PowerShell）：
  cd demo\统一响应与异常_demo
  python exercise3.py

依赖：无（Python 3.8+ 自带库即可）

预期输出（大致）：
  [PASS] get memo_id=1 -> code=0
  [PASS] get memo_id=99 -> code=404
  [PASS] delete memo_id=99 -> code=404
  [PASS] plain Exception -> code=500
  ---
  成功: {'code': 0, 'message': 'success', 'data': {'id': 1, 'title': '买菜清单'}}
  404:  {'code': 404, 'message': '备忘录不存在', 'data': None}
  500:  {'code': 500, 'message': '服务器内部错误: 数据库连接失败', 'data': None}
"""

from __future__ import annotations


class BusinessException(Exception):
    """业务异常：预期内的失败，携带 code 和 message"""

    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code
        super().__init__(message)


def success(data=None, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


def to_error_json(exc: BusinessException) -> dict:
    return {"code": exc.code, "message": exc.message, "data": None}


def to_500_json(exc: Exception) -> dict:
    return {"code": 500, "message": f"服务器内部错误: {exc}", "data": None}


# ---------- 模拟 service 层 ----------

DB = {1: {"id": 1, "title": "买菜清单"}}


def get_memo(memo_id: int) -> dict:
    if memo_id not in DB:
        raise BusinessException("备忘录不存在", code=404)
    return DB[memo_id]


def delete_memo(memo_id: int) -> None:
    if memo_id not in DB:
        raise BusinessException("备忘录不存在", code=404)
    del DB[memo_id]


# ---------- 模拟 API 层：统一处理 ----------

def handle_get_memo(memo_id: int) -> dict:
    try:
        memo = get_memo(memo_id)
        return success(memo)
    except BusinessException as e:
        return to_error_json(e)
    except Exception as e:
        return to_500_json(e)


def handle_delete_memo(memo_id: int) -> dict:
    try:
        delete_memo(memo_id)
        return success(message="删除成功")
    except BusinessException as e:
        return to_error_json(e)
    except Exception as e:
        return to_500_json(e)


def simulate_db_crash() -> dict:
    """演示：未用 BusinessException 的异常会变成 500"""
    try:
        raise Exception("数据库连接失败")
    except BusinessException as e:
        return to_error_json(e)
    except Exception as e:
        return to_500_json(e)


# ---------- 自动测试 ----------

def assert_eq(label: str, actual: dict, expected_code: int, expected_message_part: str = "") -> None:
    ok = actual.get("code") == expected_code
    if expected_message_part:
        ok = ok and expected_message_part in (actual.get("message") or "")
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {label} -> code={actual.get('code')}")
    if not ok:
        print(f"       expected code={expected_code}, got {actual}")
        raise SystemExit(1)


def main() -> None:
    r1 = handle_get_memo(1)
    r2 = handle_get_memo(99)
    r3 = handle_delete_memo(99)
    r4 = simulate_db_crash()

    assert_eq("get memo_id=1", r1, 0)
    assert_eq("get memo_id=99", r2, 404, "备忘录不存在")
    assert_eq("delete memo_id=99", r3, 404, "备忘录不存在")
    assert_eq("plain Exception", r4, 500, "服务器内部错误")

    print("---")
    print("成功:", r1)
    print("404: ", r2)
    print("500: ", r4)


if __name__ == "__main__":
    main()
