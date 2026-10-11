"""四则运算。

约定：除法不吞异常，除数为 0 直接抛 ZeroDivisionError，由调用方决定怎么处理。
这是 Agent 工具函数的通用写法——工具报错要让上层看得到，才能触发重试或换策略。
"""

from __future__ import annotations

from src.utils.logger import get_logger

logger = get_logger(__name__)


def add(a: float, b: float) -> float:
    result = a + b
    logger.info("add(%s, %s) = %s", a, b, result)
    return result


def subtract(a: float, b: float) -> float:
    result = a - b
    logger.info("subtract(%s, %s) = %s", a, b, result)
    return result


def divide(a: float, b: float) -> float:
    if b == 0:
        logger.error("divide by zero: a=%s", a)
        raise ZeroDivisionError("division by zero")
    result = a / b
    logger.info("divide(%s, %s) = %s", a, b, result)
    return result


# ---------------------------------------------------------------------------
# TODO(10-10 ③做)：自己补两个函数，别照抄上面
#   1. power(base: float, exp: float) -> float        用 ** 实现
#   2. average(nums: list[float]) -> float            空列表要抛 ValueError
# 提示：写完后在 tests/test_ops.py 里加 2 个新测试，pytest 全绿才算完成
# ---------------------------------------------------------------------------

def power(base: float, exp: float) -> float:
    result = base**exp
    logger.info("power(%s, %s) = %s", base, exp, result)
    return result


def average(nums: list[float]) -> float:
    if not nums:
        logger.error("average failed: empty list")
        raise ValueError("average() needs at least one number")
    result = sum(nums) / len(nums)
    logger.info("average(%s) = %s", nums, result)
    return result
